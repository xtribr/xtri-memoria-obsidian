# Supabase - banco de questões

## Classificação

- Tipo: projeto Supabase
- Nome: `banco de questões`
- Project ref: `fbykcqcssykopvcrsfoo`
- URL pública: https://fbykcqcssykopvcrsfoo.supabase.co
- Organização: `eazfgctzojzsbojaxgdo`
- Região: West US (Oregon)
- Status: `ACTIVE_HEALTHY`
- Criado em UTC: 2026-03-17 13:21:50
- Banco: PostgreSQL 17 / 17.6.1.084
- Host do banco: `db.fbykcqcssykopvcrsfoo.supabase.co`

## Finalidade

Pendente de validação.

Hipótese pelo nome: projeto relacionado ao acervo de questões, itens, alternativas, gabaritos, habilidades e metadados pedagógicos. Confirmar antes de usar como fonte oficial.

## Ponto de atenção

Este projeto está em região fora do Brasil. Se armazenar dados pessoais, respostas individuais ou desempenho de alunos, registrar análise de governança e requisitos operacionais antes de ampliar uso em produção.

## O que documentar

- Origem das questões
- Direitos de uso
- Tabelas de itens, alternativas, habilidades e provas
- Parâmetros TRI, se existirem
- RLS e permissões de leitura/escrita

## Requisitos técnicos derivados dos artigos

- Nota canônica: [[Requisitos - Banco de Questões XTRI]]
- Checklist de auditoria: [[Checklist - Auditoria do Schema Banco de Questões]]
- Auditoria do schema real: [[Auditoria - Schema Real Banco de Questões]]
- API própria relacionada: [[API Própria - Questões XTRI]]
- Base conceitual: [[Síntese - Artigos TRI e ENEM para XTRI]]

### Campos mínimos que o banco deve suportar

- Item: enunciado, área, disciplina, competência, habilidade, origem, ano, direitos de uso e status.
- Alternativas: texto, ordem, gabarito, tipo de distrator e justificativa pedagógica.
- Aplicação: prova, simulado, caderno, posição, ordem da área e data.
- Suporte visual: tipo, arquivo, descrição textual, OCR/transcrição e revisão humana.
- Desempenho: taxa de acerto, distribuição por alternativa, amostra, discriminação e método de cálculo.
- Psicometria: modelo, parâmetros `a`, `b`, `c`, erro, ajuste, amostra, fonte e data.
- IA/PLN: modelo, tarefa, saída estruturada, confiança, prompt e validação humana.

## Segurança

Não registrar chaves, tokens, senhas, dumps ou dados pessoais nesta nota.

## Notas relacionadas

- [[Supabase - Inventário de Projetos]]
- [[Glossário ENEM, TRI e SISU]]
- [[Fontes de Dados Oficiais]]
- [[Requisitos - Banco de Questões XTRI]]
- [[Checklist - Auditoria do Schema Banco de Questões]]
- [[Auditoria - Schema Real Banco de Questões]]
- [[API Própria - Questões XTRI]]
