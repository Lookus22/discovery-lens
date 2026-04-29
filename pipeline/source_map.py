"""
source_map.py
Builds the chunk-level traceability index after clustering.

Input:
    chunks   — output of chunker.py
    clusters — output of clusterer.py

Output:
    source_map (dict) — chunk_id → {text, filename, source_type, cluster_id}
    Stored in st.session_state["source_map"]

This module has no dependencies beyond the stdlib.
It must be called after clusterer.py and before llm.py.
"""

from typing import Any


def build_source_map(
    chunks: list[dict[str, Any]],
    clusters: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """
    Build a flat lookup from chunk_id to its text, origin, and cluster assignment.

    Args:
        chunks:   output of chunker.py
        clusters: output of clusterer.py

    Returns:
        dict mapping chunk_id → {text, filename, source_type, cluster_id}
        cluster_id is None if the chunk was not assigned to any cluster.
    """
    # Build reverse lookup: chunk_id → cluster_id from clusters output
    chunk_to_cluster: dict[str, int] = {
        chunk_id: c["cluster_id"]
        for c in clusters
        for chunk_id in c["all_chunk_ids"]
    }

    return {
        chunk["chunk_id"]: {
            "text": chunk["text"],
            "filename": chunk["filename"],
            "source_type": chunk["source_type"],
            "cluster_id": chunk_to_cluster.get(chunk["chunk_id"]),  # None if unassigned
        }
        for chunk in chunks
    }
