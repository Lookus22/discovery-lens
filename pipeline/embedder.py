"""
embedder.py — Chunks → embeddings
Owner: Mengda

DATA CONTRACT (see docs/data_contracts.md):
    Input:  chunks (list[dict])
    Output: np.ndarray shape (n_chunks, 384)
"""

import numpy as np
import streamlit as st


@st.cache_resource
def _load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def embed(chunks: list[dict]) -> np.ndarray:
    if not chunks:
        return np.empty((0, 384))
    model = _load_model()
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=False)
    return np.array(embeddings)
