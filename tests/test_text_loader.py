import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from ingestion import load_text
def test_load_text_normalizes_newlines():
    p = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    try:
        p.write(b"hello\r\nworld\r\n"); p.close()
        out = load_text(p.name)
        assert out == "hello\nworld"
    finally:
        os.unlink(p.name)
