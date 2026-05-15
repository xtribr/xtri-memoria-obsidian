# index

Catálogo operacional da LLM Wiki da XTRI.

Este arquivo é content-oriented: lista as páginas importantes da wiki com resumo curto e links. Deve ser atualizado em todo ingest relevante.

## Entradas principais

- [[Memória XTRI - Índice]] - página inicial humana do vault.
- [[Bem-vindo]] - porta de entrada simples do Obsidian.
- [[LLM Wiki - Operação da Memória XTRI]] - processo de manutenção da wiki por LLM.
- [[log]] - histórico cronológico de ingests, auditorias, queries e lint.
- [[AGENTS]] - schema operacional para agentes manterem esta wiki.

## Institucional

- [[XTRI - Visão Geral]] - identidade, missão, público-alvo e pilares da XTRI.
- [[Professor Xandão - Perfil e Papel]] - papel do fundador, responsabilidades e regras de trabalho.
- [[Padrão de Conteúdo e Linguagem]] - tom, português brasileiro e padrões de comunicação pública.

## Projetos e Ativos

- [[Índice - Produtos e Projetos]] - índice da pasta de produtos, projetos e backlog.
- [[Projetos Ativos]] - visão geral dos projetos mapeados.
- [[Mapa Operacional de Projetos XTRI]] - mapa com caminho local, GitHub, Supabase, deploy, status e pendências.
- [[Backlog - Banco de Questões]] - backlog priorizado a partir da auditoria do schema, API própria e requisitos.
- [[Roadmap - Banco de Questões]] - fases propostas para segurança, consistência, produto e auditoria contínua.
- [[Supabase - Inventário de Projetos]] - inventário dos projetos Supabase acessíveis pela CLI.
- [[Supabase - Projeto qgqliquusdkkwnfuzdwi]] - projeto crítico `banco de dados INEP ENEM SISU`.
- [[Supabase - banco de questões]] - projeto Supabase do banco de questões.
- [[API Própria - Questões XTRI]] - API própria de consulta de provas, questões, alternativas e habilidades ENEM.
- [[Supabase - sisu2025]] - projeto Supabase `sisu2025`.
- [[Supabase - cronograma-de-estudos]] - projeto Supabase de cronograma de estudos.
- [[Supabase - xtri-provas-sp]] - projeto Supabase de provas.
- [[Supabase - xtri-escolas]] - projeto Supabase de escolas.
- [[Supabase - xtri-gabaritos]] - projeto Supabase de gabaritos.

## Dados, Schema e Auditorias

- [[Índice - Dados e Fontes]] - índice operacional de fontes, bancos, auditorias e pipelines de dados.
- [[Fontes de Dados Oficiais]] - fontes permitidas e regras de uso.
- [[Requisitos - Banco de Questões XTRI]] - requisitos técnicos para o banco de questões.
- [[Checklist - Auditoria do Schema Banco de Questões]] - checklist de comparação entre requisito e schema real.
- [[Auditoria - Schema Real Banco de Questões]] - achados reais do Supabase `banco de questões`.
- [[Auditoria - API Própria Questões XTRI]] - auditoria controlada das respostas reais da API pública de questões.

## ENEM, TRI e SISU

- [[Índice - ENEM, TRI e SISU]] - índice do domínio ENEM/TRI/SISU e resumos de artigos.
- [[Glossário ENEM, TRI e SISU]] - conceitos fundamentais.
- [[Acervo de Artigos TRI e ENEM]] - localização e prioridade do acervo de PDFs.
- [[Síntese - Artigos TRI e ENEM para XTRI]] - síntese transversal dos artigos com conexão de produto.
- [Corretor X Redação ENEM](11%20-%20Corretor%20X%20Reda%C3%A7%C3%A3o%20ENEM/index.html) - base HTML para corretor pedagógico de redação com manual oficial, padrões nota 1000, protocolo e prompt operacional.

## Resumos de Artigos

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

## Corretor X e XTRI-RED

- [[13 - XTRI-RED App Mac]] - app macOS local que opera o Corretor X usando o vault Obsidian como cérebro metodológico.
- [[12 - Integração Sabiá]] - integração operacional com Sabiá, validação Pydantic, política de recuperação e entrega Excel.

## Processos

- [[Regras Operacionais do Codex na XTRI]] - regras absolutas de trabalho.
- [[LLM Wiki - Operação da Memória XTRI]] - ingest, query, lint, index e log.
- [[Convenções de Status e Evidência]] - padrão para status, evidência, hipóteses e pendências.
- [[Padrão - Mapeamento de Simulados ENEM Dia 1]] - formato validado para planilha de mapeamento do D1.

## Stack e Infra

- [[Stack Oficial da XTRI]] - tecnologias oficiais e separação por contexto.

## Decisões

- [[Decisões Arquiteturais]] - decisões técnicas e operacionais registradas.

## Templates

- [[Template - Nota Canônica]]
- [[Template - Projeto Supabase]]
- [[Template - Fonte Ingerida]]
- [[Template - Decisão Técnica]]
- [[Template - Lint da Wiki]]

## Inbox

- [[Capturas Rápidas]] - entradas não processadas.

## Lacunas conhecidas

- Falta auditar RLS/policies do Supabase `banco de questões` com `SUPABASE_DB_PASSWORD`.
- Falta decidir política de exposição de gabarito da [[API Própria - Questões XTRI]].
- Falta criar notas individuais para decisões técnicas recentes.
- Falta confirmar GitHub, deploy e caminhos locais no [[Mapa Operacional de Projetos XTRI]] quando o Kingston estiver montado.
