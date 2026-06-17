"""Agent schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    kb_ids: list[str] = Field(default_factory=list)
    prompt_config: str | None = None
    answer_style: str = "detailed"
    citation_policy: str = "required"
    no_answer_policy: str = "prompt"


class AgentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    kb_ids: list[str] | None = None
    prompt_config: str | None = None
    answer_style: str | None = None
    citation_policy: str | None = None
    no_answer_policy: str | None = None


class AgentResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    kb_ids: list[str] = []
    prompt_config: str | None = None
    answer_style: str
    citation_policy: str
    no_answer_policy: str
    status: str
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    items: list[AgentResponse]
    total: int


class AgentGenerateRequest(BaseModel):
    kb_id: str
    name: str | None = None
