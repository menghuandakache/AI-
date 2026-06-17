"""Chat schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    agent_id: str | None = None
    kb_id: str | None = None
    question: str = Field(..., min_length=1)
    llm_config_id: str | None = None
    conversation_id: str | None = None


class CitationSource(BaseModel):
    knowledge_id: str
    chunk_id: str | None = None
    title: str
    source_file: str | None = None
    score: float


class ChatResponse(BaseModel):
    id: str
    status: str  # answered / no_answer / failed
    answer: str
    sources: list[CitationSource] = []
    question: str
    created_at: datetime | None = None


class ChatHistoryItem(BaseModel):
    id: str
    question: str
    answer: str | None = None
    status: str
    feedback: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    items: list[ChatHistoryItem]
    total: int
