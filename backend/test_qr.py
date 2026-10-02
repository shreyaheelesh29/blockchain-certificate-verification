from app.services.qr_service import (
    generate_certificate_qr
)


certificate_id = "CERT-A99C4750FD"

qr_path = generate_certificate_qr(
    certificate_id
)

print("QR Generated Successfully")
print("QR Path:", qr_path)