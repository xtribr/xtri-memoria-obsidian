#!/usr/bin/env python3
"""Corrige uma redação ENEM com Sabiá e preenche o template Excel do Corretor X.

Uso mínimo:
  export SABIA_API_KEY="..."
  python3 scripts/corrigir_com_sabia.py \
    --tema-file entradas/caso-001/tema.txt \
    --redacao-file entradas/caso-001/redacao.txt \
    --case-id CASO-001 \
    --aluno-id "Aluno 001" \
    --out-xlsx "Cérebro do 1000/casos/exports/CASO-001.xlsx"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


API_URL = "https://chat.maritaca.ai/api/chat/completions"
DEFAULT_MODEL = "sabia-4"
VALID_SCORES = {0, 40, 80, 120, 160, 200}
COMPETENCIAS = ["C1", "C2", "C3", "C4", "C5"]


RUBRICAS = {
    "C1": (
        "Competência I: demonstrar domínio da modalidade escrita formal da língua portuguesa. "
        "Avalie desvios gramaticais, convenções da escrita, registro, vocabulário e estrutura sintática."
    ),
    "C2": (
        "Competência II: compreender a proposta de redação e desenvolver o tema nos limites "
        "do texto dissertativo-argumentativo. Avalie aderência ao tema, tipo textual e repertório "
        "sociocultural legitimado, pertinente e produtivo."
    ),
    "C3": (
        "Competência III: selecionar, relacionar, organizar e interpretar informações, fatos, "
        "opiniões e argumentos em defesa de um ponto de vista. Avalie projeto de texto, autoria, "
        "progressão e consistência argumentativa."
    ),
    "C4": (
        "Competência IV: demonstrar conhecimento dos mecanismos linguísticos necessários para "
        "a construção da argumentação. Avalie coesão, operadores argumentativos, referenciação "
        "e articulação entre períodos e parágrafos."
    ),
    "C5": (
        "Competência V: elaborar proposta de intervenção para o problema abordado, respeitando "
        "os direitos humanos. Avalie agente, ação, meio, efeito/finalidade, detalhamento e "
        "articulação com a discussão."
    ),
}


@dataclass
class AvaliacaoCompetencia:
    competencia: str
    nota_corretor_x: int
    comentario_do_erro: str
    evidencia_no_texto: str
    sugestao_de_melhoria: str
    nivel_confianca: str


def read_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Arquivo vazio: {path}")
    return text


def load_competencia_prompt(competencia: str, prompts_dir: Path) -> str:
    prompt_path = prompts_dir / f"{competencia.lower()}.md"
    if prompt_path.exists():
        return read_text(prompt_path)
    return RUBRICAS[competencia]


def extract_json(content: str) -> dict[str, Any]:
    content = content.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    if fenced:
        content = fenced.group(1)
    else:
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            content = content[start : end + 1]
    return json.loads(content)


def build_prompt(competencia: str, tema: str, redacao: str, status_ocr: str, rubrica: str) -> str:
    return f"""
Você é o Corretor X da XTRI EdTECH, especializado em redação do ENEM.

Avalie SOMENTE a {competencia}. Use exclusivamente as faixas oficiais:
0, 40, 80, 120, 160 ou 200 pontos.

Autoridade metodológica:
- A Cartilha do Participante / Manual Oficial ENEM 2025 é a referência principal.
- Redações nota 1000 servem como referência de padrão, não como regra absoluta.

Rubrica da competência:
{rubrica}

Regras obrigatórias:
- Não invente tema, texto motivador, erro, repertório ou dado.
- Cite evidência que exista no texto do aluno.
- Se faltar informação para avaliar com segurança, reduza o nível de confiança.
- Não escreva uma redação pronta para o aluno.
- Seja rigoroso e pedagógico.
- Responda apenas em JSON válido, sem Markdown.

Formato JSON obrigatório:
{{
  "competencia": "{competencia}",
  "nota_corretor_x": 0,
  "comentario_do_erro": "comentário pedagógico objetivo",
  "evidencia_no_texto": "trecho curto ou descrição fiel do texto",
  "sugestao_de_melhoria": "orientação prática sem substituir autoria",
  "nivel_confianca": "Alta|Média|Baixa"
}}

Tema:
{tema}

Status OCR/transcrição:
{status_ocr}

