"""Knowledge Base routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.schemas.kb import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseStatusUpdate,
    KnowledgeBaseResponse, KnowledgeBaseListResponse, KnowledgeBaseOverview,
)
from app.services.kb_service import KnowledgeBaseService

router = APIRouter()


@router.get("", response_model=KnowledgeBaseListResponse)
async def list_kbs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    domain: str = Query(None),
    status: str = Query(None),
    keyword: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List knowledge bases."""
    service = KnowledgeBaseService(db)
    return service.list_all(page=page, page_size=page_size, domain=domain,
                            status=status, keyword=keyword)


@router.post("", response_model=KnowledgeBaseResponse)
async def create_kb(
    request: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a knowledge base."""
    service = KnowledgeBaseService(db)
    return service.create(
        name=request.name,
        description=request.description,
        domain=request.domain,
        owner_id=request.owner_id,
        created_by=str(current_user.id),
    )


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_kb(
    kb_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get knowledge base detail."""
    service = KnowledgeBaseService(db)
    return service.get_by_id(kb_id)


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_kb(
    kb_id: str,
    request: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a knowledge base."""
    service = KnowledgeBaseService(db)
    return service.update(kb_id, **request.model_dump(exclude_none=True))


@router.delete("/{kb_id}")
async def delete_kb(
    kb_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a knowledge base."""
    service = KnowledgeBaseService(db)
    return service.delete(kb_id)


@router.patch("/{kb_id}/status")
async def update_kb_status(
    kb_id: str,
    request: KnowledgeBaseStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Enable or disable a knowledge base."""
    service = KnowledgeBaseService(db)
    return service.update_status(kb_id, request.status)


@router.get("/{kb_id}/overview", response_model=KnowledgeBaseOverview)
async def get_kb_overview(
    kb_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get knowledge base overview stats."""
    service = KnowledgeBaseService(db)
    return service.get_overview(kb_id)
