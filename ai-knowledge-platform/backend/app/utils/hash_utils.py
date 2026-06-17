"""Hash utility functions."""
import hashlib


def file_hash(file_path: str, algorithm: str = "md5") -> str:
    """Calculate file hash."""
    h = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def text_hash(text: str, algorithm: str = "md5") -> str:
    """Calculate text hash (used for deduplication)."""
    h = hashlib.new(algorithm)
    h.update(text.encode("utf-8"))
    return h.hexdigest()
