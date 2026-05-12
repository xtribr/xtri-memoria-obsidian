# Índice - Dados e Fontes

## Objetivo

Centralizar fontes reais, bancos, APIs, auditorias, requisitos e restrições de dados usados pela XTRI.

## Status

- status: ativo
- última revisão: 2026-05-12
- fonte: organização interna da wiki e notas já ingeridas

## Regras

- Não registrar segredo, token, senha, `service_role key`, dump com dados pessoais ou resposta individual de aluno.
- Diferenciar fato verificado, hipótese operacional e pendência.
- Toda contagem, schema ou conclusão de dados precisa de fonte e data da coleta.
- Se a fonte não estiver disponível, marcar como `bloqueado` ou `pendente`, não inferir.

## Fontes e inventários

- [[Fontes de Dados Oficiais]] - fontes permitidas e restrições.
- [[Supabase - Inventário de Projetos]] - inventário dos projetos Supabase.
- [[API Própria - Questões XTRI]] - API pública própria de questões.

## Projetos Supabase

- [[Supabase - Projeto qgqliquusdkkwnfuzdwi]]
- [[Supabase - banco de questões]]
- [[Supabase - cronograma-de-estudos]]
- [[Supabase - sisu2025]]
- [[Supabase - xtri-escolas]]
- [[Supabase - xtri-gabaritos]]
- [[Supabase - xtri-provas-sp]]

## Auditorias e requisitos

- [[Auditoria - API Própria Questões XTRI]]
- [[Auditoria - Schema Real Banco de Questões]]
- [[Checklist - Auditoria do Schema Banco de Questões]]
- [[Requisitos - Banco de Questões XTRI]]

## Pipeline e linhagem de dados

- pendente: criar notas canônicas para linhagem SISU/INEP/ENEM, sync de escolas, scrapers SISU e bridge de habilidades quando as fontes forem verificadas.

## Campos mínimos para notas de dados

- fonte:
- data da coleta:
- método:
- N amostral ou contagem:
- sensibilidade:
- limitações:
- próxima ação:

## Pendências

- Auditar RLS/policies dos projetos críticos quando houver acesso seguro.
- Confirmar vínculo real entre frontends e Supabase por `.env` ou configuração de deploy.
- Registrar data e método em notas antigas que ainda estejam sem metadados completos.
