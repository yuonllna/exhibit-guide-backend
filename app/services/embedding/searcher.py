import os, pickle, faiss, numpy as np
from typing import Tuple, List, Dict

def load_index(base_dir: str) -> Tuple[faiss.Index, List[Dict]]:
    index = faiss.read_index(os.path.join(base_dir, "faiss_index.idx"))
    with open(os.path.join(base_dir, "documents.pkl"), "rb") as f:
        docs = pickle.load(f)
    return index, docs

def search(index, query_vec: np.ndarray, k: int = 3):
    if query_vec.ndim == 1:
        query_vec = query_vec[None, :]
    if query_vec.dtype != np.float32:
        query_vec = query_vec.astype("float32")
    return index.search(query_vec, k)
