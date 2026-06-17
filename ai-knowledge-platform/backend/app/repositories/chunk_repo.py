"""Knowledge Chunk repository with pgvector operations."""
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_item import KnowledgeItem
from app.models.knowledge_base import KnowledgeBase


class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, knowledge_id: str, kb_id: str, chunk_text: str, chunk_index: int,
               embedding: list[float] = None, metadata: dict = None,
               token_count: int = None) -> KnowledgeChunk:
        chunk = KnowledgeChunk(
            knowledge_id=knowledge_id,
            kb_id=kb_id,
            chunk_text=chunk_text,
            chunk_index=chunk_index,
            embedding=embedding,
            chunk_metadata=metadata or {},
            token_count=token_count,
        )
        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)
        return chunk

    def batch_create(self, chunks: list[dict]) -> list[KnowledgeChunk]:
        """Batch create chunks. Each dict should have the required fields."""
        created = []
        for chunk_data in chunks:
            chunk = KnowledgeChunk(**chunk_data)
            self.db.add(chunk)
            created.append(chunk)
        self.db.commit()
        for c in created:
            self.db.refresh(c)
        return created

    def get_by_id(self, chunk_id: str) -> KnowledgeChunk | None:
        return self.db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()

    def delete_by_knowledge_id(self, knowledge_id: str) -> int:
        """Delete all chunks for a knowledge item. Returns count deleted."""
        count = self.db.query(KnowledgeChunk).filter(
            KnowledgeChunk.knowledge_id == knowledge_id
        ).delete()
        self.db.commit()
        return count

    def get_by_knowledge_id(self, knowledge_id: str) -> list[KnowledgeChunk]:
        return self.db.query(KnowledgeChunk).filter(
            KnowledgeChunk.knowledge_id == knowledge_id
        ).order_by(KnowledgeChunk.chunk_index).all()

    def vector_search(self, query_embedding: list[float], kb_id: str = None,
                      top_k: int = 5, similarity_threshold: float = 0.5) -> list:
        """Perform vector similarity search using pgvector."""
        embedding_str = json.dumps(query_embedding)
        params = {
            "embedding": embedding_str,
            "threshold": similarity_threshold,
            "top_k": top_k,
        }

        query_sql = """
            SELECT
                kc.id as chunk_id,
                kc.knowledge_id,
                kc.kb_id,
                kc.chunk_text,
                kc.chunk_index,
                kc.chunk_metadata,
                1 - (kc.embedding <=> CAST(:embedding AS vector)) as similarity_score
            FROM knowledge_chunks kc
            JOIN knowledge_items ki ON kc.knowledge_id = ki.id
            JOIN knowledge_bases kb ON kc.kb_id = kb.id
            WHERE ki.status = 'available'
            AND kb.status = 'enabled'
            AND 1 - (kc.embedding <=> CAST(:embedding AS vector)) > :threshold
        """

        if kb_id:
            query_sql += " AND kc.kb_id = :kb_id"
            params["kb_id"] = kb_id

        query_sql += " ORDER BY similarity_score DESC LIMIT :top_k"

        result = self.db.execute(text(query_sql), params)
        rows = result.fetchall()
        return [
            {
                "chunk_id": str(row[0]),
                "knowledge_id": str(row[1]),
                "kb_id": str(row[2]),
                "chunk_text": row[3],
                "chunk_index": row[4],
                "metadata": row[5],
                "score": float(row[6]),
            }
            for row in rows
        ]

    def _extract_chinese_keywords(self, query: str) -> list[str]:
        """Extract meaningful keywords from Chinese query.
        Removes question words and tries progressively shorter substrings."""
        import re
        # Common Chinese question patterns to strip
        question_patterns = ['怎么', '如何', '怎样', '为什么', '哪里', '请问', '能否',
                             '可以', '吗', '呢', '什么', '是什么', '怎么做']
        cleaned = query
        for p in question_patterns:
            cleaned = cleaned.replace(p, ' ')
        # Also remove punctuation
        cleaned = re.sub(r'[，。！？、；：\s]+', ' ', cleaned).strip()

        # Split into words by spaces
        words = [w.strip() for w in cleaned.split() if w.strip()]
        if not words:
            return [query]

        # Filter very short/stop words
        stop_chars = {'的', '我', '要', '想', '是', '在', '有', '和', '了', '不', '啊', '嘛', '吗', '呢'}
        result = [w for w in words if w not in stop_chars and len(w) > 1]
        return result if result else [query]

    def keyword_search(self, query: str, kb_id: str = None, top_k: int = 5) -> list:
        """Keyword search using ILIKE on chunk text and knowledge title.
        Falls back to direct knowledge_items search if no chunks exist."""
        # Extract keywords from Chinese query
        keywords = self._extract_chinese_keywords(query)
        # Build OR conditions for each keyword
        or_conditions = []
        params: dict = {"top_k": top_k}
        for i, kw in enumerate(keywords):
            param_name = f"query_{i}"
            or_conditions.append(f"(kc.chunk_text ILIKE :{param_name} OR ki.title ILIKE :{param_name})")
            params[param_name] = f"%{kw}%"

        where_clause = " OR ".join(or_conditions) if or_conditions else "(kc.chunk_text ILIKE :query0 OR ki.title ILIKE :query0)"
        if not params.get("query0"):
            params["query0"] = f"%{query}%"

        # Try chunk-based search first
        query_sql = """
            SELECT
                kc.id as chunk_id,
                kc.knowledge_id,
                kc.kb_id,
                kc.chunk_text,
                kc.chunk_index,
                kc.chunk_metadata,
                0.8 as score
            FROM knowledge_chunks kc
            JOIN knowledge_items ki ON kc.knowledge_id = ki.id
            JOIN knowledge_bases kb ON kc.kb_id = kb.id
            WHERE ki.status = 'available'
            AND kb.status = 'enabled'
            AND ({w})
        """.format(w=where_clause)

        if kb_id:
            query_sql += " AND kc.kb_id = :kb_id"
            params["kb_id"] = kb_id

        query_sql += " ORDER BY score DESC LIMIT :top_k"

        result = self.db.execute(text(query_sql), params)
        rows = result.fetchall()

        # Fallback: search knowledge_items directly (no chunks yet)
        if not rows:
            rows = self._direct_knowledge_search(query, kb_id, top_k)

        return [
            {
                "chunk_id": str(row[0]) if row[0] else None,
                "knowledge_id": str(row[1]),
                "kb_id": str(row[2]),
                "chunk_text": row[3] or "",
                "chunk_index": row[4] if len(row) > 4 else 0,
                "metadata": row[5] if len(row) > 5 else {},
                "score": float(row[6]) if len(row) > 6 and row[6] else 0.5,
            }
            for row in rows
        ]

    def _direct_knowledge_search(self, query: str, kb_id: str = None, top_k: int = 5) -> list:
        """Search knowledge_items directly when no chunks exist."""
        keywords = self._extract_chinese_keywords(query)
        or_conditions = []
        params: dict = {"top_k": top_k}
        for i, kw in enumerate(keywords):
            param_name = f"q_{i}"
            or_conditions.append(f"(ki.content ILIKE :{param_name} OR ki.title ILIKE :{param_name})")
            params[param_name] = f"%{kw}%"
        where_clause = " OR ".join(or_conditions) if or_conditions else "(ki.content ILIKE :q0 OR ki.title ILIKE :q0)"
        if not params.get("q0"):
            params["q0"] = f"%{query}%"

        sql = f"""
            SELECT
                NULL as chunk_id,
                ki.id as knowledge_id,
                ki.kb_id,
                ki.content as chunk_text,
                0 as chunk_index,
                '{{}}'::jsonb as chunk_metadata,
                0.5 as score
            FROM knowledge_items ki
            JOIN knowledge_bases kb ON ki.kb_id = kb.id
            WHERE ki.status = 'available'
            AND kb.status = 'enabled'
            AND ({where_clause})
        """
        if kb_id:
            sql += " AND ki.kb_id = :kb_id"
            params["kb_id"] = kb_id
        sql += " ORDER BY score DESC LIMIT :top_k"

        result = self.db.execute(text(sql), params)
        return result.fetchall()

    def update_metadata(self, chunk_id: str, metadata: dict) -> KnowledgeChunk | None:
        chunk = self.get_by_id(chunk_id)
        if chunk:
            chunk.chunk_metadata = metadata
            self.db.commit()
            self.db.refresh(chunk)
        return chunk
