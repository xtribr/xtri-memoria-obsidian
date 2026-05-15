#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${VAULT_DIR}/../.." && pwd)"
PYTHON_BIN="${PROJECT_ROOT}/.venv/bin/python"
KEYCHAIN_SERVICE="online.xtri.red"
KEYCHAIN_ACCOUNT="SABIA_API_KEY"
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
