"""
llm.py — Clusters + scored_clusters + goal → OST JSON via Groq
Owner: Lucas

DATA CONTRACT (see docs/data_contracts.md / CLAUDE2.md):
    Input:  clusters (list[dict]), scored_clusters (list[dict]), goal (str)
    Output: OST dict {goal, opportunities: [...]} with scores injected from scored_clusters
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

PRIMARY_MODEL = "llama-3.1-8b-instant"
FALLBACK_MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "system_prompt.txt"


def build_ost(clusters: list[dict], scored_clusters: list[dict], goal: str) -> dict:
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    user_prompt = _build_user_prompt(clusters, scored_clusters, goal)

    raw = _call_groq(system_prompt, user_prompt, PRIMARY_MODEL)
    ost = _parse_json(raw)

    if ost is None:
        raw = _call_groq(system_prompt, user_prompt, FALLBACK_MODEL)
        ost = _parse_json(raw)

    if ost is None:
        return {"goal": goal, "opportunities": []}

    return _inject_scores(ost, scored_clusters, goal)


def _build_user_prompt(clusters: list[dict], scored_clusters: list[dict], goal: str) -> str:
    score_map = {s["cluster_id"]: s for s in scored_clusters}
    lines = [f"Product goal: {goal}\n"]
    for cl in clusters:
        cid = cl["cluster_id"]
        score = score_map.get(cid, {})
        quotes = [c["text"] for c in cl.get("representative_chunks", [])]
        lines.append(f"Cluster {cid} (priority_score={score.get('priority_score', 0):.2f}):")
        for q in quotes:
            lines.append(f"  - {q}")
    return "\n".join(lines)


def _call_groq(system_prompt: str, user_prompt: str, model: str) -> str:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def _parse_json(raw: str) -> dict | None:
    try:
        text = raw.strip().strip("```json").strip("```").strip()
        return json.loads(text)
    except Exception:
        return None


def _inject_scores(ost: dict, scored_clusters: list[dict], goal: str) -> dict:
    score_map = {s["cluster_id"]: s for s in scored_clusters}
    opportunities = []
    for opp in ost.get("opportunities", []):
        cid = opp.get("cluster_id")
        sc = score_map.get(cid, {})
        opp["importance"] = sc.get("importance")
        opp["satisfaction"] = sc.get("satisfaction")
        opp["source_type_diversity"] = sc.get("source_type_diversity")
        opp["odi_score"] = sc.get("odi_score")
        opp["evidence_robustness"] = sc.get("evidence_robustness")
        opp["priority_score"] = sc.get("priority_score")
        opp.pop("priority_score_llm", None)
        opportunities.append(opp)
    return {"goal": goal, "opportunities": opportunities}
