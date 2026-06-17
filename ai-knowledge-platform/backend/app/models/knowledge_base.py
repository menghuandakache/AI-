"""KnowledgeBase model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=True)
    owner_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String(50), nullable=False, default="enabled", index=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    knowledge_items = relationship("KnowledgeItem", back_populates="knowledge_base", lazy="dynamic")
    documents = relationship("Document", back_populates="knowledge_base", lazy="dynamic")

    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, name={self.name}, status={self.status})>"
