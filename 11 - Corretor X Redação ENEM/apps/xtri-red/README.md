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
- Mostrar tema, status da transcrição e prévia da redação.
- Rodar dry-run ou correção real chamando `scripts/run_caso_sabia.sh`.
- Abrir o Excel gerado.

## Importação

Use `Importar Pasta` quando houver um lote com um arquivo por aluno. Use `Importar Arquivo` para casos avulsos ou seleção manual de poucos arquivos. Os botões também aparecem na barra lateral como `Pasta` e `Arquivos`.

Arquivos `.txt` são importados como transcrição pronta e ficam liberados para correção. Arquivos `.pdf`, `.jpg`, `.jpeg`, `.png`, `.heic`, `.tif` e `.tiff` são copiados como `original.ext`, criam o caso no vault e ficam marcados como `aguardando_ocr` até existir uma transcrição em `redacao.txt`.

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
