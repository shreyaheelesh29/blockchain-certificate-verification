from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import tempfile

from app.database.db import get_db
from app.models.certificate import Certificate
from app.services.hashing_service import calculate_file_hash
from app.services.blockchain_service import (
    verify_certificate_on_blockchain,
    get_certificate_from_blockchain
)


router = APIRouter(
    prefix="/verification",
    tags=["Verification"]
)

@router.get("/status/{certificate_id}")
def get_certificate_status(
    certificate_id: str,
    db: Session = Depends(get_db)
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

    try:
        blockchain_certificate = (
            get_certificate_from_blockchain(
                certificate_id
            )
        )

        if blockchain_certificate["revoked"]:
            return {
                "certificate_id": certificate_id,
                "status": "REVOKED",
                "message": "Certificate has been revoked."
            }

        return {
            "certificate_id": certificate_id,
            "status": "VALID",
            "message": "Certificate is registered and valid on the blockchain."
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Blockchain verification failed: {str(error)}"
        )

@router.post("/verify")
async def verify_certificate(
    certificate_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
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

    temp_path = None

    try:
        file_data = await file.read()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name

        uploaded_hash = calculate_file_hash(
            temp_path
        )

        blockchain_result = (
            verify_certificate_on_blockchain(
                certificate_id,
                uploaded_hash
            )
        )

        is_valid = blockchain_result["is_valid"]
        is_revoked = blockchain_result["is_revoked"]

        if is_revoked:
            status = "REVOKED"
            message = "Certificate has been revoked."

        elif is_valid:
            status = "VALID"
            message = "Certificate verified successfully."

        else:
            status = "INVALID"
            message = "Certificate does not match the blockchain record."

        return {
            "certificate_id": certificate_id,
            "is_valid": is_valid,
            "is_revoked": is_revoked,
            "status": status,
            "message": message
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)