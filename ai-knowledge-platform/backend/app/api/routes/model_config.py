"""Model configuration routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.schemas.model_config import (
    ModelConfigCreate, ModelConfigUpdate, ModelConfigResponse, ModelConfigListResponse,
)
from app.services.model_config_service import ModelConfigService

router = APIRouter()


@router.get("", response_model=ModelConfigListResponse)
async def list_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all model configs."""
    service = ModelConfigService(db)
    return service.list_all()


@router.post("", response_model=ModelConfigResponse)
async def create_config(
    request: ModelConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a model config."""
    service = ModelConfigService(db)
    return service.create(
        label=request.label,
        model_name=request.model_name,
        base_url=request.base_url,
        api_key=request.api_key,
        is_default=request.is_default,
    )


@router.get("/{config_id}", response_model=ModelConfigResponse)
async def get_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a model config detail."""
    service = ModelConfigService(db)
    return service.get_by_id(config_id)


@router.put("/{config_id}", response_model=ModelConfigResponse)
async def update_config(
    config_id: str,
    request: ModelConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a model config."""
    service = ModelConfigService(db)
    return service.update(config_id, **request.model_dump(exclude_none=True))


@router.delete("/{config_id}")
async def delete_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a model config."""
    service = ModelConfigService(db)
    return service.delete(config_id)
