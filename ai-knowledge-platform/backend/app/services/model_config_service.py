"""Model config service."""
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException
from app.repositories.model_config_repo import ModelConfigRepository


class ModelConfigService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ModelConfigRepository(db)

    def create(self, label: str, model_name: str, base_url: str, api_key: str,
               is_default: bool = False) -> dict:
        cfg = self.repo.create(label, model_name, base_url, api_key, is_default)
        return self._to_dict(cfg)

    def get_by_id(self, cfg_id: str) -> dict:
        cfg = self.repo.get_by_id(cfg_id)
        if not cfg:
            raise NotFoundException(f"Model config {cfg_id} not found")
        return self._to_dict(cfg)

    def list_all(self) -> dict:
        items = self.repo.list_all()
        return {
            "items": [self._to_dict(c) for c in items],
            "total": len(items),
        }

    def update(self, cfg_id: str, **kwargs) -> dict:
        cfg = self.repo.update(cfg_id, **kwargs)
        if not cfg:
            raise NotFoundException(f"Model config {cfg_id} not found")
        return self._to_dict(cfg)

    def delete(self, cfg_id: str) -> dict:
        ok = self.repo.delete(cfg_id)
        if not ok:
            raise NotFoundException(f"Model config {cfg_id} not found")
        return {"message": "Model config deleted"}

    def get_default(self) -> dict | None:
        cfg = self.repo.get_default()
        return self._to_dict(cfg) if cfg else None

    def _to_dict(self, cfg) -> dict:
        return {
            "id": str(cfg.id),
            "label": cfg.label,
            "model_name": cfg.model_name,
            "base_url": cfg.base_url,
            "api_key": cfg.api_key,
            "is_default": cfg.is_default,
            "status": cfg.status,
            "created_at": cfg.created_at,
            "updated_at": cfg.updated_at,
        }
