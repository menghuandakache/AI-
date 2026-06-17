"""Search routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.search import (
    KeywordSearchRequest, SemanticSearchRequest, HybridSearchRequest, SearchResponse,
)
from app.services.retrieval_service import RetrievalService

router = APIRouter()


@router.post("/keyword", response_model=SearchResponse)
async def keyword_search(
    request: KeywordSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Keyword-based knowledge search."""
    service = RetrievalService(db)
    results = service.keyword_search(request.query, kb_id=request.kb_id)
    return SearchResponse(
        items=results,
        total=len(results),
        query=request.query,
    )


@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Semantic (vector) knowledge search."""
    service = RetrievalService(db)
    results = service.semantic_search(request.query, kb_id=request.kb_id, top_k=request.top_k)
    return SearchResponse(
        items=results,
        total=len(results),
        query=request.query,
    )


@router.post("/hybrid", response_model=SearchResponse)
async def hybrid_search(
    request: HybridSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Hybrid search combining keyword and semantic approaches."""
    service = RetrievalService(db)
    results = service.hybrid_search(request.query, kb_id=request.kb_id, top_k=request.top_k)
    return SearchResponse(
        items=results,
        total=len(results),
        query=request.query,
    )
