"""
embedder.py — Chunks → embeddings
Owner: Mengda

DATA CONTRACT (see docs/data_contracts.md):
    Input:  chunks (list[dict])
    Output: np.ndarray shape (n_chunks, 384)

TODO: load all-MiniLM-L6-v2 via sentence-transformers and encode chunk texts
Hint: use @st.cache_resource so the model loads only once per session
"""

def embed(chunks: list[dict]):
    raise NotImplementedError("Mengda: implement embed() here")