Redação do aluno:
{redacao}
""".strip()


def call_sabia(api_key: str, model: str, prompt: str, timeout: int, retries: int) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        request = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"]
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise RuntimeError(f"Falha na chamada ao Sabiá: {exc}") from exc
    raise RuntimeError(f"Falha na chamada ao Sabiá: {last_error}")


def normalize_avaliacao(raw: dict[str, Any], competencia: str) -> AvaliacaoCompetencia:
    nota = int(raw.get("nota_corretor_x"))
    if nota not in VALID_SCORES:
        raise ValueError(f"Nota inválida para {competencia}: {nota}")
    nivel = str(raw.get("nivel_confianca", "")).strip()
    if nivel not in {"Alta", "Média", "Baixa"}:
        nivel = "Baixa"
    return AvaliacaoCompetencia(
        competencia=competencia,
        nota_corretor_x=nota,
        comentario_do_erro=str(raw.get("comentario_do_erro", "")).strip(),
        evidencia_no_texto=str(raw.get("evidencia_no_texto", "")).strip(),
        sugestao_de_melhoria=str(raw.get("sugestao_de_melhoria", "")).strip(),
        nivel_confianca=nivel,
    )


def fill_workbook(
    template_path: Path,
    output_path: Path,
    case_id: str,
    aluno_id: str,
    tema: str,
    status_ocr: str,
    avaliacoes: list[AvaliacaoCompetencia],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template_path, output_path)
    wb = load_workbook(output_path)
    ws = wb["Devolutiva"]
    for idx, avaliacao in enumerate(avaliacoes, start=5):
        ws.cell(idx, 1).value = case_id
        ws.cell(idx, 2).value = aluno_id
        ws.cell(idx, 3).value = tema
        ws.cell(idx, 4).value = avaliacao.competencia
        ws.cell(idx, 5).value = avaliacao.nota_corretor_x
        ws.cell(idx, 6).value = avaliacao.comentario_do_erro
        ws.cell(idx, 7).value = avaliacao.evidencia_no_texto
        ws.cell(idx, 8).value = avaliacao.sugestao_de_melhoria
        ws.cell(idx, 12).value = avaliacao.nivel_confianca
        ws.cell(idx, 13).value = status_ocr
        ws.cell(idx, 14).value = "aguardando validação"
    wb.save(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Corrige redação ENEM com Sabiá e preenche Excel.")
    parser.add_argument("--tema-file", required=True, type=Path)
    parser.add_argument("--redacao-file", required=True, type=Path)
    parser.add_argument("--case-id", default="CASO-001")
    parser.add_argument("--aluno-id", default="Aluno 001")
    parser.add_argument("--status-ocr", default="Não necessário")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", default=90, type=int)
    parser.add_argument("--retries", default=1, type=int)
    parser.add_argument("--dry-run", action="store_true", help="Não chama API; só valida entradas.")
    parser.add_argument(
        "--brain-prompts-dir",
        type=Path,
        default=Path("app-config/prompts"),
        help="Diretório do vault com prompts/rubricas por competência.",
    )
    parser.add_argument(
        "--template-xlsx",
        type=Path,
        default=Path("Cérebro do 1000/templates/Template - Entrega Excel Corretor X.xlsx"),
    )
    parser.add_argument(
        "--out-xlsx",
        type=Path,
        default=Path("Cérebro do 1000/casos/exports/CASO-001.xlsx"),
    )
    args = parser.parse_args()

    tema = read_text(args.tema_file)
    redacao = read_text(args.redacao_file)

    if args.dry_run:
        print("Entradas válidas.")
        print(f"Tema: {len(tema)} caracteres")
        print(f"Redação: {len(redacao)} caracteres")
        print("Dry-run: nenhuma chamada ao Sabiá foi feita.")
        return 0

    api_key = os.environ.get("SABIA_API_KEY")
    if not api_key:
        print("Erro: defina SABIA_API_KEY no ambiente. Nunca coloque a chave no repositório.", file=sys.stderr)
        return 2

    avaliacoes: list[AvaliacaoCompetencia] = []
    for competencia in COMPETENCIAS:
        rubrica = load_competencia_prompt(competencia, args.brain_prompts_dir)
        prompt = build_prompt(competencia, tema, redacao, args.status_ocr, rubrica)
        content = call_sabia(api_key, args.model, prompt, args.timeout, args.retries)
        raw = extract_json(content)
        avaliacoes.append(normalize_avaliacao(raw, competencia))
        print(f"{competencia}: {avaliacoes[-1].nota_corretor_x}/200 ({avaliacoes[-1].nivel_confianca})")

    fill_workbook(
        args.template_xlsx,
        args.out_xlsx,
        args.case_id,
        args.aluno_id,
        tema,
        args.status_ocr,
        avaliacoes,
    )
    print(f"Excel salvo em: {args.out_xlsx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
