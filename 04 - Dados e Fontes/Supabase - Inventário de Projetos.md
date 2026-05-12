# Supabase - Inventário de Projetos

## Escopo

- Fonte: `supabase projects list --output json`
- Data da consulta: 2026-05-12
- Organização: `eazfgctzojzsbojaxgdo`
- Regra: inventário de metadados apenas, sem chaves, tokens, senhas ou dados de usuários.

## Projetos encontrados

| Projeto | Project ref | Região | Status | Criado em UTC | Banco | Nota |
|---|---|---|---|---|---|---|
| sisu2025 | `sisymqzxvuktdcbsbpbp` | South America (São Paulo) | `ACTIVE_HEALTHY` | 2026-01-16 23:25:41 | PostgreSQL 17 / 17.6.1.063 | [[Supabase - sisu2025]] |
| cronograma-de-estudos | `comwcnmvnuzqqbypjtqn` | South America (São Paulo) | `ACTIVE_HEALTHY` | 2026-03-27 09:46:54 | PostgreSQL 17 / 17.6.1.084 | [[Supabase - cronograma-de-estudos]] |
| banco de dados INEP ENEM SISU | `qgqliquusdkkwnfuzdwi` | South America (São Paulo) | `ACTIVE_HEALTHY` | 2026-03-28 09:59:05 | PostgreSQL 17 / 17.6.1.084 | [[Supabase - Projeto qgqliquusdkkwnfuzdwi]] |
| banco de questões | `fbykcqcssykopvcrsfoo` | West US (Oregon) | `ACTIVE_HEALTHY` | 2026-03-17 13:21:50 | PostgreSQL 17 / 17.6.1.084 | [[Supabase - banco de questões]] |
| xtri-provas-sp | `uhqdkaftqjxenobdfqkd` | South America (São Paulo) | `ACTIVE_HEALTHY` | 2025-12-29 00:34:36 | PostgreSQL 17 / 17.6.1.063 | [[Supabase - xtri-provas-sp]] |
| xtri-escolas | `rqzxcturezryjbwsptld` | South America (São Paulo) | `ACTIVE_HEALTHY` | 2025-12-29 21:38:12 | PostgreSQL 17 / 17.6.1.063 | [[Supabase - xtri-escolas]] |
| xtri-gabaritos | `axtmozyrnsrhqrnktshz` | South America (São Paulo) | `ACTIVE_HEALTHY` | 2026-01-06 19:54:44 | PostgreSQL 17 / 17.6.1.063 | [[Supabase - xtri-gabaritos]] |

## Observações iniciais

- Todos os projetos listados estão com status `ACTIVE_HEALTHY`.
- O projeto `banco de questões` está em `West US (Oregon)`; os demais estão em `South America (São Paulo)`.
- Se algum projeto em região fora do Brasil armazenar dados pessoais de alunos, registrar análise de governança, latência e requisitos legais antes de ampliar uso em produção.
- Nenhum projeto aparece vinculado ao diretório local atual pela CLI.

## Próximas ações recomendadas

- Confirmar a finalidade real de cada projeto.
- Vincular cada projeto ao repositório correspondente.
- Mapear tabelas críticas sem exportar registros reais.
- Registrar políticas de RLS e Edge Functions por projeto.
- Classificar quais projetos armazenam dados pessoais ou educacionais sensíveis.

## Notas relacionadas

- [[Fontes de Dados Oficiais]]
- [[Stack Oficial da XTRI]]
- [[Projetos Ativos]]
- [[Supabase - Projeto qgqliquusdkkwnfuzdwi]]
