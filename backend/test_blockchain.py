from app.services.blockchain_service import (
    get_certificate_from_blockchain
)


certificate_id = "CERT-DEMO-001"

result = get_certificate_from_blockchain(
    certificate_id
)

print("\nBlockchain Certificate")
print("---------------------")

print("Certificate ID:", result["certificate_id"])
print("Student Name:", result["student_name"])
print("Course:", result["course"])
print("Institution:", result["institution"])
print("Hash:", result["certificate_hash"])
print("Issue Date:", result["issue_date"])
print("Issuer:", result["issuer"])
print("Revoked:", result["revoked"])