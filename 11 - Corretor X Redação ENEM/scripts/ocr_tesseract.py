#!/usr/bin/env python3
"""OCR local com Tesseract para imagens de redação.

Saída: JSON em stdout, sem texto extra. O XTRI-RED usa este script como
primeiro motor local de OCR. A transcrição é sempre tratada como rascunho,
porque Tesseract não valida fidelidade literal suficiente para C1.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


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


def clean_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if should_drop_line(line):
            continue
        lines.append(line)
    return lines


def quality_score(text: str) -> float:
    letters = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]", text)
    if not text or not letters:
        return 0.0
    total = len(text)
    letter_ratio = len(letters) / max(total, 1)
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]{3,}", text)
    common_pt = re.findall(
        r"\b(?:que|para|com|uma|como|dos|das|por|não|nao|mais|educa[cç][aã]o|brasil|sociedade|governo|estado)\b",
        text,
        flags=re.IGNORECASE,
    )
    word_ratio = min(len(words) / 160, 1.0)
    common_ratio = min(len(common_pt) / 20, 1.0)
    return round((letter_ratio * 0.45) + (word_ratio * 0.35) + (common_ratio * 0.20), 4)


def find_tesseract() -> str | None:
    for candidate in (
        shutil.which("tesseract"),
        "/opt/homebrew/bin/tesseract",
        "/usr/local/bin/tesseract",
    ):
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def run_tesseract(image_path: Path, lang: str, psm: int) -> dict[str, object]:
    tesseract = find_tesseract()
    if not tesseract:
        raise FileNotFoundError("tesseract não encontrado no PATH")

    started_at = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="xtri-tesseract-") as tmpdir:
        output_base = Path(tmpdir) / "out"
        cmd = [
            tesseract,
            str(image_path),
            str(output_base),
            "-l",
            lang,
            "--psm",
            str(psm),
            "--oem",
            "1",
            "-c",
            "preserve_interword_spaces=1",
        ]
        completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
        raw_text = output_base.with_suffix(".txt").read_text(encoding="utf-8", errors="replace")

    elapsed_s = round(time.monotonic() - started_at, 3)
    lines = clean_lines(raw_text)
    text = "\n".join(lines).strip()
    score = quality_score(text)

    return {
        "ok": bool(text) and score >= 0.65,
        "engine": "tesseract",
        "lang": lang,
        "psm": psm,
        "image_path": str(image_path),
        "text": text,
        "raw_character_count": len(raw_text),
        "line_count": len(lines),
        "character_count": len(text),
        "quality_score": score,
        "inference_time_s": elapsed_s,
        "status": "parcial: OCR automatico por Tesseract; revisar transcricao antes de corrigir.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa OCR com Tesseract em uma imagem.")
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--lang", default="por+eng")
    parser.add_argument("--psm", type=int, default=6)
    args = parser.parse_args()

    try:
        if not args.image.exists():
            raise FileNotFoundError(args.image)
        result = run_tesseract(args.image, args.lang, args.psm)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["ok"] else 2
    except Exception as exc:
        payload = {
            "ok": False,
            "engine": "tesseract",
            "image_path": str(args.image),
            "text": "",
            "error": f"{type(exc).__name__}: {exc}",
            "status": "ocr_degradado: Tesseract falhou; usar fallback ou revisar imagem manualmente.",
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
