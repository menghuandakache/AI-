"""Knowledge Item service."""
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException, BusinessException
from app.core.constants import KNOWLEDGE_STATUS_AVAILABLE, KNOWLEDGE_STATUS_UNAVAILABLE
from app.repositories.knowledge_repo import KnowledgeRepository
from app.repositories.chunk_repo import ChunkRepository
from app.repositories.kb_repo import KnowledgeBaseRepository


class KnowledgeService:
    def __init__(self, db: Session):
        self.db = db
        self.knowledge_repo = KnowledgeRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.kb_repo = KnowledgeBaseRepository(db)

    def create(self, kb_id: str, title: str, content: str, summary: str = None,
               category: str = None, tags: list = None, status: str = "draft",
               source_type: str = "manual", source_file_id: str = None,
               created_by: str = None) -> dict:
        # Verify knowledge base exists
        kb = self.kb_repo.get_by_id(kb_id)
        if not kb:
            raise NotFoundException(f"Knowledge base {kb_id} not found")

        knowledge = self.knowledge_repo.create(
            kb_id=kb_id, title=title, content=content, summary=summary,
            category=category, tags=tags, status=status,
            source_type=source_type, source_file_id=source_file_id,
            created_by=created_by,
        )
        return self._to_dict(knowledge)

    def get_by_id(self, knowledge_id: str) -> dict:
        knowledge = self.knowledge_repo.get_by_id(knowledge_id)
        if not knowledge:
            raise NotFoundException(f"Knowledge item {knowledge_id} not found")
        return self._to_dict(knowledge)

    def list_all(self, kb_id: str = None, keyword: str = None, category: str = None,
                 tags: list[str] = None, status: str = None, page: int = 1,
                 page_size: int = 20) -> dict:
        items = self.knowledge_repo.list_all(
            kb_id=kb_id, keyword=keyword, category=category,
            tags=tags, status=status, page=page, page_size=page_size,
        )
        total = self.knowledge_repo.count_all(
            kb_id=kb_id, keyword=keyword, category=category,
            tags=tags, status=status,
        )
        return {
            "items": [self._to_dict(k) for k in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def update(self, knowledge_id: str, **kwargs) -> dict:
        knowledge = self.knowledge_repo.get_by_id(knowledge_id)
        if not knowledge:
            raise NotFoundException(f"Knowledge item {knowledge_id} not found")
        knowledge = self.knowledge_repo.update(knowledge_id, **kwargs)
        return self._to_dict(knowledge)

    def publish(self, knowledge_id: str) -> dict:
        knowledge = self.knowledge_repo.get_by_id(knowledge_id)
        if not knowledge:
            raise NotFoundException(f"Knowledge item {knowledge_id} not found")
        if knowledge.status == KNOWLEDGE_STATUS_AVAILABLE:
            raise BusinessException("Knowledge is already published")

        self.knowledge_repo.publish(knowledge_id)
        # Trigger embedding task (would be async in production)
        return {"message": "Knowledge published successfully", "knowledge_id": knowledge_id}

    def disable(self, knowledge_id: str) -> dict:
        knowledge = self.knowledge_repo.get_by_id(knowledge_id)
        if not knowledge:
            raise NotFoundException(f"Knowledge item {knowledge_id} not found")
        if knowledge.status == KNOWLEDGE_STATUS_UNAVAILABLE:
            raise BusinessException("Knowledge is already disabled")
        self.knowledge_repo.disable(knowledge_id)
        return {"message": "Knowledge disabled successfully"}

    def delete(self, knowledge_id: str) -> dict:
        knowledge = self.knowledge_repo.get_by_id(knowledge_id)
        if not knowledge:
            raise NotFoundException(f"Knowledge item {knowledge_id} not found")
        self.knowledge_repo.soft_delete(knowledge_id)
        return {"message": "Knowledge deleted successfully"}

    def get_chunks(self, knowledge_id: str) -> list:
        knowledge = self.knowledge_repo.get_by_id(knowledge_id)
        if not knowledge:
            raise NotFoundException(f"Knowledge item {knowledge_id} not found")
        chunks = self.chunk_repo.get_by_knowledge_id(knowledge_id)
        return [
            {
                "id": str(c.id),
                "knowledge_id": str(c.knowledge_id),
                "chunk_text": c.chunk_text,
                "chunk_index": c.chunk_index,
                "metadata": c.chunk_metadata,
                "token_count": c.token_count,
            }
            for c in chunks
        ]

    def _to_dict(self, knowledge) -> dict:
        chunk_count = self.knowledge_repo.get_chunk_count(str(knowledge.id))
        return {
            "id": str(knowledge.id),
            "kb_id": str(knowledge.kb_id),
            "title": knowledge.title,
            "content": knowledge.content,
            "summary": knowledge.summary,
            "category": knowledge.category,
            "tags": knowledge.tags or [],
            "status": knowledge.status,
            "source_type": knowledge.source_type,
            "source_file_id": str(knowledge.source_file_id) if knowledge.source_file_id else None,
            "created_by": str(knowledge.created_by) if knowledge.created_by else None,
            "updated_by": str(knowledge.updated_by) if knowledge.updated_by else None,
            "created_at": knowledge.created_at,
            "updated_at": knowledge.updated_at,
            "chunk_count": chunk_count,
        }
