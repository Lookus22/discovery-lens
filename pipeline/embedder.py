"""
embedder.py — Chunks → embeddings

CONTRACT:
    Input:  chunks (list[dict])
    Output: np.ndarray shape (n_chunks, 384)
"""
import numpy as np
import streamlit as st

@st.cache_resource(show_spinner="Loading embedding model…")
def _load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

def embed(chunks: list[dict]) -> "np.ndarray":
    if not chunks:
        return np.empty((0, 384))
    model = _load_model()
    return model.encode([c["text"] for c in chunks], show_progress_bar=False, convert_to_numpy=True)
