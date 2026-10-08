import os
import sys
import tempfile
from datetime import date, datetime, time, timezone
from pathlib import Path
from uuid import uuid4

import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

load_dotenv(ROOT / ".env")

from app.database.db import Base, SessionLocal, engine
from app.models.certificate import Certificate
from app.services.hashing_service import calculate_file_hash
from app.services.pdf_service import generate_certificate_pdf
from app.services.blockchain_service import (
    issue_certificate_on_blockchain,
    verify_certificate_on_blockchain,
    get_certificate_from_blockchain,
    revoke_certificate_on_blockchain,
)

Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title="CertiChain | Blockchain Certificate Verification",
    page_icon="🔐",
    layout="wide",
)

st.markdown("""
<style>
.main-title {font-size: 2.4rem; font-weight: 800; margin-bottom: .2rem;}
.subtitle {color: #64748b; font-size: 1.05rem; margin-bottom: 1.5rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🔐 CertiChain</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Blockchain-based certificate issuance, verification and revocation</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Go to",
        [
            "Dashboard",
            "Issue Certificate",
            "Verify Certificate",
            "Certificate Details",
            "Revoke Certificate",
        ],
    )
    st.divider()
    st.caption("Blockchain: Ganache / Web3")
    st.caption("Hashing: SHA-256")
    st.caption("Smart Contract: Solidity")
    st.caption("Database: SQLite")


def get_db():
    return SessionLocal()


def certificate_dict(c):
    return {
        "Certificate ID": c.certificate_id,
        "Student": c.student_name,
        "Roll Number": c.roll_number or "N/A",
        "Course": c.course,
        "Institution": c.institution,
        "Issue Date": c.issue_date,
        "Status": c.status,
        "Certificate Hash": c.certificate_hash or "",
        "Transaction Hash": c.blockchain_tx_hash or "",
        "Block Number": c.blockchain_record_id,
    }


if page == "Dashboard":
    db = get_db()
    try:
        certificates = (
            db.query(Certificate)
            .order_by(Certificate.id.desc())
            .all()
        )

        total = len(certificates)
        issued = sum(c.status == "ISSUED" for c in certificates)
        revoked = sum(c.status == "REVOKED" for c in certificates)
        failed = sum(
            c.status in ("FAILED", "BLOCKCHAIN_FAILED")
            for c in certificates
        )

        st.subheader("System Overview")
        a, b, c, d = st.columns(4)
        a.metric("Total Certificates", total)
        b.metric("Issued", issued)
        c.metric("Revoked", revoked)
        d.metric("Failed", failed)

        st.divider()
        st.subheader("Recent Certificates")

        if certificates:
            rows = [
                {
                    "Certificate ID": x.certificate_id,
                    "Student": x.student_name,
                    "Course": x.course,
                    "Issue Date": x.issue_date,
                    "Status": x.status,
                    "Block": x.blockchain_record_id or "-",
                }
                for x in certificates[:15]
            ]
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("No certificates have been issued yet.")
    finally:
        db.close()


elif page == "Issue Certificate":
    st.subheader("📜 Issue a New Certificate")
    st.info(
        "The certificate PDF is generated, hashed with SHA-256, "
        "and the hash is registered on the blockchain."
    )

    with st.form("issue_form"):
        col1, col2 = st.columns(2)

        with col1:
            student_name = st.text_input("Student Name *")
            roll_number = st.text_input("Roll Number")
            course = st.text_input("Course *")

        with col2:
            institution = st.text_input("Institution *")
            issue_date = st.date_input("Issue Date", value=date.today())

        submitted = st.form_submit_button(
            "🔗 Issue Certificate",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not student_name.strip() or not course.strip() or not institution.strip():
            st.error("Please fill all required fields.")
        else:
            db = get_db()

            try:
                certificate_id = "CERT-" + uuid4().hex[:10].upper()

                cert = Certificate(
                    certificate_id=certificate_id,
                    student_name=student_name.strip(),
                    roll_number=roll_number.strip() or None,
                    course=course.strip(),
                    institution=institution.strip(),
                    issue_date=issue_date.isoformat(),
                    status="PENDING",
                )

                db.add(cert)
                db.commit()
                db.refresh(cert)

                with st.spinner("Generating certificate PDF..."):
                    pdf_path = generate_certificate_pdf(
                        certificate_id=certificate_id,
                        student_name=student_name.strip(),
                        roll_number=roll_number.strip() or None,
                        course=course.strip(),
                        institution=institution.strip(),
                        issue_date=issue_date.isoformat(),
                    )

                    cert_hash = calculate_file_hash(pdf_path)
                    cert.pdf_path = pdf_path
                    cert.certificate_hash = cert_hash
                    db.commit()

                with st.spinner("Registering certificate on blockchain..."):
                    issue_timestamp = int(
                        datetime.combine(
                            issue_date,
                            time.min,
                            tzinfo=timezone.utc,
                        ).timestamp()
                    )

                    result = issue_certificate_on_blockchain(
                        certificate_id=certificate_id,
                        student_name=student_name.strip(),
                        course=course.strip(),
                        institution=institution.strip(),
                        certificate_hash=cert_hash,
                        issue_date=issue_timestamp,
                    )

                cert.blockchain_tx_hash = result["transaction_hash"]
                cert.blockchain_record_id = result["block_number"]
                cert.status = "ISSUED"
                db.commit()

                st.success(f"Certificate issued successfully: {certificate_id}")
                st.write("**SHA-256 hash:**")
                st.code(cert_hash)
                st.write(f"**Blockchain block:** {result['block_number']}")
                st.write(f"**Transaction:** `{result['transaction_hash']}`")

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Certificate PDF",
                        f,
                        file_name=f"{certificate_id}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

            except Exception as e:
                db.rollback()
                st.error(f"Certificate issuance failed: {e}")

            finally:
                db.close()


elif page == "Verify Certificate":
    st.subheader("🔍 Verify Certificate")
    st.write(
        "Upload the original certificate PDF and compare its SHA-256 "
        "hash with the blockchain record."
    )

    certificate_id = st.text_input(
        "Certificate ID",
        placeholder="CERT-XXXXXXXXXX",
    )

    uploaded = st.file_uploader(
        "Upload Certificate PDF",
        type=["pdf"],
    )

    if st.button(
        "🔎 Verify on Blockchain",
        type="primary",
        use_container_width=True,
    ):
        if not certificate_id.strip() or uploaded is None:
            st.warning("Enter a Certificate ID and upload the certificate PDF.")
        else:
            db = get_db()
            temp_path = None

            try:
                cert = (
                    db.query(Certificate)
                    .filter(
                        Certificate.certificate_id
                        == certificate_id.strip()
                    )
                    .first()
                )

                if not cert:
                    st.error("Certificate not found in the local database.")
                else:
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf",
                    ) as tmp:
                        tmp.write(uploaded.getvalue())
                        temp_path = tmp.name

                    uploaded_hash = calculate_file_hash(temp_path)

                    result = verify_certificate_on_blockchain(
                        certificate_id.strip(),
                        uploaded_hash,
                    )

                    st.write("**Uploaded PDF SHA-256:**")
                    st.code(uploaded_hash)

                    if result["is_revoked"]:
                        st.error(
                            "❌ REVOKED — This certificate has been revoked."
                        )
                    elif result["is_valid"]:
                        st.success(
                            "✅ VALID — Certificate matches the blockchain record."
                        )
                    else:
                        st.error(
                            "❌ INVALID — The uploaded certificate does not "
                            "match the blockchain hash."
                        )

                    with st.expander("Certificate record"):
                        st.json(certificate_dict(cert))

            except Exception as e:
                st.error(f"Verification failed: {e}")

            finally:
                db.close()
                if temp_path:
                    Path(temp_path).unlink(missing_ok=True)


elif page == "Certificate Details":
    st.subheader("📋 Certificate Details")

    certificate_id = st.text_input(
        "Enter Certificate ID",
        placeholder="CERT-XXXXXXXXXX",
    )

    if st.button("Fetch Blockchain Record", type="primary"):
        if not certificate_id.strip():
            st.warning("Enter a Certificate ID.")
        else:
            try:
                result = get_certificate_from_blockchain(
                    certificate_id.strip()
                )

                left, right = st.columns(2)

                with left:
                    st.write("**Certificate ID:**", result["certificate_id"])
                    st.write("**Student:**", result["student_name"])
                    st.write("**Course:**", result["course"])
                    st.write("**Institution:**", result["institution"])

                with right:
                    st.write("**Issuer:**", result["issuer"])
                    st.write("**Issue timestamp:**", result["issue_date"])
                    st.write(
                        "**Revoked:**",
                        "Yes" if result["revoked"] else "No",
                    )

                st.write("**Blockchain SHA-256 hash:**")
                st.code(result["certificate_hash"])

            except Exception as e:
                st.error(f"Could not fetch certificate: {e}")


elif page == "Revoke Certificate":
    st.subheader("🚫 Revoke Certificate")

    st.warning(
        "Revocation is an on-chain operation and marks the certificate "
        "as revoked in the smart contract."
    )

    certificate_id = st.text_input(
        "Certificate ID",
        placeholder="CERT-XXXXXXXXXX",
    )

    if st.button("Revoke on Blockchain", type="primary"):
        if not certificate_id.strip():
            st.warning("Enter a Certificate ID.")
        else:
            db = get_db()

            try:
                cert = (
                    db.query(Certificate)
                    .filter(
                        Certificate.certificate_id
                        == certificate_id.strip()
                    )
                    .first()
                )

                if not cert:
                    st.error("Certificate not found.")

                elif cert.status == "REVOKED":
                    st.warning("Certificate is already revoked.")

                else:
                    result = revoke_certificate_on_blockchain(
                        certificate_id.strip()
                    )

                    cert.status = "REVOKED"
                    db.commit()

                    st.success("Certificate revoked successfully.")
                    st.write(f"**Block:** {result['block_number']}")
                    st.write(
                        f"**Transaction:** `{result['transaction_hash']}`"
                    )

            except Exception as e:
                db.rollback()
                st.error(f"Revocation failed: {e}")

            finally:
                db.close()
