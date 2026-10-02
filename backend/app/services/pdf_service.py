from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from app.services.qr_service import generate_certificate_qr


GENERATED_DIR = Path("generated/certificates")
GENERATED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def generate_certificate_pdf(
    certificate_id: str,
    student_name: str,
    roll_number: str | None,
    course: str,
    institution: str,
    issue_date: str
) -> str:

    file_path = GENERATED_DIR / f"{certificate_id}.pdf"

    # Generate QR code for this certificate
    qr_path = generate_certificate_qr(
        certificate_id
    )

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        str(file_path),
        pagesize=(page_width, page_height)
    )

    center_x = page_width / 2

    # ==================================================
    # BACKGROUND
    # ==================================================

    pdf.setFillColor(colors.HexColor("#F8FAFC"))
    pdf.rect(
        0,
        0,
        page_width,
        page_height,
        fill=1,
        stroke=0
    )

    # ==================================================
    # OUTER BORDER
    # ==================================================

    pdf.setStrokeColor(colors.HexColor("#1E3A8A"))
    pdf.setLineWidth(4)

    pdf.rect(
        25,
        25,
        page_width - 50,
        page_height - 50
    )

    # ==================================================
    # INNER BORDER
    # ==================================================

    pdf.setStrokeColor(colors.HexColor("#D4AF37"))
    pdf.setLineWidth(2)

    pdf.rect(
        38,
        38,
        page_width - 76,
        page_height - 76
    )

    # ==================================================
    # HEADER
    # ==================================================

    pdf.setFillColor(colors.HexColor("#1E3A8A"))
    pdf.setFont("Helvetica-Bold", 26)

    pdf.drawCentredString(
        center_x,
        385,
        "CERTIFICATE OF ACHIEVEMENT"
    )

    # Decorative line
    pdf.setStrokeColor(colors.HexColor("#D4AF37"))
    pdf.setLineWidth(2)

    pdf.line(
        center_x - 160,
        365,
        center_x + 160,
        365
    )

    # ==================================================
    # QR CODE
    # ==================================================

    pdf.drawImage(
        qr_path,
        page_width - 125,
        410,
        width=75,
        height=75,
        preserveAspectRatio=True,
        mask="auto"
    )

    pdf.setFillColor(colors.HexColor("#374151"))
    pdf.setFont("Helvetica", 8)

    pdf.drawCentredString(
        page_width - 87.5,
        400,
        "Scan to Verify"
    )

    # ==================================================
    # PRESENTED TO
    # ==================================================

    pdf.setFillColor(colors.HexColor("#374151"))
    pdf.setFont("Helvetica", 14)

    pdf.drawCentredString(
        center_x,
        330,
        "This certificate is proudly presented to"
    )

    # ==================================================
    # STUDENT NAME
    # ==================================================

    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.setFont("Helvetica-Bold", 34)

    pdf.drawCentredString(
        center_x,
        285,
        student_name
    )

    # Name underline
    pdf.setStrokeColor(colors.HexColor("#D4AF37"))
    pdf.setLineWidth(1)

    pdf.line(
        center_x - 145,
        270,
        center_x + 145,
        270
    )

    # ==================================================
    # ACHIEVEMENT TEXT
    # ==================================================

    pdf.setFillColor(colors.HexColor("#374151"))
    pdf.setFont("Helvetica", 14)

    pdf.drawCentredString(
        center_x,
        235,
        "for successfully completing the"
    )

    # ==================================================
    # COURSE
    # ==================================================

    pdf.setFillColor(colors.HexColor("#1E3A8A"))
    pdf.setFont("Helvetica-Bold", 19)

    pdf.drawCentredString(
        center_x,
        200,
        course
    )

    # ==================================================
    # INSTITUTION
    # ==================================================

    pdf.setFillColor(colors.HexColor("#374151"))
    pdf.setFont("Helvetica", 14)

    pdf.drawCentredString(
        center_x,
        170,
        f"at {institution}"
    )

    # ==================================================
    # DETAILS SECTION
    # ==================================================

    detail_line_y = 125

    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.setLineWidth(1)

    pdf.line(
        75,
        145,
        page_width - 75,
        145
    )

    # Certificate ID
    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawString(
        75,
        detail_line_y,
        "CERTIFICATE ID"
    )

    pdf.setFont("Helvetica", 10)

    pdf.drawString(
        75,
        detail_line_y - 16,
        certificate_id
    )

    # Roll number
    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawCentredString(
        center_x,
        detail_line_y,
        "ROLL NUMBER"
    )

    pdf.setFont("Helvetica", 10)

    pdf.drawCentredString(
        center_x,
        detail_line_y - 16,
        roll_number or "N/A"
    )

    # Issue date
    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawRightString(
        page_width - 75,
        detail_line_y,
        "ISSUE DATE"
    )

    pdf.setFont("Helvetica", 10)

    pdf.drawRightString(
        page_width - 75,
        detail_line_y - 16,
        issue_date
    )

    # ==================================================
    # SIGNATURE SECTION
    # ==================================================

    signature_y = 65

    pdf.setStrokeColor(colors.HexColor("#6B7280"))
    pdf.setLineWidth(1)

    pdf.line(
        85,
        signature_y,
        225,
        signature_y
    )

    pdf.line(
        page_width - 225,
        signature_y,
        page_width - 85,
        signature_y
    )

    pdf.setFillColor(colors.HexColor("#374151"))
    pdf.setFont("Helvetica", 10)

    pdf.drawCentredString(
        155,
        48,
        "Certificate Coordinator"
    )

    pdf.drawCentredString(
        page_width - 155,
        48,
        "Authorized Issuer"
    )

    # ==================================================
    # SAVE
    # ==================================================

    pdf.save()

    return str(file_path)