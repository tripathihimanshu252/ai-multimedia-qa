import os
import numpy as np
from config import FAISS_DIR

VECTOR_AVAILABLE = False  # disabled on free tier - Gemini handles Q&A directly

def _index_path(file_id: str) -> str:
    os.makedirs(FAISS_DIR, exist_ok=True)
    return os.path.join(FAISS_DIR, f"{file_id}.index")

def build_index(file_id: str, chunks: list[str]):
    pass  # no-op on free tier

def search_index(file_id: str, query: str, top_k: int = 5) -> list[str]:
    return []  # Gemini uses full text directly
