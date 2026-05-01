import os
import numpy as np
from config import FAISS_DIR

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False
    print("⚠️ faiss/sentence-transformers not available - using Gemini direct mode")

def _index_path(file_id: str) -> str:
    os.makedirs(FAISS_DIR, exist_ok=True)
    return os.path.join(FAISS_DIR, f"{file_id}.index")

def build_index(file_id: str, chunks: list[str]):
    if not VECTOR_AVAILABLE:
        return  # skip silently
    vectors = _model.encode(chunks).astype("float32")
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, _index_path(file_id))

def search_index(file_id: str, query: str, top_k: int = 5) -> list[str]:
    if not VECTOR_AVAILABLE:
        return []  # Gemini will use full text instead
    path = _index_path(file_id)
    if not os.path.exists(path):
        return []
    index = faiss.read_index(path)
    q_vec = _model.encode([query]).astype("float32")
    faiss.normalize_L2(q_vec)
    _, ids = index.search(q_vec, top_k)
    return ids[0].tolist()
