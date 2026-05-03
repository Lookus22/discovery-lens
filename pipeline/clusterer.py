"""
clusterer.py — Embeddings → clusters
Owner: Mengda

DATA CONTRACT (see docs/data_contracts.md):
    Input:  chunks (list[dict]), embeddings (np.ndarray)
    Output: list of dicts [{cluster_id, representative_chunks, all_chunk_ids}]
"""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def cluster(chunks: list[dict], embeddings: np.ndarray) -> list[dict]:
    n = len(chunks)
    if n == 0:
        return []

    k = _best_k(embeddings, k_min=3, k_max=min(7, n - 1))
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)

    clusters = []
    for cluster_id in range(k):
        indices = [i for i, lbl in enumerate(labels) if lbl == cluster_id]
        if not indices:
            continue

        centroid = kmeans.cluster_centers_[cluster_id]
        cluster_embeddings = embeddings[indices]
        distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
        closest = sorted(zip(distances, indices))[:3]
        representative_chunks = [chunks[i] for _, i in closest]

        clusters.append({
            "cluster_id": cluster_id,
            "representative_chunks": representative_chunks,
            "all_chunk_ids": [chunks[i]["chunk_id"] for i in indices],
        })

    return clusters


def _best_k(embeddings: np.ndarray, k_min: int, k_max: int) -> int:
    if k_max < k_min:
        return k_min

    best_k, best_score = k_min, -1
    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(embeddings)
        if len(set(labels)) < 2:
            continue
        score = silhouette_score(embeddings, labels)
        if score > best_score:
            best_score, best_k = score, k

    return best_k
