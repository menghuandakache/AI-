"""Agent model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    kb_ids = Column(JSONB, nullable=False, default=list)
    prompt_config = Column(Text, nullable=True)
    answer_style = Column(String(50), nullable=True, default="detailed")
    citation_policy = Column(String(50), nullable=True, default="required")
    no_answer_policy = Column(String(50), nullable=True, default="prompt")
    status = Column(String(50), nullable=False, default="enabled")
    created_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, status={self.status})>"
