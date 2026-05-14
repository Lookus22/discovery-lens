"""
persona_detector.py — chunks → 2-3 behavioural personas

Second K-means pass that operates on per-chunk BEHAVIOURAL features
(not text embeddings). Personas are concepts of behaviour patterns,
not real users — multiple users can exhibit the same persona, and
one user can switch personas across chunks.

Lucas's clarification (2026-05-04):
    "Persona is not an actual person, meaning it's not related to
    one user but to a concept of a user described by the behaviour
    that then relates to multiple users. So, it would most likely
    be a cluster of chunks that describe a certain behaviour."

    "definitely b. I understand a as it would do the same thing as
    for the opportunity clustering and we don't need that, we need
    clusters from different behaviours."

Why metadata features (not embeddings):
    Text embeddings encode WHAT the chunk talks about (already done
    by clusterer.py). For BEHAVIOUR we need HOW the chunk speaks —
    short and angry vs long and reflective vs structured and neutral.

Contract (see docs/data_contracts.md — to be added):
    Input:
        chunks: list[dict]   # output of chunker.py
        n_personas: int      # default 3, must be 2 or 3

    Output:
        personas: list[dict]
            persona_id: int
            label: str                  # auto-generated descriptor
            size: int                   # number of chunks in persona
            centroid: dict              # raw centroid features
            sample_chunks: list[dict]   # 3 closest chunks to centroid
            dominant_source_type: str
        chunk_personas: dict[str, int]  # chunk_id → persona_id
"""

from __future__ import annotations

import re
from typing import Any

import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Initialise once at module level — avoids reloading the lexicon on every call
_vader = SentimentIntensityAnalyzer()

# Source types — kept in sync with extractor.py and chunker.py
ALLOWED_SOURCE_TYPES = ["interview", "review", "ticket", "usability"]

# First-person markers used as a behavioural signal — high frequency
# correlates with self-disclosure / personal narrative voice
FIRST_PERSON_PATTERN = re.compile(
    r"\b(I|me|my|mine|myself|we|us|our|ours)\b", re.IGNORECASE
)


