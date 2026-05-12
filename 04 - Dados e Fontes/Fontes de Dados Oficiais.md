# Fontes de Dados Oficiais

## Regra principal

Nenhum dado deve ser tratado como oficial sem origem confirmada.

## Fontes mapeadas

### Dados fornecidos diretamente pelo Professor Xandão

- Uso permitido quando enviados ou validados explicitamente.
- Exigem contexto de origem, período e finalidade.

### Baserow

- Uso: gerenciamento de bases educacionais da XTRI
- Observação: pode conter dados de grande volume sobre candidatos ENEM
- Regra: token nunca deve ser exposto no frontend

### Supabase

- Uso: banco de dados principal para novos produtos
- Regra: RLS deve estar ativo nas tabelas com dados de usuário
- Inventário: [[Supabase - Inventário de Projetos]]

#### Projeto `qgqliquusdkkwnfuzdwi`

- Nota canônica: [[Supabase - Projeto qgqliquusdkkwnfuzdwi]]
- URL pública: https://qgqliquusdkkwnfuzdwi.supabase.co
- Classificação: projeto crítico da XTRI
- Regra: documentar arquitetura e metadados; não registrar chaves nem dados sensíveis no Obsidian

### WordPress / MySQL

- Uso: dados do site legado e conteúdo institucional

## Metadados recomendados para qualquer base

- Origem
- Responsável
- Período coberto
- Estrutura dos campos
- Sensibilidade dos dados
- Restrições legais ou operacionais

## Notas relacionadas

- [[Regras Operacionais do Codex na XTRI]]
- [[Stack Oficial da XTRI]]
- [[Glossário ENEM, TRI e SISU]]
