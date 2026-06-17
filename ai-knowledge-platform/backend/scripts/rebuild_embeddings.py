"""Script to rebuild all embeddings for available knowledge."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.repositories.knowledge_repo import KnowledgeRepository
from app.tasks.embedding_tasks import generate_embeddings_task


def rebuild_all():
    """Rebuild embeddings for all available knowledge items."""
    db = SessionLocal()
    try:
        knowledge_repo = KnowledgeRepository(db)
        items = knowledge_repo.list_available(page_size=10000)

        print(f"Found {len(items)} available knowledge items")

        for item in items:
            print(f"Submitting embedding task for: {item.title}")
            generate_embeddings_task.delay(str(item.id))

        print("All embedding tasks submitted!")

    finally:
        db.close()


if __name__ == "__main__":
    rebuild_all()
