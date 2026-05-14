# Corretor X Mac

App nativo macOS em SwiftUI para operar o Corretor X usando o vault do Obsidian como cérebro.

## Rodar em desenvolvimento

```bash
cd "/Volumes/KINGSTON 2/apps/apps/corretor de redação/corretor x/11 - Corretor X Redação ENEM/apps/corretor-x-mac"
swift run
```

## Função deste primeiro corte

- Ler casos em `entradas/caso-*`.
- Ler prompts/rubricas em `app-config/prompts`.
- Mostrar tema, status da transcrição e prévia da redação.
- Rodar dry-run ou correção real chamando `scripts/run_caso_sabia.sh`.
- Abrir o Excel gerado.

## Segurança

A chave `SABIA_API_KEY` não é salva pelo app. Ela pode ser digitada no campo seguro da interface ou herdada do ambiente quando o app é iniciado pelo terminal.
