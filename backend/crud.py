from typing import Iterable, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from . import models

def get_document_by_hash(db: Session, sha256: str) -> models.Document | None:
    return db.query(models.Document).filter(models.Document.sha256 == sha256).first()

def create_document(db: Session, filename: str, sha256: str, num_pages: int) -> models.Document:
    doc = models.Document(filename=filename, sha256=sha256, num_pages=num_pages)
    db.add(doc)
    db.flush()  # assign id
    return doc

def add_pages(db: Session, document: models.Document, page_texts: Iterable[str]) -> List[models.Page]:
    pages: List[models.Page] = []
    for idx, text in enumerate(page_texts, start=1):
        t = (text or "").strip()
        p = models.Page(
            document_id=document.id,
            page_number=idx,
            text=t,
            char_count=len(t),
        )
        db.add(p)
        pages.append(p)
    return pages

def upsert_document_with_pages(db: Session, filename: str, sha256: str, page_texts: list[str]) -> models.Document:
    existing = get_document_by_hash(db, sha256)
    if existing:
        return existing  # idempotent re-upload
    doc = create_document(db, filename=filename, sha256=sha256, num_pages=len(page_texts))
    add_pages(db, doc, page_texts)
    db.commit()
    db.refresh(doc)
    return doc

def list_documents(db: Session, limit: int = 50, offset: int = 0) -> list[models.Document]:
    return (
        db.query(models.Document)
          .order_by(models.Document.created_at.desc(), models.Document.id.desc())
          .offset(offset).limit(limit).all()
    )

def get_document_detail(db: Session, doc_id: int) -> models.Document | None:
    return db.query(models.Document).filter(models.Document.id == doc_id).first()

def search_pages(db: Session, q: str, limit: int = 20) -> list[models.Page]:
    stmt = select(models.Page).where(models.Page.text.like(f"%{q}%")).limit(limit)
    return db.execute(stmt).scalars().all()
