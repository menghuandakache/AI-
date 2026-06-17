"""Document schemas."""
from datetime import datetime
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int | None = None
    parse_status: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class DocumentParseRequest(BaseModel):
    chunk_method: str = "auto"  # auto, fixed, h1, h2, h3, sentence, paragraph


class DocumentParseResponse(BaseModel):
    id: str
    parse_status: str
    message: str


class DocumentParseAsyncResponse(BaseModel):
    id: str
    parse_status: str
    message: str
    task_id: str | None = None


class DocumentImportRequest(BaseModel):
    draft_ids: list[str]


class DocumentImportResponse(BaseModel):
    imported_count: int
    message: str


class DocumentStatusResponse(BaseModel):
    id: str
    kb_id: str
    filename: str
    file_type: str
    parse_status: str
    parse_error: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class DocumentListItem(BaseModel):
    id: str
    kb_id: str
    filename: str
    file_type: str
    file_size: int | None = None
    parse_status: str
    parse_error: str | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    draft_count: int = 0

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    items: list[DocumentListItem]
    total: int
    page: int
    page_size: int


class DraftKnowledgeResponse(BaseModel):
    id: str
    title: str
    content: str
    chunk_index: int
    category: str | None = None
    tags: list[str] = []
