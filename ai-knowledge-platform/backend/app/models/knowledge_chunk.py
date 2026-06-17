"""KnowledgeChunk model with pgvector support."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    knowledge_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_items.id"), nullable=False, index=True)
    kb_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(Vector(1024), nullable=True)  # bge-m3 produces 1024-dimensional vectors
    chunk_metadata = Column(JSONB, nullable=True, default=dict)
    token_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    knowledge_item = relationship("KnowledgeItem", back_populates="chunks")

    def __repr__(self):
        return f"<KnowledgeChunk(id={self.id}, knowledge_id={self.knowledge_id}, chunk_index={self.chunk_index})>"
