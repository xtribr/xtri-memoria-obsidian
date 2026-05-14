# App Mac Corretor X

Status: protótipo funcional

## Objetivo

Operar correções em lote no macOS usando o vault do Obsidian como cérebro metodológico.

## Papel do app

- Listar casos em `entradas/caso-*`.
- Mostrar tema, status de transcrição e prévia da redação.
- Ler prompts/rubricas em `app-config/prompts`.
- Executar dry-run e correção real via `scripts/run_caso_sabia.sh`.
- Abrir o Excel gerado em `Cérebro do 1000/casos/exports`.

## Papel do Obsidian

O Obsidian continua sendo a fonte de governança:

- rubricas;
- prompts por competência;
- banco de casos;
- decisões de calibração;
- registro de limitações e validações humanas.

## Local do app

- `apps/corretor-x-mac`

## Rodar

```bash
cd "/Volumes/KINGSTON 2/apps/apps/corretor de redação/corretor x/11 - Corretor X Redação ENEM/apps/corretor-x-mac"
swift run
```

## Regra de segurança

A chave `SABIA_API_KEY` não deve ser salva no Git. O app aceita a chave em campo seguro apenas para a sessão ou herda a variável de ambiente quando iniciado pelo terminal.

## Conexões

- [[12 - Integração Sabiá]]
- [[03 - Banco de Casos Corrigidos]]
- [[05 - Calibração por Competência]]
