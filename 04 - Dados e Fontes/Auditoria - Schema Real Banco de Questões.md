# Auditoria - Schema Real Banco de Questões

## Escopo

- Projeto: [[Supabase - banco de questões]]
- Project ref: `fbykcqcssykopvcrsfoo`
- Data da auditoria: 2026-05-12
- Método principal: PostgREST OpenAPI com chave de serviço, sem leitura de registros.
- Método auxiliar: `supabase inspect db table-stats` e `supabase functions list`.
- Storage: consulta de metadados de buckets, sem listar objetos.

## Limitação da auditoria

O dump completo de schema e a leitura de policies/RLS via conexão Postgres falharam porque a CLI exigiu `SUPABASE_DB_PASSWORD`. O pooler bloqueou novas tentativas temporariamente após falhas de autenticação.

Consequência:

- Foi possível auditar tabelas, views, colunas expostas, buckets e Edge Functions.
- Não foi possível confirmar RLS, policies, triggers, índices completos, constraints completas e funções SQL internas.

## Resumo executivo

O projeto já contém uma base relevante para itens ENEM/INEP:

- Itens oficiais com parâmetros TRI em `itens`.
- Relação item-prova-caderno-posição em `itens_prova`.
- Matriz de áreas, competências e habilidades em `areas_conhecimento`, `competencias` e `habilidades`.
- Questões externas com enunciado, alternativas, gabarito, imagens e dificuldade textual em `questoes_externas`.
- View consolidada `v_itens_completo`.

Mas o schema ainda não atende completamente aos requisitos definidos em [[Requisitos - Banco de Questões XTRI]]:

- Alternativas de questões externas estão em `jsonb`, não em tabela relacional.
- Não há histórico agregado de desempenho por item.
- Não há tabela formal de psicometria com método, amostra, erro, fonte e data de calibração.
- Não há tabela de revisões pedagógicas, psicométricas, direitos ou IA.
- Não há rastreabilidade estruturada de IA/PLN.
- Suporte visual existe, mas sem descrição acessível, OCR, tipo visual e revisão humana.
- O projeto contém tabelas de usuário e sessões, o que exige verificação imediata de RLS e LGPD.

## Relações expostas no schema público

### Núcleo de questões e ENEM

| Relação | Estimativa de linhas | Função observada |
|---|---:|---|
| `itens` | 3.686 | Itens ENEM/INEP com parâmetros TRI e metadados básicos |
| `itens_prova` | 31.623 | Relação entre item, prova, posição e cor/caderno |
| `questoes_externas` | 3.640 | Questões externas com enunciado, alternativas em JSON, imagens e gabarito |
| `codigos_prova` | 650 | Códigos de prova por ano, área e categoria |
| `areas_conhecimento` | 4 | Áreas ENEM |
| `competencias` | 30 | Competências por área |
| `habilidades` | 120 | Habilidades por área/competência |
| `v_itens_completo` | view | View consolidada de itens com área, habilidade e competência |

### Usuários, sessões e gamificação

| Relação | Estimativa de linhas | Observação |
|---|---:|---|
| `user_profiles` | 309 | Contém `email`, `full_name`, `auth_uid` e perfil |
| `user_sessions` | 147 | Contém `resultado`, `nota_tri`, `total_acertos`, `config` e vínculo com usuário |
| `user_gamification_profile` | 251 | Perfil de XP e streak |
| `xp_events` | 135 | Eventos de XP por usuário |
| `user_missions` | 1.375 | Missões por usuário |
| `user_achievements` | 62 | Conquistas por usuário |
| `missions` | 3 | Cadastro de missões |
| `achievements` | 4 | Cadastro de conquistas |

Ponto crítico:

- O projeto chamado `banco de questões` também armazena dados de usuário e sessões. Isso precisa de revisão de arquitetura, RLS e LGPD.

## Tabelas principais contra os requisitos

### `itens`

Campos relevantes encontrados:

- `co_item`
- `ano`
- `sg_area`
- `co_habilidade`
- `tx_gabarito`
- `nu_param_a`
- `nu_param_b`
- `nu_param_c`
- `in_item_aban`
- `tx_motivo_aban`
- `link_imagem`
- `aplicacao_img`
- `num_cadernos`
- `tp_lingua`
- `fonte`
- `is_reaplicacao`

