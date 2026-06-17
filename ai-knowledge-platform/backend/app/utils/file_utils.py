"""File utility functions."""
import os
import uuid

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".md", ".markdown"}


def get_safe_filename(original_filename: str) -> str:
    """Generate a safe unique filename."""
    ext = os.path.splitext(original_filename)[1].lower()
    return f"{uuid.uuid4()}{ext}"


def validate_file_type(filename: str) -> bool:
    """Check if file type is allowed."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def save_upload_file(file_content: bytes, file_path: str):
    """Save uploaded file to disk."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file_content)


def get_file_extension(filename: str) -> str:
    """Get lowercase file extension."""
    return os.path.splitext(filename)[1].lower()


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(file_path)


def delete_file(file_path: str):
    """Delete a file if it exists."""
    if os.path.exists(file_path):
        os.remove(file_path)
