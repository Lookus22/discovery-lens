"""
chunker.py — Raw text → chunks
Owner: Dmitrii

DATA CONTRACT (see docs/data_contracts.md):
    Input:  raw_text (str), filename (str), source_type (str)
    Output: list of dicts [{chunk_id, text, filename, source_type}]

TODO: split text into 2-4 sentence chunks with source metadata
Hint: try nltk sentence tokenizer, or simple regex split on . ! ?
"""

def chunk(raw_text: str, filename: str, source_type: str) -> list[dict]:
    raise NotImplementedError("Dmitrii: implement chunk() here")
