import qrcode
from pathlib import Path


FRONTEND_URL = "http://192.168.43.225:5173"


def generate_certificate_qr(
    certificate_id: str
) -> str:

    verification_url = (
        f"{FRONTEND_URL}/verify/{certificate_id}"
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )

    qr.add_data(verification_url)
    qr.make(fit=True)

    qr_image = qr.make_image()

    base_dir = Path(__file__).resolve().parents[2]

    qr_directory = (
        base_dir
        / "generated"
        / "qr"
    )

    qr_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    qr_path = (
        qr_directory
        / f"{certificate_id}.png"
    )

    qr_image.save(qr_path)

    return str(qr_path)