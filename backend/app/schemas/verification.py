from pydantic import BaseModel


class VerificationResponse(BaseModel):
    certificate_id: str
    is_valid: bool
    is_revoked: bool
    status: str
    message: str