"""Document model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, BigInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kb_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    parse_status = Column(String(50), nullable=False, default="uploaded", index=True)
    parse_error = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, parse_status={self.parse_status})>"
