from fastapi import APIRouter
from pydantic import BaseModel
from src.embedding.index import load_index_and_chunks
from src.embedding.model import get_embedder
from src.retrieval.prompt import build_prompt
from src.llm.inference import get_llm_response
import numpy as np
import os
import json
from datetime import datetime

router = APIRouter()

class QueryRequest(BaseModel):
    project: str
    question: str

@router.post("/")
def ask_question(req: QueryRequest):
    try:
        # Save question to backend disk under chunks folder
        os.makedirs("data/chunks", exist_ok=True)
        safe_project = req.project.replace("/", "_").replace(" ", "_")
        filepath = f"data/chunks/{safe_project}_questions.json"
        question_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": req.question
        }

        data = []
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = []

        data.append(question_entry)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        # Load FAISS index + chunks
        index_path = f"data/vector_stores/{req.project}"
        index, chunks = load_index_and_chunks(index_path)

        # Get embedding for the question
        embedder = get_embedder()
        q_vector = embedder.encode([req.question]).astype("float32")

        # Search for top 5 relevant chunks
        D, I = index.search(q_vector, k=5)
        relevant_chunks = [chunks[i] for i in I[0] if i < len(chunks)]

        # Build prompt
        prompt = build_prompt(req.question, relevant_chunks)

        # Get answer (stubbed or real)
        answer = get_llm_response(prompt)

        return {
            "question": req.question,
            "answer": answer,
            "chunks": relevant_chunks
        }
    except Exception as e:
        return {"error": str(e)}
