"""Conversation routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate, ConversationResponse, ConversationListResponse,
    ConversationDetailResponse,
)
from app.repositories.conversation_repo import ConversationRepository

router = APIRouter()


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    agent_id: str = Query(..., description="Agent ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List conversations for an agent."""
    repo = ConversationRepository(db)
    items = repo.list_by_agent_user(agent_id, str(current_user.id))
    return {
        "items": [
            {
                "id": str(c.id),
                "agent_id": str(c.agent_id),
                "user_id": str(c.user_id) if c.user_id else None,
                "title": c.title,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            }
            for c in items
        ],
        "total": len(items),
    }


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new conversation."""
    repo = ConversationRepository(db)
    conv = repo.create(
        agent_id=request.agent_id,
        user_id=str(current_user.id),
        title=request.title,
    )
    return {
        "id": str(conv.id),
        "agent_id": str(conv.agent_id),
        "user_id": str(conv.user_id) if conv.user_id else None,
        "title": conv.title,
        "created_at": conv.created_at,
        "updated_at": conv.updated_at,
    }


@router.get("/{conv_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conv_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get conversation with messages."""
    repo = ConversationRepository(db)
    conv = repo.get_by_id(conv_id)
    if not conv:
        return {"id": conv_id, "agent_id": "", "title": "", "messages": [], "created_at": None}
    messages = repo.get_messages(conv_id)
    return {
        "id": str(conv.id),
        "agent_id": str(conv.agent_id),
        "title": conv.title,
        "messages": [
            {
                "id": str(m.id),
                "role": "user",
                "content": m.question,
                "created_at": m.created_at,
            }
            for m in messages
        ] + [
            {
                "id": str(m.id) + "_a",
                "role": "assistant",
                "content": m.answer or "",
                "sources": m.cited_knowledge_ids or [],
                "status": m.status,
                "created_at": m.created_at,
            }
            for m in messages if m.answer
        ],
        "created_at": conv.created_at,
    }


@router.delete("/{conv_id}")
async def delete_conversation(
    conv_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a conversation."""
    repo = ConversationRepository(db)
    ok = repo.delete(conv_id)
    return {"message": "deleted" if ok else "not found"}
