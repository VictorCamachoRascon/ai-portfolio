from contextlib import contextmanager
import io
import chardet

def normalize_text(text: str) -> str:
    """
    Basic cleanup:
      - strip BOMs
      - unify newlines to \n
      - trim trailing spaces on lines
      - collapse excessive blank lines (optional, conservative)
    """
    if not text:
        return ""
    # Remove UTF-8 BOM if present
    text = text.lstrip("\ufeff")
    # Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Trim right spaces per line
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    # 👇 remove trailing newline(s)
    text = text.rstrip("\n")
    return text

@contextmanager
def smart_open_text(path: str, fallback_encodings=("utf-8", "latin-1")):
    """
    Open text with best-effort encoding detection.
    Tries chardet, then fallbacks.
    Yields a TextIOBase.
    """
    # Try detection with chardet
    with open(path, "rb") as fb:
        raw = fb.read()
    guessed = chardet.detect(raw)
    enc = guessed.get("encoding") or fallback_encodings[0]

    try:
        yield io.StringIO(raw.decode(enc, errors="ignore"))
    except LookupError:
        # If unknown codec, try fallbacks
        for fe in fallback_encodings:
            try:
                yield io.StringIO(raw.decode(fe, errors="ignore"))
                break
            except Exception:
                continue

