# Síntese - Artigos TRI e ENEM para XTRI

## Objetivo

Consolidar os pontos em comum entre os artigos da pasta `/Volumes/Kingston 1/OBSIDIAN/PDFS TRI ARTIGOS` e os projetos da XTRI.

Esta nota não substitui os PDFs originais. Ela serve para orientar produto, dados, conteúdo, análise TRI e decisões técnicas.

## Teses comuns do acervo

### 1. Nota do ENEM não é apenas quantidade de acertos

Os artigos sobre TRI reforçam que a nota depende do padrão de resposta, da dificuldade dos itens, da discriminação, do acerto ao acaso e dos pressupostos do modelo. Isso conversa diretamente com a proposta da XTRI de explicar aos alunos por que dois candidatos com a mesma quantidade de acertos podem ter notas diferentes.

Conexão XTRI:

- [[Glossário ENEM, TRI e SISU]]
- [[Supabase - Projeto qgqliquusdkkwnfuzdwi]]
- [[Supabase - banco de questões]]

Aplicação prática:

- Painéis que mostrem acertos brutos e leitura TRI separadamente.
- Alertas de coerência pedagógica do padrão de respostas.
- Conteúdos públicos explicando diferença entre acerto, proficiência e nota.

### 2. O item precisa ser tratado como unidade estratégica

Vários artigos tratam dificuldade, posição, caderno, pré-teste, itens excluídos e características textuais. Para a XTRI, isso indica que o banco de questões não deve guardar apenas enunciado, alternativas e gabarito. Ele precisa guardar metadados pedagógicos, psicométricos e operacionais.

Conexão XTRI:

- [[Supabase - banco de questões]]
- [[Supabase - xtri-gabaritos]]
- [[Supabase - xtri-provas-sp]]

Aplicação prática:

- Campos para habilidade, competência, área, dificuldade estimada, fonte, ano, caderno, posição, tipo de suporte e justificativa pedagógica.
- Histórico de desempenho por item.
- Registro de itens problemáticos ou pedagogicamente informativos, mesmo quando não entram no cálculo final.

### 3. TRI exige governança estatística

Os artigos de TRI, TCT, Rasch multifacetas e TRI profundo mostram que existem muitas formas de estimar desempenho. A XTRI pode usar esses estudos para pesquisa e produto, mas qualquer estimativa de nota ou aprovação precisa declarar metodologia, fonte e limitação.

Conexão XTRI:

- [[Regras Operacionais do Codex na XTRI]]
- [[Fontes de Dados Oficiais]]
- [[Decisões Arquiteturais]]

Aplicação prática:

- Notas técnicas para cada modelo de estimativa.
- Separação clara entre cálculo oficial, simulação, aproximação e hipótese de pesquisa.
- Validação contra dados reais antes de uso público.

### 4. IA é útil, mas precisa de avaliação controlada

Os artigos sobre GPT, Sabiá, NorBERTo e ensemble de LLMs mostram potencial para resolver questões, analisar textos, apoiar redação e classificar conteúdo em português. O ponto comum é que modelos precisam ser avaliados em contexto brasileiro e com métricas explícitas.

Conexão XTRI:

- [[Supabase - banco de questões]]
- [[Supabase - Projeto qgqliquusdkkwnfuzdwi]]
- [[Projetos Ativos]]

Aplicação prática:

- Classificação automática de itens com revisão humana.
- Geração de explicações de alternativas.
- Apoio preliminar à correção de redação, mantendo professor no ciclo.
- Benchmark interno com questões ENEM separadas por área, imagem, texto, matemática e distratores.

### 5. A prática do aluno precisa ser guiada, não apenas disponibilizada

Os artigos sobre estratégias de aprendizagem e testes de múltipla escolha indicam que alunos nem sempre regulam bem o próprio estudo. Eles podem praticar menos do que o necessário ou usar estratégias de curto prazo que parecem eficientes, mas não sustentam retenção.

Conexão XTRI:

- [[Supabase - cronograma-de-estudos]]
- [[Projetos Ativos]]

Aplicação prática:

- Cronogramas com repetição espaçada, recuperação ativa e metas mínimas de domínio.
- Simulados que recomendem nova tentativa quando o aluno acerta pouco ou acerta por provável chute.
- Feedback que transforme erro em plano de estudo.

### 6. Dashboard bom transforma dado em decisão

O artigo sobre dashboard educacional reforça que visualização precisa apoiar gestores e pesquisadores. Para a XTRI, painéis devem priorizar decisão: onde o aluno está, qual risco existe, qual ação vem depois.

Conexão XTRI:

- [[Supabase - xtri-escolas]]
- [[Supabase - Projeto qgqliquusdkkwnfuzdwi]]

Aplicação prática:

- Dashboards por escola, turma, área e habilidade.
- Comparação temporal de desempenho.
- Visualizações de proficiência, acerto, coerência e evolução.

## Resumos por artigo

- [[Resumo - Como os escores do ENEM são atribuídos pela TRI]]
- [[Resumo - Estrutura interna do ENEM em Ciências Naturais]]
- [[Resumo - TCT e TRI no ENEM]]
- [[Resumo - Rasch multifacetas e cadernos de prova]]
- [[Resumo - TRI Profundo]]
- [[Resumo - Efeito de posição dos itens no ENEM]]
- [[Resumo - Dashboard educacional com R e Shiny]]
- [[Resumo - Ensemble de LLMs na correção de redações]]
- [[Resumo - PLN e interdisciplinaridade no ENEM]]
- [[Resumo - Predição de dificuldade de itens sem pré-teste]]
- [[Resumo - NorBERTo e PLN em português]]
- [[Resumo - GPT-4 Vision no ENEM]]
- [[Resumo - Estratégias de aprendizagem]]
- [[Resumo - Autorregulação em testes de múltipla escolha]]
- [[Resumo - Itens excluídos pela TRI]]
- [[Resumo - Fundamentos de Psicometria e TCT]]
- [[Resumo - GPT-3.5 e GPT-4 no ENEM]]
- [[Resumo - Sabiá-3]]

## Próximas decisões para a XTRI

- Definir quais metadados mínimos cada questão precisa ter no banco. Documento criado: [[Requisitos - Banco de Questões XTRI]].
- Criar uma política de validação para estimativas TRI e predição de nota.
- Separar uso de IA em três níveis: apoio interno, recomendação ao aluno e decisão sensível.
- Criar benchmark XTRI com questões ENEM para avaliar modelos de linguagem antes de uso em produto.
- Mapear quais projetos Supabase guardam dados de aluno, questão, prova, gabarito e histórico de desempenho.

## Notas relacionadas

- [[Acervo de Artigos TRI e ENEM]]
- [[Glossário ENEM, TRI e SISU]]
- [[Supabase - Inventário de Projetos]]
- [[Supabase - Projeto qgqliquusdkkwnfuzdwi]]
- [[Supabase - banco de questões]]
- [[Supabase - cronograma-de-estudos]]
- [[Requisitos - Banco de Questões XTRI]]
- [[Checklist - Auditoria do Schema Banco de Questões]]
