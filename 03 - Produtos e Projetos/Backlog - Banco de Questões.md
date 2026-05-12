# Backlog - Banco de Questões

## Objetivo

Transformar as lacunas identificadas em [[Auditoria - Schema Real Banco de Questões]], [[API Própria - Questões XTRI]] e [[Requisitos - Banco de Questões XTRI]] em trabalho executável.

## Status geral

- Produto: banco de questões ENEM/XTRI
- Supabase relacionado: [[Supabase - banco de questões]]
- API relacionada: [[API Própria - Questões XTRI]]
- Estado atual: em auditoria técnica
- Prioridade: alta

## Legenda

- `P0`: crítico, desbloqueia segurança ou decisão de arquitetura.
- `P1`: essencial para produto robusto.
- `P2`: importante, mas pode vir após fundação.
- `P3`: melhoria futura.

## Épico 1 - Segurança, LGPD e fronteira de dados

### P0 - Confirmar RLS e policies do Supabase

Status: bloqueado

Motivo:

- O projeto contém `user_profiles`, `user_sessions` e tabelas de gamificação.
- A auditoria não conseguiu confirmar RLS/policies sem `SUPABASE_DB_PASSWORD`.

Tarefas:

- Obter `SUPABASE_DB_PASSWORD` de forma segura, apenas como variável de ambiente local.
- Consultar `pg_policies`.
- Confirmar RLS em tabelas com dados de usuário.
- Documentar resultado em [[Auditoria - Schema Real Banco de Questões]].

Critério de aceite:

- Tabelas sensíveis classificadas.
- RLS/policies documentadas.
- Lacunas de segurança registradas com ação recomendada.

### P0 - Revisar Edge Functions públicas

Status: pendente

Funções:

- `mentor-ia`
- `monitor-bancoenem-users`

Motivo:

- Ambas aparecem com `verify_jwt = false`.

Tarefas:

- Revisar código das funções.
- Verificar autenticação própria.
- Verificar CORS.
- Verificar rate limit.
- Verificar validação de payload.
- Decidir se devem continuar públicas.

Critério de aceite:

- Cada função classificada como pública intencional, interna ou precisa de correção.
- Riscos documentados.
- Próximas ações definidas.

### P0 - Decidir fronteira entre banco de questões e dados de usuário

Status: pendente

Motivo:

- Um banco de questões ideal não deveria misturar conteúdo estável de itens com sessões e perfis de usuários sem justificativa clara.

Tarefas:

- Mapear quem consome `user_profiles`, `user_sessions` e gamificação.
- Decidir se esses dados permanecem no projeto atual.
- Se permanecerem, documentar finalidade e RLS.
- Se saírem, planejar migração.

Critério de aceite:

- Decisão registrada em `09 - Decisões`.
- Fronteira de dados documentada.

## Épico 2 - Contrato oficial de consulta via API

### P0 - Auditar respostas reais controladas da API própria

Status: concluído parcialmente

Motivo:

- A [[API Própria - Questões XTRI]] parece ser a interface mais limpa para consumo dos produtos.

Tarefas:

- [x] Testar `/api/years/`.
- [x] Testar `/api/exams/`.
- [x] Testar `/api/questions/?page=1`.
- [x] Testar uma questão por ID.
- [x] Testar filtros por `year`, `discipline`, `skill` e `param_b`.
- [x] Não baixar volume grande de dados.
- [x] Registrar relatório em [[Auditoria - API Própria Questões XTRI]].

Critério de aceite:

- Exemplos pequenos documentados.
- Campos reais comparados ao OpenAPI.
- Riscos de exposição de gabarito avaliados.

Resultado:

- API funcional.
- Risco de gabarito público identificado.
- Lacuna de CORS para `xtri.online` identificada.
- Completude de `skill` e `param_b` precisa de monitoramento por ano.

### P1 - Decidir se a API é interface oficial para produtos XTRI

Status: pendente

Tarefas:

- Comparar consumo direto do Supabase versus consumo via API.
- Avaliar cache, versionamento e estabilidade de contrato.
- Definir se produtos novos devem usar a API.

Critério de aceite:

- Decisão registrada em `09 - Decisões`.
- Padrão de integração documentado.

### P1 - Planejar versionamento da API

Status: pendente

Motivo:

- A API informa versão `1.0.0`, mas os paths não usam `/api/v1/`.

Tarefas:

- Definir política de breaking changes.
- Decidir se cria `/api/v1/`.
- Documentar campos estáveis.

