from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import crud, models, schemas

import hashlib
import io
import pdfplumber

# Dev-only table creation; swap to Alembic in prod
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Portfolio Backend - Text Store")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/documents", response_model=list[schemas.DocumentOut])
def list_docs(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    return crud.list_documents(db, limit=limit, offset=offset)

@app.get("/documents/{doc_id}", response_model=schemas.DocumentDetailOut)
def get_doc_detail(doc_id: int, db: Session = Depends(get_db)):
    doc = crud.get_document_detail(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@app.post("/upload-pdf", response_model=schemas.DocumentDetailOut)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    raw = await file.read()
    sha256 = hashlib.sha256(raw).hexdigest()

    # Idempotent re-upload: return existing doc if hash matches
    existing = crud.get_document_by_hash(db, sha256)
    if existing:
        return existing

    # Extract page texts with pdfplumber
    try:
        page_texts: list[str] = []
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                page_texts.append(text.strip())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {e}")

    doc = crud.upsert_document_with_pages(
        db,
        filename=file.filename,
        sha256=sha256,
        page_texts=page_texts,
    )
    return doc

@app.get("/search", response_model=list[schemas.PageOut])
def search_pages(q: str, limit: int = 20, db: Session = Depends(get_db)):
    q = (q or "").strip()
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    return crud.search_pages(db, q=q, limit=limit)


from .qa import router as qa_router
app.include_router(qa_router)
