#!/usr/bin/env python3
"""
Fase 6 step 1: baixa o detail completo das 3.123 questões via /api/questions/{id}/.

Cada detail retorna:
  - context, contextLocal, alternativesIntroduction
  - alternatives[] (5, cada com letter/text/image/isCorrect)
  - skill (dict), discipline, language
  - param_a, param_b, param_c (TRI 3PL completo)
  - files, in_item_aban

Output: ~/phase6-cache/questions-detail.jsonl
"""
import json
import sys
import time
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

CACHE = Path.home() / "phase6-cache"
CACHE.mkdir(exist_ok=True)
OUT = CACHE / "questions-detail.jsonl"
BASE = "https://api.questoes.xtri.online/api"


def list_all_ids():
    """Pega lista de IDs da paginação básica."""
    ids = []
    page = 1
    while True:
        r = urllib.request.urlopen(f"{BASE}/questions/?page={page}", timeout=20)
        d = json.load(r)
        ids.extend(q["id"] for q in d.get("results", []))
        if not d.get("next"):
            break
        page += 1
    return ids


def fetch_detail(qid, retries=3):
    for attempt in range(retries):
        try:
            r = urllib.request.urlopen(f"{BASE}/questions/{qid}/", timeout=15)
            return json.load(r)
        except Exception as e:
            if attempt == retries - 1:
                return {"id": qid, "_error": str(e)}
            time.sleep(1)


print("→ listando IDs")
ids = list_all_ids()
print(f"  {len(ids)} IDs")

print(f"→ baixando detail (parallel, 12 workers)")
start = time.time()
done = 0
errors = 0
with OUT.open("w", encoding="utf-8") as f, ThreadPoolExecutor(max_workers=12) as pool:
    futures = [pool.submit(fetch_detail, qid) for qid in ids]
    for fut in as_completed(futures):
        d = fut.result()
        if d.get("_error"):
            errors += 1
        f.write(json.dumps(d, ensure_ascii=False) + "\n")
        done += 1
        if done % 200 == 0:
            elapsed = time.time() - start
            rate = done / elapsed if elapsed else 0
            eta = (len(ids) - done) / rate if rate else 0
            print(f"  {done:>4}/{len(ids)} · {elapsed:.0f}s · {rate:.1f}/s · ETA {eta:.0f}s · errors={errors}", flush=True)

print(f"\n✓ {OUT}")
print(f"  done={done} errors={errors} time={time.time()-start:.0f}s")
