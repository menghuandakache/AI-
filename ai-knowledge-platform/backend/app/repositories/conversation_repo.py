"""Conversation repository."""
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.qa_log import QALog


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, agent_id: str, user_id: str = None, title: str = "新对话") -> Conversation:
        conv = Conversation(
            agent_id=agent_id,
            user_id=user_id,
            title=title,
        )
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def get_by_id(self, conv_id: str) -> Conversation | None:
        return self.db.query(Conversation).filter(Conversation.id == conv_id).first()

    def list_by_agent_user(self, agent_id: str, user_id: str = None) -> list[Conversation]:
        return self.db.query(Conversation).filter(
            Conversation.agent_id == agent_id,
        ).order_by(Conversation.updated_at.desc()).all()

    def update_title(self, conv_id: str, title: str) -> Conversation | None:
        conv = self.get_by_id(conv_id)
        if conv:
            conv.title = title
            self.db.commit()
            self.db.refresh(conv)
        return conv

    def touch(self, conv_id: str):
        """Update updated_at timestamp."""
        conv = self.get_by_id(conv_id)
        if conv:
            from datetime import datetime, timezone
            conv.updated_at = datetime.now(timezone.utc)
            self.db.commit()

    def delete(self, conv_id: str) -> bool:
        conv = self.get_by_id(conv_id)
        if conv:
            self.db.delete(conv)
            self.db.commit()
            return True
        return False

    def get_messages(self, conv_id: str) -> list[QALog]:
        return self.db.query(QALog).filter(
            QALog.conversation_id == conv_id
        ).order_by(QALog.created_at).all()
