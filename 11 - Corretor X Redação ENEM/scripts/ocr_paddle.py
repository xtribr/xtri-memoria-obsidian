#!/usr/bin/env python3
"""OCR local com PaddleOCR para imagens de redação.

Saída: JSON em stdout, sem texto extra. O XTRI-RED usa este script como motor
preferencial de OCR e cai para Apple Vision se ele falhar.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sys
import time
from pathlib import Path
from statistics import mean
from typing import Any


BOILERPLATE_PATTERNS = [
    r"^folha\s+de\s+reda[cç][aã]o$",
    r"^verifique\s+o\s+seu\s+cpf",
    r"^n[º°]?\s*de\s*inscri[cç][aã]o",
    r"^transcreva\s+a\s+sua\s+reda",
    r"^cpf[:\s]",
    r"^data\s+de\s+nascimento",
    r"^nome\s+completo",
    r"^nome$",
    r"^propostas?$",
    r"^de\s+reda[cç][aã]o$",
    r"^@?predacao$",
]


def normalize_for_filter(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def should_drop_line(line: str) -> bool:
    normalized = normalize_for_filter(line)
    if not normalized:
        return True
    if normalized.isdigit() and len(normalized) <= 2:
        return True
    if re.fullmatch(r"[0-9.\-_/ ]{3,}", normalized):
        return True
    return any(re.search(pattern, normalized) for pattern in BOILERPLATE_PATTERNS)


def clean_lines(lines: list[str]) -> list[str]:
    cleaned: list[str] = []
    for line in lines:
        text = line.strip()
        if should_drop_line(text):
            continue
        cleaned.append(text)
    return cleaned


def extract_result_data(result: Any) -> tuple[list[str], list[float]]:
    texts: list[str] = []
    scores: list[float] = []

    for item in result:
        data = getattr(item, "json", None)
        if isinstance(data, dict) and "res" in data:
            data = data["res"]
        elif not isinstance(data, dict):
            data = item if isinstance(item, dict) else {}

        item_texts = data.get("rec_texts", []) if isinstance(data, dict) else []
        item_scores = data.get("rec_scores", []) if isinstance(data, dict) else []

        texts.extend(str(text).strip() for text in item_texts if str(text).strip())
        for score in item_scores:
            try:
                scores.append(float(score))
            except (TypeError, ValueError):
                continue

    return texts, scores


def run_paddle_ocr(image_path: Path, lang: str) -> dict[str, Any]:
    os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

    from paddleocr import PaddleOCR

    started_at = time.monotonic()
    ocr = PaddleOCR(
        lang=lang,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        engine="paddle",
    )
    loaded_s = round(time.monotonic() - started_at, 3)

    started_at = time.monotonic()
    result = ocr.predict(str(image_path))
    inference_s = round(time.monotonic() - started_at, 3)

    raw_lines, scores = extract_result_data(result)
    lines = clean_lines(raw_lines)
    text = "\n".join(lines).strip()
    avg_score = round(mean(scores), 4) if scores else None

    return {
        "ok": bool(text),
        "engine": "paddleocr",
        "lang": lang,
        "image_path": str(image_path),
        "text": text,
        "raw_line_count": len(raw_lines),
        "line_count": len(lines),
        "character_count": len(text),
        "avg_score": avg_score,
        "load_time_s": loaded_s,
        "inference_time_s": inference_s,
        "status": "parcial: OCR automatico por PaddleOCR; revisar transcricao antes de corrigir.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa OCR com PaddleOCR em uma imagem.")
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--lang", default="pt")
    args = parser.parse_args()

    try:
        if not args.image.exists():
            raise FileNotFoundError(args.image)
        with contextlib.redirect_stdout(sys.stderr):
            result = run_paddle_ocr(args.image, args.lang)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["ok"] else 2
    except Exception as exc:
        payload = {
            "ok": False,
            "engine": "paddleocr",
            "image_path": str(args.image),
            "text": "",
            "error": f"{type(exc).__name__}: {exc}",
            "status": "ocr_degradado: PaddleOCR falhou; usar fallback ou revisar imagem manualmente.",
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
