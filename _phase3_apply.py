#!/usr/bin/env python3
"""
Phase 3 step 4: merge sub-agent classifications back into the question .md files.

Reads: /tmp/phase3-classified-*.jsonl  (one per sub-agent)
Each line: {"id": int, "disciplina": str, "confianca": "ai-high|ai-medium|ai-low",
            "justificativa": str}

For each classified question, updates the existing .md frontmatter:
  - disciplina: indeterminada                 → <new disciplina>
  - disciplina_confianca: indeterminada       → <new confianca>  (ai-*)
  - disciplina_candidatos: [...]              → removed
  - disciplina_fonte: ...                     → "phase3-ocr-claude"
  - tags: + classifies tags (replace 'precisa-ocr' with 'classificado-ia')
Adds an AI Audit section to the body with justificativa.
"""
import json
import re
from collections import Counter
from pathlib import Path

VAULT = Path("/Users/home/Library/Mobile Documents/com~apple~CloudDocs/OBSIDIAN - QUESTÕES ENEM/Questões ENEM")
CLASS_DIR = Path.home() / "phase3-cache"

# Load all classifications
all_class = {}
for f in sorted(CLASS_DIR.glob("phase3-classified-*.jsonl")):
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        all_class[rec["id"]] = rec
print(f"loaded {len(all_class)} classifications")

# Index questions by id
print("indexing vault notes...")
note_by_id: dict[int, Path] = {}
for p in (VAULT / "Questions").glob("*/*.md"):
    text = p.read_text(encoding="utf-8")
    m = re.search(r"^id:\s*(\d+)", text, re.MULTILINE)
    if m:
        note_by_id[int(m.group(1))] = p
print(f"  {len(note_by_id)} notes indexed")

# Helpers
def safe_slug(s: str) -> str:
    return re.sub(r"[^\w-]", "-", s.lower().replace("ç", "c").replace("ã", "a")
                  .replace("õ", "o").replace("á", "a").replace("é", "e")
                  .replace("í", "i").replace("ó", "o").replace("ú", "u"))

# Apply
updated = 0
skipped = 0
counts = Counter()
for qid, rec in all_class.items():
    path = note_by_id.get(qid)
    if not path:
        skipped += 1
        continue
    text = path.read_text(encoding="utf-8")
    disc = rec["disciplina"]
    conf = rec.get("confianca", "ai-medium")
    just = rec.get("justificativa", "")

    # Replace frontmatter fields
    text = re.sub(r"^disciplina: indeterminada$", f"disciplina: {disc}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_confianca: indeterminada$", f"disciplina_confianca: {conf}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_candidatos: \[.*?\]\n", "", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_fonte: .*$", "disciplina_fonte: phase3-ocr-claude", text, count=1, flags=re.MULTILINE)

    # Update tags
    new_tag = safe_slug(disc)
    def fix_tags(m):
        items = [t.strip() for t in m.group(1).split(",")]
        items = [t for t in items if t != "precisa-ocr"]
        if new_tag not in items:
            items.append(new_tag)
        items.append("classificado-ia")
        return f"tags: [{', '.join(items)}]"
    text = re.sub(r"^tags: \[(.*?)\]", fix_tags, text, count=1, flags=re.MULTILINE)

    # Body update — replace the ⚠️ warning if present, else append AI audit section
    warning_pat = r"> ⚠️ Disciplina não determinável.*\n"
    audit = (
        f"\n## Classificação Fase 3 (IA)\n\n"
        f"- **Disciplina atribuída**: **{disc}**\n"
        f"- **Confiança**: `{conf}`\n"
        f"- **Justificativa do classificador**: {just}\n"
        f"- **Método**: OCR (Tesseract) + Claude judgment via sub-agent paralelo\n"
        f"- **Data**: 2026-05-17\n"
    )
    if re.search(warning_pat, text):
        text = re.sub(warning_pat, "", text, count=1)

    # Append audit section before metadata if not already there
    if "## Classificação Fase 3 (IA)" not in text:
        text = re.sub(r"(## Metadados)", audit + "\n\\1", text, count=1)

    path.write_text(text, encoding="utf-8")
    updated += 1
    counts[disc] += 1
    counts[f"_conf:{conf}"] += 1

print(f"\n✓ updated {updated}/{len(all_class)} (skipped {skipped})")
print("\n=== Distribuição final ===")
for k, v in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {k:30} {v}")
