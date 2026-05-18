---
type: Note
generated_at: 2026-05-18
generator: _phase7_index_refresh.py
canonical_source: phase6-text-claude
---
# Questões ENEM — Memória completa

Vault com **3.123 questões** de **17 edições** do ENEM, sincronizadas com [`api.questoes.xtri.online`](https://api.questoes.xtri.online/api/docs/).

> **Fonte canônica**: classificação Fase 6 (Claude lendo `context + alternativesIntroduction + alternatives` do detail endpoint). Esta é a versão definitiva — sobrescreve Fases 1–5.

## Estrutura

- [[Exams/_index|Exams]] — edições
- [[Disciplines/_index|Disciplines]] — 4 áreas
- [[Skills/_index|Skills]] — 120 habilidades INEP
- `Questions/` — 3.123 notas
- [[_taxonomia]] — taxonomia de disciplinas
- [[_api-spec]] — contrato da API XTRI

## Status da classificação (real)

| Confiança | Qtd | % |
|---|---:|---:|
| 🟢 `text-high` | 2.989 | 95,7% |
| 🟡 `text-medium` | 130 | 4,2% |
| 🟠 `text-low` | 2 | 0,1% |
| ⚪ `alta` | 1 | 0,0% |
| ⚪ `media` | 1 | 0,0% |
| **Total** | **3.123** | **100,0%** |

## Distribuição por disciplina

| Disciplina | Questões | % |
|---|---:|---:|
| Matemática | 759 | 24,3% |
| Português | 344 | 11,0% |
| História | 278 | 8,9% |
| Biologia | 265 | 8,5% |
| Geografia | 260 | 8,3% |
| Química | 251 | 8,0% |
| Física | 236 | 7,6% |
| Literatura | 187 | 6,0% |
| Sociologia | 117 | 3,7% |
| Filosofia | 107 | 3,4% |
| Arte | 95 | 3,0% |
| Espanhol | 80 | 2,6% |
| Inglês | 78 | 2,5% |
| Educação Física | 66 | 2,1% |
| **Total** | **3.123** | **100,0%** |

## Distribuição por área

| Área | Questões | % |
|---|---:|---:|
| LC — Linguagens, Códigos e suas Tecnologias | 850 | 27,2% |
| CH — Ciências Humanas e suas Tecnologias | 762 | 24,4% |
| MT — Matemática e suas Tecnologias | 759 | 24,3% |
| CN — Ciências da Natureza e suas Tecnologias | 752 | 24,1% |

## Cobertura por ano

| Ano | Questões | LC | CH | CN | MT |
|---|---:|---:|---:|---:|---:|
| [[enem-2009|2009]] | 179 | 45 | 48 | 41 | 45 |
| [[enem-2010|2010]] | 185 | 49 | 48 | 43 | 45 |
| [[enem-2011|2011]] | 184 | 50 | 44 | 45 | 45 |
| [[enem-2012|2012]] | 185 | 50 | 46 | 44 | 45 |
| [[enem-2013|2013]] | 185 | 50 | 45 | 45 | 45 |
| [[enem-2014|2014]] | 185 | 50 | 45 | 45 | 45 |
| [[enem-2015|2015]] | 184 | 50 | 45 | 45 | 44 |
| [[enem-2016|2016]] | 185 | 50 | 45 | 45 | 45 |
| [[enem-2017|2017]] | 185 | 52 | 43 | 45 | 45 |
| [[enem-2018|2018]] | 184 | 49 | 45 | 46 | 44 |
| [[enem-2019|2019]] | 181 | 51 | 43 | 42 | 45 |
| [[enem-2020|2020]] | 182 | 52 | 43 | 45 | 42 |
| [[enem-2021|2021]] | 185 | 49 | 46 | 45 | 45 |
| [[enem-2022|2022]] | 185 | 50 | 45 | 45 | 45 |
| [[enem-2023|2023]] | 183 | 49 | 45 | 44 | 45 |
| [[enem-2024|2024]] | 184 | 52 | 43 | 44 | 45 |
| [[enem-2025|2025]] | 182 | 52 | 43 | 43 | 44 |
| **Total** | **3.123** | **850** | **762** | **752** | **759** |

## Cobertura de campos críticos

| Campo | Preenchidos | % |
|---|---:|---:|
| `correctAlternative` (gabarito) | 3.123 | 100,0% |
| `skill` (habilidade INEP) | 2.849 | 91,2% |
| `param_b` (dificuldade TRI) | 2.523 | 80,8% |
| `param_a` (discriminação TRI) | 2.522 | 80,8% |
| `param_c` (acerto ao acaso) | 2.522 | 80,8% |

## Sincronização

Índice regenerado em **2026-05-18** por `_phase7_index_refresh.py`.
Para re-rodar: `python3 _phase7_index_refresh.py` na raiz do vault.
Para preview sem sobrescrever: `python3 _phase7_index_refresh.py --out _index_preview.md`.
