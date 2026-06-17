"""AuditLog model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    detail = Column(JSONB, nullable=True, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource_type={self.resource_type})>"
