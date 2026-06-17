"""Celery application configuration."""
from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ai_knowledge_platform",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_queue="default",
    task_queues={
        "document_queue": {"exchange": "document", "routing_key": "document"},
        "embedding_queue": {"exchange": "embedding", "routing_key": "embedding"},
        "index_queue": {"exchange": "index", "routing_key": "index"},
        "maintenance_queue": {"exchange": "maintenance", "routing_key": "maintenance"},
    },
    task_default_exchange="default",
    task_default_routing_key="default",
    task_routes={
        "app.tasks.document_tasks.*": {"queue": "document_queue"},
        "app.tasks.embedding_tasks.*": {"queue": "embedding_queue"},
        "app.tasks.index_tasks.*": {"queue": "index_queue"},
        "app.tasks.cleanup_tasks.*": {"queue": "maintenance_queue"},
    },
)

celery_app.autodiscover_tasks([
    "app.tasks.document_tasks",
    "app.tasks.embedding_tasks",
    "app.tasks.index_tasks",
    "app.tasks.cleanup_tasks",
])
