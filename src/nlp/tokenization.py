from typing import List

def simple_whitespace_tokenize(text: str) -> List[str]:
    """
    Minimal tokenizer: split on whitespace.
    Replace later with nltk/transformers tokenizers as needed.
    """
    return text.split()
