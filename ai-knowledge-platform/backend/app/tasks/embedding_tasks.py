"""Async embedding generation tasks."""
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.embedding_service import EmbeddingService
from app.services.chunk_service import ChunkService
from app.repositories.knowledge_repo import KnowledgeRepository
from app.repositories.chunk_repo import ChunkRepository


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def generate_embeddings_task(self, knowledge_id: str):
    """Generate embeddings for a published knowledge item."""
    db = SessionLocal()
    try:
        knowledge_repo = KnowledgeRepository(db)
        chunk_repo = ChunkRepository(db)
        chunk_service = ChunkService()
        embedding_service = EmbeddingService()

        knowledge = knowledge_repo.get_by_id(knowledge_id)
        if not knowledge:
            return {"error": f"Knowledge item {knowledge_id} not found"}

        # Delete old chunks
        chunk_repo.delete_by_knowledge_id(knowledge_id)

        # Split knowledge content into chunks
        chunks = chunk_service.split_text(knowledge.content, method="auto")

        # Generate embeddings for each chunk
        chunk_texts = [c["text"] for c in chunks]
        embeddings = embedding_service.encode_batch(chunk_texts)

        # Create chunk records with metadata
        for i, chunk in enumerate(chunks):
            token_count = chunk_service.estimate_tokens(chunk["text"])
            chunk_repo.create(
                knowledge_id=knowledge_id,
                kb_id=str(knowledge.kb_id),
                chunk_text=chunk["text"],
                chunk_index=i,
                embedding=embeddings[i],
                metadata={
                    "knowledge_id": knowledge_id,
                    "kb_id": str(knowledge.kb_id),
                    "title": knowledge.title,
                    "category": knowledge.category,
                    "tags": knowledge.tags or [],
                    "source_type": knowledge.source_type,
                    "source_file": "",
                    "page": None,
                    "section": chunk.get("title", ""),
                },
                token_count=token_count,
            )

        return {
            "knowledge_id": knowledge_id,
            "chunk_count": len(chunks),
            "status": "completed",
        }

    except Exception as e:
        raise self.retry(exc=e)

    finally:
        db.close()
