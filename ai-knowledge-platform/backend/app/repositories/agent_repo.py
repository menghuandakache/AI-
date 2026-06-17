"""Agent repository."""
from sqlalchemy.orm import Session
from app.models.agent import Agent


class AgentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, description: str = None, kb_ids: list = None,
               prompt_config: str = None, answer_style: str = "detailed",
               citation_policy: str = "required", no_answer_policy: str = "prompt",
               created_by: str = None) -> Agent:
        agent = Agent(
            name=name,
            description=description,
            kb_ids=kb_ids or [],
            prompt_config=prompt_config,
            answer_style=answer_style,
            citation_policy=citation_policy,
            no_answer_policy=no_answer_policy,
            status="enabled",
            created_by=created_by,
        )
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def get_by_id(self, agent_id: str) -> Agent | None:
        return self.db.query(Agent).filter(Agent.id == agent_id).first()

    def list_all(self, status: str = None, page: int = 1, page_size: int = 20) -> list[Agent]:
        query = self.db.query(Agent)
        if status:
            query = query.filter(Agent.status == status)
        return query.order_by(Agent.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    def count_all(self, status: str = None) -> int:
        query = self.db.query(Agent)
        if status:
            query = query.filter(Agent.status == status)
        return query.count()

    def update(self, agent_id: str, **kwargs) -> Agent | None:
        agent = self.get_by_id(agent_id)
        if agent:
            for key, value in kwargs.items():
                if value is not None and hasattr(agent, key):
                    setattr(agent, key, value)
            self.db.commit()
            self.db.refresh(agent)
        return agent

    def disable(self, agent_id: str) -> Agent | None:
        return self.update(agent_id, status="disabled")

    def enable(self, agent_id: str) -> Agent | None:
        return self.update(agent_id, status="enabled")

    def get_enabled(self) -> list[Agent]:
        return self.db.query(Agent).filter(Agent.status == "enabled").all()
