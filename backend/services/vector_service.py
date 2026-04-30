import os, asyncio, pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
from config import FAISS_DIR

_embedder = None

def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

def _index_path(file_id: str) -> str:
    return os.path.join(FAISS_DIR, f"{file_id}.index")

def _meta_path(file_id: str) -> str:
    return os.path.join(FAISS_DIR, f"{file_id}.meta")

def build_index_sync(file_id: str, chunks: List[str]) -> None:
    embedder = _get_embedder()
    vectors  = embedder.encode(chunks, convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, _index_path(file_id))
    with open(_meta_path(file_id), "wb") as f:
        pickle.dump(chunks, f)

async def build_index(file_id: str, chunks: List[str]) -> None:
    await asyncio.to_thread(build_index_sync, file_id, chunks)

def search_index_sync(file_id: str, query: str, top_k: int = 5) -> List[str]:
    if not os.path.exists(_index_path(file_id)):
        return []
    embedder = _get_embedder()
    index    = faiss.read_index(_index_path(file_id))
    with open(_meta_path(file_id), "rb") as f:
        chunks = pickle.load(f)
    q_vec = embedder.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(q_vec)
    _, idxs = index.search(q_vec, min(top_k, len(chunks)))
    return [chunks[i] for i in idxs[0] if i != -1]

async def search_index(file_id: str, query: str, top_k: int = 5) -> List[str]:
    return await asyncio.to_thread(search_index_sync, file_id, query, top_k)
