# XTRI-RED

App nativo macOS em SwiftUI para operar correções de redação ENEM usando o vault do Obsidian como cérebro.

## Rodar em desenvolvimento

```bash
cd "/Volumes/KINGSTON 2/apps/apps/corretor de redação/corretor x/11 - Corretor X Redação ENEM/apps/xtri-red"
swift run XTRI-RED
```

## Gerar app clicável

```bash
cd "/Volumes/KINGSTON 2/apps/apps/corretor de redação/corretor x/11 - Corretor X Redação ENEM/apps/xtri-red"
./package_app.sh
open "dist/XTRI-RED.app"
```

O bundle local fica em:

```text
dist/XTRI-RED.app
```

Este app é assinado ad-hoc para uso local. Para distribuição externa, ainda será necessário assinar com certificado Apple Developer e notarizar.

## Função deste primeiro corte

- Importar uma pasta com um arquivo por aluno.
- Importar um ou mais arquivos avulsos.
- Ler casos em `entradas/caso-*`.
- Ler prompts/rubricas em `app-config/prompts`.
- Mostrar tema, status da transcrição e editor de transcrição.
- Salvar transcrição revisada antes de liberar correção.
- Rodar dry-run ou correção real chamando `scripts/run_caso_sabia.sh`.
- Abrir o Excel gerado.

Observação de interface: os prompts e rubricas continuam no vault e são usados pelo motor, mas não aparecem na tela principal. A interface operacional mostra apenas vault, importação, casos, redação, ações e execução.

## Importação

Use `Importar Pasta` quando houver um lote com um arquivo por aluno. Use `Importar Arquivo` para casos avulsos ou seleção manual de poucos arquivos. Os botões também aparecem na barra lateral como `Pasta` e `Arquivos`.

Arquivos `.txt` são importados como transcrição pronta e ficam liberados para correção. Imagens `.jpg`, `.jpeg`, `.png`, `.heic`, `.tif` e `.tiff` tentam OCR em camadas: OpenAI Vision com `gpt-5.2` quando `OPENAI_API_KEY` estiver disponível, PaddleOCR (`lang=pt`) quando as dependências estiverem instaladas, e Apple Vision como fallback local. A camada OpenAI Vision usa prompt de transcrição literal, preservando acentos, erros, hífens, quebras de linha e parágrafos sempre que perceptíveis. Quando há texto extraído por OCR, o caso fica marcado como `parcial` e não libera `Corrigir` até a transcrição ser revisada e salva no app. PDFs são copiados como `original.pdf` e continuam marcados como `aguardando_ocr` até existir uma transcrição revisada.

Casos de imagem podem ser processados ou reprocessados pelo botão `Rodar OCR`/`Reprocessar OCR`, exibido no painel do caso quando há `original.ext` compatível.

Para revisar imagem manuscrita, use `Abrir imagem`, corrija a transcrição no editor e clique em `Salvar transcrição`. O status muda para `ok` e o caso fica liberado para dry-run/correção.

Para instalar o OCR opcional com PaddleOCR:

```bash
cd "/Volumes/KINGSTON 2/apps/apps/corretor de redação"
.venv/bin/python -m pip install -r "corretor x/11 - Corretor X Redação ENEM/scripts/requirements-ocr.txt"
```

Para habilitar a camada OpenAI Vision no app aberto pelo Finder, salve a chave no mesmo serviço do Keychain:

```bash
security add-generic-password -U -s "online.xtri.red" -a "OPENAI_API_KEY" -w "SUA_CHAVE_OPENAI"
```

Também é possível iniciar pelo terminal com `OPENAI_API_KEY` no ambiente. A chave não deve ser salva em arquivo do projeto.

O modelo padrão dessa camada é `gpt-5.2`. Para testar outro modelo, defina `OPENAI_VISION_MODEL` no ambiente antes de abrir o app pelo terminal.

Para cada arquivo aceito, o app cria:

```text
entradas/caso-001/
  aluno-nome.txt
  tema.txt
  status-tema.txt
  status-ocr.txt
  redacao.txt
  original.ext
  metadados-importacao.txt
```

## Segurança

A chave `SABIA_API_KEY` não deve ser hardcoded nem salva no Git. O app permite salvar a chave no Keychain do macOS pelo botão `Salvar`; nas próximas aberturas, ela é carregada automaticamente. Também é possível usar a variável de ambiente quando o app é iniciado pelo terminal.

Quando há chave salva, o XTRI-RED mostra `Sabiá conectado` e esconde o campo da chave. Use `Trocar chave` apenas quando precisar substituir o segredo salvo.

Os runners de terminal também leem a mesma chave do Keychain. Depois de salvar uma vez no XTRI-RED, comandos como `scripts/run_caso_sabia.sh` funcionam sem exportar `SABIA_API_KEY`.
