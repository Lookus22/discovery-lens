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

### Mid-project presentation date — TBD ⚠
Confirm from bootcamp calendar before standup.

---
