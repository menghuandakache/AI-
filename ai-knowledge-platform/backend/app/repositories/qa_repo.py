"""QA Log repository."""
from sqlalchemy.orm import Session
from app.models.qa_log import QALog


class QARepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str = None, agent_id: str = None, kb_id: str = None,
               question: str = "", answer: str = None, retrieved_chunk_ids: list = None,
               cited_knowledge_ids: list = None, status: str = "answered",
               latency_ms: int = None, conversation_id: str = None) -> QALog:
        qa_log = QALog(
            user_id=user_id,
            agent_id=agent_id,
            kb_id=kb_id,
            question=question,
            answer=answer,
            retrieved_chunk_ids=retrieved_chunk_ids or [],
            cited_knowledge_ids=cited_knowledge_ids or [],
            status=status,
            latency_ms=latency_ms,
            conversation_id=conversation_id,
        )
        self.db.add(qa_log)
        self.db.commit()
        self.db.refresh(qa_log)
        return qa_log

    def get_by_id(self, qa_log_id: str) -> QALog | None:
        return self.db.query(QALog).filter(QALog.id == qa_log_id).first()

    def list_by_user(self, user_id: str, page: int = 1, page_size: int = 20) -> list[QALog]:
        return self.db.query(QALog).filter(
            QALog.user_id == user_id
        ).order_by(QALog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    def count_by_user(self, user_id: str) -> int:
        return self.db.query(QALog).filter(QALog.user_id == user_id).count()

    def update_feedback(self, qa_log_id: str, feedback: str) -> QALog | None:
        qa_log = self.get_by_id(qa_log_id)
        if qa_log:
            qa_log.feedback = feedback
            self.db.commit()
            self.db.refresh(qa_log)
        return qa_log

    def list_low_satisfaction(self, limit: int = 20) -> list[QALog]:
        return self.db.query(QALog).filter(
            QALog.feedback == "dislike"
        ).order_by(QALog.created_at.desc()).limit(limit).all()

    def list_no_answer(self, limit: int = 20) -> list[QALog]:
        return self.db.query(QALog).filter(
            QALog.status == "no_answer"
        ).order_by(QALog.created_at.desc()).limit(limit).all()

    def list_recent(self, limit: int = 20) -> list[QALog]:
        return self.db.query(QALog).order_by(QALog.created_at.desc()).limit(limit).all()
