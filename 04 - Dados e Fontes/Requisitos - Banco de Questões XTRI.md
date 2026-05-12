# Requisitos - Banco de Questões XTRI

## Objetivo

Definir os requisitos mínimos para o banco de questões da XTRI, conectando evidências dos artigos de TRI/ENEM com necessidades reais de produto, análise pedagógica, simulados, IA e governança estatística.

Este documento é uma especificação técnica. Ele não confirma que o schema atual do Supabase já possui esses campos.

## Projeto relacionado

- Supabase: [[Supabase - banco de questões]]
- API própria: [[API Própria - Questões XTRI]]
- Project ref: `fbykcqcssykopvcrsfoo`
- URL pública: https://fbykcqcssykopvcrsfoo.supabase.co
- Atenção: projeto está em `West US (Oregon)`. Se armazenar dados pessoais, respostas individuais ou desempenho de alunos, é necessário registrar análise de governança e LGPD.

## Princípios

- Uma questão é uma unidade pedagógica, psicométrica, operacional e estatística.
- O banco deve preservar histórico de aplicação, não apenas o enunciado.
- Dificuldade estimada não é parâmetro TRI calibrado.
- Item psicometricamente ruim pode ter valor pedagógico.
- IA pode apoiar classificação e explicação, mas deve deixar rastros de revisão humana.
- Nenhum dado pessoal de aluno deve entrar neste banco sem necessidade explícita, RLS e finalidade documentada.

## Entidades mínimas

### 1. `questions`

Tabela central de itens/questões.

Campos mínimos:

| Campo | Tipo sugerido | Obrigatório | Finalidade |
|---|---|---:|---|
| `id` | `uuid` | sim | Identificador interno |
| `external_id` | `text` | não | ID de origem, se houver |
| `source` | `text` | sim | Origem da questão: ENEM, XTRI, simulado, parceiro, outro |
| `source_year` | `integer` | não | Ano de origem |
| `source_exam` | `text` | não | Nome da prova ou aplicação |
| `area` | `text` | sim | Área ENEM |
| `discipline` | `text` | não | Disciplina ou componente |
| `competency_code` | `text` | não | Competência da matriz |
| `skill_code` | `text` | não | Habilidade da matriz |
| `content_tags` | `text[]` ou tabela relacional | não | Conteúdos e assuntos |
| `statement` | `text` | sim | Enunciado |
| `support_text` | `text` | não | Texto-base, se separado do enunciado |
| `command_text` | `text` | não | Comando da questão |
| `question_type` | `text` | sim | Múltipla escolha, discursiva, redação, outro |
| `language` | `text` | sim | Idioma principal |
| `has_visual_support` | `boolean` | sim | Indica imagem, gráfico, tabela, mapa ou figura |
| `visual_support_type` | `text` | não | Imagem, gráfico, tabela, mapa, charge, fórmula, diagrama |
| `visual_support_description` | `text` | não | Descrição textual acessível e útil para IA |
| `storage_path` | `text` | não | Caminho do arquivo no Supabase Storage |
| `estimated_difficulty` | `numeric` | não | Dificuldade inicial estimada antes de calibração |
| `estimated_difficulty_method` | `text` | não | Humana, PLN, histórico, modelo, heurística |
| `estimated_difficulty_confidence` | `numeric` | não | Confiança da estimativa, se houver |
| `official_answer` | `text` | não | Alternativa correta ou resposta oficial |
| `explanation` | `text` | não | Resolução validada |
| `pedagogical_notes` | `text` | não | Observações de aprendizagem, erros comuns e alertas |
| `psychometric_status` | `text` | sim | Status psicométrico do item |
| `pedagogical_status` | `text` | sim | Status pedagógico/editorial |
| `review_status` | `text` | sim | Rascunho, revisado, aprovado, arquivado |
| `rights_status` | `text` | sim | Direito de uso e origem legal |
| `created_at` | `timestamptz` | sim | Auditoria |
| `updated_at` | `timestamptz` | sim | Auditoria |

Regras:

