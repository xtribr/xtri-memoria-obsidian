#!/usr/bin/env python3
"""
Lê `Spot-Check YYYY-MM-DD.md` após revisão humana e calcula:
  - taxa de erro por bucket (ai-high, ai-medium, ai-low, media)
  - 95% CI de Wilson para cada taxa
  - lista de questões marcadas erradas + disciplina corrigida sugerida
"""
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

VAULT = Path("/Users/home/Library/Mobile Documents/com~apple~CloudDocs/OBSIDIAN - QUESTÕES ENEM/Questões ENEM")

# Find latest spot-check file
files = sorted(VAULT.glob("Spot-Check *.md"), reverse=True)
if not files:
    print("Nenhum Spot-Check *.md encontrado")
    sys.exit(1)
SRC = files[0]
print(f"→ lendo {SRC.name}")

text = SRC.read_text(encoding="utf-8")

# Parse blocks
# Each Q-block starts with "### Q{idx} ENEM {year} · id `{id}` · {area}"
# Bucket header: "## Bucket: `{bucket}` (...)"
QHEAD = re.compile(r"^### Q\d+ ENEM \d+ · id `(\d+)` · (\w+)$", re.MULTILINE)
BUCKET = re.compile(r"^## Bucket: `([\w-]+)`", re.MULTILINE)
APPROVED = re.compile(r"- \[x\]\s+✅", re.IGNORECASE)
WRONG = re.compile(r"- \[x\]\s+❌\s*Errado\s*[—-]+\s*deveria ser:\s*(.+?)(?:\n|$)", re.IGNORECASE)

# Split into per-question blocks
blocks = re.split(r"(?=^### Q\d+ ENEM)", text, flags=re.MULTILINE)
# Track current bucket as we go through (bucket header appears before its questions)
current_bucket = "unknown"
results = []
for blk in blocks:
    m_bucket = BUCKET.search(blk)
    if m_bucket:
        current_bucket = m_bucket.group(1)
    m_head = QHEAD.search(blk)
    if not m_head:
        continue
    qid = int(m_head.group(1))
    area = m_head.group(2)
    has_approved = bool(APPROVED.search(blk))
    m_wrong = WRONG.search(blk)
    has_wrong = bool(m_wrong)
    correction = m_wrong.group(1).strip() if m_wrong else ""
    if not (has_approved or has_wrong):
        status = "pending"
    elif has_approved and has_wrong:
        status = "conflict"
    elif has_approved:
        status = "approved"
    else:
        status = "wrong"
    results.append({
        "id": qid, "area": area, "bucket": current_bucket,
        "status": status, "correction": correction,
    })

print(f"  {len(results)} questões na amostra")

# Wilson 95% CI
def wilson_ci(p, n, z=1.96):
    if n == 0:
        return (0, 1)
    denom = 1 + z*z/n
    centre = p + z*z/(2*n)
    spread = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return ((centre - spread)/denom, (centre + spread)/denom)

by_bucket = defaultdict(list)
for r in results:
    by_bucket[r["bucket"]].append(r)

print("\n=== Resultado por bucket ===")
print(f"{'bucket':12} {'reviewed':>8} {'approved':>9} {'wrong':>6} {'pending':>8} {'error%':>7} {'95% CI':>16}")
print("-" * 80)
for b in ("ai-high", "ai-medium", "ai-low", "media"):
    bk = by_bucket.get(b, [])
    n = len(bk)
    pend = sum(1 for r in bk if r["status"] == "pending")
    rev = n - pend
    approved = sum(1 for r in bk if r["status"] == "approved")
    wrong = sum(1 for r in bk if r["status"] == "wrong")
    if rev > 0:
        rate = wrong / rev
        lo, hi = wilson_ci(rate, rev)
        ci = f"[{lo*100:.0f}%–{hi*100:.0f}%]"
    else:
        rate, ci = float('nan'), "—"
    print(f"{b:12} {rev:>8} {approved:>9} {wrong:>6} {pend:>8} {rate*100:>6.0f}% {ci:>16}")

# List wrong items
wrong_items = [r for r in results if r["status"] == "wrong"]
if wrong_items:
    print(f"\n=== {len(wrong_items)} questões marcadas erradas ===")
    for r in wrong_items:
        print(f"  id {r['id']} ({r['area']} · {r['bucket']}) → correção sugerida: {r['correction']}")
else:
    print("\n(nenhuma questão marcada errada)")

conflicts = [r for r in results if r["status"] == "conflict"]
if conflicts:
    print(f"\n⚠️  {len(conflicts)} questões com checkboxes conflitantes (ambos ✅ e ❌ marcados):")
    for r in conflicts:
        print(f"  id {r['id']}")
