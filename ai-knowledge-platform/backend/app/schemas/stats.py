"""Statistics schemas."""
from pydantic import BaseModel


class OverviewStatsResponse(BaseModel):
    total_knowledge: int
    available_knowledge: int
    draft_knowledge: int
    total_kb: int
    enabled_kb: int
    total_qa: int
    answered_qa: int
    like_count: int
    dislike_count: int


class HotKnowledgeItem(BaseModel):
    knowledge_id: str
    title: str
    kb_name: str
    category: str | None = None
    cite_count: int


class FeedbackStatsResponse(BaseModel):
    total_feedback: int
    like_count: int
    dislike_count: int
    like_rate: float


class NoAnswerQuestion(BaseModel):
    question: str
    count: int
    last_asked: str | None = None


class RecentQAItem(BaseModel):
    id: str
    question: str
    answer: str | None = None
    status: str
    feedback: str | None = None
    created_at: str | None = None