- `statement` não deve misturar alternativa, gabarito e explicação.
- `estimated_difficulty` deve ser rotulada como estimativa quando não vier de aplicação real.
- `has_visual_support = true` exige `visual_support_type` e, quando possível, `visual_support_description`.
- Questões com origem externa precisam de `rights_status`.

### 2. `question_options`

Alternativas das questões objetivas.

Campos mínimos:

| Campo | Tipo sugerido | Obrigatório | Finalidade |
|---|---|---:|---|
| `id` | `uuid` | sim | Identificador |
| `question_id` | `uuid` | sim | Relação com `questions` |
| `label` | `text` | sim | A, B, C, D, E |
| `option_text` | `text` | sim | Texto da alternativa |
| `is_correct` | `boolean` | sim | Gabarito |
| `distractor_type` | `text` | não | Tipo de erro ou armadilha |
| `distractor_rationale` | `text` | não | Por que o aluno escolheria essa alternativa |
| `order_index` | `integer` | sim | Ordem de exibição |

Regras:

- Para questões ENEM, preservar rótulo original da alternativa.
- `distractor_rationale` é essencial para feedback e IA explicativa.
- Deve existir no máximo uma alternativa correta para item objetivo simples.

### 3. `question_applications`

Histórico de uso da questão em provas, simulados ou listas.

Campos mínimos:

| Campo | Tipo sugerido | Obrigatório | Finalidade |
|---|---|---:|---|
| `id` | `uuid` | sim | Identificador |
| `question_id` | `uuid` | sim | Questão aplicada |
| `exam_id` | `uuid` | não | Prova ou simulado |
| `application_name` | `text` | sim | Nome da aplicação |
| `application_date` | `date` | não | Data |
| `booklet_code` | `text` | não | Caderno, cor ou versão |
| `position_in_booklet` | `integer` | não | Posição da questão |
| `area_order` | `integer` | não | Ordem da área no caderno |
| `is_official_application` | `boolean` | sim | ENEM oficial ou aplicação XTRI |
| `created_at` | `timestamptz` | sim | Auditoria |

Regras:

- Uma mesma questão pode aparecer em várias aplicações.
- Posição e caderno devem ser preservados por causa dos efeitos de posição e dificuldade.
- Comparações de desempenho precisam considerar `booklet_code` e `position_in_booklet`.

### 4. `question_performance_stats`

Estatísticas agregadas de desempenho por questão e aplicação.

Campos mínimos:

| Campo | Tipo sugerido | Obrigatório | Finalidade |
|---|---|---:|---|
| `id` | `uuid` | sim | Identificador |
| `question_id` | `uuid` | sim | Questão |
| `application_id` | `uuid` | não | Aplicação específica |
| `sample_size` | `integer` | sim | Quantidade de respostas |
| `correct_rate` | `numeric` | não | Taxa de acerto |
| `option_distribution` | `jsonb` | não | Distribuição agregada por alternativa |
| `mean_score_group` | `numeric` | não | Média do grupo, se aplicável |
| `discrimination_index` | `numeric` | não | Índice clássico ou estimado |
| `item_total_correlation` | `numeric` | não | Correlação item-total |
| `guessing_indicator` | `numeric` | não | Indicador de chute ou comportamento anômalo |
| `calculated_at` | `timestamptz` | sim | Data do cálculo |
| `method` | `text` | sim | Método usado |

Regras:

- Guardar apenas estatísticas agregadas neste banco, salvo decisão explícita em contrário.
- Dados individuais de alunos pertencem a projeto com RLS próprio e finalidade documentada.
- Toda estatística precisa ter `sample_size` e `method`.

### 5. `question_psychometrics`

Parâmetros psicométricos e histórico de calibração.

Campos mínimos:

