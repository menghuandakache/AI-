"""Model config schemas."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ModelConfigCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    label: str = Field(..., min_length=1, max_length=200)
    model_name: str = Field(..., min_length=1, max_length=200)
    base_url: str = Field(..., min_length=1, max_length=500)
    api_key: str = Field(..., min_length=1, max_length=500)
    is_default: bool = False


class ModelConfigUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    label: str | None = Field(None, max_length=200)
    model_name: str | None = Field(None, max_length=200)
    base_url: str | None = Field(None, max_length=500)
    api_key: str | None = Field(None, max_length=500)
    is_default: bool | None = None


class ModelConfigResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

    id: str
    label: str
    model_name: str
    base_url: str
    api_key: str
    is_default: bool
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ModelConfigListResponse(BaseModel):
    items: list[ModelConfigResponse]
    total: int
