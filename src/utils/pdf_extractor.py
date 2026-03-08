# src/utils/pdf_extractor.py
"""Modular PDF text extraction for GitHub Actions environment"""

import re
from pathlib import Path
from typing import Optional


def extract_text_from_pdf(
    pdf_path: str | Path,
    max_pages: Optional[int] = None
) -> str:
    """Extract clean text from PDF file."""
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            pages = reader.pages[:max_pages] if max_pages else reader.pages
            text_parts = []
            for page in pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    page_text = re.sub(r'Page \d+ of \d+', '', page_text)
                    page_text = re.sub(r'www\.\S+', '', page_text)
                    page_text = re.sub(r'\s+', ' ', page_text).strip()
                    if len(page_text) > 100:
                        text_parts.append(page_text)
            return " ".join(text_parts)
    except ImportError:
        print("⚠️ PyPDF2 not installed")
        return ""
    except Exception as e:
        print(f"⚠️ PDF extraction error: {e}")
        return ""


def chunk_text_smart(
    text: str,
    chunk_size: int = 6000,
    overlap: int = 300
) -> list[str]:
    """Split text into chunks preserving semantic boundaries."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            for sep in ['. ', '\n\n', '! ', '? ']:
                pos = text.rfind(sep, start + chunk_size - 400, end)
                if pos != -1:
                    end = pos + len(sep)
                    break
        chunk = text[start:end].strip()
        if len(chunk) > 300:
            chunks.append(chunk)
        start = end - overlap if end < len(text) else len(text)
    
    return chunks