Critério de aceite:

- Política de versionamento escrita.
- Campos críticos protegidos por contrato.

## Épico 3 - Normalização de questões e alternativas

### P1 - Criar `question_options`

Status: pendente

Motivo:

- `questoes_externas.alternativas` está em `jsonb`.
- A API já expõe alternativas estruturadas como `Alternative`.

Tarefas:

- Desenhar tabela relacional.
- Mapear dados existentes do JSON.
- Incluir `letter`, `text`, `image`, `file`, `localFile`, `is_correct`, `order_index`.
- Adicionar campos futuros de distrator.

Critério de aceite:

- Migration proposta.
- Plano de backfill sem perda de dados.
- Relação com API documentada.

### P1 - Criar estrutura de distratores

Status: pendente

Tarefas:

- Adicionar `distractor_type`.
- Adicionar `distractor_rationale`.
- Definir taxonomia inicial de erros.
- Permitir revisão humana.

Critério de aceite:

- Distratores podem virar feedback pedagógico.
- Estrutura não depende exclusivamente de IA.

### P1 - Vincular questões externas à matriz ENEM

Status: pendente

Motivo:

- `questoes_externas` não parece ligada a `habilidades` e `competencias`.

Tarefas:

- Criar relação entre questão externa e habilidade.
- Permitir habilidade primária.
- Avaliar habilidades secundárias.
- Registrar método da classificação: humano, IA, importação ou heurística.

Critério de aceite:

- Questões externas consultáveis por habilidade e competência.
- Método de classificação rastreável.

## Épico 4 - Psicometria, dificuldade e desempenho

### P1 - Criar `question_psychometrics`

Status: pendente

Motivo:

- `itens` guarda `a`, `b`, `c`, mas não método, erro, amostra, fonte e data.

Tarefas:

- Criar tabela de parâmetros psicométricos.
- Incluir modelo: TCT, Rasch, 1PL, 2PL, 3PL, ML3.
- Incluir `parameter_a`, `parameter_b`, `parameter_c`.
- Incluir `standard_error`, `fit_statistics`, `sample_size`, `calibration_source`, `calibration_date`, `software`, `is_official`.

Critério de aceite:

- Parâmetro oficial, interno e experimental distinguíveis.
- Dificuldade textual não confundida com parâmetro calibrado.

### P1 - Criar `question_performance_stats`

Status: pendente

Motivo:

- Não há estatísticas agregadas por item/aplicação.

Tarefas:

- Criar tabela agregada por questão e aplicação.
- Incluir `sample_size`, `correct_rate`, `option_distribution`, `discrimination_index`, `item_total_correlation`, `method`, `calculated_at`.
- Garantir que não exponha resposta individual de aluno.

Critério de aceite:

- Cada estatística tem método, data e amostra.
- Dados individuais permanecem fora do banco de questões ou protegidos por RLS.

### P2 - Padronizar dificuldade estimada

Status: pendente

Motivo:

- `questoes_externas.nivel_dificuldade` existe, mas sem método/confiança.

Tarefas:

- Criar campos ou tabela para dificuldade estimada.
- Registrar método: humano, IA, PLN, histórico, heurística.
- Registrar confiança.
- Separar dificuldade estimada de `param_b`.

Critério de aceite:

- Toda dificuldade tem origem explícita.

## Épico 5 - Aplicações, cadernos e posição

### P1 - Criar `question_applications`

Status: pendente

Motivo:

- `itens_prova` cobre ENEM oficial, mas não simulados, listas e aplicações XTRI.

Tarefas:

- Criar tabela genérica de aplicação.
- Incluir `question_id`, `exam_id`, `application_name`, `application_date`, `booklet_code`, `position_in_booklet`, `area_order`, `application_type`.
- Mapear relação com `itens_prova`.

Critério de aceite:

- A XTRI consegue saber onde, quando e em qual posição cada questão foi aplicada.

### P2 - Registrar ordem da área e contexto de prova

Status: pendente

Tarefas:

- Definir `area_order`.
- Registrar duração/bloco quando aplicável.
- Registrar se aplicação é oficial, piloto, treino, simulado ou lista.

Critério de aceite:

- Análises futuras conseguem controlar efeito de posição e cansaço.

## Épico 6 - Suporte visual e acessibilidade

### P1 - Criar metadados visuais por questão

Status: pendente

Motivo:

- Há imagens e arquivos, mas não descrição acessível, OCR, tipo visual e revisão.

