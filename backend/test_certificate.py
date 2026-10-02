from app.database.db import SessionLocal
from app.models.certificate import Certificate


db = SessionLocal()

certificate = (
    db.query(Certificate)
    .filter(
        Certificate.certificate_id == "CERT-C1485C7825"
    )
    .first()
)

if certificate:
    print("Certificate ID:", certificate.certificate_id)
    print("PDF Path:", certificate.pdf_path)
    print("SHA-256 Hash:", certificate.certificate_hash)
    print("Status:", certificate.status)
else:
    print("Certificate not found")

db.close()