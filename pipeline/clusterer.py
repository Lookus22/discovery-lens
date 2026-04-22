"""
clusterer.py — Embeddings → clusters

CONTRACT:
    Input:  chunks (list[dict]), embeddings (np.ndarray)
    Output: list of dicts [{cluster_id, representative_chunks, all_chunk_ids}]
"""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import euclidean_distances

K_CANDIDATES = [3, 4, 5, 6, 7]

def cluster(chunks: list[dict], embeddings: np.ndarray) -> list[dict]:
    n = len(chunks)
    if n == 0:
        return []
    k = _pick_k(embeddings, n)
    labels = _fit(embeddings, k)
    return _build(chunks, embeddings, labels, k)

def _pick_k(embeddings, n):
    candidates = [k for k in K_CANDIDATES if n >= k * 3]
    if not candidates:
        return 3
    best_k, best_score = candidates[0], -1.0
    for k in candidates:
        labels = _fit(embeddings, k)
        if len(set(labels)) < 2:
            continue
        score = silhouette_score(embeddings, labels, sample_size=min(500, n))
        if score > best_score:
            best_score, best_k = score, k
    return best_k

def _fit(embeddings, k):
    return KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(embeddings)

def _build(chunks, embeddings, labels, k):
    groups = {i: [] for i in range(k)}
    for idx, label in enumerate(labels):
        groups[int(label)].append(idx)
    centroids = np.array([embeddings[groups[i]].mean(axis=0) for i in range(k)])
    result = []
    for cid in range(k):
        idxs = groups[cid]
        if not idxs:
            continue
        dists = euclidean_distances(embeddings[idxs], centroids[cid].reshape(1,-1)).flatten()
        closest = [chunks[idxs[i]] for i in np.argsort(dists)[:3]]
        result.append({"cluster_id": cid, "representative_chunks": closest, "all_chunk_ids": [chunks[i]["chunk_id"] for i in idxs]})
    return result
