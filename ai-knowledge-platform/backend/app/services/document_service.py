"""Document service."""
import os
import uuid
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.exceptions import NotFoundException, ValidationException
from app.repositories.document_repo import DocumentRepository
from app.repositories.knowledge_repo import KnowledgeRepository

settings = get_settings()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".md", ".markdown"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/markdown",
    "text/plain",
}


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)

    def upload(self, kb_id: str, filename: str, file_content: bytes, created_by: str = None) -> dict:
        """Handle file upload and create document record."""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationException(f"File type '{ext}' not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

        file_size = len(file_content)
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise ValidationException(f"File size exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit")

        # Map extension to file_type
        if ext in (".docx", ".doc"):
            file_type = "docx"
        elif ext == ".pdf":
            file_type = "pdf"
        else:
            file_type = "md"

        # Save file
        upload_dir = settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        safe_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(upload_dir, safe_filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        doc = self.doc_repo.create(
            kb_id=kb_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            created_by=created_by,
        )
        return {
            "id": str(doc.id),
            "filename": doc.filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "parse_status": doc.parse_status,
            "created_at": doc.created_at,
        }

    def get_status(self, document_id: str) -> dict:
        doc = self.doc_repo.get_by_id(document_id)
        if not doc:
            raise NotFoundException(f"Document {document_id} not found")
        return {
            "id": str(doc.id),
            "kb_id": str(doc.kb_id),
            "filename": doc.filename,
            "file_type": doc.file_type,
            "parse_status": doc.parse_status,
            "parse_error": doc.parse_error,
            "created_at": doc.created_at,
        }

    def list_by_kb(self, kb_id: str, page: int = 1, page_size: int = 20) -> dict:
        """List documents for a knowledge base with draft counts."""
        docs = self.doc_repo.list_by_kb(kb_id, page=page, page_size=page_size)
        total = self.doc_repo.count_by_kb(kb_id)

        knowledge_repo = KnowledgeRepository(self.db)
        doc_ids = [str(doc.id) for doc in docs]
        draft_counts = knowledge_repo.count_drafts_by_source_file_ids(doc_ids) if doc_ids else {}

        items = []
        for doc in docs:
            items.append({
                "id": str(doc.id),
                "kb_id": str(doc.kb_id),
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "parse_status": doc.parse_status,
                "parse_error": doc.parse_error,
                "created_by": str(doc.created_by) if doc.created_by else None,
                "created_at": doc.created_at,
                "updated_at": doc.updated_at,
                "draft_count": draft_counts.get(str(doc.id), 0),
            })
        return {"items": items, "total": total, "page": page, "page_size": page_size}
