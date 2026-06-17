"""Knowledge Item repository."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.knowledge_item import KnowledgeItem
from app.models.knowledge_chunk import KnowledgeChunk


class KnowledgeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, kb_id: str, title: str, content: str, summary: str = None,
               category: str = None, tags: list = None, status: str = "draft",
               source_type: str = "manual", source_file_id: str = None,
               created_by: str = None) -> KnowledgeItem:
        knowledge = KnowledgeItem(
            kb_id=kb_id,
            title=title,
            content=content,
            summary=summary,
            category=category,
            tags=tags or [],
            status=status,
            source_type=source_type,
            source_file_id=source_file_id,
            created_by=created_by,
        )
        self.db.add(knowledge)
        self.db.commit()
        self.db.refresh(knowledge)
        return knowledge

    def get_by_id(self, knowledge_id: str) -> KnowledgeItem | None:
        return self.db.query(KnowledgeItem).filter(
            KnowledgeItem.id == knowledge_id,
            KnowledgeItem.status != "deleted",
        ).first()

    def list_all(self, kb_id: str = None, keyword: str = None, category: str = None,
                 tags: list[str] = None, status: str = None, page: int = 1,
                 page_size: int = 20) -> list[KnowledgeItem]:
        query = self.db.query(KnowledgeItem).filter(KnowledgeItem.status != "deleted")
        if kb_id:
            query = query.filter(KnowledgeItem.kb_id == kb_id)
        if keyword:
            query = query.filter(
                (KnowledgeItem.title.ilike(f"%{keyword}%")) |
                (KnowledgeItem.content.ilike(f"%{keyword}%"))
            )
        if category:
            query = query.filter(KnowledgeItem.category == category)
        if status:
            query = query.filter(KnowledgeItem.status == status)
        if tags:
            query = query.filter(KnowledgeItem.tags.op("?|")(tags))
        return query.order_by(KnowledgeItem.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    def count_all(self, kb_id: str = None, keyword: str = None, category: str = None,
                  tags: list[str] = None, status: str = None) -> int:
        query = self.db.query(KnowledgeItem).filter(KnowledgeItem.status != "deleted")
        if kb_id:
            query = query.filter(KnowledgeItem.kb_id == kb_id)
        if keyword:
            query = query.filter(
                (KnowledgeItem.title.ilike(f"%{keyword}%")) |
                (KnowledgeItem.content.ilike(f"%{keyword}%"))
            )
        if category:
            query = query.filter(KnowledgeItem.category == category)
        if status:
            query = query.filter(KnowledgeItem.status == status)
        if tags:
            query = query.filter(KnowledgeItem.tags.op("?|")(tags))
        return query.count()

    def update(self, knowledge_id: str, **kwargs) -> KnowledgeItem | None:
        knowledge = self.get_by_id(knowledge_id)
        if knowledge:
            for key, value in kwargs.items():
                if value is not None and hasattr(knowledge, key):
                    setattr(knowledge, key, value)
            self.db.commit()
            self.db.refresh(knowledge)
        return knowledge

    def publish(self, knowledge_id: str) -> KnowledgeItem | None:
        return self.update(knowledge_id, status="available")

    def disable(self, knowledge_id: str) -> KnowledgeItem | None:
        return self.update(knowledge_id, status="unavailable")

    def soft_delete(self, knowledge_id: str) -> KnowledgeItem | None:
        from datetime import datetime, timezone
        return self.update(knowledge_id, status="deleted", deleted_at=datetime.now(timezone.utc))

    def get_chunk_count(self, knowledge_id: str) -> int:
        return self.db.query(KnowledgeChunk).filter(
            KnowledgeChunk.knowledge_id == knowledge_id
        ).count()

    def list_available(self, kb_id: str = None, page: int = 1, page_size: int = 100) -> list[KnowledgeItem]:
        query = self.db.query(KnowledgeItem).filter(KnowledgeItem.status == "available")
        if kb_id:
            query = query.filter(KnowledgeItem.kb_id == kb_id)
        return query.order_by(KnowledgeItem.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    def count_drafts_by_source_file_ids(self, source_file_ids: list[str]) -> dict[str, int]:
        """Return a map of source_file_id -> count of draft knowledge items."""
        if not source_file_ids:
            return {}
        rows = (
            self.db.query(KnowledgeItem.source_file_id, func.count(KnowledgeItem.id))
            .filter(
                KnowledgeItem.source_file_id.in_(source_file_ids),
                KnowledgeItem.status == "draft",
            )
            .group_by(KnowledgeItem.source_file_id)
            .all()
        )
        return {str(row[0]): row[1] for row in rows}
