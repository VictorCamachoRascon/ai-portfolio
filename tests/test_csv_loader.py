import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from ingestion import load_csv
def test_load_csv_reads_rows():
    p = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w")
    try:
        p.write("a,b\n1,x\n2,y\n"); p.close()
        df = load_csv(p.name)
        assert df.shape == (2, 2)
        assert list(df.columns) == ["a","b"]
    finally:
        os.unlink(p.name)
