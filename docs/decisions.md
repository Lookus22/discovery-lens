# Discovery Lens — Architecture Decisions Log

Running log of all technical and product decisions. Owner: Lucas.

---

## Apr 22 — Architecture session (Day 1)

### Session state keys — CONFIRMED
Keys: goal, product_name, chunks, embeddings, clusters, ost, source_map
Locked. Change requires PM sign-off.

### Chunk size — CONFIRMED
3-sentence sliding window, 1-sentence overlap. Min 40 chars. No hard token limit for MVP.

### LLM JSON schema — CONFIRMED
Locked in docs/llm_output_schema.json. priority_score computed by pipeline, not LLM.

### System prompt owner — CONFIRMED
Lucas owns prompts/system_prompt.txt and pipeline/llm.py.
Dmitrii owns pipeline/extractor.py and pipeline/chunker.py.

### LLM models — CONFIRMED
Primary: llama-3.1-8b-instant. Fallback: llama-3.3-70b-versatile.

### Standup format — CONFIRMED
Google Meet, daily. Time: TBD at standup 17:00.

### GitHub Issues manager — TBD
Assign at standup 17:00.

---

## Apr 22

- session_state keys: confirmed as per CLAUDE.md
- chunk size: 2–4 sentences (no hard token limit for MVP)
- system prompt owner: Lucas
- LLM JSON schema: approved — see docs/llm_output_schema.json
  - representative_quotes on opportunity (not solution) — traceability at cluster level
  - priority_score computed by pipeline, not LLM — keeps LLM output deterministic
  - chunk_id is the join key to source_map in session_state
- Standup time and format: 5PM google meets
- Mid-project presentation date: 6th May

---

## Apr 23

- priority_score removed from LLM output and from system_prompt.txt
- ODI fields (importance, satisfaction, opportunity_score) injected post-parse by llm.py
- scored_clusters added as input parameter to llm.py
- Merge step: llm.py joins on cluster_id after parsing LLM response
- Consistent with Apr 22 decision: pipeline computes real value, LLM stays deterministic
- system_prompt.txt committed to main via PR (feature/llm-prompt)
- docs/llm_output_schema.json updated and committed — last_updated: 2026-04-23
- session_state keys: confirmed, locked, no changes
- chunk size: 2–4 sentences confirmed, no token limit
  - rationale: simpler, no tokenizer dependency, human-verifiable
- System prompt owner confirmed: Lucas
- Mock OST JSON fixture shared with Mengda and Asma for results page development
- UI mockup created and shared with Mengda and Asma
- llama-3.1-8b-instant produces malformed JSON ~50% of runs on complex outputs
- Cleaning step (trailing comma removal) handles some cases
- llm.py must implement fallback to llama-3.3-70b-versatile on JSONDecodeError
- This is per the original CLAUDE.md spec — confirmed necessary by testing

---

## Apr 29

### Scoring system — REDESIGNED
PM sign-off: Lucas.

`opportunity_score` retired. Replaced by three independent scores per cluster:

| Score | Formula | What it answers |
|-------|---------|-----------------|
| `odi_score` | `importance × (1 - satisfaction)` | How underserved is this need? |
| `evidence_robustness` | `(source_type_diversity × 0.65) + (importance × 0.35)` | How robustly evidenced across source types? |
| `priority_score` | `(odi_score × 0.60) + (evidence_robustness × 0.40)` | What should a PM act on first? |

Rationale:
- `odi_score` preserves the classic ODI mechanic (importance × unmet need)
- `evidence_robustness` adds cross-source corroboration — a cluster evidenced across interviews, reviews, and tickets is stronger signal than the same volume from one channel
- `priority_score` is a weighted synthesis; `odi_score` weighted 0.60 because unmet need is the primary driver, `evidence_robustness` weighted 0.40 to reward multi-source themes
- `source_type_diversity` normalised as unique source types in cluster / total unique source types across all chunks — so all three component scores are on the same 0–1 scale

All three scores are displayed independently in the UI per opportunity card.
Sort key for results page is `priority_score` descending.

### source_map.py — NEW MODULE
New pipeline module added: `pipeline/source_map.py`
Builds chunk-level traceability index after clustering.
Output: `dict[chunk_id → {text, filename, source_type, cluster_id}]`
Stored in `st.session_state["source_map"]`.
Must be called after `clusterer.py` and before `llm.py`.

### llm.py — IMPLEMENTED
Stub replaced with full implementation.
Groq call with system_prompt.txt, JSON parse, fallback to llama-3.3-70b-versatile on failure.
Post-parse merge injects all six score fields from scored_clusters on cluster_id.

### docs/ost_tree_spec.md — NEW
Component spec created for Asma.
Defines render_ost_tree(ost) layout: goal header, vertical opportunity cards, score panel (three st.metric), solutions with risk badges.
File: docs/ost_tree_spec.md

### Files updated today
- pipeline/odi_scorer.py — three-score system
- pipeline/llm.py — full implementation
- pipeline/source_map.py — new module
- docs/data_contracts.md — contracts updated for all changed modules
- docs/llm_output_schema.json — opportunity_score retired, three scores added, changelog entry
- docs/ost_tree_spec.md — new component spec for Asma
- CLAUDE.md — odi_scorer contract, llm.py injected fields, score definitions table
