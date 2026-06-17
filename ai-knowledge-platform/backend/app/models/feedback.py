"""Feedback model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    qa_log_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    feedback_type = Column(String(50), nullable=False)  # like / dislike
    feedback_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Feedback(id={self.id}, feedback_type={self.feedback_type})>"
