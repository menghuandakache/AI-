"""Knowledge Base repository."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.knowledge_base import KnowledgeBase
from app.models.knowledge_item import KnowledgeItem


class KnowledgeBaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, description: str = None, domain: str = None,
               owner_id: str = None, created_by: str = None) -> KnowledgeBase:
        kb = KnowledgeBase(
            name=name,
            description=description,
            domain=domain,
            owner_id=owner_id,
            created_by=created_by,
            status="enabled",
        )
        self.db.add(kb)
        self.db.commit()
        self.db.refresh(kb)
        return kb

    def get_by_id(self, kb_id: str) -> KnowledgeBase | None:
        return self.db.query(KnowledgeBase).filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.status != "deleted",
        ).first()

    def list_all(self, page: int = 1, page_size: int = 20, domain: str = None,
                 status: str = None, keyword: str = None) -> list[KnowledgeBase]:
        query = self.db.query(KnowledgeBase).filter(KnowledgeBase.status != "deleted")
        if domain:
            query = query.filter(KnowledgeBase.domain == domain)
        if status:
            query = query.filter(KnowledgeBase.status == status)
        if keyword:
            query = query.filter(KnowledgeBase.name.ilike(f"%{keyword}%"))
        return query.order_by(KnowledgeBase.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    def count_all(self, domain: str = None, status: str = None, keyword: str = None) -> int:
        query = self.db.query(KnowledgeBase).filter(KnowledgeBase.status != "deleted")
        if domain:
            query = query.filter(KnowledgeBase.domain == domain)
        if status:
            query = query.filter(KnowledgeBase.status == status)
        if keyword:
            query = query.filter(KnowledgeBase.name.ilike(f"%{keyword}%"))
        return query.count()

    def update(self, kb_id: str, **kwargs) -> KnowledgeBase | None:
        kb = self.get_by_id(kb_id)
        if kb:
            for key, value in kwargs.items():
                if value is not None and hasattr(kb, key):
                    setattr(kb, key, value)
            self.db.commit()
            self.db.refresh(kb)
        return kb

    def update_status(self, kb_id: str, status: str) -> KnowledgeBase | None:
        return self.update(kb_id, status=status)

    def soft_delete(self, kb_id: str) -> KnowledgeBase | None:
        return self.update(kb_id, status="deleted")

    def get_knowledge_count(self, kb_id: str) -> int:
        return self.db.query(KnowledgeItem).filter(
            KnowledgeItem.kb_id == kb_id,
            KnowledgeItem.status != "deleted",
        ).count()

    def check_name_exists(self, name: str, exclude_id: str = None) -> bool:
        query = self.db.query(KnowledgeBase).filter(
            KnowledgeBase.name == name,
            KnowledgeBase.status != "deleted",
        )
        if exclude_id:
            query = query.filter(KnowledgeBase.id != exclude_id)
        return query.first() is not None
