# src/utils/pdf_extractor.py\n"""Modular PDF text extraction for GitHub Actions environment"""\n
import re
from pathlib import Path
from typing import Optional

def extract_text_from_pdf(
    pdf_path: str | Path, 
    max_pages: Optional[int] = None
) -> str:
    """\n    Extract clean text from PDF file.
    
    Args:
        pdf_path: Path to PDF file
        max_pages: Limit extraction to N pages (None = all)
    
    Returns:
        Extracted text string (empty string on error)
    """\n    try:
        import PyPDF2
        
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            pages = reader.pages[:max_pages] if max_pages else reader.pages
            
            text_parts = []
            for page in pages:
                page_text = page.extract_text() or ""\n                if page_text.strip():
                    # Clean common PDF artifacts
                    page_text = re.sub(r'Page \d+ of \d+', '', page_text)
                    page_text = re.sub(r'www\.\S+', '', page_text)
                    page_text = re.sub(r'\s+', ' ', page_text).strip()
                    if len(page_text) > 100:
                        text_parts.append(page_text)
            
            return " ".join(text_parts)
            
    except ImportError:
        print("⚠️ PyPDF2 not installed - install with: pip install PyPDF2")
        return ""\n    except Exception as e:
        print(f"⚠️ PDF extraction error: {e}")
        return ""\n

def chunk_text_smart(
    text: str, 
    chunk_size: int = 6000, 
    overlap: int = 300
) -> list[str]:
    """\n    Split text into chunks preserving semantic boundaries.
    
    Args:
        text: Input text to chunk
        chunk_size: Target characters per chunk
        overlap: Characters to overlap between chunks
    
    Returns:
        List of text chunks
    """\n    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Try to break at sentence/paragraph boundaries
        if end < len(text):
            for sep in ['. ', '\n\n', '! ', '? ']:
                pos = text.rfind(sep, start + chunk_size - 400, end)
                if pos != -1:
                    end = pos + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if len(chunk) > 300:  # Skip tiny chunks
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap if end < len(text) else len(text)
    
    return chunks