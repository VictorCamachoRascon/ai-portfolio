from typing import Optional
import pdfplumber
from .utils import normalize_text

def load_pdf(path: str, *, normalize: bool = True) -> str:
    """Extract text from a PDF file, concatenating page text."""
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            # Some PDFs return None for empty pages
            page_text: Optional[str] = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    text = "\n".join(text_parts)
    return normalize_text(text) if normalize else text

