import faiss
import pickle
import os

VECTOR_DIM = 384  # Based on MiniLM

def build_and_save_index(vectors, chunks, save_path: str):
    index = faiss.IndexFlatL2(VECTOR_DIM)
    index.add(vectors)

    # Save index
    faiss.write_index(index, f"{save_path}.index")

    # Save chunk metadata
    with open(f"{save_path}.chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)
