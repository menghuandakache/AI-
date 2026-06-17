"""KnowledgeItem model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kb_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSONB, nullable=True, default=list)
    status = Column(String(50), nullable=False, default="draft", index=True)
    source_type = Column(String(50), nullable=False, default="manual")
    source_file_id = Column(UUID(as_uuid=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="knowledge_items")
    chunks = relationship("KnowledgeChunk", back_populates="knowledge_item", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<KnowledgeItem(id={self.id}, title={self.title}, status={self.status})>"
