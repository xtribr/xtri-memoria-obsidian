#!/usr/bin/env python3
"""
Gera uma amostra estratificada de questões classificadas para spot-check humano.

Estrato:
  - 23 ai-high   (todas — só 23 no total)
  - 30 ai-medium (estratificado por área: LC/CH/CN)
  - 30 ai-low    (estratificado por área)
  - 30 media     (Fase 2 skill mapping curado, estratificado por área)
Total: ~113 questões.

Saída: `Spot-Check 2026-05-17.md` na raiz do vault.
Cada questão renderiza a imagem (Obsidian abre external URLs) + checkboxes.
"""
import random
import re
import time
from collections import defaultdict
from pathlib import Path

VAULT = Path("/Users/home/Library/Mobile Documents/com~apple~CloudDocs/OBSIDIAN - QUESTÕES ENEM/Questões ENEM")
random.seed(42)  # reproducível

SAMPLE_PLAN = {
    "ai-high":  ("all", None),          # pega todas
    "ai-medium": ("stratified", 30),
    "ai-low":    ("stratified", 30),
    "media":     ("stratified", 30),
}


def parse_fm(text):
    fm = {}
    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            if in_fm:
                break
            in_fm = True
            continue
        if in_fm and ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


# Index all questions
print("→ indexando vault")
questions = []
for p in (VAULT / "Questions").glob("*/*.md"):
    text = p.read_text(encoding="utf-8")
    fm = parse_fm(text)
    if not fm.get("id"):
        continue
    questions.append({
        "id": int(fm["id"]),
        "year": int(fm.get("year") or 0),
        "index_q": int(fm.get("index") or 0),
        "area": fm.get("area", "?"),
        "disciplina": fm.get("disciplina", "?"),
        "sub_tema": fm.get("sub_tema") or "",
        "confianca": fm.get("disciplina_confianca", "?"),
        "skill": fm.get("skill") or "",
        "fonte": fm.get("disciplina_fonte") or "",
        "gabarito": fm.get("correctAlternative") or "?",
        "path": p,
        "text": text,
    })
print(f"  {len(questions)} questões indexadas")


def extract_image_url(text):
    m = re.search(r"!\[enunciado\]\((https?://[^)]+)\)", text)
    return m.group(1) if m else None


def extract_justificativa(text):
    m = re.search(r"\*\*Justificativa do classificador\*\*:\s*(.+)", text)
    return m.group(1).strip() if m else ""


# Stratified sample per confidence bucket
print("→ sampling")
sample = []
for conf, (mode, n) in SAMPLE_PLAN.items():
    pool = [q for q in questions if q["confianca"] == conf]
    if mode == "all":
        chosen = pool
    else:
        by_area = defaultdict(list)
        for q in pool:
            by_area[q["area"]].append(q)
        # roughly equal slots per area; remainder distributed
        areas = list(by_area.keys())
        per_area = n // len(areas) if areas else 0
        chosen = []
        for a in areas:
            ax = by_area[a]
            random.shuffle(ax)
            chosen.extend(ax[:per_area])
        # fill up to n with remaining random
        rest = [q for q in pool if q not in chosen]
        random.shuffle(rest)
        chosen.extend(rest[: max(0, n - len(chosen))])
    for q in chosen:
        sample.append({**q, "bucket": conf})
    print(f"  {conf:12} pool={len(pool):>4} sample={len(chosen)}")

print(f"\n  TOTAL na amostra: {len(sample)}")


# Generate the markdown
print("→ writing Spot-Check md")
out_path = VAULT / f"Spot-Check {time.strftime('%Y-%m-%d')}.md"
lines = [
    "---",
    "type: Note",
    f"created: {time.strftime('%Y-%m-%d')}",
    "---",
    f"# Spot-Check Fase 3 — {time.strftime('%Y-%m-%d')}",
    "",
    f"Amostra estratificada de **{len(sample)} questões** para validação humana da classificação automática.",
    "",
    "## Como revisar",
    "",
    "1. Para cada questão, abra a imagem (clique no link) e verifique se a disciplina atribuída faz sentido.",
    "2. Marque `[x]` em ✅ correto OU em ❌ e escreva a disciplina correta após `→`.",
    "3. Ao terminar, rode `_phase3_spotcheck_compute.py` (gera depois) para o erro % por bucket.",
    "",
    "## Distribuição da amostra",
    "",
    "| Bucket | N na amostra | População total |",
    "|---|---|---|",
]

total_by_bucket = defaultdict(int)
for q in questions:
    total_by_bucket[q["confianca"]] += 1
sample_by_bucket = defaultdict(int)
for q in sample:
    sample_by_bucket[q["bucket"]] += 1
for b in ("ai-high", "ai-medium", "ai-low", "media"):
    lines.append(f"| `{b}` | {sample_by_bucket[b]} | {total_by_bucket.get(b, 0)} |")

lines += [
    "",
    "---",
    "",
]

# Group sample by bucket for organized review
sample.sort(key=lambda x: (x["bucket"], x["area"], x["year"], x["index_q"]))
current_bucket = None
for q in sample:
    if q["bucket"] != current_bucket:
        current_bucket = q["bucket"]
        lines += [f"## Bucket: `{current_bucket}` ({sample_by_bucket[current_bucket]} questões)", ""]

    img_url = extract_image_url(q["text"])
    just = extract_justificativa(q["text"])
    note_link = f"[[{q['path'].stem}|ver nota completa]]"
    sub_part = f" · sub-tema: **{q['sub_tema']}**" if q["sub_tema"] else ""
    just_line = f"- **Justificativa**: {just}" if just else ""
    fonte_line = f"- **Fonte da classificação**: `{q['fonte']}`" if q["fonte"] else ""

    lines += [
        f"### Q{q['index_q']} ENEM {q['year']} · id `{q['id']}` · {q['area']}",
        "",
        f"- **Disciplina atribuída**: **{q['disciplina']}**{sub_part}",
        f"- **Confiança**: `{q['confianca']}`",
        f"- **Skill INEP**: `{q['skill']}`" if q["skill"] else "- **Skill INEP**: (não mapeada)",
        f"- **Gabarito oficial**: `{q['gabarito']}`",
        fonte_line,
        just_line,
        f"- {note_link}",
        "",
    ]
    if img_url:
        lines.append(f"![enunciado]({img_url})")
    else:
        lines.append("_(sem imagem na API — classificação baseada apenas em `skill_label`)_")
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

out_path.write_text("\n".join(lines), encoding="utf-8")
print(f"\n✓ {out_path}")
print(f"  {len(sample)} questões para revisar")
