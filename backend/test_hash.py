from app.services.hashing_service import calculate_file_hash


file_path = "generated/certificates/CERT-7B6A0E473F.pdf"

certificate_hash = calculate_file_hash(file_path)

print("SHA-256 Hash:")
print(certificate_hash)