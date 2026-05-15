#!/usr/bin/env python3
"""Transcrição literal de imagem manuscrita com modelo OpenAI Vision.

Saída: JSON em stdout, sem texto extra. A transcrição continua como rascunho:
o XTRI-RED exige revisão humana antes de liberar correção.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


PROMPT = """Você é um transcritor literal de redações manuscritas do ENEM em português brasileiro.

TAREFA
Transcreva exatamente o texto manuscrito pelo participante na área de redação.

REGRAS ABSOLUTAS
- Não corrija ortografia, acentuação, concordância, pontuação, crase, regência ou vocabulário.
- Preserve acentos exatamente como aparecem no manuscrito.
- Se uma palavra parece não ter acento, transcreva sem acento.
- Se o acento está visível, preserve-o: á, à, â, ã, é, ê, í, ó, ô, õ, ú, ç.
- Preserve letras maiúsculas/minúsculas conforme forem perceptíveis.
- Preserve sinais de pontuação quando estiverem escritos.
- Preserve hífens de quebra de linha quando estiverem escritos no fim da linha.
- Preserve a separação de parágrafos. Use uma linha em branco entre parágrafos.
- Preserve as quebras de linha internas aproximadas do manuscrito dentro de cada parágrafo.
- Não junte parágrafos diferentes em um único bloco.
- Não transforme erro do aluno em forma correta.
- Não normalize palavras para português padrão.
- Não complete palavras ilegíveis por contexto.
- Preserve rasuras legíveis como o texto final que ficou escrito.
- Se uma palavra estiver parcialmente ilegível, transcreva a parte legível e marque [?].
- Se um trecho estiver ilegível, escreva [ilegível].
- Ignore instruções impressas da folha, cabeçalho, CPF, número de inscrição e textos padronizados.
- Não resuma, não reescreva e não melhore a redação.
- Não invente palavras para preencher lacunas.

ATENÇÃO
A transcrição será usada para correção de redação ENEM. Corrigir acentos, palavras, pontuação ou paragrafação muda injustamente a nota. Literalidade é mais importante do que fluidez.

FORMATO DE SAÍDA
Retorne apenas JSON válido:
{
  "texto": "transcrição literal com parágrafos separados por linha em branco",
  "linhas_estimadas": 0,
  "paragrafos_estimados": 0,
  "palavras_incertas": [
    {"trecho": "forma transcrita", "motivo": "ilegível|acentuação_duvidosa|letra_duvidosa|rasura|paragrafacao_duvidosa"}
  ],
  "trechos_incertos": ["..."],
  "observacoes": "breve nota sobre legibilidade"
}
"""


def image_to_data_url(path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(path.name)
    if mime_type not in {"image/png", "image/jpeg", "image/webp", "image/gif"}:
        raise ValueError(
            f"Formato não suportado pela API de visão: {path.suffix or path.name}. "
            "Use PNG, JPEG, WEBP ou GIF não animado."
        )
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def extract_output_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]

    chunks: list[str] = []
    for item in response.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            text = content.get("text")
            if isinstance(text, str):
                chunks.append(text)
    return "\n".join(chunks).strip()


def parse_model_json(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    return json.loads(text)


def request_transcription(image_path: Path, model: str, api_key: str) -> dict[str, Any]:
    payload = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": PROMPT},
                    {
                        "type": "input_image",
                        "image_url": image_to_data_url(image_path),
                        "detail": "high",
                    },
                ],
            }
        ],
    }

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))

    model_text = extract_output_text(data)
    parsed = parse_model_json(model_text)
    literal_text = str(parsed.get("texto", "")).strip()
    uncertain = parsed.get("trechos_incertos", [])
    if not isinstance(uncertain, list):
        uncertain = []
    uncertain_words = parsed.get("palavras_incertas", [])
    if not isinstance(uncertain_words, list):
        uncertain_words = []

    return {
        "ok": bool(literal_text),
        "engine": "openai_vision",
        "model": model,
        "image_path": str(image_path),
        "text": literal_text,
        "line_count": int(parsed.get("linhas_estimadas") or literal_text.count("\n") + 1),
        "paragraph_count": int(
            parsed.get("paragrafos_estimados")
            or len([block for block in literal_text.split("\n\n") if block.strip()])
        ),
        "character_count": len(literal_text),
        "uncertain_spans": [str(item) for item in uncertain],
        "uncertain_words": uncertain_words,
        "notes": str(parsed.get("observacoes", "")).strip(),
        "status": "parcial: transcricao automatica por OpenAI Vision; revisar literalmente antes de corrigir.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcreve imagem com OpenAI Vision.")
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--model", default=os.environ.get("OPENAI_VISION_MODEL", "gpt-5.2"))
    args = parser.parse_args()

    started_at = time.monotonic()
    try:
        if not args.image.exists():
            raise FileNotFoundError(args.image)
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY ausente.")

        result = request_transcription(args.image, args.model, api_key)
        result["elapsed_time_s"] = round(time.monotonic() - started_at, 3)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["ok"] else 2
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        payload = {
            "ok": False,
            "engine": "openai_vision",
            "image_path": str(args.image),
            "text": "",
            "error": f"HTTPError {exc.code}: {body[:1000]}",
            "status": "ocr_degradado: OpenAI Vision falhou; usar fallback ou revisar imagem manualmente.",
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 1
    except Exception as exc:
        payload = {
            "ok": False,
            "engine": "openai_vision",
            "image_path": str(args.image),
            "text": "",
            "error": f"{type(exc).__name__}: {exc}",
            "status": "ocr_degradado: OpenAI Vision falhou; usar fallback ou revisar imagem manualmente.",
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
