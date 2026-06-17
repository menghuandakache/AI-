"""Retrieval service - keyword, vector, and hybrid search."""
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.repositories.chunk_repo import ChunkRepository
from app.repositories.knowledge_repo import KnowledgeRepository
from app.services.embedding_service import EmbeddingService

settings = get_settings()


class RetrievalService:
    """Handles all retrieval strategies: keyword, semantic, and hybrid."""

    def __init__(self, db: Session):
        self.db = db
        self.chunk_repo = ChunkRepository(db)
        self.knowledge_repo = KnowledgeRepository(db)
        self.embedding_service = EmbeddingService()

    def keyword_search(self, query: str, kb_id: str = None, top_k: int = None) -> list[dict]:
        """Perform keyword-based search."""
        top_k = top_k or settings.RETRIEVAL_TOP_K
        raw_results = self.chunk_repo.keyword_search(query, kb_id=kb_id, top_k=top_k)
        return self._enrich_results(raw_results)

    def semantic_search(self, query: str, kb_id: str = None, top_k: int = None) -> list[dict]:
        """Perform vector similarity search."""
        top_k = top_k or settings.RETRIEVAL_TOP_K
        query_embedding = self.embedding_service.encode_query(query)
        threshold = settings.SIMILARITY_THRESHOLD
        raw_results = self.chunk_repo.vector_search(
            query_embedding, kb_id=kb_id, top_k=top_k, similarity_threshold=threshold,
        )
        return self._enrich_results(raw_results)

    def hybrid_search(self, query: str, kb_id: str = None, top_k: int = None) -> list[dict]:
        """Combine keyword and semantic search results."""
        top_k = top_k or settings.RETRIEVAL_TOP_K

        keyword_results = self.keyword_search(query, kb_id=kb_id, top_k=top_k * 2)
        # Semantic search: only attempt if model is already loaded (avoid hanging on first download)
        semantic_results = []
        if self.embedding_service.is_available():
            try:
                semantic_results = self.semantic_search(query, kb_id=kb_id, top_k=top_k * 2)
            except Exception:
                pass  # gracefully degrade to keyword-only

        # Merge and deduplicate by knowledge_id
        seen = set()
        merged = []

        for r in keyword_results + semantic_results:
            kid = r.get("knowledge_id")
            if kid not in seen:
                seen.add(kid)
                merged.append(r)

        # Sort by score descending
        merged.sort(key=lambda x: x.get("score", 0), reverse=True)
        return merged[:top_k]

    def _enrich_results(self, raw_results: list[dict]) -> list[dict]:
        """Enrich search results with knowledge item and KB info."""
        enriched = []
        for r in raw_results:
            knowledge = self.knowledge_repo.get_by_id(r["knowledge_id"])
            if not knowledge:
                continue

            kb_info = None
            try:
                from app.repositories.kb_repo import KnowledgeBaseRepository
                kb_repo = KnowledgeBaseRepository(self.db)
                kb = kb_repo.get_by_id(r["kb_id"])
                kb_info = kb.name if kb else None
            except Exception:
                pass

            metadata = r.get("metadata") or {}
            enriched.append({
                "knowledge_id": r["knowledge_id"],
                "chunk_id": r.get("chunk_id"),
                "title": knowledge.title,
                "chunk_text": r["chunk_text"],
                "content": knowledge.content,
                "category": knowledge.category,
                "tags": knowledge.tags or [],
                "source_file": metadata.get("source_file", ""),
                "score": r["score"],
                "kb_id": r["kb_id"],
                "kb_name": kb_info,
            })
        return enriched
