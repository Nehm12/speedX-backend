import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey
from app.models.base import Base


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    success = "success"
    failed = "failed"

class ExtractionJob(Base):
    __tablename__ = "extraction_job"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    submitted_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.pending)
    pdf_filename = Column(String, nullable=False)