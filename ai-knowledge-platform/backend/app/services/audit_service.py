"""Audit service for recording key operations."""
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log(self, user_id: str, action: str, resource_type: str,
            resource_id: str = None, detail: dict = None) -> AuditLog:
        """Record an audit log entry."""
        audit = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail or {},
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def list_by_user(self, user_id: str, page: int = 1, page_size: int = 50) -> list[AuditLog]:
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
