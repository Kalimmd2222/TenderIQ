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

        print(f"📂 File saved: {file_path}")

        # Extract text
        text = extract_text(file_path)
        print(f"📄 Extracted text length: {len(text)}")

        if not text.strip():
            return {"error": "File text could not be extracted or is empty."}

        # Chunk the text
        chunks = split_into_chunks(text)
        print(f"🔪 Number of chunks: {len(chunks)}")
        if chunks:
            print(f"💡 First chunk preview: {chunks[0][:100]}")

        # Embed chunks
        embedder = get_embedder()
        embeddings = embedder.encode(chunks).tolist()
        print(f"📏 Embeddings count: {len(embeddings)}")

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