# `components/ost_tree.py` — Component Spec

**Owner:** Asma
**Last updated:** Apr 29, 2026
**Status:** Ready to implement

---

## Purpose

Renders the Opportunity-Solution Tree (OST) on the results page.
Receives a fully populated `ost` dict and displays it as a vertical list of opportunity cards.

This component only renders. It never calls pipeline modules, never reads session_state directly, and never computes scores.

---

## Function signature

```python
def render_ost_tree(ost: dict) -> None
```

Called from `pages/3_results.py` as:

```python
from components.ost_tree import render_ost_tree
render_ost_tree(st.session_state["ost"])
```

---

## Input shape

The `ost` dict matches the approved schema in `docs/llm_output_schema.json`. Relevant fields:

```python
{
  "goal": str,
  "opportunities": [
    {
      "jtbd": str,
      "cluster_id": int,
      "odi_score": float | None,
      "evidence_robustness": float | None,
      "priority_score": float | None,
      "solutions": [
        {
          "label": str,
          "assumptions": [
            {
              "text": str,
              "risk": "low" | "medium" | "high"
            }
          ]
        }
      ]
    }
  ]
}
```

Opportunities arrive **pre-sorted by `priority_score` descending** — iterate in order, do not re-sort.

---

## Layout spec

### 1. Goal header
Display `ost["goal"]` as a prominent header at the top of the component.

```python
st.header(ost["goal"])
```

---

### 2. Opportunity cards
One card per opportunity, expanded by default. Use `st.container()` with a divider between cards.

#### 2a. JTBD statement
Full text, not truncated. Display as the card title.

```python
st.subheader(opportunity["jtbd"])
```

#### 2b. Score panel
Three metrics side by side using `st.columns(3)` and `st.metric`.

| Column | Label | Field |
|--------|-------|-------|
| 1 | ODI Score | `opportunity["odi_score"]` |
| 2 | Evidence Robustness | `opportunity["evidence_robustness"]` |
| 3 | Priority Score | `opportunity["priority_score"]` |

Format values to 2 decimal places. If a field is `None`, display `"—"` — do not crash.

Score definitions for tooltips or help text (optional but recommended):
- **ODI Score** — how underserved is this need? (importance × unmet satisfaction)
- **Evidence Robustness** — how well corroborated across source types?
- **Priority Score** — synthesis of both; primary sort key

#### 2c. Solutions
For each solution under `opportunity["solutions"]`:

- Solution `label` in **bold**
- Assumptions as a tight list below the label
- Each assumption displays its `text` with a colour-coded risk badge:

| Risk value | Colour |
|------------|--------|
| `"low"` | 🟢 green |
| `"medium"` | 🟠 orange |
| `"high"` | 🔴 red |

Suggested implementation using `st.markdown`:

```python
RISK_BADGE = {
    "low": "🟢 Low",
    "medium": "🟠 Medium",
    "high": "🔴 High",
}

for solution in opportunity["solutions"]:
    st.markdown(f"**{solution['label']}**")
    for assumption in solution["assumptions"]:
        badge = RISK_BADGE.get(assumption["risk"], assumption["risk"])
        st.markdown(f"- {assumption['text']} &nbsp; `{badge}`")
```

---

## Null safety

All three score fields (`odi_score`, `evidence_robustness`, `priority_score`) can be `None` if the LLM returned a `cluster_id` with no match in `scored_clusters`. Handle this everywhere scores are displayed:

```python
def _fmt(value: float | None) -> str:
    return f"{value:.2f}" if value is not None else "—"
```

---

## What this component does NOT do

- Does not read `st.session_state` directly — receives `ost` as a parameter
- Does not display source quotes or traceability — that is a separate view
- Does not call any pipeline module
- Does not sort opportunities — data arrives pre-sorted
- Does not compute or modify any score field

---

## File location

```
components/ost_tree.py
```
