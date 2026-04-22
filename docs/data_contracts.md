# Discovery Lens — Data Contracts

Source of truth for all pipeline module I/O. Last updated: Apr 22, 2026.
If a contract needs to change, open a GitHub Issue and tag Lucas first.

## Pipeline flow

UploadedFile → extractor.py → raw_text (str)
→ chunker.py → chunks (list[dict])
→ embedder.py → embeddings (np.ndarray, n_chunks × 384)
→ clusterer.py → clusters (list[dict])
→ llm.py → ost (dict) → st.session_state["ost"]

## extractor.py
Input:  file (UploadedFile), source_type (str: interview|review|ticket|usability)
Output: raw_text (str)

## chunker.py
Input:  raw_text (str), filename (str), source_type (str)
Output: [{"chunk_id": str, "text": str, "filename": str, "source_type": str}, ...]
Notes:  chunk_id format = "{safe_filename}_{zero_padded_index}" e.g. "interview_01_001"

## embedder.py
Input:  chunks (list[dict])
Output: np.ndarray shape (n_chunks, 384)
Notes:  chunks[i] and embeddings[i] share the same index — never reorder independently.

## clusterer.py
Input:  chunks (list[dict]), embeddings (np.ndarray)
Output: [{"cluster_id": int, "representative_chunks": list[dict], "all_chunk_ids": list[str]}, ...]
Notes:  representative_chunks = top 3 closest to centroid (full chunk dicts).

## llm.py
Input:  clusters (list[dict]), goal (str)
Output: {"goal": str, "opportunities": [{"jtbd": str, "priority_score": float, "cluster_id": int, "solutions": [{"label": str, "assumptions": [{"text": str, "risk": str}]}]}]}
Notes:  jtbd strictly = "When I..., I want to..., so I can..."
        priority_score computed by pipeline (Week 2), not LLM.

## session_state keys
"goal"         str        — product goal
"product_name" str        — product name
"chunks"       list[dict] — output of chunker
"embeddings"   np.ndarray — output of embedder
"clusters"     list[dict] — output of clusterer
"ost"          dict       — full OST JSON
"source_map"   dict       — chunk_id → {text, filename, source_type, cluster_id}
