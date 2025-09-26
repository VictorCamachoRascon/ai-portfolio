from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import html

from .retriever import SimpleRetriever

router = APIRouter(prefix="/qa", tags=["qa"])

DATA_DIR = Path(__file__).resolve().parents[1] / "sample_data"
_retriever = SimpleRetriever(DATA_DIR)
num_chunks = _retriever.build()
print(f"[qa] Retriever ready with {num_chunks} chunks from {DATA_DIR}")

class QARequest(BaseModel):
    question: str = Field(..., min_length=2)
    top_k: int = Field(3, ge=1, le=10)

class QAPassage(BaseModel):
    doc_id: str
    source_path: str
    score: float
    text: str
    highlighted: Optional[str] = None

class QAResponse(BaseModel):
    question: str
    answers: List[QAPassage]

@router.get("/ping")
def ping():
    return {"status": "ok", "chunks_indexed": num_chunks}

def _highlight(text: str, query: str, max_chars: int = 420) -> str:
    safe = html.escape(text)
    q_words = [w for w in query.lower().split() if len(w) > 2][:6]
    for w in q_words:
        safe = safe.replace(html.escape(w), f"<mark>{html.escape(w)}</mark>")
        safe = safe.replace(html.escape(w.capitalize()), f"<mark>{html.escape(w.capitalize())}</mark>")
    return safe if len(safe) <= max_chars else safe[:max_chars] + "…"

@router.post("", response_model=QAResponse)
def ask(payload: QARequest):
    if num_chunks == 0:
        raise HTTPException(status_code=503, detail="Corpus is empty. Put files in sample_data/ and restart.")
    hits = _retriever.query(payload.question, top_k=payload.top_k)
    answers = []
    for c, score in hits:
        answers.append(QAPassage(
            doc_id=c.doc_id,
            source_path=c.source_path,
            score=round(score, 6),
            text=c.text,
            highlighted=_highlight(c.text, payload.question),
        ))
    return QAResponse(question=payload.question, answers=answers)
