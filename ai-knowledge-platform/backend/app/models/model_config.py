"""Model configuration for LLM providers."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ModelConfig(Base):
    __tablename__ = "model_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label = Column(String(200), nullable=False)          # 显示名称，如"GPT-4o"
    model_name = Column(String(200), nullable=False)      # 模型名，如"gpt-4o"
    base_url = Column(String(500), nullable=False)        # API 地址
    api_key = Column(String(500), nullable=False)          # API Key
    is_default = Column(Boolean, default=False)           # 默认模型
    status = Column(String(50), default="enabled")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<ModelConfig(id={self.id}, label={self.label}, model={self.model_name})>"
