# Convenções de Status e Evidência

## Objetivo

Padronizar como a wiki diferencia fato verificado, hipótese, pendência e decisão, evitando que dado incompleto vire verdade operacional.

## Status

- status: ativo
- última revisão: 2026-05-12
- fonte: [[AGENTS]] e prática operacional da LLM Wiki

## Status de notas

- `rascunho`: nota útil, mas ainda incompleta.
- `validado`: conteúdo revisado contra fonte real registrada.
- `em auditoria`: conteúdo em revisão, com lacunas conhecidas.
- `bloqueado`: falta acesso, credencial, arquivo, volume ou decisão.
- `ativo`: usado na operação atual.
- `arquivado`: mantido por histórico, sem uso operacional ativo.
- `hipótese`: inferência plausível, ainda não confirmada.

## Grau de evidência

- `fato verificado`: confirmado em fonte acessada, arquivo local, API, banco, commit ou documento.
- `dado real, acesso parcial`: veio de fonte real, mas sem auditoria completa.
- `hipótese operacional`: inferência útil, explicitamente não confirmada.
- `pendência`: algo necessário para fechar uma análise.
- `decisão`: escolha assumida pela operação ou arquitetura, registrada em `09 - Decisões`.

## Campos mínimos para notas críticas

- objetivo:
- fonte ou origem:
- status:
- data da revisão:
- responsável:
- conexões:
- limitações:
- próxima ação:

## Separação obrigatória

Use seções explícitas quando houver risco de confusão:

### Fatos verificados

Conteúdo confirmado por fonte real.

### Hipóteses

Inferências úteis, mas não confirmadas.

### Pendências

O que falta para validar ou executar.

## Dados educacionais

- Não inventar N, notas, scores, cortes, contagens ou estatísticas.
- Sempre registrar fonte e data.
- Sempre explicitar N amostral quando houver análise.
- Se o dado real não estiver acessível, registrar bloqueio e perguntar ao usuário.

## Notas relacionadas

- [[AGENTS]]
- [[LLM Wiki - Operação da Memória XTRI]]
- [[Template - Nota Canônica]]
- [[Template - Fonte Ingerida]]
- [[Template - Lint da Wiki]]

