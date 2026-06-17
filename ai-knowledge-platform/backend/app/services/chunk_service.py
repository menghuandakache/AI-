"""Chunk service - text splitting and chunk management."""
import re
from app.core.config import get_settings

settings = get_settings()


class ChunkService:
    """Splits text into chunks for embedding and retrieval."""

    # Supported chunk methods
    CHUNK_METHODS = {
        "auto": "自动检测（优先标题→段落→固定长度）",
        "fixed": "固定长度切分",
        "h1": "Markdown 一级标题（#）",
        "h2": "Markdown 二级标题（##）",
        "h3": "Markdown 三级标题（###）",
        "sentence": "按句号切分（。！？.!?）",
        "paragraph": "按段落切分",
    }

    def split_text(self, text: str, method: str = "auto") -> list[dict]:
        """
        Split text into chunks based on the specified method.

        Methods:
        - auto: tries heading → paragraph → fixed (best-effort)
        - fixed: fixed character length with overlap
        - h1/h2/h3: markdown heading level 1/2/3
        - sentence: split by sentence delimiters
        - paragraph: split by blank lines (paragraphs)
        """
        if method == "fixed":
            return self._split_by_fixed_length(text)
        elif method == "h1":
            return self._split_by_heading(text, level=1)
        elif method == "h2":
            return self._split_by_heading(text, level=2)
        elif method == "h3":
            return self._split_by_heading(text, level=3)
        elif method == "sentence":
            return self._split_by_sentence(text)
        elif method == "paragraph":
            return self._split_by_paragraph(text)
        else:
            # Auto: try heading first, then paragraph, then fixed
            chunks = self._split_by_heading(text, level=None)
            if len(chunks) <= 1:
                chunks = self._split_by_paragraph(text)
            if len(chunks) <= 1:
                chunks = self._split_by_fixed_length(text)
            return chunks

    def _split_by_heading(self, text: str, level: int | None = None) -> list[dict]:
        """
        Split text by markdown-style headings.

        Args:
            level: Specific heading level (1-4). None = all levels (1-4).
        """
        if level is not None:
            # Match only headings of the exact level, e.g. "^# " for level 1
            heading_pattern = re.compile(rf'^{"#" * level}\s+.+$', re.MULTILINE)
        else:
            # Match any heading level 1-4
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

            if len(section) > settings.CHUNK_SIZE:
                sub_chunks = self._split_by_fixed_length(section)
                for j, sub in enumerate(sub_chunks):
                    chunks.append({
                        "text": sub["text"],
                        "title": f"{title} ({j + 1})",
                    })
            else:
                chunks.append({"text": section, "title": title})
        return chunks

    def _split_by_paragraph(self, text: str) -> list[dict]:
        """Split text by paragraphs and merge small ones.
        For text without clear paragraph breaks (common in PDFs), falls back to line-based splitting."""
        # First try double-newline (true paragraphs)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        # If only one huge paragraph (common in PDFs), fall back to line-based splitting
        if len(paragraphs) <= 1:
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            if len(lines) > 1:
                # Merge consecutive lines into paragraph-like chunks
                paragraphs = []
                current = ""
                for line in lines:
                    if current:
                        current += "\n" + line
                    else:
                        current = line
                    # Break when line ends with sentence-ending punctuation
                    if line and line[-1] in '。！？.!?':
                        paragraphs.append(current)
                        current = ""
                if current.strip():
                    paragraphs.append(current)

        if not paragraphs:
            return []

        chunks = []
        current_chunk = ""
        current_len = 0
        chunk_index = 0

        for para in paragraphs:
            para_len = len(para)
            if current_len + para_len > settings.CHUNK_SIZE and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "title": f"Paragraph {chunk_index + 1}",
                })
                chunk_index += 1
                current_chunk = para
                current_len = para_len
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
                current_len += para_len

        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "title": f"Paragraph {chunk_index + 1}",
            })

        return chunks

    def _split_by_fixed_length(self, text: str) -> list[dict]:
        """Split text by fixed character length with overlap."""
        chunk_size = settings.CHUNK_SIZE
        chunk_overlap = settings.CHUNK_OVERLAP

        if len(text) <= chunk_size:
            return [{"text": text, "title": ""}]

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "title": f"Chunk {chunk_index + 1}",
                })
            start = end - chunk_overlap
            chunk_index += 1

        return chunks

    def _split_by_sentence(self, text: str) -> list[dict]:
        """
        Split text by sentence delimiters (。！？.!?) and merge
        small sentences into chunks up to CHUNK_SIZE.
        """
        # Split on sentence-ending punctuation while keeping the delimiter
        sentence_pattern = re.compile(r'([^。！？.!?\n]+[。！？.!?]+)')
        sentences = sentence_pattern.findall(text)

        # If no sentence delimiters found, fall back to fixed-length
        if not sentences:
            remaining = text.strip()
            if remaining:
                return self._split_by_fixed_length(remaining)
            return []

        chunks = []
        current_chunk = ""
        current_len = 0
        chunk_index = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sent_len = len(sentence)
            if current_len + sent_len > settings.CHUNK_SIZE and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "title": f"Sentences {chunk_index + 1}",
                })
                chunk_index += 1
                current_chunk = sentence
                current_len = sent_len
            else:
                if current_chunk:
                    current_chunk += sentence
                else:
                    current_chunk = sentence
                current_len += sent_len

        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "title": f"Sentences {chunk_index + 1}",
            })

        return chunks

    def estimate_tokens(self, text: str) -> int:
        """Roughly estimate token count for Chinese + English mixed text."""
        chinese_chars = len(re.findall(r'[一-鿿]', text))
        other_chars = len(text) - chinese_chars
        return chinese_chars + (other_chars // 4)
