#!/usr/bin/env python3
"""
Aplica as classificações Fase 5 (Vision SEM constraint de área).
Diferente da Fase 4, esta TAMBÉM atualiza o campo `area` quando a Vision
identifica que a área da API estava errada.

Sobrescreve todos os ai-*/vision-* anteriores para as 310 questões.
"""
import json
import re
from collections import Counter
from pathlib import Path

VAULT = Path("/Users/home/Library/Mobile Documents/com~apple~CloudDocs/OBSIDIAN - QUESTÕES ENEM/Questões ENEM")
CLASS_DIR = Path.home() / "phase3-cache"

all_class = {}
for f in sorted(CLASS_DIR.glob("phase5-classified-*.jsonl")):
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        rec = json.loads(line)
        all_class[rec["id"]] = rec
print(f"loaded {len(all_class)} Phase 5 classifications")

note_by_id = {}
for p in (VAULT / "Questions").glob("*/*.md"):
    text = p.read_text(encoding="utf-8")
    m = re.search(r"^id:\s*(\d+)", text, re.MULTILINE)
    if m:
        note_by_id[int(m.group(1))] = p


def safe_slug(s):
    return re.sub(r"[^\w-]", "-", s.lower()
                  .replace("ç","c").replace("ã","a").replace("õ","o")
                  .replace("á","a").replace("é","e").replace("í","i")
                  .replace("ó","o").replace("ú","u"))


updated = 0
area_changes = 0
stats = Counter()
for qid, rec in all_class.items():
    path = note_by_id.get(qid)
    if not path:
        continue
    text = path.read_text(encoding="utf-8")
    disc = rec["disciplina"]
    area_new = rec.get("area_corrigida", rec.get("area_anterior", "?"))
    area_old = rec.get("area_anterior", "")
    conf = rec.get("confianca", "vision-medium")
    just = rec.get("justificativa", "")

    if area_new != area_old:
        area_changes += 1

    # Frontmatter
    text = re.sub(r"^area:.*$", f"area: {area_new}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina:.*$", f"disciplina: {disc}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_confianca:.*$", f"disciplina_confianca: {conf}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_candidatos:\s*\[.*?\]\n", "", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_fonte:.*$", "disciplina_fonte: phase5-vision-no-area-constraint", text, count=1, flags=re.MULTILINE)

    # Tags
    new_disc_tag = safe_slug(disc) if disc != "indeterminada" else "indeterminada"
    new_area_tag = area_new.lower()
    def fix_tags(m):
        items = [t.strip() for t in m.group(1).split(",")]
        items = [t for t in items if t not in (
            "ch","cn","lc","mt","precisa-ocr","classificado-ia","classificado-vision",
            "indeterminada","português","matemática","biologia","física","química",
            "geografia","historia","história","sociologia","filosofia","literatura",
            "arte","educacao-fisica","inglês","espanhol")]
        if new_area_tag not in items:
            items.append(new_area_tag)
        if new_disc_tag not in items:
            items.append(new_disc_tag)
        items.append("classificado-vision-livre")
        return f"tags: [{', '.join(items)}]"
    text = re.sub(r"^tags:\s*\[(.*?)\]", fix_tags, text, count=1, flags=re.MULTILINE)

    # Body line
    BODY = re.compile(
        r"\*\*Disciplina\*\*:\s*\*\*[^*]+\*\*(?:\s*—\s*sub-tema:\s*\*\*[^*]+\*\*)?\s*\(`confiança:\s*[^`]+`\)"
    )
    text = BODY.sub(f"**Disciplina**: **{disc}** (`confiança: {conf}`)", text, count=1)
    # Update "Área" link
    text = re.sub(r"\*\*Área\*\*:\s*\[\[discipline-[a-z]+\|[A-Z]+\]\]",
                  f"**Área**: [[discipline-{area_new.lower()}|{area_new}]]", text, count=1)

    # Replace any previous Phase classification section
    prev_section = re.compile(r"## Classificação Fase [34].*?(?=\n## |\Z)", re.DOTALL)
    new_section = (
        f"## Classificação Fase 5 (Vision sem constraint)\n\n"
        f"- **Disciplina atribuída**: **{disc}**\n"
        f"- **Área corrigida**: **{area_new}**" + (f" (anterior na API: {area_old})" if area_new != area_old else "") + "\n"
        f"- **Confiança**: `{conf}`\n"
        f"- **Justificativa**: {just}\n"
        f"- **Método**: Claude Vision via sub-agent paralelo, sem viés da área da API\n"
        f"- **Data**: 2026-05-17\n"
    )
    if prev_section.search(text):
        text = prev_section.sub(new_section + "\n", text, count=1)
    elif "## Classificação Fase 5" not in text:
        text = re.sub(r"(## Metadados)", new_section + "\n\\1", text, count=1)

    path.write_text(text, encoding="utf-8")
    updated += 1
    stats[disc] += 1
    stats[f"_conf:{conf}"] += 1
    stats[f"_area:{area_new}"] += 1

print(f"\n✓ updated {updated}/{len(all_class)}")
print(f"  área corrigida em {area_changes} questões ({area_changes/updated*100:.1f}%)")
print(f"\nBreakdown:")
for k, v in sorted(stats.items(), key=lambda x: -x[1])[:25]:
    print(f"  {k:30} {v}")
