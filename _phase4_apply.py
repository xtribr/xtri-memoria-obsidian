#!/usr/bin/env python3
"""
Fase 4 step 4: aplica as classificações Vision às notas .md.

Sobrescreve a Fase 3 (que tinha alta taxa de erro) com a Vision real, para as
~310 questões que tinham imagem. As 786 sem imagem continuam com classificação
Fase 3 (em sua maioria 'ai-impossivel'/'ai-low').
"""
import json
import re
from collections import Counter
from pathlib import Path

VAULT = Path("/Users/home/Library/Mobile Documents/com~apple~CloudDocs/OBSIDIAN - QUESTÕES ENEM/Questões ENEM")
CLASS_DIR = Path.home() / "phase3-cache"

# Load Phase 4 classifications
all_class = {}
for f in sorted(CLASS_DIR.glob("phase4-classified-*.jsonl")):
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        rec = json.loads(line)
        all_class[rec["id"]] = rec
print(f"loaded {len(all_class)} Phase 4 classifications")

# Index notes by id
note_by_id = {}
for p in (VAULT / "Questions").glob("*/*.md"):
    text = p.read_text(encoding="utf-8")
    m = re.search(r"^id:\s*(\d+)", text, re.MULTILINE)
    if m:
        note_by_id[int(m.group(1))] = p
print(f"{len(note_by_id)} notes indexed")


def safe_slug(s):
    return re.sub(r"[^\w-]", "-", s.lower()
                  .replace("ç", "c").replace("ã", "a").replace("õ", "o")
                  .replace("á", "a").replace("é", "e").replace("í", "i")
                  .replace("ó", "o").replace("ú", "u"))


updated = 0
skipped = 0
stats = Counter()
for qid, rec in all_class.items():
    path = note_by_id.get(qid)
    if not path:
        skipped += 1
        continue
    text = path.read_text(encoding="utf-8")
    disc = rec["disciplina"]
    conf = rec.get("confianca", "vision-medium")
    just = rec.get("justificativa", "")

    # Update frontmatter
    text = re.sub(r"^disciplina:.*$", f"disciplina: {disc}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_confianca:.*$", f"disciplina_confianca: {conf}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_candidatos:\s*\[.*?\]\n", "", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_fonte:.*$", "disciplina_fonte: phase4-vision-claude", text, count=1, flags=re.MULTILINE)

    # Update tags
    new_tag = safe_slug(disc) if disc != "indeterminada" else "indeterminada"
    def fix_tags(m):
        items = [t.strip() for t in m.group(1).split(",")]
        items = [t for t in items if t not in ("precisa-ocr", "classificado-ia", "indeterminada")]
        if new_tag and new_tag not in items:
            items.append(new_tag)
        items.append("classificado-vision")
        return f"tags: [{', '.join(items)}]"
    text = re.sub(r"^tags:\s*\[(.*?)\]", fix_tags, text, count=1, flags=re.MULTILINE)

    # Body line update
    BODY = re.compile(
        r"\*\*Disciplina\*\*:\s*\*\*[^*]+\*\*(?:\s*—\s*sub-tema:\s*\*\*[^*]+\*\*)?\s*\(`confiança:\s*[^`]+`\)"
    )
    new_body = f"**Disciplina**: **{disc}** (`confiança: {conf}`)"
    text = BODY.sub(new_body, text, count=1)

    # Replace Phase 3 audit section with Phase 4
    audit_phase3 = re.compile(r"## Classificação Fase 3 \(IA\).*?(?=\n##|\Z)", re.DOTALL)
    audit_phase4 = (
        f"## Classificação Fase 4 (Vision)\n\n"
        f"- **Disciplina atribuída**: **{disc}**\n"
        f"- **Confiança**: `{conf}`\n"
        f"- **Justificativa do classificador**: {just}\n"
        f"- **Método**: Claude Vision via sub-agent paralelo (imagem lida diretamente)\n"
        f"- **Data**: 2026-05-17\n"
    )
    if audit_phase3.search(text):
        text = audit_phase3.sub(audit_phase4 + "\n", text, count=1)
    elif "## Classificação Fase 4" not in text:
        text = re.sub(r"(## Metadados)", audit_phase4 + "\n\\1", text, count=1)

    path.write_text(text, encoding="utf-8")
    updated += 1
    stats[disc] += 1
    stats[f"_conf:{conf}"] += 1

print(f"\n✓ updated {updated}/{len(all_class)} (skipped {skipped})")
print(f"\nFinal:")
for k, v in sorted(stats.items(), key=lambda x: -x[1]):
    print(f"  {k:30} {v}")
