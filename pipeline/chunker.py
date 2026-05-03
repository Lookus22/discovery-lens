"""
chunker.py — Raw text → chunks
Owner: Dmitrii

DATA CONTRACT (see docs/data_contracts.md):
    Input:  raw_text (str), filename (str), source_type (str)
    Output: list of dicts [{chunk_id, text, filename, source_type}]
"""

import re


def chunk(raw_text: str, filename: str, source_type: str) -> list[dict]:
    safe_filename = re.sub(r"[^a-z0-9]+", "_", filename.lower()).strip("_")
    sentences = _split_sentences(raw_text)
    chunks = []
    window = 3

    i = 0
    while i < len(sentences):
        group = sentences[i:i + window]
        text = " ".join(group).strip()
        if len(text.split()) >= 5:
            chunk_id = f"{safe_filename}_{len(chunks):03d}"
            chunks.append({
                "chunk_id": chunk_id,
                "text": text,
                "filename": filename,
                "source_type": source_type,
            })
        i += window

    return chunks


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    raw = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in raw if len(s.strip().split()) >= 3]
    return sentences
