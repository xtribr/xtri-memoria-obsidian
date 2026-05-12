# Roadmap - Banco de Questões

## Objetivo

Organizar as próximas entregas do Banco de Questões XTRI a partir de requisitos, auditorias e backlog já registrados na wiki.

## Status

- status: rascunho
- última revisão: 2026-05-12
- fonte: [[Backlog - Banco de Questões]], [[Requisitos - Banco de Questões XTRI]], [[Auditoria - Schema Real Banco de Questões]] e [[Auditoria - API Própria Questões XTRI]]

## Fatos verificados

- Existe backlog priorizado em [[Backlog - Banco de Questões]].
- Existem requisitos técnicos em [[Requisitos - Banco de Questões XTRI]].
- A API própria foi auditada em chamadas controladas em [[Auditoria - API Própria Questões XTRI]].
- O schema do Supabase `banco de questões` foi auditado parcialmente em [[Auditoria - Schema Real Banco de Questões]].

## Fases propostas

### Fase 1 - Segurança e governança

- Revisar exposição pública de gabarito na [[API Própria - Questões XTRI]].
- Auditar RLS, policies, triggers e funções SQL quando houver acesso seguro.
- Definir regra de exposição para `correctAlternative` e `isCorrect`.

### Fase 2 - Consistência de dados

- Completar campos nulos críticos em questões recentes, especialmente `skill` e parâmetros TRI quando aplicável.
- Documentar origem por ano/prova/caderno/item.
- Registrar limitações de itens sem matriz divulgada.

### Fase 3 - Produto e uso pedagógico

- Separar visão professor/aluno/admin para gabarito, resolução e metadados TRI.
- Definir quais campos entram em treino, simulado, relatório e análise TRI.
- Integrar requisitos de suporte visual, alternativas e habilidades.

### Fase 4 - Auditoria contínua

- Criar rotina de lint de dados: item sem habilidade, alternativa sem gabarito, imagem quebrada, parâmetro TRI ausente e fonte incompleta.
- Registrar resultados sem expor dados pessoais.
- Atualizar [[Checklist - Auditoria do Schema Banco de Questões]] após cada rodada.

## Hipóteses

- O banco de questões será consumido por múltiplos produtos XTRI.
- A política de exposição de gabarito precisa variar por contexto de uso.

## Pendências

- Confirmar decisão de produto sobre gabarito público.
- Confirmar acesso seguro para auditoria de RLS.
- Transformar fases em issues ou tarefas por repositório quando o GitHub do projeto for confirmado.

## Notas relacionadas

- [[Backlog - Banco de Questões]]
- [[Requisitos - Banco de Questões XTRI]]
- [[Auditoria - Schema Real Banco de Questões]]
- [[Auditoria - API Própria Questões XTRI]]
- [[Mapa Operacional de Projetos XTRI]]
