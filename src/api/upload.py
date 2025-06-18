from fastapi import APIRouter, UploadFile, File, Form
import os
from src.processing.parser import extract_text
from src.processing.chunker import split_into_chunks
from src.embedding.model import get_embedder
from src.embedding.index import save_index

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
def upload_document(
    file: UploadFile = File(...),
    project: str = Form(...),
    doc_type: str = Form(...),
    version: str = Form(...)
):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save file to disk
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Extract text
        text = extract_text(file_path)
        if not text.strip():
            return {"error": "File text could not be extracted or is empty."}

        # Chunk the text
        chunks = split_into_chunks(text)

        # Embed chunks
        embedder = get_embedder()
        embeddings = embedder.encode(chunks).tolist()

        # Save index + metadata
        save_index(embeddings, chunks, project)

        return {
            "project": project,
            "doc_type": doc_type,
            "version": version,
            "num_chunks": len(chunks),
            "message": "Upload and processing successful."
        }

    except Exception as e:
        return {"error": str(e)}