Atende:

- Item oficial com ID INEP.
- Área.
- Habilidade.
- Gabarito.
- Parâmetros TRI `a`, `b`, `c`.
- Sinalização de item abandonado/excluído.
- Link de imagem.

Lacunas:

- Não há enunciado no schema exposto.
- Não há alternativas.
- Não há explicação validada.
- Não há status pedagógico.
- Não há `psychometric_status` formal.
- Não há método, amostra, erro padrão, estatísticas de ajuste, data ou fonte da calibração.
- Não há descrição textual do suporte visual.

Ação recomendada:

- Manter `itens` como tabela de item oficial/calibrado.
- Criar tabela complementar para conteúdo textual, suporte visual, revisão e documentação psicométrica.
- Separar `in_item_aban` e `tx_motivo_aban` de um status psicométrico mais completo.

### `questoes_externas`

Campos relevantes encontrados:

- `id`
- `id_externo`
- `codigo`
- `fonte`
- `vestibular`
- `ano`
- `disciplina`
- `segmento`
- `tipo`
- `enunciado_texto`
- `enunciado_html`
- `texto_adicional`
- `texto_adicional_html`
- `alternativas`
- `gabarito`
- `imagens`
- `assuntos`
- `nivel_dificuldade`
- `tem_comentario_professor`

Atende:

- Enunciado em texto e HTML.
- Texto adicional.
- Alternativas.
- Gabarito.
- Imagens.
- Fonte, vestibular, ano e disciplina.
- Assuntos.
- Dificuldade textual.

Lacunas:

- Alternativas estão em `jsonb`, o que dificulta análise de distratores, distribuição por alternativa e histórico de performance.
- Não há competência/habilidade ENEM estruturada.
- Não há descrição acessível das imagens.
- Não há método ou confiança para `nivel_dificuldade`.
- Não há direitos de uso formalizados.
- Não há revisão pedagógica/psicométrica estruturada.
- Não há conexão direta com `itens`, `habilidades` ou `competencias`.

Ação recomendada:

- Criar `question_options` relacional para alternativas.
- Criar relação entre questões externas e matriz ENEM quando aplicável.
- Criar campos ou tabela para direitos de uso e revisão.
- Transformar `nivel_dificuldade` em dificuldade estimada com método e confiança.

### `itens_prova`

Campos relevantes encontrados:

- `co_item`
- `co_prova`
- `co_posicao`
- `tx_cor`
- `ano`

Atende:

- Histórico de aplicação oficial por item.
- Caderno/cor.
- Posição no caderno.
- Ano.

Lacunas:

- Não há tipo de aplicação: oficial, piloto, treino, simulado.
- Não há data da aplicação.
- Não há ordem da área como campo explícito.
- Não cobre questões externas ou simulados XTRI, pelo schema exposto.

Ação recomendada:

- Manter como tabela de aplicação oficial INEP.
- Criar `question_applications` para aplicações XTRI, simulados e listas.

### `competencias`, `habilidades`, `areas_conhecimento`

Atende:

- Existe matriz estruturada com áreas, competências e habilidades.
- `habilidades` referencia área e competência por códigos.

Lacunas:

- Não foi identificada tabela para habilidades secundárias por questão.
- Não foi identificada versionamento da matriz.
- `questoes_externas` não usa essa matriz diretamente.

Ação recomendada:

- Criar tabela de relação `question_skills` quando uma questão puder ter habilidade primária e secundárias.
- Registrar fonte e versão da matriz.

## Storage

Buckets encontrados:

| Bucket | Público | Limite | MIME types |
|---|---:|---:|---|
| `questoes-externas` | sim | 5 MB | JPEG, PNG, GIF, WebP, SVG |
| `questoes-enem` | sim | sem limite configurado | sem restrição configurada |

Lacunas:

- `questoes-enem` está público sem limite de tamanho e sem MIME types restritos.
- Não foi encontrada, no schema exposto, tabela de metadados visuais com OCR, descrição acessível e revisão humana.

Ação recomendada:

