"""Cleanup and maintenance tasks."""
import os
from datetime import datetime, timedelta, timezone
from app.tasks.celery_app import celery_app
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.repositories.chunk_repo import ChunkRepository

settings = get_settings()


@celery_app.task
def cleanup_temp_files():
    """Clean up temp upload files older than 24 hours."""
    upload_dir = settings.UPLOAD_DIR
    if not os.path.exists(upload_dir):
        return {"message": "Upload directory does not exist"}

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    cleaned = 0

    for filename in os.listdir(upload_dir):
        if filename == ".gitkeep":
            continue
        filepath = os.path.join(upload_dir, filename)
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc)
            if mtime < cutoff:
                os.remove(filepath)
                cleaned += 1
        except Exception:
            pass

    return {"cleaned_files": cleaned}


@celery_app.task
def cleanup_orphan_chunks():
    """Clean up chunks for soft-deleted knowledge items."""
    db = SessionLocal()
    try:
        from app.models.knowledge_item import KnowledgeItem
        from app.models.knowledge_chunk import KnowledgeChunk

        # Find chunks for deleted knowledge items
        deleted_knowledge_ids = db.query(KnowledgeItem.id).filter(
            KnowledgeItem.status == "deleted"
        ).subquery()

        count = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.knowledge_id.in_(deleted_knowledge_ids)
        ).delete(synchronize_session=False)

        db.commit()
        return {"deleted_chunks": count}

    finally:
        db.close()
