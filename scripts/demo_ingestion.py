import os
import sys

# allow running from repo root without installing a package
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(REPO_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from ingestion import load_text, load_pdf, load_csv

def main():
    print("=== TEXT ===")
    try:
        print(load_text("sample_data/sample.txt")[:300], "...\n")
    except Exception as e:
        print("Text demo skipped:", e)

    print("=== PDF ===")
    try:
        print(load_pdf("sample_data/sample.pdf")[:300], "...\n")
    except Exception as e:
        print("PDF demo skipped:", e)

    print("=== CSV ===")
    try:
        df = load_csv("sample_data/sample.csv")
        print(df.head(), "\n")
    except Exception as e:
        print("CSV demo skipped:", e)

if __name__ == "__main__":
    main()

