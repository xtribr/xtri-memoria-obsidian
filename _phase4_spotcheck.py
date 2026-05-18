#!/usr/bin/env python3
"""
Spot-check da Fase 4 (Vision). Sample estratificado:
  - 25 vision-high   (de 261 — 10%)
  - 25 vision-medium (de 36 — 70%)
  - 10 vision-low    (todas)
  - 3  vision-impossivel (todas)
Total: ~63 questões.
"""
import random
import re
import time
from collections import defaultdict
from pathlib import Path

VAULT = Path("/Users/home/Library/Mobile Documents/com~apple~CloudDocs/OBSIDIAN - QUESTÕES ENEM/Questões ENEM")
random.seed(42)

SAMPLE = {
    "vision-high":      25,
    "vision-medium":    25,
    "vision-low":       10,
    "vision-impossivel": 3,
}


def parse_fm(text):
    fm = {}
    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            if in_fm: break
            in_fm = True
            continue
        if in_fm and ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def extract_image_url(text):
    m = re.search(r"!\[enunciado\]\((https?://[^)]+)\)", text)
    return m.group(1) if m else None


def extract_just(text):
    m = re.search(r"\*\*Justificativa do classificador\*\*:\s*(.+)", text)
    return m.group(1).strip() if m else ""


questions = []
for p in (VAULT / "Questions").glob("*/*.md"):
    text = p.read_text(encoding="utf-8")
    fm = parse_fm(text)
    if not fm.get("id"): continue
    questions.append({
        "id": int(fm["id"]),
        "year": int(fm.get("year") or 0),
        "index_q": int(fm.get("index") or 0),
        "area": fm.get("area", "?"),
        "disciplina": fm.get("disciplina", "?"),
        "confianca": fm.get("disciplina_confianca", "?"),
        "skill": fm.get("skill") or "",
        "gabarito": fm.get("correctAlternative") or "?",
        "path": p,
        "text": text,
    })
print(f"  {len(questions)} questões indexadas")

sample = []
for conf, n in SAMPLE.items():
    pool = [q for q in questions if q["confianca"] == conf]
    random.shuffle(pool)
    chosen = pool[:n]
    for q in chosen:
        sample.append({**q, "bucket": conf})
    print(f"  {conf:18} pool={len(pool):>4} sample={len(chosen)}")
print(f"\n  TOTAL: {len(sample)}")

# Generate markdown
out = VAULT / f"Spot-Check Fase 4 — {time.strftime('%Y-%m-%d')}.md"
lines = [
    "---", "type: Note", f"created: {time.strftime('%Y-%m-%d')}", "---",
    f"# Spot-Check Fase 4 (Vision) — {time.strftime('%Y-%m-%d')}",
    "",
    f"Amostra estratificada de **{len(sample)} questões** classificadas pela Fase 4 (Claude Vision real).",
    "",
    "## Como revisar",
    "",
    "Para cada questão: abra a imagem, confirme se a disciplina atribuída faz sentido, marque `[x]` em ✅ ou ❌.",
    "Ao terminar, rode `_phase4_spotcheck_compute.py` para o erro % por bucket.",
    "",
    "## Distribuição",
    "",
    "| Bucket | N amostra | Pop total |",
    "|---|---|---|",
]
totals = defaultdict(int)
for q in questions:
    totals[q["confianca"]] += 1
sample_by = defaultdict(int)
for q in sample:
    sample_by[q["bucket"]] += 1
for b in SAMPLE:
    lines.append(f"| `{b}` | {sample_by[b]} | {totals.get(b, 0)} |")

lines += ["", "---", ""]

sample.sort(key=lambda x: (x["bucket"], x["area"], x["year"], x["index_q"]))
current = None
for q in sample:
    if q["bucket"] != current:
        current = q["bucket"]
        lines += [f"## Bucket: `{current}`", ""]
    img = extract_image_url(q["text"])
    just = extract_just(q["text"])
    lines += [
        f"### Q{q['index_q']} ENEM {q['year']} · id `{q['id']}` · {q['area']}",
        "",
        f"- **Disciplina**: **{q['disciplina']}**",
        f"- **Confiança**: `{q['confianca']}`",
        f"- **Skill INEP**: `{q['skill']}`" if q["skill"] else "- **Skill INEP**: (não mapeada)",
        f"- **Gabarito**: `{q['gabarito']}`",
        f"- **Justificativa do classificador**: {just}" if just else "",
        f"- [[{q['path'].stem}|ver nota completa]]",
        "",
    ]
    if img:
        lines.append(f"![enunciado]({img})")
    else:
        lines.append("_(sem imagem na API)_")
    lines += [
        "",
        "**Avaliação:**",
        "",
        "- [ ] ✅ Correto",
        "- [ ] ❌ Errado — deveria ser: ___________________",
        "",
        "---",
        "",
    ]

out.write_text("\n".join(lines), encoding="utf-8")
print(f"\n✓ {out.name}")
