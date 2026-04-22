"""
llm.py — Clusters → OST JSON via Groq

CONTRACT:
    Input:  clusters (list[dict]), goal (str)
    Output: OST dict {goal, opportunities: [{jtbd, priority_score, cluster_id, solutions}]}

Models:
    Primary:  llama-3.1-8b-instant
    Fallback: llama-3.3-70b-versatile
"""
import json, os
from pathlib import Path
from groq import Groq

PRIMARY_MODEL = "llama-3.1-8b-instant"
FALLBACK_MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "system_prompt.txt"

def build_ost(clusters: list[dict], goal: str) -> dict:
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8") if SYSTEM_PROMPT_PATH.exists() else "Return only valid JSON. No preamble."
    user_message = json.dumps({"goal": goal, "clusters": [{"cluster_id": c["cluster_id"], "representative_quotes": [ch["text"] for ch in c["representative_chunks"]], "total_chunks": len(c["all_chunk_ids"])} for c in clusters]}, ensure_ascii=False)

    raw = _call(PRIMARY_MODEL, system_prompt, user_message)
    ost = _parse(raw)
    if ost is None:
        raw = _call(FALLBACK_MODEL, system_prompt, user_message)
        ost = _parse(raw)
    if ost is None:
        raise ValueError("LLM returned invalid JSON after retry. Check the system prompt.")

    ost["goal"] = goal
    for i, opp in enumerate(ost.get("opportunities", [])):
        opp.setdefault("cluster_id", i)
        opp.setdefault("priority_score", 0.5)
    return ost

def _call(model, system_prompt, user_message):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    r = client.chat.completions.create(model=model, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}], temperature=0.3, max_tokens=4096)
    return r.choices[0].message.content

def _parse(text):
    try:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception:
        return None
