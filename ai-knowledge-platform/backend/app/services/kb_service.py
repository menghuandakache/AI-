"""Knowledge Base service."""
from sqlalchemy.orm import Session
from app.core.exceptions import DuplicateResourceException, NotFoundException, BusinessException
from app.repositories.kb_repo import KnowledgeBaseRepository
from app.repositories.knowledge_repo import KnowledgeRepository


class KnowledgeBaseService:
    def __init__(self, db: Session):
        self.db = db
        self.kb_repo = KnowledgeBaseRepository(db)
        self.knowledge_repo = KnowledgeRepository(db)

    def create(self, name: str, description: str = None, domain: str = None,
               owner_id: str = None, created_by: str = None) -> dict:
        if self.kb_repo.check_name_exists(name):
            raise DuplicateResourceException(f"Knowledge base '{name}' already exists")
        kb = self.kb_repo.create(
            name=name, description=description, domain=domain,
            owner_id=owner_id, created_by=created_by,
        )
        return self._to_dict(kb)

    def get_by_id(self, kb_id: str) -> dict:
        kb = self.kb_repo.get_by_id(kb_id)
        if not kb:
            raise NotFoundException(f"Knowledge base {kb_id} not found")
        return self._to_dict(kb)

    def list_all(self, page: int = 1, page_size: int = 20, domain: str = None,
                 status: str = None, keyword: str = None) -> dict:
        items = self.kb_repo.list_all(page=page, page_size=page_size, domain=domain,
                                       status=status, keyword=keyword)
        total = self.kb_repo.count_all(domain=domain, status=status, keyword=keyword)
        return {
            "items": [self._to_dict(kb) for kb in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def update(self, kb_id: str, **kwargs) -> dict:
        kb = self.kb_repo.get_by_id(kb_id)
        if not kb:
            raise NotFoundException(f"Knowledge base {kb_id} not found")
        if "name" in kwargs and kwargs["name"] and kwargs["name"] != kb.name:
            if self.kb_repo.check_name_exists(kwargs["name"], exclude_id=kb_id):
                raise DuplicateResourceException(f"Knowledge base '{kwargs['name']}' already exists")
        kb = self.kb_repo.update(kb_id, **kwargs)
        return self._to_dict(kb)

    def update_status(self, kb_id: str, status: str) -> dict:
        kb = self.kb_repo.get_by_id(kb_id)
        if not kb:
            raise NotFoundException(f"Knowledge base {kb_id} not found")
        kb = self.kb_repo.update_status(kb_id, status)
        return self._to_dict(kb)

    def delete(self, kb_id: str) -> dict:
        kb = self.kb_repo.get_by_id(kb_id)
        if not kb:
            raise NotFoundException(f"Knowledge base {kb_id} not found")
        # Check if there are undeleted knowledge items
        knowledge_count = self.knowledge_repo.count_all(kb_id=kb_id)
        if knowledge_count > 0:
            raise BusinessException(
                f"Cannot delete knowledge base with {knowledge_count} knowledge items. "
                "Please delete or transfer them first.",
                code="HAS_DEPENDENCIES"
            )
        self.kb_repo.soft_delete(kb_id)
        return {"message": "Knowledge base deleted successfully"}

    def get_overview(self, kb_id: str) -> dict:
        kb = self.kb_repo.get_by_id(kb_id)
        if not kb:
            raise NotFoundException(f"Knowledge base {kb_id} not found")
        total = self.knowledge_repo.count_all(kb_id=kb_id)
        available = self.knowledge_repo.count_all(kb_id=kb_id, status="available")
        draft = self.knowledge_repo.count_all(kb_id=kb_id, status="draft")
        return {
            "kb_id": kb_id,
            "kb_name": kb.name,
            "total_knowledge": total,
            "available_knowledge": available,
            "draft_knowledge": draft,
            "qa_count": 0,
        }

    def _to_dict(self, kb) -> dict:
        knowledge_count = self.kb_repo.get_knowledge_count(str(kb.id))
        return {
            "id": str(kb.id),
            "name": kb.name,
            "description": kb.description,
            "domain": kb.domain,
            "owner_id": str(kb.owner_id) if kb.owner_id else None,
            "status": kb.status,
            "created_by": str(kb.created_by) if kb.created_by else None,
            "created_at": kb.created_at,
            "updated_at": kb.updated_at,
            "knowledge_count": knowledge_count,
        }
