# Checklist - Auditoria do Schema Banco de Questões

## Objetivo

Comparar o schema real do Supabase `banco de questões` com os requisitos definidos em [[Requisitos - Banco de Questões XTRI]].

## Projeto

- Supabase: [[Supabase - banco de questões]]
- Project ref: `fbykcqcssykopvcrsfoo`
- Região: West US (Oregon)
- Status conhecido: `ACTIVE_HEALTHY`

## Regra de auditoria

Auditar schema, tabelas, colunas, políticas e funções. Não exportar registros reais de alunos, respostas individuais, tokens ou segredos.

## Resultado resumido

- Auditoria realizada em: 2026-05-12
- Relatório completo: [[Auditoria - Schema Real Banco de Questões]]
- Status geral: schema parcialmente aderente aos requisitos, com lacunas críticas em desempenho agregado, revisões, IA/PLN, governança psicométrica e confirmação de RLS.
- Bloqueio: dump completo de schema e policies exigiu `SUPABASE_DB_PASSWORD`.

## Checklist

### Inventário técnico

- [x] Listar relações expostas no schema público: 16 relações via PostgREST OpenAPI.
- [x] Listar views expostas: `v_itens_completo`.
- [ ] Listar schemas privados: bloqueado sem `SUPABASE_DB_PASSWORD`.
- [ ] Listar funções SQL internas: bloqueado sem `SUPABASE_DB_PASSWORD`.
- [ ] Listar triggers: bloqueado sem `SUPABASE_DB_PASSWORD`.
- [x] Listar buckets de Storage: `questoes-externas` e `questoes-enem`.
- [x] Listar Edge Functions relacionadas: `dynamic-processor`, `mentor-ia`, `monitor-bancoenem-users`.

### Questões

- [x] Existe tabela central para itens oficiais: `itens`.
- [x] Existe tabela para questões externas: `questoes_externas`.
- [x] Existe identificador interno estável: `itens.id`, `itens.co_item`, `questoes_externas.id`.
- [x] Existe origem da questão: `itens.fonte`, `questoes_externas.fonte`, `questoes_externas.vestibular`.
- [x] Existe ano de origem: `itens.ano`, `questoes_externas.ano`.
- [x] Existe área ENEM nos itens oficiais: `itens.sg_area`.
- [x] Existe disciplina ou componente em questões externas: `questoes_externas.disciplina`.
- [x] Existe competência via matriz: `competencias`, relacionada indiretamente por `habilidades`.
- [x] Existe habilidade em itens oficiais: `itens.co_habilidade`.
- [x] Existe enunciado separado das alternativas em `questoes_externas`.
- [x] Existe texto-base ou suporte textual separado em `questoes_externas`.
- [x] Existe campo de tipo de questão em `questoes_externas.tipo`.
- [ ] Existe status pedagógico/editorial: lacuna.
- [x] Existe status psicométrico parcial: `itens.in_item_aban` e `itens.tx_motivo_aban`.
- [ ] Existe controle de direitos de uso: lacuna.

### Alternativas e distratores

- [ ] Alternativas ficam em tabela separada: lacuna; hoje aparecem em `questoes_externas.alternativas` como `jsonb`.
- [ ] Cada alternativa preserva rótulo original: provável no JSON, mas não confirmado como coluna relacional.
- [x] Existe indicação de alternativa correta: `questoes_externas.gabarito` e `itens.tx_gabarito`.
- [ ] Existe ordem de exibição: provável no JSON, mas não confirmado como coluna relacional.
- [ ] Existe justificativa do distrator: lacuna.
- [ ] Existe explicação da alternativa correta: lacuna estruturada; apenas `tem_comentario_professor` indica possível comentário.

### Suporte visual

- [x] Existe indicação/caminho de suporte visual: `itens.link_imagem`, `questoes_externas.imagens`.
- [x] Existem buckets de imagens: `questoes-externas` e `questoes-enem`.
- [ ] Existe tipo de suporte visual: lacuna.
- [ ] Existe descrição textual acessível: lacuna.
- [ ] Existe OCR/transcrição quando aplicável: lacuna.
- [ ] Existe revisão humana da descrição visual: lacuna.

### Aplicações, caderno e posição

- [x] Existe histórico de aplicação por item oficial: `itens_prova`.
- [x] Existe prova vinculada: `itens_prova.co_prova`.
- [x] Existe caderno, cor ou versão: `itens_prova.tx_cor`.
- [x] Existe posição da questão no caderno: `itens_prova.co_posicao`.
- [ ] Existe ordem da área: lacuna como campo explícito.
- [ ] Existe distinção entre aplicação oficial, piloto, treino e simulado: lacuna.

### Desempenho agregado

- [ ] Existe amostra por aplicação: lacuna.
- [ ] Existe taxa de acerto: lacuna.
- [ ] Existe distribuição por alternativa: lacuna.
- [ ] Existe índice de discriminação ou equivalente: lacuna para desempenho agregado; há `nu_param_a` em `itens`.
- [ ] Existe correlação item-total ou equivalente: lacuna.
- [ ] Existe método de cálculo: lacuna.
- [ ] Existe data do cálculo: lacuna.
- [ ] Estatísticas são agregadas e não expõem aluno individual: não confirmado; há `user_sessions` com resultados individuais.

