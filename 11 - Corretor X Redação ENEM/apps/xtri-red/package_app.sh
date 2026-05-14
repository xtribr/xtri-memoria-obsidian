#!/usr/bin/env bash
set -euo pipefail

APP_NAME="XTRI-RED"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
TMP_DIR="${ROOT_DIR}/.package-tmp"
APP_BUNDLE="${DIST_DIR}/${APP_NAME}.app"
CONTENTS_DIR="${APP_BUNDLE}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"
ICONSET_DIR="${TMP_DIR}/AppIcon.iconset"
ICON_SVG="${ROOT_DIR}/Resources/AppIcon.svg"
ICON_ICNS="${TMP_DIR}/AppIcon.icns"
INFO_PLIST="${ROOT_DIR}/Resources/Info.plist"

command -v swift >/dev/null || { echo "Erro: swift não encontrado." >&2; exit 1; }
command -v iconutil >/dev/null || { echo "Erro: iconutil não encontrado." >&2; exit 1; }
command -v sips >/dev/null || { echo "Erro: sips não encontrado." >&2; exit 1; }
command -v codesign >/dev/null || { echo "Erro: codesign não encontrado." >&2; exit 1; }

cd "${ROOT_DIR}"

echo "Compilando ${APP_NAME} em release..."
swift build -c release --product "${APP_NAME}"

EXECUTABLE_PATH="${ROOT_DIR}/.build/release/${APP_NAME}"
if [[ ! -x "${EXECUTABLE_PATH}" ]]; then
  echo "Erro: executável não encontrado em ${EXECUTABLE_PATH}" >&2
  exit 2
fi

rm -rf "${TMP_DIR}" "${APP_BUNDLE}"
mkdir -p "${ICONSET_DIR}" "${MACOS_DIR}" "${RESOURCES_DIR}"

echo "Gerando ícone..."
if command -v magick >/dev/null; then
  magick -background none "${ICON_SVG}" -resize 1024x1024 "${TMP_DIR}/AppIcon-1024.png"
else
  qlmanage -t -s 1024 -o "${TMP_DIR}" "${ICON_SVG}" >/dev/null 2>&1
  mv "${TMP_DIR}/AppIcon.svg.png" "${TMP_DIR}/AppIcon-1024.png"
fi

sips -z 16 16 "${TMP_DIR}/AppIcon-1024.png" --out "${ICONSET_DIR}/icon_16x16.png" >/dev/null
sips -z 32 32 "${TMP_DIR}/AppIcon-1024.png" --out "${ICONSET_DIR}/icon_16x16@2x.png" >/dev/null
sips -z 32 32 "${TMP_DIR}/AppIcon-1024.png" --out "${ICONSET_DIR}/icon_32x32.png" >/dev/null
sips -z 64 64 "${TMP_DIR}/AppIcon-1024.png" --out "${ICONSET_DIR}/icon_32x32@2x.png" >/dev/null
sips -z 128 128 "${TMP_DIR}/AppIcon-1024.png" --out "${ICONSET_DIR}/icon_128x128.png" >/dev/null
sips -z 256 256 "${TMP_DIR}/AppIcon-1024.png" --out "${ICONSET_DIR}/icon_128x128@2x.png" >/dev/null
sips -z 256 256 "${TMP_DIR}/AppIcon-1024.png" --out "${ICONSET_DIR}/icon_256x256.png" >/dev/null
sips -z 512 512 "${TMP_DIR}/AppIcon-1024.png" --out "${ICONSET_DIR}/icon_256x256@2x.png" >/dev/null
sips -z 512 512 "${TMP_DIR}/AppIcon-1024.png" --out "${ICONSET_DIR}/icon_512x512.png" >/dev/null
cp "${TMP_DIR}/AppIcon-1024.png" "${ICONSET_DIR}/icon_512x512@2x.png"
iconutil -c icns "${ICONSET_DIR}" -o "${ICON_ICNS}"

echo "Montando bundle .app..."
cp "${EXECUTABLE_PATH}" "${MACOS_DIR}/${APP_NAME}"
cp "${INFO_PLIST}" "${CONTENTS_DIR}/Info.plist"
cp "${ICON_ICNS}" "${RESOURCES_DIR}/AppIcon.icns"
chmod +x "${MACOS_DIR}/${APP_NAME}"

echo "Assinando ad-hoc..."
codesign --force --deep --sign - "${APP_BUNDLE}" >/dev/null
codesign --verify --deep --strict --verbose=2 "${APP_BUNDLE}"

echo "App gerado em:"
echo "${APP_BUNDLE}"
