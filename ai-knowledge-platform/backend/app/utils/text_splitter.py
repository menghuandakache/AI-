"""Text splitting utilities."""
import re
from app.core.config import get_settings

settings = get_settings()


def split_by_heading(text: str, level: int | None = None) -> list[dict]:
    """
    Split text by markdown-style headings.

    Args:
        level: Specific heading level (1-4). None = all levels.
    """
    if level is not None:
        heading_pattern = re.compile(rf'^{"#" * level}\s+.+$', re.MULTILINE)
    else:
        heading_pattern = re.compile(r'^#{1,4}\s+.+$', re.MULTILINE)

    sections = heading_pattern.split(text)
    headings = heading_pattern.findall(text)

    if not sections or len(sections) <= 1:
        return []

    chunks = []
    for i, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue
        heading = headings[i - 1].strip() if i > 0 else ""
        title = heading.lstrip("#").strip() if heading else f"Section {i}"

        chunks.append({"text": section, "title": title, "chunk_index": i})

    return chunks


def split_by_paragraph(text: str) -> list[dict]:
    """Split text by paragraphs. Falls back to line-based for PDF-style text."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # Fallback: PDFs often don't have double newlines between paragraphs
    if len(paragraphs) <= 1:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if len(lines) > 1:
            paragraphs = []
            current = ""
            for line in lines:
                if current:
                    current += "\n" + line
                else:
                    current = line
                if line and line[-1] in '。！？.!?':
                    paragraphs.append(current)
                    current = ""
            if current.strip():
                paragraphs.append(current)

    chunks = []
    current = ""
    idx = 0

    for para in paragraphs:
        if len(current) + len(para) > settings.CHUNK_SIZE and current:
            chunks.append({"text": current.strip(), "title": f"段 {idx + 1}", "chunk_index": idx})
            idx += 1
            current = para
        else:
            current = current + "\n\n" + para if current else para

    if current.strip():
        chunks.append({"text": current.strip(), "title": f"段 {idx + 1}", "chunk_index": idx})

    return chunks


def split_by_fixed_length(text: str) -> list[dict]:
    """Split text by fixed character length with overlap."""
    chunk_size = settings.CHUNK_SIZE
    overlap = settings.CHUNK_OVERLAP

    if len(text) <= chunk_size:
        return [{"text": text, "title": "", "chunk_index": 0}]

    chunks = []
    start = 0
    idx = 0

    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({"text": chunk_text, "title": f"块 {idx + 1}", "chunk_index": idx})
        start = end - overlap
        idx += 1

    return chunks


def split_by_sentence(text: str) -> list[dict]:
    """
    Split text by sentence delimiters (。！？.!?) and merge
    small sentences into chunks up to CHUNK_SIZE.
    """
    sentence_pattern = re.compile(r'([^。！？.!?\n]+[。！？.!?]+)')
    sentences = sentence_pattern.findall(text)

    if not sentences:
        remaining = text.strip()
        if remaining:
            return split_by_fixed_length(remaining)
        return []

    chunks = []
    current = ""
    idx = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current) + len(sentence) > settings.CHUNK_SIZE and current:
            chunks.append({"text": current.strip(), "title": f"句段 {idx + 1}", "chunk_index": idx})
            idx += 1
            current = sentence
        else:
            current = current + sentence if current else sentence

    if current.strip():
        chunks.append({"text": current.strip(), "title": f"句段 {idx + 1}", "chunk_index": idx})

    return chunks


def split_text(text: str, method: str = "auto") -> list[dict]:
    """Main text splitting function."""
    if method == "fixed":
        return split_by_fixed_length(text)
    elif method == "h1":
        return split_by_heading(text, level=1)
    elif method == "h2":
        return split_by_heading(text, level=2)
    elif method == "h3":
        return split_by_heading(text, level=3)
    elif method == "sentence":
        return split_by_sentence(text)
    elif method == "paragraph":
        return split_by_paragraph(text)
    elif method == "heading":
        return split_by_heading(text, level=None)
    else:
        # auto: try heading → paragraph → fixed
        chunks = split_by_heading(text, level=None)
        if not chunks:
            chunks = split_by_paragraph(text)
        if not chunks:
            chunks = split_by_fixed_length(text)
        return chunks
