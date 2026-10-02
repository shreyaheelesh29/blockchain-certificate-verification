from pydantic import BaseModel


class CertificateCreate(BaseModel):
    student_name: str
    roll_number: str | None = None
    course: str
    institution: str
    issue_date: str


class CertificateResponse(BaseModel):
    id: int
    certificate_id: str
    student_name: str
    roll_number: str | None
    course: str
    institution: str
    issue_date: str
    certificate_hash: str | None
    blockchain_tx_hash: str | None
    blockchain_record_id: int | None
    status: str

    class Config:
        from_attributes = True