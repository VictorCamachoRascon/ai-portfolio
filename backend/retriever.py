from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import re

import pdfplumber
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class DocChunk:
    doc_id: str
    source_path: str
    text: str
    meta: dict


class SimpleRetriever:
    """
    In-memory retriever over local files.
    - Indexes TXT (paragraphs), PDF (page paragraphs), CSV (rows).
    - Uses TF-IDF + cosine similarity.
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_df=0.9,
            min_df=1,
            ngram_range=(1, 2),
        )
        self.chunks: List[DocChunk] = []
        self._tfidf = None

    @staticmethod
    def _split_paragraphs(text: str, min_len: int = 40) -> List[str]:
        parts = re.split(r"\n\s*\n|(?<=\.)\s{2,}", text)
        parts = [p.strip() for p in parts if p.strip()]
        return [p for p in parts if len(p) >= min_len]

    def _load_txt(self, path: Path):
        txt = path.read_text(encoding="utf-8", errors="ignore")
        paras = self._split_paragraphs(txt) or [txt.strip()]
        for i, para in enumerate(paras):
            if not para: continue
            self.chunks.append(DocChunk(
                doc_id=f"{path.name}#c{i}",
                source_path=str(path),
                text=para,
                meta={"type": "txt", "chunk_index": i},
            ))

    def _load_pdf(self, path: Path):
        with pdfplumber.open(path) as pdf:
            for p_i, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                paras = self._split_paragraphs(page_text) or [page_text.strip()]
                for c_i, para in enumerate(paras):
                    if not para: continue
                    self.chunks.append(DocChunk(
                        doc_id=f"{path.name}#p{p_i}c{c_i}",
                        source_path=str(path),
                        text=para,
                        meta={"type": "pdf", "page": p_i},
                    ))

    def _load_csv(self, path: Path, max_rows: int = 2000):
        df = pd.read_csv(path, nrows=max_rows)
        for i, row in df.iterrows():
            row_text = " | ".join(f"{col}: {row[col]}" for col in df.columns)
            self.chunks.append(DocChunk(
                doc_id=f"{path.name}#r{i}",
                source_path=str(path),
                text=str(row_text),
                meta={"type": "csv", "row_index": i, "columns": list(df.columns)},
            ))

    def build(self) -> int:
        paths = []
        if self.data_dir.exists():
            paths = list(self.data_dir.glob("*.txt")) + \
                    list(self.data_dir.glob("*.pdf")) + \
                    list(self.data_dir.glob("*.csv"))

        for path in paths:
            try:
                if path.suffix.lower() == ".txt":
                    self._load_txt(path)
                elif path.suffix.lower() == ".pdf":
                    self._load_pdf(path)
                elif path.suffix.lower() == ".csv":
                    self._load_csv(path)
            except Exception as ex:
                print(f"[retriever] Skipping {path.name}: {ex}")

        corpus = [c.text for c in self.chunks] or ["(empty corpus)"]
        self._tfidf = self.vectorizer.fit_transform(corpus)
        return len(self.chunks)

    def query(self, question: str, top_k: int = 3) -> List[Tuple[DocChunk, float]]:
        if not self.chunks:
            return []
        q_vec = self.vectorizer.transform([question])
        sims = cosine_similarity(q_vec, self._tfidf)[0]
        idxs = sims.argsort()[::-1][:max(1, top_k)]
        return [(self.chunks[i], float(sims[i])) for i in idxs]
