#!/usr/bin/env python3
"""
Cosmetic fix: the apply step updated frontmatter but the body still has the
old `**Disciplina**: **indeterminada** (`confiança: indeterminada`)` line.

This script:
 1. Reads each question .md
 2. Parses frontmatter for current disciplina + confianca
 3. Rewrites the matching body line + removes the warning blockquote (if leftover)
 4. Adds sub-tema in body when present in frontmatter (MT)
Idempotent.
"""
import re
from pathlib import Path
from collections import Counter

VAULT = Path("/Users/home/Library/Mobile Documents/com~apple~CloudDocs/OBSIDIAN - QUESTÕES ENEM/Questões ENEM")

# Pattern to match the descriptive Disciplina line in the body
BODY_LINE = re.compile(
    r"\*\*Disciplina\*\*:\s*\*\*[^*]+\*\*(?:\s*—\s*sub-tema:\s*\*\*[^*]+\*\*)?\s*\(`confiança:\s*[^`]+`\)"
)
WARNING_LINE = re.compile(
    r"^> ⚠️ Disciplina não determinável.*?\n", re.MULTILINE
)

def parse_frontmatter(text):
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

stats = Counter()
fixed = 0
unchanged = 0
errors = []

for p in (VAULT / "Questions").glob("*/*.md"):
    text = p.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    disc = fm.get("disciplina", "?")
    conf = fm.get("disciplina_confianca", "?")
    sub = fm.get("sub_tema")

    sub_part = f" — sub-tema: **{sub}**" if sub else ""
    new_line = f"**Disciplina**: **{disc}**{sub_part} (`confiança: {conf}`)"

    new_text, n_repl = BODY_LINE.subn(new_line, text, count=1)

    # Also remove orphan warning blockquote if disc is no longer indeterminada
    if disc != "indeterminada" and WARNING_LINE.search(new_text):
        new_text = WARNING_LINE.sub("", new_text, count=1)
        # also strip the empty line after if it exists
        new_text = re.sub(r"\n\n\n+", "\n\n", new_text)

    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        fixed += 1
        stats[f"conf:{conf}"] += 1
    else:
        unchanged += 1

print(f"✓ fixed: {fixed}")
print(f"  unchanged: {unchanged}")
print(f"  errors: {len(errors)}")
print(f"\nBreakdown of fixed by confianca:")
for k, v in sorted(stats.items(), key=lambda x: -x[1]):
    print(f"  {k:25} {v}")
