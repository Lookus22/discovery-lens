"""
clusterer.py — Embeddings → clusters
Owner: Mengda

DATA CONTRACT (see docs/data_contracts.md):
    Input:  chunks (list[dict]), embeddings (np.ndarray)
    Output: list of dicts [{cluster_id, representative_chunks, all_chunk_ids}]

TODO: KMeans clustering, pick best k using silhouette score
Hint: try k in [3,4,5,6,7], pick highest silhouette score
"""

def cluster(chunks: list[dict], embeddings) -> list[dict]:
    raise NotImplementedError("Mengda: implement cluster() here")
