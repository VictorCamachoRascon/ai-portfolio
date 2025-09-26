from typing import List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ChunkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    page_id: int
    chunk_index: int
    text: str
    start_char: int
    end_char: int

class PageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    document_id: int
    page_number: int
    text: str
    char_count: int
    chunks: List[ChunkOut] = []

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    sha256: str
    num_pages: int
    created_at: datetime

class DocumentDetailOut(DocumentOut):
    pages: List[PageOut] = []
