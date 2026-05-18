#!/usr/bin/env python3
"""Calcula erro % por bucket da Fase 4 spot-check + 95% CI Wilson."""
import math, re, sys
from collections import defaultdict
from pathlib import Path

VAULT = Path("/Users/home/Library/Mobile Documents/com~apple~CloudDocs/OBSIDIAN - QUESTÕES ENEM/Questões ENEM")

files = sorted(VAULT.glob("Spot-Check Fase 4*.md"), reverse=True)
if not files:
    print("Nenhum Spot-Check Fase 4 *.md encontrado")
    sys.exit(1)
SRC = files[0]
print(f"→ lendo {SRC.name}")

text = SRC.read_text(encoding="utf-8")
QHEAD = re.compile(r"^### Q\d+ ENEM \d+ · id `(\d+)` · (\w+)$", re.MULTILINE)
BUCKET = re.compile(r"^## Bucket: `([\w-]+)`", re.MULTILINE)
APPROVED = re.compile(r"- \[x\]\s+✅", re.IGNORECASE)
WRONG = re.compile(r"- \[x\]\s+❌\s*Errado\s*[—-]+\s*deveria ser:\s*(.+?)(?:\n|$)", re.IGNORECASE)

blocks = re.split(r"(?=^### Q\d+ ENEM)", text, flags=re.MULTILINE)
current_bucket = "unknown"
results = []
for blk in blocks:
    mb = BUCKET.search(blk)
    if mb: current_bucket = mb.group(1)
    mh = QHEAD.search(blk)
    if not mh: continue
    qid = int(mh.group(1))
    area = mh.group(2)
    ok = bool(APPROVED.search(blk))
    mw = WRONG.search(blk)
    wrong = bool(mw)
    corr = mw.group(1).strip() if mw else ""
    status = ("pending" if not (ok or wrong) else
              "conflict" if (ok and wrong) else
              "approved" if ok else "wrong")
    results.append({"id": qid, "area": area, "bucket": current_bucket,
                    "status": status, "correction": corr})

print(f"  {len(results)} questões na amostra\n")

def wilson(p, n, z=1.96):
    if n == 0: return (0, 1)
    denom = 1 + z*z/n
    centre = p + z*z/(2*n)
    spread = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return ((centre-spread)/denom, (centre+spread)/denom)

by = defaultdict(list)
for r in results:
    by[r["bucket"]].append(r)

print(f"{'bucket':18} {'reviewed':>8} {'OK':>4} {'wrong':>6} {'pending':>8} {'error%':>7} {'95% CI':>15}")
print("-" * 85)
for b in ("vision-high", "vision-medium", "vision-low", "vision-impossivel"):
    bk = by.get(b, [])
    n = len(bk)
    pend = sum(1 for r in bk if r["status"] == "pending")
    rev = n - pend
    okc = sum(1 for r in bk if r["status"] == "approved")
    wc = sum(1 for r in bk if r["status"] == "wrong")
    if rev > 0:
        rate = wc / rev
        lo, hi = wilson(rate, rev)
        ci = f"[{lo*100:.0f}%-{hi*100:.0f}%]"
    else:
        rate, ci = float('nan'), "—"
    print(f"{b:18} {rev:>8} {okc:>4} {wc:>6} {pend:>8} {rate*100:>6.0f}% {ci:>15}")

wrongs = [r for r in results if r["status"] == "wrong"]
if wrongs:
    print(f"\n=== {len(wrongs)} questões erradas ===")
    for r in wrongs:
        print(f"  id {r['id']} ({r['area']} · {r['bucket']}) → {r['correction'] or '(sem correção)'}")
