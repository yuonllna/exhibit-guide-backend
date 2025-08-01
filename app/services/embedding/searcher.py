import faiss, pickle, os
import numpy as np

def load_index(base_dir="data/faiss"):
    index = faiss.read_index(os.path.join(base_dir, "faiss_index.idx"))
    with open(os.path.join(base_dir, "documents.pkl"), "rb") as f:
        docs = pickle.load(f)
    return index, docs

def search(index, query_vec: np.ndarray, k=5):
    D, I = index.search(query_vec, k)
    return D, I