"""
extractor.py — File → raw text
Owner: Dmitrii

DATA CONTRACT (see docs/data_contracts.md):
    Input:  file (UploadedFile), source_type (str)
    Output: raw_text (str)
"""

import pandas as pd


def extract(file, source_type: str) -> str:
    filename = file.name.lower()

    if filename.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")

    if filename.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(file)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            return f"[PDF extraction error: {e}]"

    if filename.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(file)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            return f"[DOCX extraction error: {e}]"

    if filename.endswith(".csv"):
        try:
            df = pd.read_csv(file)
            text_cols = [c for c in df.columns if df[c].dtype == object]
            rows = []
            for _, row in df.iterrows():
                parts = [str(row[c]) for c in text_cols if pd.notna(row[c]) and str(row[c]).strip()]
                if parts:
                    rows.append(" | ".join(parts))
            return "\n".join(rows)
        except Exception as e:
            return f"[CSV extraction error: {e}]"

    return file.read().decode("utf-8", errors="ignore")
