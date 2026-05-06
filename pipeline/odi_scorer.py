"""
odi_scorer.py — Clusters + chunks → three ODI scores (deterministic)
Owner: Asma

DATA CONTRACT (see docs/data_contracts.md / CLAUDE2.md):
    Input:  clusters (list[dict]), chunks (list[dict])
    Output: list of dicts sorted by priority_score descending

Scores:
    importance          = cluster_size / total_chunks
    avg_sentiment       = mean VADER compound score across chunks in cluster
    satisfaction        = (avg_sentiment + 1) / 2
    source_type_diversity = unique source types in cluster / total unique source types
    odi_score           = importance * (1 - satisfaction)
    evidence_robustness = (source_type_diversity * 0.65) + (importance * 0.35)
    priority_score      = (odi_score * 0.60) + (evidence_robustness * 0.40)
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def score(clusters: list[dict], chunks: list[dict]) -> list[dict]:
    analyser = SentimentIntensityAnalyzer()
    chunk_map = {c["chunk_id"]: c for c in chunks}
    total_chunks = len(chunks)
    all_source_types = {c.get("source_type", "") for c in chunks if c.get("source_type")}
    total_source_types = max(len(all_source_types), 1)

    scored = []
    for cl in clusters:
        chunk_ids = cl.get("all_chunk_ids", [])
        cluster_chunks = [chunk_map[cid] for cid in chunk_ids if cid in chunk_map]
        cluster_size = len(cluster_chunks)

        sentiments = [analyser.polarity_scores(c["text"])["compound"] for c in cluster_chunks]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

        source_types_in_cluster = {c.get("source_type", "") for c in cluster_chunks if c.get("source_type")}
        source_type_diversity = len(source_types_in_cluster) / total_source_types

        importance = cluster_size / total_chunks if total_chunks > 0 else 0.0
        satisfaction = (avg_sentiment + 1) / 2
        odi_score = importance * (1 - satisfaction)
        evidence_robustness = (source_type_diversity * 0.65) + (importance * 0.35)
        priority_score = (odi_score * 0.60) + (evidence_robustness * 0.40)

        scored.append({
            "cluster_id": cl["cluster_id"],
            "cluster_size": cluster_size,
            "importance": round(importance, 4),
            "avg_sentiment": round(avg_sentiment, 4),
            "satisfaction": round(satisfaction, 4),
            "source_type_diversity": round(source_type_diversity, 4),
            "odi_score": round(odi_score, 4),
            "evidence_robustness": round(evidence_robustness, 4),
            "priority_score": round(priority_score, 4),
        })

    return sorted(scored, key=lambda x: x["priority_score"], reverse=True)