- Definir limite e MIME types para `questoes-enem`.
- Criar metadados de suporte visual por questão.
- Confirmar se buckets públicos são realmente necessários.

## Edge Functions

Funções encontradas:

| Slug | Status | `verify_jwt` | Observação |
|---|---|---:|---|
| `dynamic-processor` | ACTIVE | true | Nome exibido como `mentor-ia` |
| `mentor-ia` | ACTIVE | false | Endpoint ativo sem verificação JWT pela plataforma |
| `monitor-bancoenem-users` | ACTIVE | false | Endpoint ativo sem verificação JWT pela plataforma |

Ponto crítico:

- Funções com `verify_jwt = false` podem ser públicas. Isso pode ser correto para webhooks ou endpoints controlados internamente, mas precisa de autenticação própria, rate limit e validação de entrada no código.

Ação recomendada:

- Revisar código das Edge Functions.
- Confirmar se `mentor-ia` e `monitor-bancoenem-users` precisam ser públicas.
- Se forem públicas, documentar autenticação própria, CORS, rate limit e validação de payload.

## Resultado por área

| Área | Status | Lacuna principal | Ação recomendada |
|---|---|---|---|
| Questões oficiais ENEM | Parcial | Tem item, habilidade, gabarito e TRI, mas falta enunciado/alternativas no schema exposto | Criar camada textual e editorial ou vincular fonte externa |
| Questões externas | Parcial | Alternativas em JSON, sem habilidade/competência estruturada | Normalizar alternativas e matriz ENEM |
| Alternativas/distratores | Parcial | Existem em `jsonb` só para `questoes_externas`; não há distrator estruturado | Criar `question_options` |
| Suporte visual | Parcial | Há links/imagens, mas sem descrição acessível/OCR/revisão | Criar metadados visuais |
| Caderno e posição | Parcial bom | `itens_prova` cobre ENEM oficial, mas não XTRI/simulados | Criar `question_applications` |
| Desempenho agregado | Ausente | Não há stats por item/aplicação | Criar `question_performance_stats` |
| Psicometria | Parcial | `a`, `b`, `c` existem em `itens`, mas sem método, erro, amostra e data | Criar `question_psychometrics` |
| IA e PLN | Ausente no schema | Não há tabela de anotações/rastreio de IA | Criar `question_ai_annotations` |
| Revisões | Ausente | Não há revisão pedagógica, direitos, IA ou psicometria | Criar `question_reviews` |
| Matriz ENEM | Parcial bom | Matriz existe, mas sem versionamento e sem ligação com externas | Criar versão e relações |
| Usuários e sessões | Risco alto | Dados de usuário dentro do banco de questões | Confirmar RLS, LGPD e separação arquitetural |
| Storage | Risco médio | Buckets públicos; um sem limite/MIME | Revisar políticas e restrições |
| Edge Functions | Risco alto | Duas funções com `verify_jwt = false` | Auditar autenticação própria |
| RLS/policies | Bloqueado | Falta senha Postgres para confirmar | Rodar auditoria com `SUPABASE_DB_PASSWORD` |

## Próximas ações técnicas

1. Obter acesso seguro ao `SUPABASE_DB_PASSWORD` somente em variável de ambiente local, sem registrar no Obsidian.
2. Rodar dump de schema e consulta de `pg_policies` para confirmar RLS.
3. Revisar código das Edge Functions `mentor-ia` e `monitor-bancoenem-users`.
4. Planejar migration incremental para tabelas ausentes: `question_options`, `question_applications`, `question_performance_stats`, `question_psychometrics`, `question_reviews`, `question_ai_annotations` e relação de habilidades.
5. Decidir se dados de usuário devem permanecer neste projeto ou migrar para um projeto/tabelas com fronteira clara de produto e LGPD.
6. Auditar a [[API Própria - Questões XTRI]] como interface oficial de consulta do banco de questões.

## Notas relacionadas

- [[Checklist - Auditoria do Schema Banco de Questões]]
- [[Requisitos - Banco de Questões XTRI]]
- [[Supabase - banco de questões]]
- [[API Própria - Questões XTRI]]
- [[Síntese - Artigos TRI e ENEM para XTRI]]
