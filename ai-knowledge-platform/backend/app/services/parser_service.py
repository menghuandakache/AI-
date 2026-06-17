"""Document parser service - extracts text from PDF, DOCX, and Markdown files."""
import os
import re
from app.core.exceptions import FileParseException


def _count_chinese_words(text: str) -> int:
    """Count characters in valid CJK sequences (2+ consecutive CJK chars)."""
    matches = re.findall(r'[一-鿿]{2,}', text)
    return sum(len(m) for m in matches)

def _is_garbled(text: str) -> bool:
    """Heuristic: check if PDF text extraction produced garbled output."""
    if not text or len(text) < 20:
        return True
    total = len(text)
    chinese = _count_chinese_words(text)
    # Less than 5% recognizable Chinese word sequences → garbled
    if total > 100 and chinese / total < 0.05:
        return True
    # Too many single-char lines → characters decoded one-by-one
    lines = text.split('\n')
    singles = sum(1 for l in lines if len(l.strip()) == 1)
    if len(lines) > 10 and singles / len(lines) > 0.5:
        return True
    return False


class ParserService:
    """Parses documents to extract plain text.
    PDF: PyMuPDF first, falls back to OCR (Tesseract) if text is garbled."""

    def parse(self, file_path: str, file_type: str) -> str:
        """Parse a document based on its type and return plain text."""
        if not os.path.exists(file_path):
            raise FileParseException(f"File not found: {file_path}")

        if file_type == "pdf":
            return self._parse_pdf(file_path)
        elif file_type == "docx":
            return self._parse_docx(file_path)
        elif file_type == "md":
            return self._parse_markdown(file_path)
        else:
            raise FileParseException(f"Unsupported file type: {file_type}")

    def _parse_pdf(self, file_path: str) -> str:
        """Parse PDF using PyMuPDF, fall back to OCR if garbled."""
        text = ""
        try:
            import fitz
            doc = fitz.open(file_path)
            texts = []
            for page in doc:
                t = page.get_text()
                if t.strip():
                    texts.append(t.strip())
            doc.close()
            text = "\n\n".join(texts)
        except ImportError:
            raise FileParseException("PyMuPDF not installed")
        except Exception as e:
            raise FileParseException(f"Failed to parse PDF: {str(e)}")

        # Check if PyMuPDF output is garbled
        if _is_garbled(text):
            ocr_text = self._parse_pdf_ocr(file_path)
            if ocr_text:  # OCR quality > garbled quantity
                return ocr_text

        return text

    def _parse_pdf_ocr(self, file_path: str) -> str:
        """OCR fallback for PDF files using Tesseract."""
        try:
            from pdf2image import convert_from_path
            import pytesseract

            # Convert pages (limit to keep parsing time reasonable)
            images = convert_from_path(file_path, first_page=1, last_page=50, dpi=150)
            texts = []
            for i, img in enumerate(images):
                t = pytesseract.image_to_string(img, lang='chi_sim+eng')
                if t.strip():
                    texts.append(t.strip())
            return "\n\n".join(texts)
        except ImportError as e:
            pass  # OCR not available
        except Exception as e:
            pass  # OCR failed
        return ""

    def _parse_docx(self, file_path: str) -> str:
        """Parse DOCX using python-docx."""
        try:
            from docx import Document
            doc = Document(file_path)
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text.strip())
            return "\n\n".join(paragraphs)
        except ImportError:
            raise FileParseException("python-docx is not installed")
        except Exception as e:
            raise FileParseException(f"Failed to parse DOCX: {str(e)}")

    def _parse_markdown(self, file_path: str) -> str:
        """Parse Markdown file - strip formatting, keep text."""
        try:
            import markdown
            from html.parser import HTMLParser

            with open(file_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            html = markdown.markdown(md_content)

            class MLStripper(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.reset()
                    self.strict = False
                    self.convert_charrefs = True
                    self.text = []

                def handle_data(self, d):
                    self.text.append(d)

                def get_data(self):
                    return "".join(self.text)

            stripper = MLStripper()
            stripper.feed(html)
            return stripper.get_data()
        except ImportError:
            raise FileParseException("markdown module is not installed")
        except Exception as e:
            raise FileParseException(f"Failed to parse Markdown: {str(e)}")
