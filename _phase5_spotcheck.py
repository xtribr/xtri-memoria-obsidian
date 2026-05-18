#!/usr/bin/env python3
"""
Spot-check Fase 5 (Vision sem constraint de área).
Sample estratificado:
  - 25 vision-high       (de 267 — 9%)
  - 20 vision-medium     (de 37 — 54%)
  - 5  vision-low        (todas)
  - 1  vision-impossivel (todas)
Total: 51.

Estratifica também por ÁREA pra garantir cobertura das 4 áreas no vision-high.
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
    "vision-medium":    20,
    "vision-low":       5,
    "vision-impossivel": 1,
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


def extract_just_phase5(text):
    # Phase 5 audit section
    sec = re.search(r"## Classificação Fase 5 \(Vision sem constraint\).*?(?=\n## |\Z)", text, re.DOTALL)
    if not sec:
        return ""
    m = re.search(r"\*\*Justificativa\*\*:\s*(.+)", sec.group(0))
    return m.group(1).strip() if m else ""


def extract_area_change(text):
    m = re.search(r"\*\*Área corrigida\*\*:\s*\*\*(\w+)\*\*(?:\s*\(anterior na API:\s*(\w+)\))?", text)
    if m:
        new_area = m.group(1)
        old_area = m.group(2)
        if old_area and old_area != new_area:
            return f"{old_area} → {new_area}"
    return ""


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
        "area_change": extract_area_change(text),
        "path": p,
        "text": text,
    })
print(f"  {len(questions)} questões indexadas")

sample = []
for conf, n in SAMPLE.items():
    pool = [q for q in questions if q["confianca"] == conf]
    if conf == "vision-high":
        # estratifica por área
        by_area = defaultdict(list)
        for q in pool:
            by_area[q["area"]].append(q)
        chosen = []
        per_area = max(1, n // len(by_area))
        for a in by_area:
            random.shuffle(by_area[a])
            chosen.extend(by_area[a][:per_area])
        # complete até n
        rest = [q for q in pool if q not in chosen]
        random.shuffle(rest)
        chosen.extend(rest[: max(0, n - len(chosen))])
    else:
        random.shuffle(pool)
        chosen = pool[:n]
    for q in chosen:
        sample.append({**q, "bucket": conf})
    print(f"  {conf:18} pool={len(pool):>4} sample={len(chosen)}")
print(f"\n  TOTAL: {len(sample)}")

out = VAULT / f"Spot-Check Fase 5 — {time.strftime('%Y-%m-%d')}.md"
lines = [
    "---", "type: Note", f"created: {time.strftime('%Y-%m-%d')}", "---",
    f"# Spot-Check Fase 5 (Vision sem constraint) — {time.strftime('%Y-%m-%d')}",
    "",
    f"Amostra estratificada de **{len(sample)} questões** classificadas pela Fase 5 — Claude Vision com liberdade total de escolher entre as 14 disciplinas (sem viés da área da API).",
    "",
    "## Como revisar",
    "",
    "Para cada questão: abra a imagem, confirme se disciplina + área fazem sentido. Marque `[x]` em ✅ ou ❌.",
    "Ao terminar, rode `_phase5_spotcheck_compute.py` para o erro % por bucket.",
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

lines += ["", "**Foco**: validar se a Fase 5 (vision livre) baixou a taxa de erro do vision-high de 4% para perto de 0%, e do vision-medium de 42% para algo aceitável.", "", "---", ""]

sample.sort(key=lambda x: (x["bucket"], x["area"], x["year"], x["index_q"]))
current = None
for q in sample:
    if q["bucket"] != current:
        current = q["bucket"]
        lines += [f"## Bucket: `{current}`", ""]
    img = extract_image_url(q["text"])
    just = extract_just_phase5(q["text"])
    area_change_note = f" ⚠️ **área corrigida**: {q['area_change']}" if q["area_change"] else ""
    lines += [
        f"### Q{q['index_q']} ENEM {q['year']} · id `{q['id']}` · {q['area']}{area_change_note}",
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
