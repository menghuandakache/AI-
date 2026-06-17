"""Statistics repository."""
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.knowledge_item import KnowledgeItem
from app.models.knowledge_base import KnowledgeBase
from app.models.qa_log import QALog
from app.models.feedback import Feedback


class StatsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> dict:
        return {
            "total_knowledge": self.db.query(KnowledgeItem).filter(
                KnowledgeItem.status != "deleted"
            ).count(),
            "available_knowledge": self.db.query(KnowledgeItem).filter(
                KnowledgeItem.status == "available"
            ).count(),
            "draft_knowledge": self.db.query(KnowledgeItem).filter(
                KnowledgeItem.status == "draft"
            ).count(),
            "total_kb": self.db.query(KnowledgeBase).filter(
                KnowledgeBase.status != "deleted"
            ).count(),
            "enabled_kb": self.db.query(KnowledgeBase).filter(
                KnowledgeBase.status == "enabled"
            ).count(),
            "total_qa": self.db.query(QALog).count(),
            "answered_qa": self.db.query(QALog).filter(QALog.status == "answered").count(),
            "like_count": self.db.query(QALog).filter(QALog.feedback == "like").count(),
            "dislike_count": self.db.query(QALog).filter(QALog.feedback == "dislike").count(),
        }

    def get_hot_knowledge(self, limit: int = 10) -> list[dict]:
        """Get most cited knowledge items."""
        results = self.db.query(
            QALog.cited_knowledge_ids
        ).filter(
            QALog.cited_knowledge_ids.isnot(None)
        ).all()

        cite_count = {}
        for row in results:
            ids = row[0] or []
            for kid in ids:
                cite_count[kid] = cite_count.get(kid, 0) + 1

        sorted_ids = sorted(cite_count.items(), key=lambda x: x[1], reverse=True)[:limit]

        hot_items = []
        for kid, count in sorted_ids:
            knowledge = self.db.query(KnowledgeItem).filter(KnowledgeItem.id == kid).first()
            if knowledge:
                kb = self.db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge.kb_id).first()
                hot_items.append({
                    "knowledge_id": kid,
                    "title": knowledge.title,
                    "kb_name": kb.name if kb else "",
                    "category": knowledge.category,
                    "cite_count": count,
                })
        return hot_items

    def get_feedback_stats(self) -> dict:
        total_feedback = self.db.query(Feedback).count()
        like_count = self.db.query(Feedback).filter(Feedback.feedback_type == "like").count()
        dislike_count = self.db.query(Feedback).filter(Feedback.feedback_type == "dislike").count()
        return {
            "total_feedback": total_feedback,
            "like_count": like_count,
            "dislike_count": dislike_count,
            "like_rate": round(like_count / total_feedback * 100, 1) if total_feedback > 0 else 0,
        }

    def get_no_answer_questions(self, limit: int = 20) -> list[dict]:
        results = self.db.query(
            QALog.question, func.count(QALog.id), func.max(QALog.created_at)
        ).filter(
            QALog.status == "no_answer"
        ).group_by(QALog.question).order_by(
            func.count(QALog.id).desc()
        ).limit(limit).all()

        return [
            {"question": row[0], "count": row[1], "last_asked": str(row[2]) if row[2] else None}
            for row in results
        ]
