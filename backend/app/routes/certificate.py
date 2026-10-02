from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timezone

from app.database.db import get_db
from app.models.certificate import Certificate
from app.schemas.certificate import (
    CertificateCreate,
    CertificateResponse
)
from app.models.user import User
from app.utils.auth_dependency import get_current_user

from app.services.pdf_service import generate_certificate_pdf
from app.services.hashing_service import calculate_file_hash
from app.services.blockchain_service import (
    issue_certificate_on_blockchain,
    revoke_certificate_on_blockchain
)


router = APIRouter(
    prefix="/certificates",
    tags=["Certificates"]
)


@router.post(
    "/create",
    response_model=CertificateResponse
)
def create_certificate(
    certificate_data: CertificateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    certificate_id = (
        "CERT-" +
        uuid4().hex[:10].upper()
    )

    new_certificate = Certificate(
        certificate_id=certificate_id,
        student_name=certificate_data.student_name,
        roll_number=certificate_data.roll_number,
        course=certificate_data.course,
        institution=certificate_data.institution,
        issue_date=certificate_data.issue_date,
        status="PENDING"
    )

    db.add(new_certificate)
    db.commit()
    db.refresh(new_certificate)

    try:
        pdf_path = generate_certificate_pdf(
            certificate_id=certificate_id,
            student_name=certificate_data.student_name,
            roll_number=certificate_data.roll_number,
            course=certificate_data.course,
            institution=certificate_data.institution,
            issue_date=certificate_data.issue_date
        )

        certificate_hash = calculate_file_hash(
            pdf_path
        )

        new_certificate.pdf_path = pdf_path
        new_certificate.certificate_hash = certificate_hash

        db.commit()
        db.refresh(new_certificate)

    except Exception as error:
        new_certificate.status = "FAILED"
        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Certificate generation failed: {str(error)}"
        )

    try:
        issue_date_object = datetime.strptime(
            certificate_data.issue_date,
            "%Y-%m-%d"
        )

        issue_date_timestamp = int(
            issue_date_object.replace(
                tzinfo=timezone.utc
            ).timestamp()
        )

    except ValueError:
        new_certificate.status = "FAILED"
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Invalid issue_date format. Use YYYY-MM-DD."
        )

    try:
        blockchain_result = issue_certificate_on_blockchain(
            certificate_id=certificate_id,
            student_name=certificate_data.student_name,
            course=certificate_data.course,
            institution=certificate_data.institution,
            certificate_hash=certificate_hash,
            issue_date=issue_date_timestamp
        )

        new_certificate.blockchain_tx_hash = (
            blockchain_result["transaction_hash"]
        )

        new_certificate.blockchain_record_id = (
            blockchain_result["block_number"]
        )

        new_certificate.status = "ISSUED"

        db.commit()
        db.refresh(new_certificate)

    except Exception as error:
        new_certificate.status = "BLOCKCHAIN_FAILED"
        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Blockchain issuance failed: {str(error)}"
        )

    return new_certificate


@router.post("/revoke/{certificate_id}")
def revoke_certificate(
    certificate_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    certificate = (
        db.query(Certificate)
        .filter(
            Certificate.certificate_id == certificate_id
        )
        .first()
    )

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    if certificate.status == "REVOKED":
        raise HTTPException(
            status_code=400,
            detail="Certificate already revoked"
        )

    try:
        blockchain_result = revoke_certificate_on_blockchain(
            certificate_id
        )

        certificate.status = "REVOKED"

        db.commit()
        db.refresh(certificate)

        return {
            "certificate_id": certificate_id,
            "status": "REVOKED",
            "transaction_hash": blockchain_result[
                "transaction_hash"
            ],
            "block_number": blockchain_result[
                "block_number"
            ],
            "message": "Certificate revoked successfully."
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Blockchain revocation failed: {str(error)}"
        )