"""
llm.py — Clusters → OST JSON via Groq
Owner: Lucas

DATA CONTRACT (see docs/data_contracts.md):
    Input:  clusters (list[dict]), goal (str)
    Output: OST dict {goal, opportunities: [...]}

TODO: call Groq API with system_prompt.txt, parse JSON response
Hint: use groq library, handle JSON parse failure with fallback model
Models: llama-3.1-8b-instant (primary), llama-3.3-70b-versatile (fallback)
"""

def build_ost(clusters: list[dict], goal: str) -> dict:
    raise NotImplementedError("Lucas: implement build_ost() here")
