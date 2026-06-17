"""QALog model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class QALog(Base):
    __tablename__ = "qa_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    agent_id = Column(UUID(as_uuid=True), nullable=True)
    conversation_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    kb_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    retrieved_chunk_ids = Column(JSONB, nullable=True, default=list)
    cited_knowledge_ids = Column(JSONB, nullable=True, default=list)
    status = Column(String(50), nullable=False, default="answered")
    feedback = Column(String(50), nullable=True, default="none")
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<QALog(id={self.id}, status={self.status})>"
