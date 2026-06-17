"""Index rebuild tasks."""
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.repositories.knowledge_repo import KnowledgeRepository
from app.tasks.embedding_tasks import generate_embeddings_task


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def rebuild_knowledge_index_task(self, knowledge_id: str):
    """Rebuild index for a single knowledge item."""
    return generate_embeddings_task.delay(knowledge_id)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=600)
def rebuild_kb_index_task(self, kb_id: str):
    """Rebuild index for all knowledge items in a knowledge base."""
    db = SessionLocal()
    try:
        knowledge_repo = KnowledgeRepository(db)
        items = knowledge_repo.list_available(kb_id=kb_id, page_size=1000)

        task_ids = []
        for item in items:
            task = generate_embeddings_task.delay(str(item.id))
            task_ids.append(task.id)

        return {
            "kb_id": kb_id,
            "knowledge_count": len(items),
            "task_ids": task_ids,
        }

    finally:
        db.close()
