# Vault Questões ENEM - Histórico API

## Classificação

- Tipo: vault Obsidian gerado por pipeline
- Repositório: `xtribr/xtri-memoria-obsidian`
- Branch: `itens-enem-historico`
- Commit inicial: `fd1373e` (2026-05-17 06:05 BRT)
- Fonte de dados: API pública `https://api.questoes.xtri.online/api/`
- Stack do pipeline: Python 3 + urllib + Claude para classificação
- Status: `validado` (Fase 6 concluída)
- Última revisão: 2026-05-18

## Finalidade

Materializar como notas Obsidian (uma por questão) todas as questões ENEM oficiais disponíveis na [[API Própria - Questões XTRI]], com classificação curada por disciplina e área alinhada à [[Padrão - Mapeamento de Simulados ENEM Dia 1]] e à taxonomia `SIMULADOS 2026 xtri`.

## Volumetria

- 3.123 questões
- 17 edições (2009–2025)
- 4 áreas (LC, CH, CN, MT)
- 14 disciplinas curadas
- 120 habilidades INEP mapeadas
- 3.292 arquivos totais, 14 MB sem `.git`

## Pipeline de classificação (6 fases)

- `_build_vault.py` (738 LoC): puxa API, gera notas .md com frontmatter
- Fase 3 (`_phase3_*.py`): OCR + spotcheck
- Fase 4 (`_phase4_*.py`): aplicação + correções manuais do usuário
- Fase 5 (`_phase5_*.py`): refinamento
- Fase 6 (`_phase6_*.py`): classificação canônica via Claude lendo o texto da API
- Fase 7 (`_phase7_index_refresh.py`): regeneração idempotente do `_index.md`

A Fase 6 sobrescreve TODAS as classificações anteriores. Fonte canônica única: `disciplina_fonte: phase6-text-claude`.

## Estado pós-Fase 6 (validado em 2026-05-18)

### Confiança da classificação

- 🟢 `text-high`: 2.989 (95,7%)
- 🟡 `text-medium`: 130 (4,2%)
- 🟠 `text-low`: 2 (0,06%)
- ⚪ legacy (pré-Fase 6): 2 (0,06%)

### Cobertura de campos críticos

- `correctAlternative` (gabarito): 3.123 (100%)
- `skill` (habilidade INEP): 2.849 (91,2%)
- `param_b` (dificuldade TRI): 2.523 (80,8%)
- `param_a` (discriminação TRI): 2.522 (80,8%)
- `param_c` (acerto ao acaso): 2.522 (80,8%)

### Distribuição por disciplina

| Disciplina | Qtd |
|---|---:|
| Matemática | 759 |
| Português | 344 |
| História | 278 |
| Biologia | 265 |
| Geografia | 260 |
| Química | 251 |
| Física | 236 |
| Literatura | 187 |
| Sociologia | 117 |
| Filosofia | 107 |
| Arte | 95 |
| Espanhol | 80 |
| Inglês | 78 |
| Educação Física | 66 |

### Distribuição por área

- LC: 850 (27,2%)
- CH: 762 (24,4%)
- MT: 759 (24,3%)
- CN: 752 (24,1%)

## Diff com Supabase `banco de questões` (tabela `itens`)

Auditoria cruzada feita em 2026-05-18 contra o projeto `fbykcqcssykopvcrsfoo`:

| Métrica | API XTRI (este vault) | Supabase `itens` |
|---|---:|---:|
| Total | 3.123 | 3.686 |
| Anos cobertos | 2009–2025 (17) | 2010–2024 (15) |
| Aplicação regular | 3.123 | 3.402 |
| Reaplicações | 0 | 284 |
| Itens abandonados | — | 44 |
| TRI completo (`param_b`) | 80,8% | 98,8% |
| Range de ID | 14546–17672 (`id` da API) | 5773–150767 (`co_item` INEP) |

### Conclusões da auditoria

- ✅ A API e a tabela `itens` do Supabase são **bases parcialmente disjuntas**, não duplicatas.
- ✅ A API tem **2009 e 2025**, que o Supabase ainda **não tem**.
- ✅ O Supabase tem **reaplicações + ENEM Digital 2020**, que a API **não tem**.
- ⚠️ Os IDs são **incompatíveis**: a API usa ID interno do Django (14546–17672); o Supabase usa o `co_item` oficial do INEP (5773–150767).
- ⚠️ O Supabase tem TRI muito mais completo (3.641/3.686 = 98,8%) do que a API (2.523/3.123 = 80,8%).
- 🔴 **Não é possível fazer JOIN direto pelo ID**. Matching exige chave composta `(ano, sg_area, co_habilidade, ordem_caderno)`.

## Riscos e pendências

- **Sub-disciplinas de Matemática não materializadas**: 759 questões classificadas só como "Matemática", sem distinguir Geometria/Álgebra/Funções/Estatística etc. Fase 7+ deve refinar.
- **TRI ausente em 600 questões da API** (~19%): pode ser importado do Supabase via join por chave composta.
- **Skills ausentes em 274 questões** (~9%): investigar gap da API; possível inferência via Claude.
- **Duas questões com classificação legacy** (`disciplina_fonte: skill=H21` e `skill=H13`): re-rodar Fase 6 para fechar.
- **Path local hardcoded** em `_build_vault.py` e `_phase6_apply.py` (`/Users/home/Library/Mobile Documents/...`): parametrizar via env ou argumento.
- **Branch órfã**: `itens-enem-historico` está 1 commit à frente em conteúdo único e 48 commits atrás em features da `main`. Decidir estratégia: integrar como subdiretório do vault principal ou manter separado.

## Decisões pendentes (registrar em [[Decisões Arquiteturais]] quando tomadas)

- Política de merge: `itens-enem-historico` vira subdiretório (`12 - Banco de Questões ENEM/`) do vault principal, ou continua como branch separada?
- Política de sincronização: re-rodar `_build_vault.py` mensalmente, ou somente quando a API receber novo ENEM?
- Suplementação TRI: o Supabase preenche os gaps de `param_a/b/c` ausentes na API?

## Fontes

- API: `https://api.questoes.xtri.online/api/` ([[API Própria - Questões XTRI]])
- Supabase: projeto `fbykcqcssykopvcrsfoo` ([[Supabase - banco de questões]])
- Auditoria do schema do Supabase: [[Auditoria - Schema Real Banco de Questões]]
- Matriz INEP: 120 habilidades (30 por área) — `Skills/_index.md` da branch

## Segurança

- Não há credencial no vault (verificado: zero ocorrências de `sk-`, `ghp_`, `eyJ` em todo o branch).
- Path local de geração revela máquina pessoal do autor: aceitável para vault privado, parametrizar antes de tornar público.
- Frontmatter contém apenas dados pedagógicos públicos do ENEM — sem PII.

## Notas relacionadas

- [[Supabase - banco de questões]]
- [[API Própria - Questões XTRI]]
- [[Auditoria - Schema Real Banco de Questões]]
- [[Auditoria - API Própria Questões XTRI]]
- [[Requisitos - Banco de Questões XTRI]]
- [[Índice - Dados e Fontes]]
- [[Mapa Operacional de Projetos XTRI]]

## Próxima ação

1. Decidir política de merge da branch `itens-enem-historico` na `main`.
2. Cruzar IDs API↔Supabase via chave composta `(ano, sg_area, habilidade, posição)` para validar sobreposição real.
3. Importar `nu_param_b` do Supabase para as 600 questões da API que faltam TRI.
4. Criar `_phase8_subdisciplinas_matematica.py` para refinar as 759 questões de MT.
