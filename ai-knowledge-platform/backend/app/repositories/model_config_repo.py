"""Model config repository."""
from sqlalchemy.orm import Session
from app.models.model_config import ModelConfig


class ModelConfigRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, label: str, model_name: str, base_url: str, api_key: str,
               is_default: bool = False) -> ModelConfig:
        # If setting as default, unset other defaults
        if is_default:
            self.db.query(ModelConfig).filter(ModelConfig.is_default == True).update({"is_default": False})
        cfg = ModelConfig(
            label=label, model_name=model_name, base_url=base_url,
            api_key=api_key, is_default=is_default,
        )
        self.db.add(cfg)
        self.db.commit()
        self.db.refresh(cfg)
        return cfg

    def get_by_id(self, cfg_id: str) -> ModelConfig | None:
        return self.db.query(ModelConfig).filter(ModelConfig.id == cfg_id).first()

    def get_default(self) -> ModelConfig | None:
        return self.db.query(ModelConfig).filter(ModelConfig.is_default == True).first()

    def list_all(self) -> list[ModelConfig]:
        return self.db.query(ModelConfig).order_by(ModelConfig.created_at.desc()).all()

    def count_all(self) -> int:
        return self.db.query(ModelConfig).count()

    def update(self, cfg_id: str, **kwargs) -> ModelConfig | None:
        cfg = self.get_by_id(cfg_id)
        if cfg:
            if kwargs.get("is_default"):
                self.db.query(ModelConfig).filter(ModelConfig.is_default == True).update({"is_default": False})
            for key, value in kwargs.items():
                if value is not None and hasattr(cfg, key):
                    setattr(cfg, key, value)
            self.db.commit()
            self.db.refresh(cfg)
        return cfg

    def delete(self, cfg_id: str) -> bool:
        cfg = self.get_by_id(cfg_id)
        if cfg:
            self.db.delete(cfg)
            self.db.commit()
            return True
        return False
