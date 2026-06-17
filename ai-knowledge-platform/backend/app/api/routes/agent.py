"""Agent routes."""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.schemas.agent import (
    AgentCreate, AgentUpdate, AgentResponse, AgentListResponse, AgentGenerateRequest,
)
from app.schemas.chat import ChatRequest
from app.services.agent_service import AgentService
from app.services.rag_service import RAGService

router = APIRouter()


@router.get("", response_model=AgentListResponse)
async def list_agents(
    status: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all agents."""
    service = AgentService(db)
    return service.list_all(status=status, page=page, page_size=page_size)


@router.post("", response_model=AgentResponse)
async def create_agent(
    request: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create an agent."""
    service = AgentService(db)
    return service.create(
        name=request.name,
        description=request.description,
        kb_ids=request.kb_ids,
        prompt_config=request.prompt_config,
        answer_style=request.answer_style,
        citation_policy=request.citation_policy,
        no_answer_policy=request.no_answer_policy,
        created_by=str(current_user.id),
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get agent detail."""
    service = AgentService(db)
    return service.get_by_id(agent_id)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    request: AgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update agent configuration."""
    service = AgentService(db)
    return service.update(agent_id, **request.model_dump(exclude_none=True))


@router.patch("/{agent_id}/disable")
async def disable_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Disable an agent."""
    service = AgentService(db)
    return service.disable(agent_id)


@router.patch("/{agent_id}/enable")
async def enable_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Re-enable a disabled agent."""
    service = AgentService(db)
    return service.enable(agent_id)


@router.post("/generate", response_model=AgentResponse)
async def generate_agent(
    request: AgentGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Auto-generate an agent from a knowledge base."""
    service = AgentService(db)
    return service.generate(kb_id=request.kb_id, name=request.name)


@router.post("/{agent_id}/chat")
async def chat_with_agent(
    agent_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Chat with an agent (non-streaming)."""
    agent_service = AgentService(db)
    agent = agent_service.get_by_id(agent_id)

    rag_service = RAGService(db)
    kb_id = agent["kb_ids"][0] if agent["kb_ids"] else None

    return rag_service.answer(
        question=request.question,
        kb_id=kb_id,
        agent_id=agent_id,
        user_id=str(current_user.id),
        citation_policy=agent.get("citation_policy", "required"),
        llm_config_id=request.llm_config_id,
        conversation_id=request.conversation_id,
    )


@router.post("/{agent_id}/chat/stream")
async def chat_with_agent_stream(
    agent_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Chat with an agent (streaming SSE)."""
    agent_service = AgentService(db)
    agent = agent_service.get_by_id(agent_id)

    rag_service = RAGService(db)
    kb_id = agent["kb_ids"][0] if agent["kb_ids"] else None

    return StreamingResponse(
        rag_service.answer_stream(
            question=request.question,
            kb_id=kb_id,
            agent_id=agent_id,
            user_id=str(current_user.id),
            llm_config_id=request.llm_config_id,
            conversation_id=request.conversation_id,
        ),
        media_type="text/event-stream",
    )
