# LLM Wiki - Operação da Memória XTRI

## Objetivo

Definir como a memória XTRI deve funcionar como uma LLM Wiki: uma wiki persistente, incremental e mantida por agente, em vez de um conjunto solto de documentos.

## Princípio central

A wiki deve acumular conhecimento. Cada fonte nova, pergunta relevante, auditoria ou decisão deve melhorar o estado permanente da memória.

## Arquitetura da memória

### Fontes brutas

São a base de verdade. O agente pode ler e referenciar, mas não deve alterar.

Exemplos:

- PDFs em `/Volumes/Kingston 1/OBSIDIAN/PDFS TRI ARTIGOS`
- OpenAPI da [[API Própria - Questões XTRI]]
- Metadados seguros dos projetos Supabase
- Arquivos fornecidos pelo Professor Xandão

### Wiki

É o vault `XTRI PROJETOS`. O agente cria e mantém as notas.

Exemplos:

- [[Supabase - banco de questões]]
- [[Requisitos - Banco de Questões XTRI]]
- [[Auditoria - Schema Real Banco de Questões]]
- [[Síntese - Artigos TRI e ENEM para XTRI]]

### Schema

São as regras que orientam o agente.

Arquivos:

- [[AGENTS]]
- [[index]]
- [[log]]
- [[Regras Operacionais do Codex na XTRI]]

## Operação: Ingest

Use quando houver uma fonte nova.

Passos:

1. Identificar a fonte e seu tipo.
2. Ler o conteúdo ou metadados relevantes.
3. Criar nota de fonte, resumo, auditoria ou entidade.
4. Atualizar notas canônicas afetadas.
5. Criar links bidirecionais.
6. Registrar lacunas e contradições.
7. Atualizar [[index]].
8. Adicionar entrada em [[log]].

Critério de conclusão:

- Fonte registrada.
- Links criados.
- Próxima ação explícita.
- Log atualizado.

## Operação: Query

Use quando o Professor Xandão fizer uma pergunta.

Passos:

1. Ler [[index]].
2. Buscar notas relevantes com `rg`.
3. Responder com base na wiki e nas fontes.
4. Se a resposta for reutilizável, criar ou atualizar nota.
5. Registrar no [[log]] quando gerar conhecimento persistente.

## Operação: Lint

Use periodicamente para saúde da wiki.

Verificar:

- links quebrados;
- notas órfãs;
- páginas sem fonte;
- notas críticas sem status;
- decisões importantes fora de `09 - Decisões`;
- dados sem metodologia;
- hipóteses tratadas como fatos;
- contradições entre fontes;
- riscos de segurança e LGPD;
- notas que deveriam virar backlog ou decisão.

## Convenções de arquivo

Notas canônicas:

- Nome claro e estável.
- Uma nota por entidade importante.
- Links para notas relacionadas.
- Status e próxima ação quando aplicável.

Resumos:

- Prefixo `Resumo -`.
- Fonte explícita.
- Pontos úteis para a XTRI.
- Limitações metodológicas.

Auditorias:

- Prefixo `Auditoria -`.
- Escopo.
- Método.
- Achados.
- Lacunas.
- Ações recomendadas.

Decisões:

- Prefixo `Decisão -`.
- Data.
- Contexto.
- Opções.
- Decisão.
- Impacto.
- Revisão futura.

## Regra de atualização

Ao mexer em qualquer assunto importante, verificar se também precisa atualizar:

- [[index]]
- [[log]]
- [[Memória XTRI - Índice]]
- nota canônica do projeto
- nota de decisão
- checklist ou auditoria relacionada

## Não fazer

- Não salvar credenciais.
- Não copiar bases sensíveis para o vault.
- Não inventar dados.
- Não criar conclusão estatística sem fonte e metodologia.
- Não deixar descoberta importante só no chat.
- Não deixar fonte nova sem entrada no [[log]].

## Próximas melhorias

- Criar `Backlog - Banco de Questões`.
- Criar `Roadmap - Banco de Questões`.
- Criar auditoria específica da [[API Própria - Questões XTRI]].
- Criar lint mensal da wiki.
- Avaliar uso de Dataview com frontmatter em notas futuras.
