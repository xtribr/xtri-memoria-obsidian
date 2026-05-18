#!/usr/bin/env python3
"""
Fase 6 step 2: divide questions-detail.jsonl em N batches estratificados por
área da API. Cada batch ~400 questões para um sub-agente.
"""
import json
from collections import defaultdict
from pathlib import Path

SRC = Path.home() / "phase6-cache" / "questions-detail.jsonl"
OUT_DIR = Path.home() / "phase6-cache"
N_BATCHES = 20

# Constrói payload compacto para cada questão (essencial para classificação)
def compact(q):
    skill = q.get("skill") or {}
    sk_code = skill.get("code") if isinstance(skill, dict) else None
    sk_label = skill.get("label") if isinstance(skill, dict) else None
    sk_area = skill.get("area") if isinstance(skill, dict) else None
    # Pega texto das 5 alternativas
    alts = q.get("alternatives") or []
    alt_text = []
    for a in alts:
        if isinstance(a, dict) and a.get("text"):
            alt_text.append(f"{a.get('letter','?')}) {a.get('text','')[:200]}")
    return {
        "id": q.get("id"),
        "year": q.get("year"),
        "index": q.get("index"),
        "discipline_api": q.get("discipline"),
        "language": q.get("language"),
        "skill_code": sk_code,
        "skill_label": sk_label,
        "skill_area": sk_area,
        "context": (q.get("context") or "")[:1500],
        "alternativesIntroduction": (q.get("alternativesIntroduction") or "")[:400],
        "alternatives_text": " | ".join(alt_text)[:1200],
        "correctAlternative": q.get("correctAlternative"),
        "param_b": q.get("param_b"),
    }

rows = []
errors = 0
for line in SRC.read_text(encoding="utf-8").splitlines():
    if not line.strip(): continue
    q = json.loads(line)
    if q.get("_error"):
        errors += 1
        continue
    rows.append(compact(q))
print(f"loaded {len(rows)} (errors={errors})")

by_area = defaultdict(list)
for r in rows:
    api_area = (r.get("discipline_api") or "?").lower()
    if "humana" in api_area: a = "CH"
    elif "natureza" in api_area: a = "CN"
    elif "linguagens" in api_area: a = "LC"
    elif "matemat" in api_area: a = "MT"
    else: a = "?"
    by_area[a].append(r)

for a, lst in by_area.items():
    print(f"  {a}: {len(lst)}")

# Round-robin distribute
batches = [[] for _ in range(N_BATCHES)]
i = 0
for area in ("CH", "CN", "LC", "MT", "?"):
    for r in by_area.get(area, []):
        batches[i % N_BATCHES].append(r)
        i += 1

for n, batch in enumerate(batches, 1):
    out = OUT_DIR / f"phase6-batch-{n}.jsonl"
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in batch) + "\n", encoding="utf-8")
    print(f"  batch {n}: {len(batch)} → {out.name}")
