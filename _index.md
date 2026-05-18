---
type: Note
---
# Questões ENEM — Memória completa

Vault com **3,123 questões** de **17 edições** do ENEM (2009–2025), sincronizadas com [`api.questoes.xtri.online`](https://api.questoes.xtri.online/api/docs/).

## Estrutura

- [[Exams/_index|Exams]] — 17 edições
- [[Disciplines/_index|Disciplines]] — 4 áreas
- [[Skills/_index|Skills]] — 120 habilidades INEP
- `Questions/` — 3,123 notas (uma por questão, agrupadas por ano)
- [[_taxonomia]] — taxonomia de disciplinas alinhada com `SIMULADOS 2026 xtri`

## Classificação por disciplina (Fase 1 + 2)

| Confiança | Qtd | % |
|---|---|---|
| 🟢 alta (determinístico) | 1,516 | 48.5% |
| 🟡 média (skill aponta mas tem ruído) | 511 | 16.4% |
| 🔴 indeterminada (precisa OCR) | 1,096 | 35.1% |

### Distribuição por disciplina

| Disciplina | Questões |
|---|---|
| indeterminada | 1,096 |
| Matemática | 731 |
| Geografia | 269 |
| Português | 224 |
| Biologia | 162 |
| Literatura | 104 |
| Física | 81 |
| Espanhol | 77 |
| Química | 75 |
| Arte | 74 |
| Inglês | 72 |
| Sociologia | 66 |
| Educação Física | 57 |
| Filosofia | 35 |

## Cobertura por ano

| Ano | Questões | LC | CH | CN | MT |
|---|---|---|---|---|---|
| [[enem-2009|2009]] | 179 | 40 | 59 | 38 | 42 |
| [[enem-2010|2010]] | 185 | 17 | 79 | 44 | 45 |
| [[enem-2011|2011]] | 184 | 49 | 53 | 44 | 38 |
| [[enem-2012|2012]] | 185 | 50 | 49 | 44 | 42 |
| [[enem-2013|2013]] | 185 | 50 | 54 | 39 | 42 |
| [[enem-2014|2014]] | 185 | 50 | 50 | 40 | 45 |
| [[enem-2015|2015]] | 184 | 48 | 53 | 41 | 42 |
| [[enem-2016|2016]] | 185 | 50 | 47 | 43 | 45 |
| [[enem-2017|2017]] | 185 | 46 | 55 | 41 | 43 |
| [[enem-2018|2018]] | 184 | 49 | 50 | 43 | 42 |
| [[enem-2019|2019]] | 181 | 48 | 50 | 39 | 44 |
| [[enem-2020|2020]] | 182 | 48 | 49 | 45 | 40 |
| [[enem-2021|2021]] | 185 | 45 | 56 | 41 | 43 |
| [[enem-2022|2022]] | 185 | 48 | 50 | 43 | 44 |
| [[enem-2023|2023]] | 183 | 49 | 55 | 34 | 45 |
| [[enem-2024|2024]] | 184 | 50 | 45 | 44 | 45 |
| [[enem-2025|2025]] | 182 | 50 | 45 | 43 | 44 |

## Cobertura da API (verificada na geração)

- `skill` populado em **2,849 / 3,123** (91.2%)
- `param_b` (TRI) populado em **2,523 / 3,123** (80.8%)

## Próximos passos

- **Fase 3 (pendente de aprovação)**: OCR + LLM para resolver as 1,096 questões indeterminadas. Custo estimado: ~US$ 5, ~2h de execução.
- Veja [[_api-spec]] para o contrato completo

## Sincronização

Vault gerado em 2026-05-17 via `_build_vault.py` (idempotente — re-rodar = re-sincronizar).
