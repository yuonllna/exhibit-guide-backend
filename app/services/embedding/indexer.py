from sentence_transformers import SentenceTransformer
import faiss, numpy as np, pickle, os
from typing import List, Dict

def build_index(documents: List[Dict], out_dir="data/faiss", model_name="all-MiniLM-L6-v2"):
    os.makedirs(out_dir, exist_ok=True)
    texts = [d["text"] for d in documents]
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    faiss.write_index(index, os.path.join(out_dir, "faiss_index.idx"))
    with open(os.path.join(out_dir, "documents.pkl"), "wb") as f:
        pickle.dump(documents, f)