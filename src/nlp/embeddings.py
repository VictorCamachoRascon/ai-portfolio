from typing import List
import math

def dummy_embed(texts: List[str]) -> List[List[float]]:
    """
    Stub embedding: returns a trivial 3D vector per text.
    Replace with SentenceTransformers or Azure OpenAI embeddings.
    """
    out = []
    for t in texts:
        l = len(t)
        out.append([l, math.log1p(l), (l % 7) / 7.0])
    return out
