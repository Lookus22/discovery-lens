from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np


def cluster(chunks: list[dict], embeddings: np.ndarray) -> list[dict]:
    n_chunks = len(chunks)
    k_values = range(3, min(8, n_chunks + 1)) # To work out the range of k values to try, we cap the maximum k at the number of chunks we actually have.
    
    best_k = 3          # fallback default in case something goes wrong
    best_score = -1     # silhouette scores range from -1 to 1, so -1 is worst possible

    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10) # n_init=10 means KMeans tries 10 different random starting points and keeps the best.

        labels = kmeans.fit_predict(embeddings) # fit_predict(): learns the k cluster centres from the embeddings and returns a label for each chunk: which cluster it belongs to
        score = silhouette_score(embeddings, labels) # silhouette_score measures how well-separated the clusters are. Higher is better. We pass the embeddings and the labels.
        if score > best_score:
            best_score = score
            best_k = k

    final_kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    final_labels = final_kmeans.fit_predict(embeddings)

    # final_kmeans.cluster_centers_ is a 2D array of shape (best_k, 384). Each row is the "centre point" of one cluster in embedding space, the average position of all chunks in that cluster.
    centroids = final_kmeans.cluster_centers_
    results = [] #to build the output list

    for cluster_id in range(best_k):

        # Find which chunks belong to this cluster. final_labels[i] == cluster_id is True for every chunk in this cluster.
        # np.where() returns the indices (positions) where that condition is True. [0] gets the actual array out of the tuple np.where returns.
        cluster_indices = np.where(final_labels == cluster_id)[0]

        # Collect the chunk_ids for all chunks in this cluster. This becomes "all_chunk_ids" in the output.
        all_chunk_ids = [chunks[i]["chunk_id"] for i in cluster_indices]
        centroid = centroids[cluster_id] # The centroid is the centre point of this cluster (a list of 384 numbers).

        # For each chunk in this cluster, calculate how far its embedding is from the centroid. "Distance" here means Euclidean distance — the straight-line distance between two points in 384-dimensional space.
        # np.linalg.norm() computes this distance. Chunks closer to the centroid are more "typical" of the cluster.
        distances = [
            np.linalg.norm(embeddings[i] - centroid)
            for i in cluster_indices
        ]

        # Sort the chunk indices by distance (closest first). np.argsort() returns the positions that would sort the list.
        sorted_positions = np.argsort(distances)

        # Take the 3 closest. If the cluster has fewer than 3 chunks, take all.
        top_positions = sorted_positions[:3]

        # Get the actual chunk dicts for these top 3.
        representative_chunks = [chunks[cluster_indices[p]] for p in top_positions]

        # Append this cluster's dict to results
        results.append({
            "cluster_id": cluster_id,
            "representative_chunks": representative_chunks,
            "all_chunk_ids": all_chunk_ids
        })

    return results


# ── Quick local test ──────────────────────────────────────────────────────────
# Only runs when you execute: python clusterer.py. Never runs when the app imports this module.
if __name__ == "__main__":
    # We need real embeddings to test this — random numbers won't cluster meaningfully. So we import our own embedder to generate them.
    from embedder import embed_chunks

    mock_chunks = [
        {"chunk_id": "test_001", "text": "Users struggle to find past orders.", "filename": "test.txt", "source_type": "review"},
        {"chunk_id": "test_002", "text": "The checkout process is slow and confusing.", "filename": "test.txt", "source_type": "review"},
        {"chunk_id": "test_003", "text": "Customer support never replies to tickets.", "filename": "test.txt", "source_type": "ticket"},
        {"chunk_id": "test_004", "text": "I cannot find where to change my payment method.", "filename": "test.txt", "source_type": "review"},
        {"chunk_id": "test_005", "text": "The app crashes every time I open my profile.", "filename": "test.txt", "source_type": "review"},
        {"chunk_id": "test_006", "text": "Support team is very helpful and fast.", "filename": "test.txt", "source_type": "ticket"},
        {"chunk_id": "test_007", "text": "I love the new dashboard design.", "filename": "test.txt", "source_type": "review"},
        {"chunk_id": "test_008", "text": "Notifications keep arriving even after I turned them off.", "filename": "test.txt", "source_type": "review"},
        {"chunk_id": "test_009", "text": "The search bar does not return relevant results.", "filename": "test.txt", "source_type": "review"},
        {"chunk_id": "test_010", "text": "Billing information is impossible to update.", "filename": "test.txt", "source_type": "ticket"},
    ]

    # Generate real embeddings using our embedder module.
    embeddings = embed_chunks(mock_chunks)

    # Run the clustering.
    clusters = cluster(mock_chunks, embeddings)

    # Print results so you can visually verify the groupings make sense.
    print(f"Best k chosen: {len(clusters)} clusters\n")
    for c in clusters:
        print(f"Cluster {c['cluster_id']}:")
        print(f"  All chunk ids: {c['all_chunk_ids']}")
        print(f"  Representative chunks:")
        for rc in c['representative_chunks']:
            print(f"    - {rc['text']}")
        print()
