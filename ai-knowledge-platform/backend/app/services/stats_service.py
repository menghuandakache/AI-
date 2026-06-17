"""Statistics service."""
from sqlalchemy.orm import Session
from app.repositories.stats_repo import StatsRepository
from app.repositories.qa_repo import QARepository


class StatsService:
    def __init__(self, db: Session):
        self.db = db
        self.stats_repo = StatsRepository(db)
        self.qa_repo = QARepository(db)

    def get_overview(self) -> dict:
        return self.stats_repo.get_overview()

    def get_hot_knowledge(self, limit: int = 10) -> list[dict]:
        return self.stats_repo.get_hot_knowledge(limit=limit)

    def get_feedback_stats(self) -> dict:
        return self.stats_repo.get_feedback_stats()

    def get_no_answer_questions(self, limit: int = 20) -> list[dict]:
        return self.stats_repo.get_no_answer_questions(limit=limit)

    def get_recent_qa(self, limit: int = 20) -> list[dict]:
        items = self.qa_repo.list_recent(limit=limit)
        return [
            {
                "id": str(item.id),
                "question": item.question,
                "answer": item.answer[:200] if item.answer else None,
                "status": item.status,
                "feedback": item.feedback,
                "created_at": str(item.created_at) if item.created_at else None,
            }
            for item in items
        ]
