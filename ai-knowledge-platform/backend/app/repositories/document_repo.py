"""Document repository."""
from sqlalchemy.orm import Session
from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, kb_id: str, filename: str, file_path: str, file_type: str,
               file_size: int = None, created_by: str = None) -> Document:
        doc = Document(
            kb_id=kb_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            parse_status="uploaded",
            created_by=created_by,
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_by_id(self, document_id: str) -> Document | None:
        return self.db.query(Document).filter(Document.id == document_id).first()

    def update_parse_status(self, document_id: str, status: str, error: str = None) -> Document | None:
        doc = self.get_by_id(document_id)
        if doc:
            doc.parse_status = status
            if error:
                doc.parse_error = error
            self.db.commit()
            self.db.refresh(doc)
        return doc

    def list_by_kb(self, kb_id: str, page: int = 1, page_size: int = 20) -> list[Document]:
        return self.db.query(Document).filter(
            Document.kb_id == kb_id
        ).order_by(Document.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    def count_by_kb(self, kb_id: str) -> int:
        return self.db.query(Document).filter(Document.kb_id == kb_id).count()
