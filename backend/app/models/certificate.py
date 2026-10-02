from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime

from app.database.db import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    certificate_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    student_name = Column(
        String,
        nullable=False
    )

    roll_number = Column(
        String,
        nullable=True
    )

    course = Column(
        String,
        nullable=False
    )

    institution = Column(
        String,
        nullable=False
    )

    issue_date = Column(
        String,
        nullable=False
    )

    pdf_path = Column(
        String,
        nullable=True
    )

    certificate_hash = Column(
        String,
        nullable=True
    )

    blockchain_tx_hash = Column(
        String,
        nullable=True
    )

    blockchain_record_id = Column(
        Integer,
        nullable=True
    )

    status = Column(
        String,
        default="PENDING",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )