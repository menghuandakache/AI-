"""Feedback schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    qa_log_id: str
    feedback_type: str = Field(..., pattern="^(like|dislike)$")
    feedback_reason: str | None = None


class FeedbackResponse(BaseModel):
    id: str
    qa_log_id: str
    feedback_type: str
    feedback_reason: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True
