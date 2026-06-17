"""Search schemas."""
from pydantic import BaseModel, Field


class KeywordSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    kb_id: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    kb_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=50)


class HybridSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    kb_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=50)


class SearchResultItem(BaseModel):
    knowledge_id: str
    chunk_id: str | None = None
    title: str
    chunk_text: str
    content: str | None = None
    category: str | None = None
    tags: list[str] = []
    source_file: str | None = None
    score: float
    kb_id: str
    kb_name: str | None = None


class SearchResponse(BaseModel):
    items: list[SearchResultItem]
    total: int
    query: str
