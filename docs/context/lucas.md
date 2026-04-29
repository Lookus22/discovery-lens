# Discovery Lens — Lucas's Personal Context

Paste this file into your Claude Project **alongside CLAUDE.md** before every session.
Last updated: Apr 29, 2026.

Add new sections at the bottom as the project progresses. Never delete old sections —
they are a record of your decisions and reasoning.

---

## My role

PM, architecture owner, and sign-off authority. My job is to unblock the team, not to
own any single module. I approve changes to: LLM output format, OST data structure,
new pages or views, new data sources, session_state key names.

---

## Week 1 — My tasks

### 1. Architecture session — Apr 22

Run the session and log every decision in `docs/decisions.md` immediately after.
Decisions that must be made today:

- Confirm session_state key names (already in CLAUDE.md) - done
- Confirm chunk size: 2–4 sentences (or set a token limit in the future - we need to iterate in this and try both starting with the 2-4 sentence chunks. I need to be reminded when appropriate) - done
- Confirm LLM JSON schema (share the draft schema file with the team) - done
- Confirm who edits the system prompt (me) - done, now I have to work on the examples
- Who manages GitHub Issues / Kanban? (assign today)
- Standup time and format (video or Slack async?)
- Mid-project presentation date (confirm from bootcamp calendar)

### 2. Publish CLAUDE.md and personal context files — Apr 22

Commit to main as the very first push, before any branches are created:
- `CLAUDE.md` (shared context)
- `docs/context/lucas.md`
- `docs/context/mengda.md`
- `docs/context/asma.md`
- `docs/context/dmitrii.md`
- `docs/decisions.md` (start with today's architecture decisions)
- `llm_output_schema.json` → move to `docs/llm_output_schema.json`

Tell the team to pull main and paste their file into their Claude Projects
before starting any work.

### 3. EDA — Kimola NLP Datasets

**Dataset:** Kimola NLP Datasets (GitHub)
**Link:** https://github.com/Kimola/nlp-datasets
**Your notebook:** `notebooks/eda_kimola_lucas.ipynb`

This dataset is our best single source for multi-format real data — it contains both
App Store reviews AND G2 B2B SaaS reviews in clean CSV format. It is the closest
public approximation of exactly what Discovery Lens is designed to process.

#### Loading the dataset

```python
import pandas as pd

# Clone or download directly from GitHub
# https://github.com/Kimola/nlp-datasets
# Files are CSVs — load directly

# App Store reviews example
app_store = pd.read_csv("path/to/kimola/app_store_reviews.csv")

# G2 B2B SaaS reviews example
g2_reviews = pd.read_csv("path/to/kimola/g2_reviews.csv")
```

Browse the repo first to understand which files are available and their structure —
Kimola publishes multiple datasets, not all equally useful.

#### What to investigate

**Dataset inventory**
- What files are available in the repo? List them with row counts.
- Which files are App Store reviews vs G2 reviews vs other?
- What columns exist in each file? (text, rating, app/product name, date, etc.)

**Relevance assessment**
- Which apps / SaaS products are covered? Are they relevant to our demo?
  We want products similar to: project management tools, fintech apps, productivity
  software, communication tools
- Sample 30 reviews from each file manually. Quality assessment: are they specific
  enough to contain genuine product insights?

**Format comparison — App Store vs G2**
- App Store reviews: typically short, emotional, consumer language
- G2 reviews: typically longer, structured, B2B language, often with pros/cons sections
- How do these differ in average length, sentence structure, and information density?
- Which will produce better clusters for our pipeline?

**Chunking preview**
- Run samples from each format through a simple sentence splitter
- G2 reviews with explicit "Pros:" / "Cons:" sections — should we split on these headers
  before chunking, or treat the whole review as one text?
- Document your recommendation

**Cross-dataset comparison**
- Compare Kimola's App Store reviews to the Google Play reviews (Mengda's dataset)
  and Amazon Software reviews (Dmitrii's dataset) — are they complementary or redundant?
- This is important for the demo: we want diverse source types, not three datasets
  that produce identical clusters

**Output**
Write a findings summary at the bottom of the notebook (markdown cell):
- Which Kimola files are most useful for Discovery Lens?
- App Store vs G2: which format produces better pipeline input?
- How do they complement the other three datasets?
- Recommended sample size per file for the demo (target: ≤100 chunks total from Kimola)
- Any preprocessing recommendations (strip "Pros:" headers, minimum length filter, etc.)

#### What to tell Claude during EDA

> "I am doing EDA on the Kimola NLP dataset (App Store and G2 SaaS reviews) for
> Discovery Lens, an NLP pipeline that chunks text into 2–4 sentence segments, embeds
> them with all-MiniLM-L6-v2, and clusters them with KMeans. Help me [specific task:
> compare App Store vs G2 review formats / assess chunking behaviour / identify the
> most relevant files for a product management discovery tool]."

---

## Sign-off log

```
## Apr 22 — LLM JSON schema approved
Schema: see docs/llm_output_schema.json
Key decisions:
- representative_quotes on opportunity (not solution) — traceability is at cluster level
- priority_score computed by pipeline, not LLM — keeps LLM output deterministic
- chunk_id is the join key to source_map in session_state
```

```
## Apr 29 — Scoring system redesigned
opportunity_score retired. Replaced by three independent scores per cluster.

odi_score           = importance × (1 - satisfaction)
                      Preserves classic ODI mechanic. Answers: how underserved is this need?

evidence_robustness = (source_type_diversity × 0.65) + (importance × 0.35)
                      New signal. Rewards cross-source corroboration.
                      Answers: how robustly evidenced across source types?

priority_score      = (odi_score × 0.60) + (evidence_robustness × 0.40)
                      Synthesis. Primary sort key for results page.
                      Answers: what should a PM act on first?

Rationale: size is already captured in odi_score via importance. Giving diversity
the higher weight in evidence_robustness (0.65) avoids double-counting volume and
ensures the two scores are genuinely independent signals before synthesis.

All three scores displayed independently in UI per opportunity card.
Files updated: odi_scorer.py, llm.py, llm_output_schema.json, CLAUDE.md,
               data_contracts.md, decisions.md
```

```
## Apr 29 — source_map.py new module approved
New pipeline module: pipeline/source_map.py
Builds chunk_id → {text, filename, source_type, cluster_id} after clustering.
Stored in st.session_state["source_map"].
Call order: after clusterer.py, before llm.py.
```

```
## Apr 29 — llm.py implemented
Stub replaced with full implementation. Owner: Lucas.
Groq call → JSON parse → fallback to llama-3.3-70b-versatile on JSONDecodeError.
Post-parse merge injects odi_score, evidence_robustness, priority_score,
importance, satisfaction, source_type_diversity from scored_clusters on cluster_id.
```

```
## Apr 29 — ost_tree component spec published
docs/ost_tree_spec.md created for Asma.
render_ost_tree(ost) renders: goal header, vertical opportunity cards expanded by default,
score panel with three st.metric per card, solutions with colour-coded risk badges.
Sort order: priority_score descending (pre-sorted by odi_scorer.py — no re-sort needed).
```

---

## Architecture decisions log

Mirror of docs/decisions.md — keep both in sync.

```
## Apr 22
- session_state keys: confirmed as per CLAUDE.md
- chunk size: 2–4 sentences (no hard token limit for MVP)
- system prompt owner: Lucas
- LLM JSON schema: approved — see docs/llm_output_schema.json
- Standup: 5PM Google Meet
- Mid-project presentation date: 6th May
```

```
## Apr 23
- priority_score removed from LLM output and from system_prompt.txt
- ODI fields injected post-parse by llm.py from scored_clusters
- scored_clusters added as input parameter to llm.py
- system_prompt.txt committed to main via PR (feature/llm-prompt)
- llm.py fallback to llama-3.3-70b-versatile on JSONDecodeError confirmed necessary by testing
```

```
## Apr 29
- opportunity_score retired — replaced by odi_score, evidence_robustness, priority_score
- source_map.py added as new pipeline module
- llm.py stub replaced with full implementation
- docs/ost_tree_spec.md created for Asma
- All contracts and shared docs updated (CLAUDE.md, data_contracts.md,
  llm_output_schema.json, decisions.md)
```

---

## How to update this file

Add dated sections as decisions are made and tasks are completed:

```
## Apr 30 — example entry
- What was decided and why
- Which files were changed
```
