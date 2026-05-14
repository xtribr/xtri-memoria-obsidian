# Pipeline OCR

Status: preparado

## Objetivo

Extrair texto de redações em imagem ou PDF escaneado antes da correção.

## Estado do ambiente

Em 2026-05-14, `tesseract` e `ocrmypdf` não estavam instalados neste Mac. Se a primeira redação vier como imagem ou PDF escaneado, será necessário ativar uma das rotas abaixo.

## Rotas possíveis

## Texto digitado

Usar diretamente no [[Caso 001 - Primeira Redação]].

## Imagem legível

1. Preservar arquivo original em `entradas/`.
2. Gerar transcrição OCR.
3. Revisar manualmente nomes, acentos, quebras de linha e palavras ambíguas.
4. Registrar confiança do OCR.
5. Aplicar [[08 - Política de Dados dos Casos]] antes de versionar qualquer caso.

## PDF com texto selecionável

1. Extrair com `pdftotext`.
2. Conferir se o texto extraído corresponde à redação.
3. Registrar fonte e limitações.

## PDF escaneado

1. Converter páginas para imagem.
2. Rodar OCR.
3. Revisar transcrição.
4. Só corrigir depois da revisão.

## Regra de segurança

OCR não é correção. A redação transcrita precisa ser conferida antes de gerar nota.

## Conexões

- [[Template - OCR de Redação]]
- [[Caso 001 - Primeira Redação]]
- [[Protocolo de Correção]]
- [[08 - Política de Dados dos Casos]]
