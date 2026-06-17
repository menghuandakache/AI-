"""Feedback routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services.feedback_service import FeedbackService

router = APIRouter()


@router.post("", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit feedback for a QA answer."""
    service = FeedbackService(db)
    return service.submit(
        qa_log_id=request.qa_log_id,
        feedback_type=request.feedback_type,
        feedback_reason=request.feedback_reason,
        user_id=str(current_user.id),
    )


@router.get("/qa/{qa_log_id}", response_model=list[FeedbackResponse])
async def get_feedback(
    qa_log_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get feedback entries for a QA log."""
    service = FeedbackService(db)
    return service.get_by_qa_log(qa_log_id)
