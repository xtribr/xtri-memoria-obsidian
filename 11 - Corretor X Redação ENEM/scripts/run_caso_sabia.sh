#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${VAULT_DIR}/../.." && pwd)"
PYTHON_BIN="${PROJECT_ROOT}/.venv/bin/python"

CASE_DIR="${1:-caso-001}"
DEFAULT_CASE_ID="$(printf '%s' "${CASE_DIR}" | tr '[:lower:]' '[:upper:]')"
CASE_ID="${2:-${DEFAULT_CASE_ID}}"
ALUNO_ID="${3:-Aluno sem identificação}"
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

INPUT_DIR="entradas/${CASE_DIR}"
TEMA_FILE="${INPUT_DIR}/tema.txt"
REDACAO_FILE="${INPUT_DIR}/redacao.txt"
STATUS_OCR_FILE="${INPUT_DIR}/status-ocr.txt"
OUT_XLSX="Cérebro do 1000/casos/exports/${CASE_ID}.xlsx"

for required_file in "${TEMA_FILE}" "${REDACAO_FILE}" "${STATUS_OCR_FILE}"; do
  if [[ ! -f "${required_file}" ]]; then
    echo "Erro: arquivo obrigatório não encontrado: ${required_file}" >&2
    exit 4
  fi
done

STATUS_OCR="$(cat "${STATUS_OCR_FILE}")"

if [[ "${DRY_RUN}" == "1" ]]; then
  "${PYTHON_BIN}" scripts/corrigir_com_sabia.py \
    --tema-file "${TEMA_FILE}" \
    --redacao-file "${REDACAO_FILE}" \
    --case-id "${CASE_ID}" \
    --aluno-id "${ALUNO_ID}" \
    --status-ocr "${STATUS_OCR}" \
    --out-xlsx "${OUT_XLSX}" \
    --dry-run
else
  "${PYTHON_BIN}" scripts/corrigir_com_sabia.py \
    --tema-file "${TEMA_FILE}" \
    --redacao-file "${REDACAO_FILE}" \
    --case-id "${CASE_ID}" \
    --aluno-id "${ALUNO_ID}" \
    --status-ocr "${STATUS_OCR}" \
    --out-xlsx "${OUT_XLSX}"
fi
