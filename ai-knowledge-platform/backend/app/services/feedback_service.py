"""Feedback service."""
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException
from app.models.feedback import Feedback
from app.repositories.qa_repo import QARepository


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db
        self.qa_repo = QARepository(db)

    def submit(self, qa_log_id: str, feedback_type: str, feedback_reason: str = None,
               user_id: str = None) -> dict:
        """Submit user feedback for a QA log."""
        qa_log = self.qa_repo.get_by_id(qa_log_id)
        if not qa_log:
            raise NotFoundException(f"QA log {qa_log_id} not found")

        # Create feedback record
        feedback = Feedback(
            qa_log_id=qa_log_id,
            user_id=user_id,
            feedback_type=feedback_type,
            feedback_reason=feedback_reason,
        )
        self.db.add(feedback)

        # Update QA log feedback field
        self.qa_repo.update_feedback(qa_log_id, feedback_type)

        self.db.commit()
        self.db.refresh(feedback)

        return {
            "id": str(feedback.id),
            "qa_log_id": str(feedback.qa_log_id),
            "feedback_type": feedback.feedback_type,
            "feedback_reason": feedback.feedback_reason,
            "created_at": feedback.created_at,
        }

    def get_by_qa_log(self, qa_log_id: str) -> list[dict]:
        """Get feedback entries for a QA log."""
        feedbacks = self.db.query(Feedback).filter(
            Feedback.qa_log_id == qa_log_id
        ).all()
        return [
            {
                "id": str(f.id),
                "qa_log_id": str(f.qa_log_id),
                "feedback_type": f.feedback_type,
                "feedback_reason": f.feedback_reason,
                "created_at": f.created_at,
            }
            for f in feedbacks
        ]
