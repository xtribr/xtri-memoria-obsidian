#!/usr/bin/env python3
"""
Phase 3 step 2: split /tmp/phase3-ocr.jsonl into 7 batches for parallel sub-agents.

Outputs:
  /tmp/phase3-batch-1.jsonl ... phase3-batch-7.jsonl

Stratification: each batch gets a proportional mix of LC/CH/CN so that
sub-agents see a similar workload distribution.
"""
import json
from collections import defaultdict
from pathlib import Path

SRC = Path.home() / "phase3-cache" / "phase3-ocr.jsonl"
N_BATCHES = 5

rows = [json.loads(l) for l in SRC.read_text(encoding="utf-8").splitlines() if l.strip()]
print(f"loaded {len(rows)} indeterminadas")

# Bucket by area for stratification
by_area = defaultdict(list)
for r in rows:
    by_area[r["area"]].append(r)
for a, lst in by_area.items():
    print(f"  {a}: {len(lst)}")

# Round-robin distribute
batches = [[] for _ in range(N_BATCHES)]
i = 0
for area in ("CH", "CN", "LC"):  # consistent ordering
    for r in by_area.get(area, []):
        batches[i % N_BATCHES].append(r)
        i += 1

out_dir = Path.home() / "phase3-cache"
out_dir.mkdir(exist_ok=True)
for n, batch in enumerate(batches, 1):
    out = out_dir / f"phase3-batch-{n}.jsonl"
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in batch) + "\n", encoding="utf-8")
    print(f"  batch {n}: {len(batch)} questões → {out}")
