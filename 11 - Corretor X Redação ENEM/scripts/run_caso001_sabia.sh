#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${VAULT_DIR}/../.." && pwd)"
PYTHON_BIN="${PROJECT_ROOT}/.venv/bin/python"
DRY_RUN=0

if [[ "${CORRETOR_X_DRY_RUN:-}" == "1" ]]; then
  DRY_RUN=1
elif [[ -z "${SABIA_API_KEY:-}" ]]; then
  echo "Erro: defina SABIA_API_KEY antes de rodar. Nunca salve a chave no Git." >&2
  exit 2
fi

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Erro: Python do ambiente virtual não encontrado em: ${PYTHON_BIN}" >&2
  exit 3
fi

cd "${VAULT_DIR}"

STATUS_OCR="$(cat "entradas/caso-001/status-ocr.txt")"

if [[ "${DRY_RUN}" == "1" ]]; then
  "${PYTHON_BIN}" scripts/corrigir_com_sabia.py \
    --tema-file "entradas/caso-001/tema.txt" \
    --redacao-file "entradas/caso-001/redacao.txt" \
    --case-id "CASO-001" \
    --aluno-id "Aluno 001" \
    --status-ocr "${STATUS_OCR}" \
    --out-xlsx "Cérebro do 1000/casos/exports/CASO-001.xlsx" \
    --dry-run
else
  "${PYTHON_BIN}" scripts/corrigir_com_sabia.py \
    --tema-file "entradas/caso-001/tema.txt" \
    --redacao-file "entradas/caso-001/redacao.txt" \
    --case-id "CASO-001" \
    --aluno-id "Aluno 001" \
    --status-ocr "${STATUS_OCR}" \
    --out-xlsx "Cérebro do 1000/casos/exports/CASO-001.xlsx"
fi
