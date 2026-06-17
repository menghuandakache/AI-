"""Chat routes for standalone knowledge base Q&A."""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from app.services.rag_service import RAGService
from app.repositories.qa_repo import QARepository

router = APIRouter()


@router.post("/ask", response_model=ChatResponse)
async def ask(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ask a question based on knowledge base."""
    rag_service = RAGService(db)
    return rag_service.answer(
        question=request.question,
        kb_id=request.kb_id,
        agent_id=request.agent_id,
        user_id=str(current_user.id),
        llm_config_id=request.llm_config_id,
    )


@router.post("/ask/stream")
async def ask_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ask a question with streaming response."""
    rag_service = RAGService(db)
    return StreamingResponse(
        rag_service.answer_stream(
            question=request.question,
            kb_id=request.kb_id,
            agent_id=request.agent_id,
            user_id=str(current_user.id),
            llm_config_id=request.llm_config_id,
        ),
        media_type="text/event-stream",
    )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's chat history."""
    qa_repo = QARepository(db)
    items = qa_repo.list_by_user(str(current_user.id), page=page, page_size=page_size)
    total = qa_repo.count_by_user(str(current_user.id))
    return {
        "items": [
            {
                "id": str(item.id),
                "question": item.question,
                "answer": item.answer,
                "status": item.status,
                "feedback": item.feedback,
                "created_at": item.created_at,
            }
            for item in items
        ],
        "total": total,
    }
