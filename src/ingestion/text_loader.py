from .utils import smart_open_text, normalize_text

def load_text(path: str, *, normalize: bool = True) -> str:
    """Read a plain text file with robust encoding handling."""
    with smart_open_text(path) as f:
        data = f.read()
    return normalize_text(data) if normalize else data

