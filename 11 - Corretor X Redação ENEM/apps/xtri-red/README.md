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

- Ler casos em `entradas/caso-*`.
- Ler prompts/rubricas em `app-config/prompts`.
- Mostrar tema, status da transcrição e prévia da redação.
- Rodar dry-run ou correção real chamando `scripts/run_caso_sabia.sh`.
- Abrir o Excel gerado.

## Segurança

A chave `SABIA_API_KEY` não deve ser hardcoded nem salva no Git. O app permite salvar a chave no Keychain do macOS pelo botão `Salvar`; nas próximas aberturas, ela é carregada automaticamente. Também é possível usar a variável de ambiente quando o app é iniciado pelo terminal.

Os runners de terminal também leem a mesma chave do Keychain. Depois de salvar uma vez no XTRI-RED, comandos como `scripts/run_caso_sabia.sh` funcionam sem exportar `SABIA_API_KEY`.
