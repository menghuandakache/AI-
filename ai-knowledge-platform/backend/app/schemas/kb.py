"""Knowledge Base schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    domain: str | None = None
    owner_id: str | None = None


class KnowledgeBaseUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    domain: str | None = None
    owner_id: str | None = None


class KnowledgeBaseStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(enabled|disabled)$")


class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    domain: str | None = None
    owner_id: str | None = None
    status: str
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    knowledge_count: int = 0

    class Config:
        from_attributes = True


class KnowledgeBaseListResponse(BaseModel):
    items: list[KnowledgeBaseResponse]
    total: int
    page: int
    page_size: int


class KnowledgeBaseOverview(BaseModel):
    kb_id: str
    kb_name: str
    total_knowledge: int
    available_knowledge: int
    draft_knowledge: int
    qa_count: int
