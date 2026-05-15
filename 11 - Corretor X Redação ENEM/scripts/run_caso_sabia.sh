#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${VAULT_DIR}/../.." && pwd)"
PYTHON_BIN="${PROJECT_ROOT}/.venv/bin/python"
KEYCHAIN_SERVICE="online.xtri.red"
KEYCHAIN_ACCOUNT="SABIA_API_KEY"

CASE_DIR="${1:-caso-001}"
DEFAULT_CASE_ID="$(printf '%s' "${CASE_DIR}" | tr '[:lower:]' '[:upper:]')"
CASE_ID="${2:-${DEFAULT_CASE_ID}}"
ALUNO_ID="${3:-Aluno sem identificação}"
DRY_RUN=0

load_sabia_key_from_keychain() {
  if [[ -n "${SABIA_API_KEY:-}" ]]; then
    return 0
  fi
  if command -v security >/dev/null; then
    local saved_key
    saved_key="$(security find-generic-password -s "${KEYCHAIN_SERVICE}" -a "${KEYCHAIN_ACCOUNT}" -w 2>/dev/null || true)"
    if [[ -n "${saved_key}" ]]; then
      export SABIA_API_KEY="${saved_key}"
      return 0
    fi
  fi
  return 1
}

if [[ "${CORRETOR_X_DRY_RUN:-}" == "1" ]]; then
  DRY_RUN=1
elif ! load_sabia_key_from_keychain; then
  echo "Erro: defina SABIA_API_KEY ou salve a chave no Keychain pelo XTRI-RED." >&2
  exit 2
fi

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Erro: Python do ambiente virtual não encontrado em: ${PYTHON_BIN}" >&2
  exit 3
fi

cd "${VAULT_DIR}"

INPUT_DIR="entradas/${CASE_DIR}"
TEMA_FILE="${INPUT_DIR}/tema.txt"
REDACAO_LITERAL_FILE="${INPUT_DIR}/redacao-literal.txt"
REDACAO_DRAFT_FILE="${INPUT_DIR}/redacao.txt"
STATUS_OCR_FILE="${INPUT_DIR}/status-ocr.txt"
STATUS_TEMA_FILE="${INPUT_DIR}/status-tema.txt"
STATUS_ANULACAO_FILE="${INPUT_DIR}/status-anulacao.txt"
TANGENCIAMENTO_C2_FILE="${INPUT_DIR}/tangenciamento-c2.txt"
NUM_LINHAS_FILE="${INPUT_DIR}/num-linhas.txt"
OUT_XLSX="Cérebro do 1000/casos/exports/${CASE_ID}.xlsx"

for required_file in "${TEMA_FILE}" "${STATUS_OCR_FILE}"; do
  if [[ ! -f "${required_file}" ]]; then
    echo "Erro: arquivo obrigatório não encontrado: ${required_file}" >&2
    exit 4
  fi
done

STATUS_OCR="$(cat "${STATUS_OCR_FILE}")"
STATUS_OCR_NORMALIZED="$(printf '%s' "${STATUS_OCR}" | tr '[:upper:]' '[:lower:]')"

if [[ "${STATUS_OCR_NORMALIZED}" == ok:* && -s "${REDACAO_LITERAL_FILE}" ]]; then
  REDACAO_FILE="${REDACAO_LITERAL_FILE}"
elif [[ -s "${REDACAO_DRAFT_FILE}" ]]; then
  REDACAO_FILE="${REDACAO_DRAFT_FILE}"
elif [[ -s "${REDACAO_LITERAL_FILE}" ]]; then
  REDACAO_FILE="${REDACAO_LITERAL_FILE}"
else
  echo "Erro: transcrição literal não encontrada em ${REDACAO_LITERAL_FILE} nem rascunho em ${REDACAO_DRAFT_FILE}" >&2
  exit 4
fi

if [[ "${STATUS_OCR_NORMALIZED}" != ok:* ]]; then
  echo "Aviso: status OCR não validado; correção será gerada com alerta de baixa confiança." >&2
  echo "${STATUS_OCR}" >&2
fi

set -- \
  --tema-file "${TEMA_FILE}" \
  --redacao-file "${REDACAO_FILE}" \
  --case-id "${CASE_ID}" \
  --aluno-id "${ALUNO_ID}" \
  --status-ocr "${STATUS_OCR}"

if [[ -f "${STATUS_TEMA_FILE}" ]]; then
  STATUS_TEMA="$(tr -d '\r\n' < "${STATUS_TEMA_FILE}")"
  if [[ -n "${STATUS_TEMA}" ]]; then
    set -- "$@" --status-tema "${STATUS_TEMA}"
  fi
fi

if [[ -f "${STATUS_ANULACAO_FILE}" ]]; then
  STATUS_ANULACAO="$(tr -d '\r\n' < "${STATUS_ANULACAO_FILE}")"
  if [[ -n "${STATUS_ANULACAO}" ]]; then
    set -- "$@" --status-anulacao "${STATUS_ANULACAO}"
  fi
fi

if [[ -f "${TANGENCIAMENTO_C2_FILE}" ]]; then
  TANGENCIAMENTO_C2="$(tr '[:upper:]' '[:lower:]' < "${TANGENCIAMENTO_C2_FILE}" | tr -d '[:space:]')"
  if [[ "${TANGENCIAMENTO_C2}" == "true" || "${TANGENCIAMENTO_C2}" == "1" || "${TANGENCIAMENTO_C2}" == "sim" ]]; then
    set -- "$@" --tangenciamento-c2
  fi
fi

if [[ -f "${NUM_LINHAS_FILE}" ]]; then
  NUM_LINHAS="$(tr -d '[:space:]' < "${NUM_LINHAS_FILE}")"
  if [[ "${NUM_LINHAS}" =~ ^[0-9]+$ ]]; then
    set -- "$@" --num-linhas "${NUM_LINHAS}"
  fi
fi

set -- "$@" --out-xlsx "${OUT_XLSX}"

if [[ "${DRY_RUN}" == "1" ]]; then
  set -- "$@" --dry-run
fi

"${PYTHON_BIN}" scripts/corrigir_com_sabia.py "$@"