Tarefas:

- Criar tabela ou campos de suporte visual.
- Incluir tipo: imagem, gráfico, tabela, mapa, charge, fórmula, diagrama.
- Incluir descrição textual.
- Incluir OCR/transcrição quando aplicável.
- Incluir revisão humana.

Critério de aceite:

- Questões multimodais ficam pesquisáveis, acessíveis e utilizáveis por IA com menor risco.

### P1 - Revisar buckets de Storage

Status: pendente

Motivo:

- `questoes-enem` está público sem limite e sem MIME types configurados.

Tarefas:

- Confirmar necessidade de buckets públicos.
- Definir limite de tamanho.
- Restringir MIME types.
- Documentar política de arquivos.

Critério de aceite:

- Buckets com exposição e limites justificados.

## Épico 7 - Revisão humana, direitos e governança editorial

### P1 - Criar `question_reviews`

Status: pendente

Tarefas:

- Criar revisão pedagógica.
- Criar revisão psicométrica.
- Criar revisão de direitos de uso.
- Criar revisão de IA.
- Registrar status, parecer, revisor e data.

Critério de aceite:

- Nenhuma questão pública fica sem status de revisão.

### P1 - Criar controle de direitos de uso

Status: pendente

Motivo:

- O schema tem origem parcial, mas não direito de uso formal.

Tarefas:

- Criar `rights_status`.
- Registrar fonte legal.
- Registrar restrição de uso.
- Registrar se pode aparecer em produto público.

Critério de aceite:

- Cada questão tem status jurídico/editorial claro.

## Épico 8 - IA, PLN e rastreabilidade

### P2 - Criar `question_ai_annotations`

Status: pendente

Motivo:

- Não há rastreio de IA/PLN no schema exposto.

Tarefas:

- Registrar modelo.
- Registrar tarefa.
- Registrar versão de prompt.
- Registrar saída estruturada.
- Registrar confiança.
- Registrar validação humana.

Critério de aceite:

- Toda anotação de IA é auditável e reversível.

### P2 - Criar benchmark interno de IA para questões ENEM

Status: pendente

Tarefas:

- Selecionar amostra pequena de questões.
- Separar por área, habilidade, suporte visual e dificuldade.
- Avaliar modelos com métrica.
- Registrar resultados sem expor dados sensíveis.

Critério de aceite:

- Escolha de modelo passa a ser baseada em evidência.

## Épico 9 - Documentação e decisões

### P1 - Criar roadmap do banco de questões

Status: pendente

Tarefas:

- Separar fases: segurança, contrato API, normalização, psicometria, IA.
- Definir ordem de implementação.
- Definir riscos e dependências.

Critério de aceite:

- Roadmap publicado no Obsidian.

### P1 - Registrar decisões técnicas

Status: pendente

Decisões necessárias:

- API própria será a interface oficial?
- Dados de usuário ficam neste Supabase?
- Alternativas serão normalizadas em tabela?
- Questões externas serão mapeadas para matriz ENEM?
- Buckets continuarão públicos?
- `correctAlternative` e `isCorrect` serão públicos?

Critério de aceite:

- Cada decisão crítica tem nota em `09 - Decisões`.

## Ordem recomendada de execução

1. P0 - Confirmar RLS e policies do Supabase.
2. P0 - Revisar Edge Functions públicas.
3. P0 - Definir política de exposição de gabarito da API.
4. P0 - Decidir fronteira entre banco de questões e dados de usuário.
5. P1 - Decidir se a API é interface oficial.
6. P1 - Criar roadmap.
7. P1 - Normalizar alternativas.
8. P1 - Criar psicometria formal.
9. P1 - Criar desempenho agregado.
10. P1 - Criar aplicações XTRI.
11. P1 - Criar metadados visuais.
12. P1 - Criar revisões e direitos de uso.
13. P2 - Criar anotações de IA.
14. P2 - Criar benchmark interno de IA.

## Próxima ação imediata

Criar [[Roadmap - Banco de Questões]] e registrar as decisões sobre gabarito público, API oficial, CORS de produção e versionamento.

## Notas relacionadas

- [[Supabase - banco de questões]]
- [[API Própria - Questões XTRI]]
- [[Requisitos - Banco de Questões XTRI]]
- [[Auditoria - Schema Real Banco de Questões]]
- [[Checklist - Auditoria do Schema Banco de Questões]]
- [[Síntese - Artigos TRI e ENEM para XTRI]]
