# log

Registro cronológico append-only da LLM Wiki da XTRI.

Use o padrão:

```text
## [AAAA-MM-DD] tipo | título
```

## [2026-05-12] setup | Estrutura inicial da memória XTRI

Criadas pastas principais do vault, notas institucionais, notas de stack, glossário ENEM/TRI/SISU, fontes oficiais, projetos ativos, decisões e templates.

Notas principais:

- [[Memória XTRI - Índice]]
- [[XTRI - Visão Geral]]
- [[Regras Operacionais do Codex na XTRI]]
- [[Stack Oficial da XTRI]]

## [2026-05-12] ingest | Inventário Supabase da XTRI

Inventariados 7 projetos Supabase da organização `eazfgctzojzsbojaxgdo` via CLI, registrando apenas metadados seguros.

Notas principais:

- [[Supabase - Inventário de Projetos]]
- [[Supabase - Projeto qgqliquusdkkwnfuzdwi]]
- [[Supabase - banco de questões]]

## [2026-05-12] ingest | Acervo PDFS TRI ARTIGOS

Catalogados 18 PDFs sobre TRI, ENEM, psicometria, IA, PLN, aprendizagem e dashboards. Criado índice na pasta de fontes e nota de acervo no vault principal.

Notas principais:

- [[Acervo de Artigos TRI e ENEM]]
- [[Síntese - Artigos TRI e ENEM para XTRI]]

## [2026-05-12] ingest | Resumos dos artigos TRI e ENEM

Criados 18 resumos de artigos com foco em pontos úteis para a XTRI e conexões com projetos, Supabase e requisitos de produto.

Nota principal:

- [[Síntese - Artigos TRI e ENEM para XTRI]]

## [2026-05-12] analysis | Requisitos do Banco de Questões XTRI

Transformada a síntese dos artigos em requisitos técnicos para o banco de questões, incluindo item, alternativas, aplicação, caderno, posição, suporte visual, desempenho, psicometria, IA e governança.

Notas principais:

- [[Requisitos - Banco de Questões XTRI]]
- [[Checklist - Auditoria do Schema Banco de Questões]]

## [2026-05-12] audit | Schema real do Supabase banco de questões

Auditado o schema exposto do projeto `fbykcqcssykopvcrsfoo` sem exportar dados reais. Identificadas tabelas, views, buckets, Edge Functions, lacunas e riscos.

Notas principais:

- [[Auditoria - Schema Real Banco de Questões]]
- [[Checklist - Auditoria do Schema Banco de Questões]]

Bloqueio:

- RLS, policies, triggers e funções SQL internas exigem `SUPABASE_DB_PASSWORD`.

## [2026-05-12] ingest | API Própria de Questões XTRI

Registrada a API própria `https://api.questoes.xtri.online/api/docs/` como ativo crítico. Mapeado OpenAPI público com endpoints, filtros e schemas principais.

Nota principal:

- [[API Própria - Questões XTRI]]

## [2026-05-12] setup | Instanciação do padrão LLM Wiki

Criados arquivos operacionais para transformar o vault em uma LLM Wiki persistente: schema para agentes, índice operacional, log cronológico, SOP e templates.

Arquivos principais:

- [[AGENTS]]
- [[index]]
- [[log]]
- [[LLM Wiki - Operação da Memória XTRI]]

## [2026-05-12] planning | Backlog do Banco de Questões

Criado backlog priorizado a partir das lacunas de [[Auditoria - Schema Real Banco de Questões]], [[API Própria - Questões XTRI]] e [[Requisitos - Banco de Questões XTRI]].

Nota principal:

- [[Backlog - Banco de Questões]]

Próximas ações:

- Criar [[Roadmap - Banco de Questões]].
- Auditar respostas reais controladas da [[API Própria - Questões XTRI]].

## [2026-05-12] audit | Respostas reais controladas da API Própria de Questões

Auditadas chamadas pequenas da [[API Própria - Questões XTRI]] sem varrer a base: anos, provas, questões paginadas, habilidades, detalhe por ID, detalhe por ano/slug, filtros e CORS.

Nota principal:

- [[Auditoria - API Própria Questões XTRI]]

Achados principais:

- API funcional e paginada.
- `correctAlternative` e `isCorrect` expostos publicamente.
- CORS não liberou `https://xtri.online` nos testes.
- Questões recentes podem ter `skill` e `param_b` nulos.

## [2026-05-12] manutenção | Índices, status e mapa operacional

Criadas notas estruturais para melhorar navegação e governança da wiki: índices por pasta crítica, convenções de status/evidência e mapa operacional de projetos.

Notas criadas:

- [[Índice - Produtos e Projetos]]
- [[Mapa Operacional de Projetos XTRI]]
- [[Índice - Dados e Fontes]]
- [[Índice - ENEM, TRI e SISU]]
- [[Convenções de Status e Evidência]]

Observação:

- O volume `/Volumes/KINGSTON` não estava montado durante a revisão; caminhos locais de projetos foram marcados como pendentes de confirmação, não como fatos verificados.
