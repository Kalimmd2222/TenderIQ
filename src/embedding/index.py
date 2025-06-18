import faiss
import pickle
import os
import numpy as np

VECTOR_DIM = 384  # Based on MiniLM

def build_and_save_index(vectors, chunks, save_path: str):
    index = faiss.IndexFlatL2(VECTOR_DIM)
    index.add(np.array(vectors).astype("float32"))

    # Save index
    faiss.write_index(index, f"{save_path}.index")

    # Save chunk metadata
    with open(f"{save_path}.chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

def load_index_and_chunks(save_path: str):
    index = faiss.read_index(f"{save_path}.index")
    with open(f"{save_path}.chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def save_index(vectors, chunks, project_name):
    os.makedirs("data/vector_stores", exist_ok=True)
    save_path = os.path.join("data/vector_stores", project_name)
    build_and_save_index(vectors, chunks, save_path)  # Reuse base logic
