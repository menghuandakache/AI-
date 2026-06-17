"""Conversation schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    agent_id: str
    title: str = "新对话"


class ConversationResponse(BaseModel):
    id: str
    agent_id: str
    user_id: str | None = None
    title: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    items: list[ConversationResponse]
    total: int


class ConversationDetailResponse(BaseModel):
    id: str
    agent_id: str
    title: str
    messages: list[dict]
    created_at: datetime | None = None
