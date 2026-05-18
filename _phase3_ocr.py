#!/usr/bin/env python3
"""
Phase 3 step 1: download + OCR every indeterminate question.

Output: /tmp/phase3-ocr.jsonl  (one line per question)
Each line:
  {"id": int, "year": int, "area": "CH|CN|LC", "skill_code": str|null,
   "skill_label": str|null, "candidates": [...], "image_url": str,
   "ocr_text": str, "ocr_chars": int, "md_path": str}
"""
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

VAULT = Path("/Users/home/Library/Mobile Documents/com~apple~CloudDocs/OBSIDIAN - QUESTÕES ENEM/Questões ENEM")
# macOS SIP blocks tesseract from reading /tmp — use $HOME/phase3-cache
CACHE = Path.home() / "phase3-cache" / "images"
CACHE.mkdir(parents=True, exist_ok=True)
OUT = Path.home() / "phase3-cache" / "phase3-ocr.jsonl"
BASE = "https://api.questoes.xtri.online/api"

# ---------------------------------------------------------------------------
# 1. Build the indeterminate-question list from the vault notes
# ---------------------------------------------------------------------------
print("→ scanning vault for indeterminadas")
indeterminadas = []
for path in sorted((VAULT / "Questions").glob("*/*.md")):
    text = path.read_text(encoding="utf-8")
    if "disciplina_confianca: indeterminada" not in text:
        continue
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
    if fm.get("id"):
        indeterminadas.append({
            "id": int(fm["id"]),
            "year": int(fm.get("year") or 0),
            "area": fm.get("area", "?"),
            "skill_code": fm.get("skill") or None,
            "candidates": fm.get("disciplina_candidatos", "").strip("[]").split(", "),
            "md_path": str(path),
        })

print(f"  {len(indeterminadas)} indeterminadas no vault")

# ---------------------------------------------------------------------------
# 2. Enrich with image URL + skill label from API
# ---------------------------------------------------------------------------
print("→ fetching skill labels")
skills_raw = json.load(urllib.request.urlopen(f"{BASE}/skills/"))
skill_lookup = {}
for s in skills_raw:
    skill_lookup[(s["area"], s["code"])] = s["label"]

print("→ fetching image URLs (paginated)")
url_lookup = {}
page = 1
while True:
    payload = json.load(urllib.request.urlopen(f"{BASE}/questions/?page={page}"))
    for q in payload.get("results", []):
        url_lookup[q["id"]] = q.get("image")
    if not payload.get("next"):
        break
    page += 1
print(f"  {len(url_lookup)} URLs catalogadas")

for q in indeterminadas:
    q["image_url"] = url_lookup.get(q["id"])
    q["skill_label"] = skill_lookup.get((q["area"], q["skill_code"])) if q["skill_code"] else None

with_url = sum(1 for q in indeterminadas if q["image_url"])
print(f"  {with_url}/{len(indeterminadas)} com imagem")

# ---------------------------------------------------------------------------
# 3. Parallel download + OCR
# ---------------------------------------------------------------------------
def safe_filename(url: str) -> str:
    return re.sub(r"[^\w.-]", "_", url.split("/")[-1])[:120]

def download(q):
    if not q["image_url"]:
        return None
    fn = CACHE / f"{q['id']}_{safe_filename(q['image_url'])}"
    if fn.exists() and fn.stat().st_size > 0:
        return fn
    try:
        req = urllib.request.Request(q["image_url"], headers={"User-Agent": "phase3/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r, open(fn, "wb") as out:
            out.write(r.read())
        return fn
    except Exception as e:
        print(f"  ✗ {q['id']}: download {e}", file=sys.stderr)
        return None

def ocr(path):
    try:
        # binary subprocess to avoid utf-8 decode failures on stderr blobs
        result = subprocess.run(
            ["tesseract", str(path), "-", "-l", "por+eng+spa", "--psm", "6"],
            capture_output=True, timeout=60,
        )
        return result.stdout.decode("utf-8", errors="replace").strip()
    except Exception as e:
        return f"[OCR_ERROR: {e}]"

def process(q: dict) -> dict:
    img = download(q)
    text = ocr(img) if img else "[NO_IMAGE]"
    q["ocr_text"] = text
    q["ocr_chars"] = len(text)
    return q

print("→ downloading + OCR (parallel, 8 workers)")
start = time.time()
done = 0
with OUT.open("w", encoding="utf-8") as f, ThreadPoolExecutor(max_workers=8) as pool:
    futures = [pool.submit(process, q) for q in indeterminadas]
    for fut in as_completed(futures):
        q = fut.result()
        f.write(json.dumps(q, ensure_ascii=False) + "\n")
        done += 1
        if done % 50 == 0:
            elapsed = time.time() - start
            rate = done / elapsed if elapsed else 0
            eta = (len(indeterminadas) - done) / rate if rate else 0
            print(f"  {done:>4}/{len(indeterminadas)} · {elapsed:.0f}s · {rate:.1f}/s · ETA {eta:.0f}s", flush=True)

print(f"\n✓ done · {OUT}")
print(f"  cache: {CACHE} ({sum(p.stat().st_size for p in CACHE.iterdir())//1024//1024}MB)")