### Psicometria

- [x] Existe estrutura parcial para parâmetros psicométricos em `itens`.
- [ ] Existe campo para modelo: TCT, Rasch, 1PL, 2PL, 3PL, ML3, outro: lacuna.
- [x] Existe parâmetro `a`, quando aplicável: `itens.nu_param_a`.
- [x] Existe parâmetro `b`, quando aplicável: `itens.nu_param_b`.
- [x] Existe parâmetro `c`, quando aplicável: `itens.nu_param_c`.
- [ ] Existe erro padrão: lacuna.
- [ ] Existe estatística de ajuste: lacuna.
- [ ] Existe tamanho amostral: lacuna.
- [ ] Existe fonte da calibração: lacuna estruturada.
- [ ] Existe data da calibração: lacuna.
- [ ] Existe distinção entre parâmetro oficial, interno e experimental: lacuna.

### IA e PLN

- [ ] Existe tabela ou estrutura para anotações de IA: lacuna.
- [ ] Existe registro do modelo usado: lacuna.
- [ ] Existe versão de prompt: lacuna.
- [ ] Existe saída estruturada: lacuna.
- [ ] Existe confiança ou score, quando aplicável: lacuna.
- [ ] Existe validação humana: lacuna.
- [ ] IA não sobrescreve campo canônico sem revisão: não confirmado.

### Matriz e taxonomia

- [x] Existe tabela de matriz de competências e habilidades: `competencias` e `habilidades`.
- [ ] Existe fonte da matriz: lacuna estruturada.
- [ ] Existe controle de versão ou status ativo: lacuna.
- [x] Questões oficiais podem ter habilidade primária: `itens.co_habilidade`.
- [ ] Questões externas podem ter habilidade primária: lacuna.
- [ ] Questões podem ter habilidades secundárias, se necessário: lacuna.

### Segurança e governança

- [ ] RLS está ativo em tabelas sensíveis: bloqueado sem `SUPABASE_DB_PASSWORD`.
- [ ] Não há `service_role key` no frontend: não auditado nesta etapa.
- [ ] Dados pessoais não estão no banco de questões sem justificativa: risco; existem `user_profiles`, `user_sessions` e tabelas de gamificação.
- [x] Campos de auditoria existem em várias tabelas críticas: `created_at`, `updated_at` em parte do schema.
- [ ] Existem permissões por papel ou perfil: há `user_profiles.role`, mas policies não foram confirmadas.
- [x] Existe política parcial para item inadequado: `itens.in_item_aban` e `itens.tx_motivo_aban`.
- [ ] Existe rastreabilidade de origem e direito de uso: origem parcial; direitos de uso ausentes.

### Storage e Edge Functions

- [x] Bucket `questoes-externas` encontrado: público, 5 MB, MIME types de imagem restritos.
- [x] Bucket `questoes-enem` encontrado: público, sem limite e sem MIME types configurados.
- [x] Edge Function `dynamic-processor`: ativa, `verify_jwt = true`.
- [x] Edge Function `mentor-ia`: ativa, `verify_jwt = false`.
- [x] Edge Function `monitor-bancoenem-users`: ativa, `verify_jwt = false`.
- [ ] Revisar autenticação própria, CORS, rate limit e validação de entrada nas funções com `verify_jwt = false`.

## Resultado da auditoria

Preenchido com a auditoria parcial possível sem `SUPABASE_DB_PASSWORD`.

| Área | Status | Lacuna | Ação recomendada |
|---|---|---|---|
| Questões | Parcial | `itens` e `questoes_externas` cobrem partes diferentes do requisito | Unificar contrato canônico ou criar camada complementar |
| Alternativas | Parcial | Alternativas em `jsonb`, sem distratores estruturados | Criar `question_options` |
| Suporte visual | Parcial | Sem tipo, descrição acessível, OCR e revisão | Criar metadados visuais |
| Aplicações | Parcial bom | `itens_prova` cobre ENEM oficial, não simulados XTRI | Criar `question_applications` |
| Desempenho | Ausente | Sem estatísticas agregadas por item/aplicação | Criar `question_performance_stats` |
| Psicometria | Parcial | Tem `a`, `b`, `c`, mas sem método, amostra, erro e data | Criar `question_psychometrics` |
| IA e PLN | Ausente | Sem rastreio de modelo, prompt, saída e validação | Criar `question_ai_annotations` |
| Segurança | Crítico pendente | Dados de usuário no projeto; RLS não confirmado | Auditar policies com senha Postgres |

## Próxima ação técnica

Executar auditoria complementar de RLS, policies, triggers, funções SQL e constraints com `SUPABASE_DB_PASSWORD` definido apenas como variável de ambiente local.

## Notas relacionadas

- [[Requisitos - Banco de Questões XTRI]]
- [[Supabase - banco de questões]]
- [[Síntese - Artigos TRI e ENEM para XTRI]]
- [[Auditoria - Schema Real Banco de Questões]]
