"""Agent service."""
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException
from app.repositories.agent_repo import AgentRepository


class AgentService:
    def __init__(self, db: Session):
        self.db = db
        self.agent_repo = AgentRepository(db)

    def create(self, name: str, description: str = None, kb_ids: list = None,
               prompt_config: str = None, answer_style: str = "detailed",
               citation_policy: str = "required", no_answer_policy: str = "prompt",
               created_by: str = None) -> dict:
        agent = self.agent_repo.create(
            name=name, description=description, kb_ids=kb_ids,
            prompt_config=prompt_config, answer_style=answer_style,
            citation_policy=citation_policy, no_answer_policy=no_answer_policy,
            created_by=created_by,
        )
        return self._to_dict(agent)

    def get_by_id(self, agent_id: str) -> dict:
        agent = self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise NotFoundException(f"Agent {agent_id} not found")
        return self._to_dict(agent)

    def list_all(self, status: str = None, page: int = 1, page_size: int = 20) -> dict:
        items = self.agent_repo.list_all(status=status, page=page, page_size=page_size)
        total = self.agent_repo.count_all(status=status)
        return {
            "items": [self._to_dict(a) for a in items],
            "total": total,
        }

    def update(self, agent_id: str, **kwargs) -> dict:
        agent = self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise NotFoundException(f"Agent {agent_id} not found")
        agent = self.agent_repo.update(agent_id, **kwargs)
        return self._to_dict(agent)

    def disable(self, agent_id: str) -> dict:
        agent = self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise NotFoundException(f"Agent {agent_id} not found")
        self.agent_repo.disable(agent_id)
        return {"message": "Agent disabled successfully"}

    def enable(self, agent_id: str) -> dict:
        agent = self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise NotFoundException(f"Agent {agent_id} not found")
        self.agent_repo.enable(agent_id)
        return {"message": "Agent enabled successfully"}

    def generate(self, kb_id: str, name: str = None) -> dict:
        """Auto-generate an expert Agent based on a knowledge base."""
        from app.services.kb_service import KnowledgeBaseService
        kb_service = KnowledgeBaseService(self.db)
        kb = kb_service.get_by_id(kb_id)

        generated_name = name or f"{kb['domain'] or kb['name']}专家助手"
        description = f"基于「{kb['name']}」知识库的智能问答助手，可以回答{kb.get('domain', '')}相关的问题。"

        prompt_config = f"""你是{generated_name}，专注于{kb['name']}知识库的专业问答助手。
你的职责是基于知识库中的内容为用户提供准确、可靠的答案。
回答风格：结构化、详细。
引用策略：必须引用知识来源。
无答案策略：明确告知用户当前知识库中未找到相关内容。"""

        return self.create(
            name=generated_name,
            description=description,
            kb_ids=[kb_id],
            prompt_config=prompt_config,
            answer_style="detailed",
            citation_policy="required",
            no_answer_policy="prompt",
        )

    def _to_dict(self, agent) -> dict:
        return {
            "id": str(agent.id),
            "name": agent.name,
            "description": agent.description,
            "kb_ids": agent.kb_ids or [],
            "prompt_config": agent.prompt_config,
            "answer_style": agent.answer_style,
            "citation_policy": agent.citation_policy,
            "no_answer_policy": agent.no_answer_policy,
            "status": agent.status,
            "created_by": str(agent.created_by) if agent.created_by else None,
            "created_at": agent.created_at,
            "updated_at": agent.updated_at,
        }
