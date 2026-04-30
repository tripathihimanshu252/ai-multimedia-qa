import pdfplumber
from typing import List

def extract_pdf_text(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        pages = [p.extract_text() for p in pdf.pages if p.extract_text()]
    return "\n".join(pages)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    words  = text.split()
    chunks = []
    start  = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks
