# Discovery Lens — Shared AI Context

Paste this file into your Claude Project instructions before every working session.
Last updated: Apr 29, 2026. Do not edit without team agreement.

---

## What this product is

Discovery Lens is a single-user Streamlit app that helps product managers at tech companies
synthesise qualitative discovery data — interviews, app reviews, support tickets, usability
notes — into a structured Opportunity-Solution Tree (OST) grounded in evidence.

The PM sets a product goal, uploads discovery files, and the tool clusters insights, frames
opportunities in Jobs-to-be-Done (JTBD) language, scores them using deterministic ODI
signals, and shows exactly which source quotes justify each decision.

**This is a capstone project. It must run on Streamlit Community Cloud with no GPU, no
database, and no authentication. Keep every dependency CPU-only and pip-installable.**

---

## Repo structure

```
discovery-lens/
├── CLAUDE.md                  # this file — shared AI context
├── README.md
├── requirements.txt
├── .env.example               # GROQ_API_KEY=your_key_here
├── .gitignore
├── app.py                     # Streamlit entry point
├── pages/
│   ├── 1_goal.py              # goal input page
│   ├── 2_upload.py            # file upload page
│   └── 3_results.py           # OST + views
├── pipeline/
│   ├── extractor.py           # file → raw text
│   ├── chunker.py             # text → chunks
│   ├── embedder.py            # chunks → embeddings
│   ├── clusterer.py           # embeddings → clusters
│   ├── odi_scorer.py          # clusters + chunks → three scores (deterministic)
│   └── llm.py                 # clusters + scored_clusters → OST JSON (Groq)
├── components/
│   ├── ost_tree.py            # OST HTML/JS component
│   ├── priority_matrix.py     # Plotly 2×2 scatter
│   └── heatmap.py             # evidence heatmap
├── notebooks/                 # EDA and experimentation only — never imported by the app
├── prompts/
│   └── system_prompt.txt      # LLM system prompt — version controlled
├── data/
│   ├── synthetic/             # datasets A and B
│   └── public/                # sampled public datasets
└── docs/
    ├── data_contracts.md      # module I/O specs — source of truth
    ├── decisions.md           # dated log of all architecture decisions
    ├── llm_output_schema.json # approved LLM output format with examples
    └── context/               # personal Claude briefing files — one per teammate
        ├── lucas.md
        ├── mengda.md
        ├── asma.md
        └── dmitrii.md
```

---

## Tech stack — do not deviate without PM sign-off

| Layer | Choice | Notes |
|-------|--------|-------|
| App framework | Streamlit | Multi-page, session_state, custom components |
| Deployment | Streamlit Community Cloud | Free tier, connect GitHub repo |
| LLM | Groq API — llama-3.1-8b-instant | Fallback: llama-3.3-70b-versatile |
| Embeddings | sentence-transformers — all-MiniLM-L6-v2 | CPU-only, ~80MB, 384 dims |
| Clustering | scikit-learn KMeans | Elbow + silhouette for k selection |
| Sentiment | VADER (nltk) | Rule-based, no API |
| Visualisation | Plotly | Priority matrix + evidence heatmap |
| File parsing | pypdf, python-docx, pandas | PDF, DOCX, CSV/TXT |
| State | st.session_state | No database |
| Export | JSON file download | Full OST + traceability |

---

## Constraints — hard limits, never work around these

- Single-user, single-project session. No authentication.
- Max ~500 text chunks per session (Streamlit Cloud memory ceiling).
- No database. State lives entirely in st.session_state.
- No GPU. All ML must run CPU-only.
- All dependencies must be pip-installable and listed in requirements.txt.
- Notebooks (.ipynb) are for exploration only. The app imports only from pipeline/*.py.

---

## Data contracts — exact module interfaces

These are the agreed input/output formats. Every module must match these exactly.
If you think a contract needs to change, raise it with the team before writing code.
Full contracts live in `docs/data_contracts.md` — this section is a summary.

### Pipeline flow

```
UploadedFile → extractor.py → raw_text (str)
→ chunker.py → chunks (list[dict])
→ embedder.py → embeddings (np.ndarray, n_chunks × 384)
→ clusterer.py → clusters (list[dict])
→ odi_scorer.py → scored_clusters (list[dict]) → st.session_state["scored_clusters"]
→ llm.py → ost (dict) → st.session_state["ost"]
```

### extractor.py
```python
# Input
file: UploadedFile   # Streamlit UploadedFile object
source_type: str     # one of: "interview" | "review" | "ticket" | "usability"

# Output
raw_text: str        # full extracted text, plain string
```

### chunker.py
```python
# Input
raw_text: str
filename: str
source_type: str     # same enum as above

# Output — list of dicts, one per chunk
[
  {
    "chunk_id": str,        # format: "{safe_filename}_{zero_padded_index}" e.g. "interview_01_001"
    "text": str,            # 2–4 sentences
    "filename": str,
    "source_type": str
  },
  ...
]
```

### embedder.py
```python
# Input
chunks: list[dict]   # output of chunker.py

# Output
embeddings: np.ndarray   # shape: (n_chunks, 384)
# Note: chunks[i] and embeddings[i] share the same index — never reorder independently
```

### clusterer.py
```python
# Input
chunks: list[dict]        # output of chunker.py
embeddings: np.ndarray    # output of embedder.py

# Output — list of dicts, one per cluster
[
  {
    "cluster_id": int,
    "representative_chunks": list[dict],   # top 3 chunks closest to centroid
    "all_chunk_ids": list[str]             # all chunk_ids belonging to this cluster
  },
  ...
]
```

### odi_scorer.py
```python
# Input
clusters: list[dict]   # output of clusterer.py
chunks: list[dict]     # output of chunker.py
# total_chunks and total_source_types are derived internally — no extra args needed

# Output — list of dicts, one per cluster, sorted by priority_score descending
[
  {
    "cluster_id": int,
    "cluster_size": int,
    # --- Raw signals (available for UI display and debugging) ---
    "importance": float,            # cluster_size / total_chunks, range 0.0–1.0
    "avg_sentiment": float,         # raw VADER compound mean, range -1.0 to 1.0
    "satisfaction": float,          # (avg_sentiment + 1) / 2, range 0.0–1.0
    "source_type_diversity": float, # unique source types in cluster / total unique source types, range 0.0–1.0
    # --- Three scores shown in UI ---
    "odi_score": float,             # importance * (1 - satisfaction) — unmet need signal, range 0.0–1.0
    "evidence_robustness": float,   # (source_type_diversity * 0.65) + (importance * 0.35) — cross-source corroboration, range 0.0–1.0
    "priority_score": float         # (odi_score * 0.60) + (evidence_robustness * 0.40) — primary sort key, range 0.0–1.0
  },
  ...
]
# Deterministic — no LLM, no external API.
# PM sign-off (Lucas, Apr 29 2026): opportunity_score retired, replaced by three independent scores.
```

### llm.py
```python
# Input
clusters: list[dict]          # output of clusterer.py
scored_clusters: list[dict]   # output of odi_scorer.py
goal: str                     # from st.session_state["goal"]

# LLM generates — JTBD and solutions only. Never generates any score fields.
# After parsing, llm.py merges scored_clusters on cluster_id to produce the final OST:
{
  "goal": str,
  "opportunities": [
    {
      "jtbd": str,                    # "When I [situation], I want to [motivation], so I can [outcome]."
      "cluster_id": int,
      # --- Injected from scored_clusters, never LLM-generated ---
      "importance": float,
      "satisfaction": float,
      "source_type_diversity": float,
      "odi_score": float,
      "evidence_robustness": float,
      "priority_score": float,
      "solutions": [
        {
          "label": str,
          "assumptions": [
            {
              "text": str,
              "risk": str    # "low" | "medium" | "high"
            }
          ]
        }
      ]
    }
  ]
}
# If a cluster_id from the LLM has no match in scored_clusters, set all score fields to null — do not crash.
```

---

## session_state keys — use exactly these names

```python
st.session_state["goal"]            # str — product goal statement
st.session_state["product_name"]    # str — product name
st.session_state["chunks"]          # list[dict] — output of chunker.py
st.session_state["embeddings"]      # np.ndarray — output of embedder.py
st.session_state["clusters"]        # list[dict] — output of clusterer.py
st.session_state["scored_clusters"] # list[dict] — output of odi_scorer.py
st.session_state["ost"]             # dict — merged OST JSON (LLM output + injected scores)
st.session_state["source_map"]      # dict — chunk_id → {text, filename, source_type, cluster_id}
```

`scored_clusters` must be populated **before** `llm.py` is called.

---

## LLM output rules

- Always instruct the model to return **only valid JSON** — no preamble, no markdown fences.
- Always wrap JSON parsing in try/except. On failure, retry once with llama-3.3-70b-versatile.
- The JTBD format for opportunities is strictly: "When I [situation], I want to [motivation],
  so I can [outcome]."
- Score fields (`odi_score`, `evidence_robustness`, `priority_score`) are **never generated
  by the LLM** — they are injected post-parse by merging with `scored_clusters` on `cluster_id`.
- The system prompt lives in `prompts/system_prompt.txt`. Only one person edits it.
  Any change must be committed/reviewed — never use a privately modified version.

---

## Score definitions — for UI display and teammate reference

| Score | Formula | What it answers |
|-------|---------|-----------------|
| `odi_score` | `importance × (1 - satisfaction)` | How underserved is this need? |
| `evidence_robustness` | `(source_type_diversity × 0.65) + (importance × 0.35)` | How robustly evidenced across source types? |
| `priority_score` | `(odi_score × 0.60) + (evidence_robustness × 0.40)` | What should a PM act on first? |

All three scores are shown independently in the UI per opportunity. `priority_score` is the primary sort key.

---

## Git workflow

- Branch naming: `feature/module-name` or `fix/short-description`
- Never push directly to main. All work goes through pull requests (PR).
- One feature = one PR. Keep PRs small and reviewable.
- Use GitHub Issues for bugs. Labels: P1-blocker / P2-important / P3-nice-to-have.

---

## Definition of done

A task is done when:
1. Code is merged to main via PR (not direct push)
2. It does not break any existing feature
3. Lucas or one teammate has seen it work end-to-end
4. It matches the data contracts above exactly

Partial work is not done. If a task is too large, split it in the daily standup.

---

## Personal context files

Each team member has a personal briefing file in `docs/context/`. These files contain
task-specific instructions, dataset EDA guidelines, synthetic data briefs, and a running
log of personal decisions. They grow throughout the project.

**Paste CLAUDE.md + your personal file into your Claude Project before every session.**

| Person | File | Week 1 focus |
|--------|------|--------------|
| Lucas | `docs/context/lucas.md` | Architecture, sign-offs, Kimola EDA |
| Mengda | `docs/context/mengda.md` | Lidl synthetic data, Google Play EDA |
| Asma | `docs/context/asma.md` | Asana synthetic data, Twitter Support EDA |
| Dmitrii | `docs/context/dmitrii.md` | Revolut synthetic data, Amazon Reviews EDA |

Do not paste a teammate's file into your own session — it adds irrelevant context
and can cause Claude to mix up module responsibilities.

---

## Synthetic data — overview

Each teammate is generating a synthetic discovery dataset for one product. These datasets
are the primary demo inputs for Discovery Lens and must be varied and messy enough to
stress-test the pipeline. See individual context files for full briefs.

| Person | Product | Type |
|--------|---------|------|
| Mengda | Lidl Plus app | Consumer mobile / grocery retail |
| Asma | Asana | B2B SaaS / project management |
| Dmitrii | Revolut | Consumer fintech / payments |

Each dataset should include: user interview transcripts, usability test notes, app store
or G2 reviews, customer support tickets, internal sales/CS notes, and Reddit threads
(scraped where possible, generated if not). Aim for 15–20 documents per product.

All synthetic data lives in `data/synthetic/{product}/`. See individual context files
for file naming conventions and generation prompts.

---

## Public datasets — EDA assignments

| Person | Dataset | Notebook |
|--------|---------|----------|
| Lucas | Kimola NLP (App Store + G2) | `notebooks/eda_kimola_lucas.ipynb` |
| Mengda | Google Play Store Reviews | `notebooks/eda_google_play_mengda.ipynb` |
| Asma | Twitter Customer Support | `notebooks/eda_twitter_support_asma.ipynb` |
| Dmitrii | Amazon Reviews 2023 — Software | `notebooks/eda_amazon_reviews_dmitrii.ipynb` |

EDA notebooks live in `notebooks/` and are never imported by the app. Each notebook
must end with a markdown findings summary covering: usable row count, expected chunk
count, data quality issues, and recommended sample size for the demo.

---

## What to tell Claude at the start of every session

After pasting this file into your project instructions, begin each conversation with the
specific module or task you are working on. For example:

> "I am working on odi_scorer.py. It receives clusters (list[dict]) and chunks (list[dict])
> and must return a list of scored cluster dicts matching the data contract above. Help me
> implement the three-score system: odi_score, evidence_robustness, and priority_score."

The more precisely you describe your current task and reference the contracts above, the
more consistent the output will be across the team.

---

## What NOT to ask Claude to change

Without the team's sign-off, do not ask Claude to:
- Change any session_state key name
- Change the OST JSON structure
- Add a new Streamlit page or view
- Change what the LLM outputs or how it is parsed
- Add a new data source or dependency

If Claude suggests a change in any of these areas, log it as a GitHub Issue first.
