"""
extractor.py — File → raw text
Owner: Dmitrii

DATA CONTRACT (see docs/data_contracts.md):
    Input:  file (UploadedFile), source_type (str)
    Output: raw_text (str)

TODO: implement extraction for .txt, .pdf, .docx, .csv
Hint: pypdf for PDF, python-docx for DOCX, pandas for CSV
"""

def extract(file, source_type: str) -> str:
    raise NotImplementedError("Dmitrii: implement extract() here")