| Campo | Tipo sugerido | Obrigatório | Finalidade |
|---|---|---:|---|
| `id` | `uuid` | sim | Identificador |
| `question_id` | `uuid` | sim | Questão |
| `model` | `text` | sim | TCT, Rasch, 1PL, 2PL, 3PL, ML3, outro |
| `parameter_a` | `numeric` | não | Discriminação |
| `parameter_b` | `numeric` | não | Dificuldade |
| `parameter_c` | `numeric` | não | Acerto ao acaso |
| `standard_error` | `numeric` | não | Erro padrão |
| `fit_statistics` | `jsonb` | não | Estatísticas de ajuste |
| `sample_size` | `integer` | sim | Tamanho amostral |
| `calibration_source` | `text` | sim | Origem da calibração |
| `calibration_date` | `date` | sim | Data da calibração |
| `software` | `text` | não | mirt, BILOG, Winsteps, script próprio |
| `is_official` | `boolean` | sim | Parâmetro oficial ou interno |
| `notes` | `text` | não | Limitações e observações |

Regras:

- Não misturar parâmetro TRI calibrado com dificuldade estimada por texto.
- Parâmetros oficiais, internos e experimentais devem ser diferenciados.
- Calibração sem `sample_size`, método e fonte não deve ser usada para decisão sensível.

### 6. `question_reviews`

Revisões pedagógicas, editoriais, estatísticas e de IA.

Campos mínimos:

| Campo | Tipo sugerido | Obrigatório | Finalidade |
|---|---|---:|---|
| `id` | `uuid` | sim | Identificador |
| `question_id` | `uuid` | sim | Questão |
| `review_type` | `text` | sim | Pedagógica, psicométrica, linguística, IA, direitos |
| `reviewer_id` | `uuid` | não | Pessoa revisora, se houver |
| `reviewer_name` | `text` | não | Nome quando não houver usuário interno |
| `status` | `text` | sim | Aprovado, ajustar, rejeitado, arquivado |
| `notes` | `text` | não | Parecer |
| `reviewed_at` | `timestamptz` | sim | Data |

Regras:

- Classificação automática por IA deve gerar revisão ou flag, não aprovação final automática.
- Questões usadas em produto público precisam de revisão pedagógica e direitos de uso.

### 7. `question_ai_annotations`

Anotações produzidas por IA ou PLN.

Campos mínimos:

| Campo | Tipo sugerido | Obrigatório | Finalidade |
|---|---|---:|---|
| `id` | `uuid` | sim | Identificador |
| `question_id` | `uuid` | sim | Questão |
| `model_name` | `text` | sim | Modelo usado |
| `task` | `text` | sim | Classificação, explicação, dificuldade, embedding, OCR, descrição visual |
| `output` | `jsonb` | sim | Resultado estruturado |
| `confidence` | `numeric` | não | Confiança, se houver |
| `prompt_version` | `text` | não | Versão do prompt |
| `validated_by_human` | `boolean` | sim | Validação humana |
| `created_at` | `timestamptz` | sim | Auditoria |

Regras:

- Resultado de IA deve ser rastreável por modelo, prompt e data.
- IA não deve sobrescrever campos canônicos sem revisão humana.

### 8. `skills_matrix`

Matriz de competências, habilidades e conteúdos.

Campos mínimos:

| Campo | Tipo sugerido | Obrigatório | Finalidade |
|---|---|---:|---|
| `id` | `uuid` | sim | Identificador |
| `exam` | `text` | sim | ENEM, XTRI, outro |
| `area` | `text` | sim | Área |
| `competency_code` | `text` | não | Código da competência |
| `skill_code` | `text` | não | Código da habilidade |
| `description` | `text` | sim | Descrição oficial ou interna |
| `source` | `text` | sim | Origem da matriz |
| `active` | `boolean` | sim | Controle de versão |

Regras:

- A questão pode ter habilidade primária e habilidades secundárias.
- Não inventar matriz. Usar somente matriz oficial ou taxonomia interna validada.

## Status psicométrico recomendado

Valores sugeridos para `psychometric_status`:

- `not_evaluated`: ainda não avaliado.
- `estimated_only`: possui dificuldade estimada, sem aplicação real suficiente.
- `pilot_applied`: aplicado em piloto, amostra ainda insuficiente.
- `calibrated_internal`: calibrado internamente pela XTRI.
- `official_parameter`: possui parâmetro oficial conhecido e fonte documentada.
- `flagged_review`: comportamento estatístico exige revisão.
- `excluded_from_scoring`: não deve compor score, mas pode ter uso pedagógico.
- `archived`: não deve ser usado em novas aplicações.

