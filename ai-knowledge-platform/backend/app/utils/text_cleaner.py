"""Text cleaning utilities."""
import re


def clean_text(text: str) -> str:
    """Clean extracted text by removing noise and normalizing."""
    # Remove excessive whitespace
    text = re.sub(r'[ \t]+', ' ', text)

    # Normalize newlines (max 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove common header/footer patterns
    text = re.sub(r'^\d+/\d+$', '', text, flags=re.MULTILINE)

    # Normalize Chinese/English punctuation
    text = text.replace('　', ' ')

    # Remove control characters (keep common ones)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # Remove lines that are just page numbers
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

    # Remove watermark-like content (simple heuristics)
    text = re.sub(r'第\s*\d+\s*页', '', text)

    return text.strip()


def remove_empty_lines(text: str) -> str:
    """Remove completely empty lines."""
    lines = text.split('\n')
    return '\n'.join(line for line in lines if line.strip())


def normalize_punctuation(text: str) -> str:
    """Normalize Chinese and English punctuation."""
    # Standardize English quotes
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")

    return text
