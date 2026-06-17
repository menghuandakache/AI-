"""Embedding service - generates embeddings using bge-m3 model.

BGE-M3 model download from HuggingFace (~2GB) can hang in China.
Keyword search works without the model. To enable semantic search:
1. Download the model first: huggingface-cli download BAAI/bge-m3
2. Set BGE_M3_MODEL_PATH=/path/to/local/model in .env
"""
from app.core.config import get_settings

settings = get_settings()

_model = None
_load_attempted = False
_load_error = "Embedding model not loaded yet"


class EmbeddingService:
    """Generates embeddings. Falls back gracefully —
    keyword search works without the model."""

    def is_available(self) -> bool:
        """Check if model is available. Tries to load if cached."""
        global _model, _load_attempted
        if _model is not None:
            return True
        # Try loading (fast if cached, skip if already failed)
        if not _load_attempted:
            self.load_model()
        return _model is not None

    def load_model(self):
        """Explicitly load the model. This may download ~2GB from HuggingFace.
        Call this once at startup or via admin action."""
        global _model, _load_attempted, _load_error
        if _load_attempted:
            return
        _load_attempted = True
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(
                settings.BGE_M3_MODEL_PATH,
                device=settings.EMBEDDING_DEVICE,
            )
            _load_error = None
        except ImportError:
            _load_error = "sentence-transformers not installed"
        except Exception as e:
            _load_error = str(e)

    def encode_query(self, query: str) -> list[float]:
        self.load_model()
        if _model is None:
            raise RuntimeError(f"Embedding model unavailable: {_load_error}")
        embedding = _model.encode(query, normalize_embeddings=True)
        return embedding.tolist()

    def encode_batch(self, texts: list[str], batch_size: int = None) -> list[list[float]]:
        if not texts:
            return []
        self.load_model()
        if _model is None:
            raise RuntimeError(f"Embedding model unavailable: {_load_error}")
        batch_size = batch_size or settings.EMBEDDING_BATCH_SIZE
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            emb = _model.encode(batch, normalize_embeddings=True)
            all_embeddings.extend(emb.tolist())
        return all_embeddings

    def get_dimension(self) -> int:
        return _model.get_sentence_embedding_dimension() if self.is_available() else 1024