## Status pedagógico recomendado

Valores sugeridos para `pedagogical_status`:

- `draft`: rascunho.
- `needs_review`: precisa de revisão.
- `approved`: aprovado para uso.
- `approved_with_notes`: aprovado com restrições.
- `diagnostic_only`: uso diagnóstico, não avaliativo.
- `rejected`: rejeitado.
- `archived`: arquivado.

## Requisitos de suporte visual

Questões com imagem, gráfico, tabela, mapa, charge, fórmula ou diagrama devem registrar:

- arquivo original ou caminho de storage;
- tipo de suporte visual;
- descrição textual acessível;
- indicação se a imagem é essencial para resolver;
- OCR ou transcrição quando aplicável;
- fonte e direito de uso;
- revisão humana da descrição.

Motivo:

- Artigos sobre GPT-4 Vision e ENEM mostram que questões multimodais precisam ser avaliadas separadamente.
- Descrições textuais podem ajudar IA e acessibilidade.
- Sem descrição, busca semântica e explicação automática ficam frágeis.

## Requisitos para posição, caderno e aplicação

Toda questão aplicada em prova ou simulado deve registrar:

- prova ou simulado;
- data;
- caderno, cor ou versão;
- posição no caderno;
- ordem da área;
- tempo ou bloco, se houver;
- se a aplicação é oficial, piloto ou treino.

Motivo:

- Artigos sobre posição e Rasch multifacetas indicam que posição, caderno e ordem podem afetar dificuldade e proficiência.

## Requisitos para histórico de desempenho

O banco de questões deve guardar estatísticas agregadas por item e aplicação:

- quantidade de respondentes;
- taxa de acerto;
- distribuição por alternativa;
- discriminação ou correlação item-total;
- flags de comportamento anômalo;
- método de cálculo;
- data do cálculo.

Motivo:

- Sem histórico de desempenho, a XTRI fica presa a dificuldade subjetiva.
- Sem agregação por aplicação, perde-se efeito de caderno, posição e público.

## Requisitos para IA e PLN

Usos permitidos com validação:

- classificar tema, habilidade e conteúdo;
- sugerir dificuldade inicial;
- gerar descrição de suporte visual;
- sugerir explicação;
- identificar distratores;
- gerar embeddings para busca semântica;
- sinalizar itens parecidos ou duplicados.

Campos e rastros obrigatórios:

- modelo usado;
- versão do prompt;
- data;
- saída estruturada;
- confiança, quando houver;
- validação humana.

## Requisitos de governança

- Todo item deve ter origem e direito de uso.
- Toda dificuldade deve ter tipo: estimada, observada, calibrada ou oficial.
- Toda estatística deve ter método, fonte, data e amostra.
- Todo uso de IA deve ser rastreável.
- Todo item público deve passar por revisão pedagógica.
- Todo dado pessoal deve ficar fora deste banco ou protegido por RLS, com finalidade documentada.

## Perguntas para auditoria do schema real

- Já existe tabela central de questões?
- Alternativas ficam em tabela separada ou embutidas em JSON?
- O banco registra caderno e posição da questão?
- Existe histórico de aplicação?
- Existem estatísticas agregadas de desempenho?
- Existem parâmetros TRI ou apenas dificuldade textual?
- Existe controle de direitos de uso?
- Existe registro de suporte visual e descrição acessível?
- Existe revisão humana de IA?
- Existe RLS ativo nas tabelas com dados sensíveis?

## Referências internas

- [[Síntese - Artigos TRI e ENEM para XTRI]]
- [[API Própria - Questões XTRI]]
- [[Resumo - Como os escores do ENEM são atribuídos pela TRI]]
- [[Resumo - Efeito de posição dos itens no ENEM]]
- [[Resumo - Rasch multifacetas e cadernos de prova]]
- [[Resumo - Predição de dificuldade de itens sem pré-teste]]
- [[Resumo - Itens excluídos pela TRI]]
- [[Resumo - GPT-4 Vision no ENEM]]
- [[Resumo - PLN e interdisciplinaridade no ENEM]]
- [[Resumo - Autorregulação em testes de múltipla escolha]]
