#!/usr/bin/env python3
"""OCR Seguro com OpenAI Vision para redações manuscritas.

Fluxo:
1. Transcrição literal inicial.
2. Auditoria visual independente usando a imagem + transcrição inicial.
3. Comparação automática para decidir se a transcrição pode ser liberada em lote.

Mesmo quando o status sai como `ok`, os arquivos de auditoria preservam a leitura
inicial e a leitura validada para rastreabilidade pedagógica.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


TRANSCRIPTION_PROMPT = """Você é um transcritor literal de redações manuscritas do ENEM em português brasileiro.

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


def audit_prompt(initial_text: str) -> str:
    return f"""Você é o auditor de OCR Seguro da XTRI.

TAREFA
Compare a imagem original com a transcrição inicial abaixo. Sua função é detectar se a transcrição preserva literalmente o manuscrito, incluindo erros, acentos, hífens, linhas e parágrafos.

REGRAS
- Não corrija o aluno para português padrão.
- Corrija apenas erros de OCR, quando a imagem deixar claro que a transcrição inicial leu errado.
- Preserve erros reais do aluno.
- Preserve parágrafos com linha em branco entre blocos.
- Marque trechos ilegíveis como [ilegível].
- Se houver dúvida, mantenha marcação [?] e reduza a confiança.
- Se a transcrição inicial estiver muito instável, retorne confiança baixa.
- Só use confiança alta quando a leitura estiver literal e estável o suficiente para correção automática em lote.

TRANSCRIÇÃO INICIAL
{initial_text}

FORMATO DE SAÍDA
Retorne apenas JSON válido:
{{
  "texto_validado": "transcrição literal auditada",
  "confianca": "alta|media|baixa",
  "pronto_para_correcao": false,
  "linhas_estimadas": 0,
  "paragrafos_estimados": 0,
  "divergencias": [
    {{
      "tipo": "palavra|acentuacao|pontuacao|linha|paragrafo|omissao|adicao|ilegivel",
      "transcricao_inicial": "trecho inicial",
      "leitura_validada": "trecho auditado",
      "motivo": "explicação curta"
    }}
  ],
  "trechos_criticos": ["trechos que exigiriam revisão humana"],
  "observacoes": "breve nota de auditoria"
}}
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


def call_vision(prompt: str, image_data_url: str, model: str, api_key: str) -> dict[str, Any]:
    payload = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_data_url, "detail": "high"},
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

    with urllib.request.urlopen(request, timeout=180) as response:
        data = json.loads(response.read().decode("utf-8"))
    return parse_model_json(extract_output_text(data))


def paragraph_count(text: str) -> int:
    return len([block for block in text.split("\n\n") if block.strip()])


def normalized_for_similarity(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def similarity_ratio(left: str, right: str) -> float:
    left = normalized_for_similarity(left)
    right = normalized_for_similarity(right)
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0

    previous = list(range(len(right) + 1))
    for i, char_left in enumerate(left, start=1):
        current = [i]
        for j, char_right in enumerate(right, start=1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (char_left != char_right)
            current.append(min(insert_cost, delete_cost, replace_cost))
        previous = current
    distance = previous[-1]
    return round(1 - distance / max(len(left), len(right)), 4)


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def int_or_default(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def is_safe_for_correction(
    text: str,
    confidence: str,
    similarity: float,
    divergences: list[Any],
    critical_spans: list[Any],
    paragraphs: int,
) -> bool:
    if len(text) < 500:
        return False
    if confidence != "alta":
        return False
    if similarity < 0.90:
        return False
    if paragraphs < 3:
        return False
    if len(critical_spans) > 0:
        return False
    if len(divergences) > 8:
        return False
    if "[ilegível]" in text.lower():
        return False
    return True


def request_secure_transcription(image_path: Path, model: str, api_key: str) -> dict[str, Any]:
    image_data_url = image_to_data_url(image_path)

    initial = call_vision(TRANSCRIPTION_PROMPT, image_data_url, model, api_key)
    initial_text = str(initial.get("texto", "")).strip()
    if not initial_text:
        return {
            "ok": False,
            "engine": "openai_vision_secure",
            "model": model,
            "image_path": str(image_path),
            "text": "",
            "error": "Transcrição inicial vazia.",
            "status": "ocr_degradado: OpenAI Vision nao extraiu texto util.",
        }

    audit = call_vision(audit_prompt(initial_text), image_data_url, model, api_key)
    final_text = str(audit.get("texto_validado") or initial_text).strip()
    confidence = str(audit.get("confianca") or "baixa").strip().lower()
    if confidence not in {"alta", "media", "baixa"}:
        confidence = "baixa"

    divergences = as_list(audit.get("divergencias"))
    critical_spans = as_list(audit.get("trechos_criticos"))
    uncertain_words = as_list(initial.get("palavras_incertas"))
    uncertain_spans = as_list(initial.get("trechos_incertos"))
    similarity = similarity_ratio(initial_text, final_text)
    line_count = int_or_default(
        audit.get("linhas_estimadas"),
        int_or_default(initial.get("linhas_estimadas"), final_text.count("\n") + 1),
    )
    paragraphs = int_or_default(
        audit.get("paragrafos_estimados"),
        int_or_default(initial.get("paragrafos_estimados"), paragraph_count(final_text)),
    )
    safe = bool(audit.get("pronto_para_correcao")) and is_safe_for_correction(
        text=final_text,
        confidence=confidence,
        similarity=similarity,
        divergences=divergences,
        critical_spans=critical_spans,
        paragraphs=paragraphs,
    )
    status = (
        "ok: transcricao automatica validada por OCR Seguro OpenAI Vision; pronta para correcao automatica."
        if safe
        else "parcial: OCR Seguro OpenAI Vision exige revisao humana ou nova imagem antes de corrigir."
    )

    return {
        "ok": bool(final_text),
        "engine": "openai_vision_secure",
        "model": model,
        "image_path": str(image_path),
        "text": final_text,
        "initial_text": initial_text,
        "line_count": line_count,
        "paragraph_count": paragraphs,
        "character_count": len(final_text),
        "confidence": confidence,
        "similarity": similarity,
        "safe_for_correction": safe,
        "divergences": divergences,
        "critical_spans": [str(item) for item in critical_spans],
        "uncertain_spans": [str(item) for item in uncertain_spans],
        "uncertain_words": uncertain_words,
        "notes": str(audit.get("observacoes") or initial.get("observacoes") or "").strip(),
        "initial_notes": str(initial.get("observacoes", "")).strip(),
        "status": status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa OCR Seguro com OpenAI Vision.")
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

        result = request_secure_transcription(args.image, args.model, api_key)
        result["elapsed_time_s"] = round(time.monotonic() - started_at, 3)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["ok"] else 2
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        payload = {
            "ok": False,
            "engine": "openai_vision_secure",
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
            "engine": "openai_vision_secure",
            "image_path": str(args.image),
            "text": "",
            "error": f"{type(exc).__name__}: {exc}",
            "status": "ocr_degradado: OpenAI Vision falhou; usar fallback ou revisar imagem manualmente.",
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