def detect_personas(
    chunks: list[dict[str, Any]],
    n_personas: int = 3,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """
    Cluster chunks into 2-3 behavioural personas.

    Args:
        chunks: list of chunk dicts from chunker.py
        n_personas: number of personas, must be 2 or 3

    Returns:
        personas: list of persona dicts (one per cluster)
        chunk_personas: dict mapping chunk_id to persona_id

    Raises:
        ValueError: if n_personas not in {2, 3}
        ValueError: if chunks is empty
        ValueError: if there are fewer chunks than n_personas
    """
    if n_personas not in (2, 3):
        raise ValueError(f"n_personas must be 2 or 3, got {n_personas}")

    if not chunks:
        raise ValueError("chunks list is empty — cannot detect personas")

    if len(chunks) < n_personas:
        raise ValueError(
            f"need at least {n_personas} chunks for {n_personas} personas, "
            f"got {len(chunks)}"
        )

    # ---- 1. Build per-chunk behavioural feature vectors -------------------
    feature_matrix = _build_feature_matrix(chunks)

    # ---- 2. Standardise features so no single one dominates ---------------
    # Different features have different scales (sentiment in [-1, 1],
    # length in chars). Without scaling, length would swamp the signal.
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(feature_matrix)

    # ---- 3. Run K-means ---------------------------------------------------
    # n_init=10 — sklearn default since v1.4. Explicit for clarity.
    # random_state=42 for reproducibility across runs.
    km = KMeans(n_clusters=n_personas, random_state=42, n_init=10)
    labels = km.fit_predict(features_scaled)

    # ---- 4. Build persona summaries ---------------------------------------
    personas = _build_personas(
        chunks=chunks,
        labels=labels,
        feature_matrix=feature_matrix,
        scaled_centroids=km.cluster_centers_,
        scaler=scaler,
    )

    # ---- 5. Build chunk_id → persona_id mapping ---------------------------
    chunk_personas = {
        chunk["chunk_id"]: int(label) for chunk, label in zip(chunks, labels)
    }

    return personas, chunk_personas


def _build_feature_matrix(chunks: list[dict[str, Any]]) -> np.ndarray:
    """
    Extract behavioural features from each chunk.

    Features (in order):
        0. sentiment_compound  — VADER compound score, range [-1, 1]
        1. text_length_chars   — chunk length in characters
        2. word_count          — chunk length in words
        3. exclamation_density — exclamation marks per 100 chars (urgency)
        4. question_density    — question marks per 100 chars (uncertainty)
        5. caps_ratio          — fraction of words in ALL CAPS (intensity)
        6. first_person_ratio  — fraction of first-person pronouns (self-focus)
        7-10. source_type one-hot (interview, review, ticket, usability)

    Source type is included as a soft signal — Lucas's task description
    explicitly mentions "source_type + sentiment metadata". One-hot
    encoding lets K-means find natural correlations (e.g. tickets +
    short + angry → one persona) without forcing them.
    """
    rows = []
    for chunk in chunks:
        text = chunk.get("text", "")
        source_type = chunk.get("source_type", "")

        # Avoid divide-by-zero on empty text
        char_count = max(len(text), 1)
        word_count = max(len(text.split()), 1)

        sentiment = _vader.polarity_scores(text)["compound"]

        exclamations = text.count("!") / char_count * 100
        questions = text.count("?") / char_count * 100

        # ALL CAPS words signal intensity ("FROZEN", "URGENT")
        # Filter very short tokens and require length >= 2 to avoid
        # counting "I" or "A".
        caps_words = sum(
            1
            for w in text.split()
            if w.isupper() and len(w) >= 2 and any(c.isalpha() for c in w)
        )
        caps_ratio = caps_words / word_count

        first_person_count = len(FIRST_PERSON_PATTERN.findall(text))
        first_person_ratio = first_person_count / word_count

        source_one_hot = [
            float(source_type == st) for st in ALLOWED_SOURCE_TYPES
        ]

        rows.append(
            [
                sentiment,
                len(text),
                word_count,
                exclamations,
                questions,
                caps_ratio,
                first_person_ratio,
                *source_one_hot,
            ]
        )

    return np.array(rows, dtype=float)


def _build_personas(
    chunks: list[dict[str, Any]],
    labels: np.ndarray,
    feature_matrix: np.ndarray,
    scaled_centroids: np.ndarray,
    scaler: StandardScaler,
) -> list[dict[str, Any]]:
    """
    For each persona cluster, produce a summary dict with:
        - centroid in original (un-scaled) feature space — for UI display
        - 3 representative chunks closest to centroid
        - dominant source type
        - human-readable label inferred from centroid
    """
    # Convert centroids back to interpretable feature values
    raw_centroids = scaler.inverse_transform(scaled_centroids)

    personas = []
    for persona_id in range(len(scaled_centroids)):
        member_indices = np.where(labels == persona_id)[0]

        if len(member_indices) == 0:
            # Should not happen with KMeans, but guard against it
            continue

        # Find 3 chunks closest to this persona's centroid (in scaled space)
        member_features_scaled = scaler.transform(
            feature_matrix[member_indices]
        )
        distances = np.linalg.norm(
            member_features_scaled - scaled_centroids[persona_id], axis=1
        )
        closest_local_indices = np.argsort(distances)[:3]
        sample_chunk_indices = member_indices[closest_local_indices]
        sample_chunks = [chunks[i] for i in sample_chunk_indices]

        # Dominant source type within this persona
        source_types = [chunks[i].get("source_type", "") for i in member_indices]
        dominant_source_type = (
            max(set(source_types), key=source_types.count)
            if source_types
            else ""
        )

        # Pack centroid as a labelled dict for UI consumption
        centroid_raw = raw_centroids[persona_id]
        centroid = {
            "avg_sentiment": round(float(centroid_raw[0]), 4),
            "avg_length_chars": round(float(centroid_raw[1]), 1),
            "avg_word_count": round(float(centroid_raw[2]), 1),
            "exclamation_density": round(float(centroid_raw[3]), 4),
            "question_density": round(float(centroid_raw[4]), 4),
            "caps_ratio": round(float(centroid_raw[5]), 4),
            "first_person_ratio": round(float(centroid_raw[6]), 4),
        }

        label = _label_persona(centroid, dominant_source_type)

        personas.append(
            {
                "persona_id": persona_id,
                "label": label,
                "size": int(len(member_indices)),
                "centroid": centroid,
                "sample_chunks": sample_chunks,
                "dominant_source_type": dominant_source_type,
            }
        )

    # Sort by size descending — largest persona first in UI
    personas.sort(key=lambda p: p["size"], reverse=True)
    # Re-index persona_id after sort so 0 = largest
    for new_id, persona in enumerate(personas):
        persona["persona_id"] = new_id

    return personas


def _label_persona(centroid: dict[str, float], dominant_source: str) -> str:
    """
    Generate a human-readable label from centroid statistics.

    Heuristic — not a science. The goal is a useful PM-facing chip
    label. Tune the thresholds based on real data observation.
    """
    sentiment = centroid["avg_sentiment"]
    word_count = centroid["avg_word_count"]
    urgency = centroid["exclamation_density"]
    uncertainty = centroid["question_density"]
    self_focus = centroid["first_person_ratio"]

    # Rules ordered from most specific to most general.
    # Earlier rules win — keep specific behavioural signatures at the top.

    # --- Strongly negative + short + urgent → "Frustrated complainer" ---
    if sentiment < -0.2 and word_count < 50 and urgency > 0.1:
        return "Frustrated complainer"

    # --- Negative-ish + first-person heavy → "Disappointed user" ---
    if sentiment < 0 and self_focus > 0.05:
        return "Disappointed user"

    # --- Long + reflective + first-person → "Reflective interviewee" ---
    # Captures interview voice: long-form, self-disclosing, balanced sentiment.
    if word_count > 50 and self_focus > 0.05 and -0.3 < sentiment < 0.6:
        return "Reflective interviewee"

    # --- Positive + medium-to-long → "Satisfied advocate" ---
    if sentiment > 0.4 and word_count > 30:
        return "Satisfied advocate"

    # --- Very high question density → "Curious explorer" ---
    # Threshold raised: usability/interview transcripts naturally have
    # 0.05-0.15 question density. Reserve this label for genuinely
    # question-dominated centroids.
    if uncertainty > 0.30:
        return "Curious explorer"

    # --- Neutral sentiment + low self-focus → "Observer note" ---
    # Captures usability observer notes and sales notes — third-person, neutral.
    if abs(sentiment) < 0.3 and self_focus < 0.04:
        return "Observer note"

    # --- Fallback: name by dominant source type ---
    fallback_map = {
        "interview": "Interviewee voice",
        "review": "Review voice",
        "ticket": "Ticket voice",
        "usability": "Usability observer",
    }
    return fallback_map.get(dominant_source, "Mixed voice")
