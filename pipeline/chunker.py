"""
chunker.py — Raw text → chunks

CONTRACT:
    Input:  raw_text (str), filename (str), source_type (str)
    Output: list of dicts [{chunk_id, text, filename, source_type}]
"""
import re, unicodedata

MIN_CHARS = 40
WINDOW_SIZE = 3
OVERLAP = 1

def chunk(raw_text: str, filename: str, source_type: str) -> list[dict]:
    sentences = _split_sentences(raw_text)
    sentences = [s for s in sentences if len(s.strip()) >= MIN_CHARS]
    if not sentences:
        return []
    base_name = _safe_name(filename)
    chunks = []
    step = WINDOW_SIZE - OVERLAP
    for i, start in enumerate(range(0, len(sentences), step)):
        window = sentences[start: start + WINDOW_SIZE]
        text = " ".join(window).strip()
        if len(text) < MIN_CHARS:
            continue
        chunks.append({"chunk_id": f"{base_name}_{str(i+1).zfill(3)}", "text": text, "filename": filename, "source_type": source_type})
    return chunks

def _split_sentences(text: str) -> list[str]:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text).strip()
    try:
        import nltk
        try:
            tok = nltk.data.load("tokenizers/punkt/english.pickle")
        except LookupError:
            nltk.download("punkt", quiet=True)
            tok = nltk.data.load("tokenizers/punkt/english.pickle")
        return tok.tokenize(text)
    except Exception:
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", text) if s.strip()]

def _safe_name(filename: str) -> str:
    base = filename.rsplit(".", 1)[0]
    return re.sub(r"[^a-zA-Z0-9_-]", "_", base)[:40]
