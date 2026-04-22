"""
extractor.py — File → raw text

CONTRACT:
    Input:  file (UploadedFile), source_type (str)
    Output: raw_text (str)
"""
import pandas as pd

def extract(file, source_type: str) -> str:
    name = file.name.lower()
    if name.endswith(".txt"):
        return file.read().decode("utf-8", errors="replace")
    elif name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif name.endswith(".docx"):
        from docx import Document
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    elif name.endswith(".csv"):
        df = pd.read_csv(file)
        text_cols = df.select_dtypes(include="object").columns.tolist()
        return "\n".join(
            " ".join(str(row[col]) for col in text_cols if pd.notna(row[col]))
            for _, row in df.iterrows()
        )
    else:
        raise ValueError(f"Unsupported file type: {file.name}")
