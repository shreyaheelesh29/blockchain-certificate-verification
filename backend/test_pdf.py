from app.services.pdf_service import generate_certificate_pdf


file_path = generate_certificate_pdf(
    certificate_id="CERT-7B6A0E473F",
    student_name="Jay Mishra",
    roll_number="CE2026-001",
    course="B.E. Computer Engineering",
    institution="MCT Rajiv Gandhi Institute of Technology",
    issue_date="2026-09-24"
)

print("PDF Created Successfully")
print("File:", file_path)