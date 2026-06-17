"""Statistics routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.stats import (
    OverviewStatsResponse, HotKnowledgeItem, FeedbackStatsResponse,
    NoAnswerQuestion, RecentQAItem,
)
from app.services.stats_service import StatsService

router = APIRouter()


@router.get("/overview", response_model=OverviewStatsResponse)
async def get_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get overview statistics."""
    service = StatsService(db)
    return service.get_overview()


@router.get("/hot-knowledge", response_model=list[HotKnowledgeItem])
async def get_hot_knowledge(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get most cited knowledge items."""
    service = StatsService(db)
    return service.get_hot_knowledge(limit=limit)


@router.get("/feedback", response_model=FeedbackStatsResponse)
async def get_feedback_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get feedback statistics."""
    service = StatsService(db)
    return service.get_feedback_stats()


@router.get("/no-answer", response_model=list[NoAnswerQuestion])
async def get_no_answer_questions(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get frequently asked but unanswered questions."""
    service = StatsService(db)
    return service.get_no_answer_questions(limit=limit)


@router.get("/recent-qa", response_model=list[RecentQAItem])
async def get_recent_qa(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get recent QA logs."""
    service = StatsService(db)
    return service.get_recent_qa(limit=limit)
