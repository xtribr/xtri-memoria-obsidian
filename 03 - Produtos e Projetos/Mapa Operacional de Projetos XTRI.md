# Mapa Operacional de Projetos XTRI

## Objetivo

Centralizar, em uma visão única, os projetos XTRI com links de operação: caminho local, repositório, banco Supabase, deploy e status de verificação.

## Status

- status: em auditoria
- última revisão: 2026-05-12
- fonte: notas do vault e tentativa de verificação local em `/Volumes/KINGSTON/apps/apps`
- limitação: no momento desta revisão, o volume `/Volumes/KINGSTON` não estava montado; caminhos locais abaixo ficam como pendentes de confirmação.

## Regra de preenchimento

- `verificado`: confirmado por arquivo local, Git ou fonte registrada.
- `não verificado`: citado por memória operacional/notas, mas ainda sem confirmação no ciclo atual.
- `pendente`: precisa de acesso, credencial, volume externo ou decisão.
- `não aplicável`: campo não se aplica ao projeto.

## Projetos

| Projeto | Status | Caminho local | GitHub | Supabase | Deploy | Próxima ação |
|---|---|---|---|---|---|---|
| MIRT / XTRI Engine | ativo, pendente de verificação local | `/Volumes/KINGSTON/apps/apps/MIRT` | não verificado | não aplicável ou indireto | não verificado | Confirmar repo local/remoto quando Kingston montar |
| RANKING ENEM | ativo, pendente de verificação local | `/Volumes/KINGSTON/apps/apps/RANKING ENEM` | não verificado | [[Supabase - xtri-escolas]], [[Supabase - Projeto qgqliquusdkkwnfuzdwi]] | Hostinger/Coolify citado em notas anteriores; não verificado nesta wiki | Confirmar GitHub, deploy e banco consumidor |
| PROVAS 2.0 | ativo, pendente de verificação local | `/Volumes/KINGSTON/apps/apps/PROVAS 2.0` | não verificado | [[Supabase - xtri-provas-sp]] | Hostinger/Coolify citado em operação; não verificado nesta wiki | Separar alteração de prompt, AGENTS e artefatos antes de commit |
| PROVAS 3.0 Refatorado | ativo, pendente de verificação local | `/Volumes/KINGSTON/apps/apps/provas-3.0-refatorado` | não verificado | [[Supabase - xtri-provas-sp]] | não verificado | Validar scripts de importação XTRI antes de commit |
| Cronogramas | ativo, pendente de verificação local | `/Volumes/KINGSTON/apps/apps/cronogramas` | não verificado | [[Supabase - cronograma-de-estudos]] | não verificado | Confirmar RPCs/RLS de coordenadores antes de commit |
| Horário de Estudos / xtri.online | ativo, pendente de verificação local | `/Volumes/KINGSTON/apps/apps/horario de estudos 2.0` | não verificado | [[Supabase - xtri-gabaritos]], possível [[Supabase - cronograma-de-estudos]] | não verificado | Confirmar vínculo real por `.env` |
| SISU 2.0 / sisu2025 | ativo, pendente de verificação local | `/Volumes/KINGSTON/apps/apps/Sisu2.0/sisu2025` | não verificado | [[Supabase - sisu2025]] | não verificado | Validar script de pesos 2026 e fonte MeuSISU |
| Banco de Questões ENEM | ativo, pendente de verificação local | `/Volumes/KINGSTON/apps/apps/banco questoes enem/xtri-banco-questoes` | não verificado | [[Supabase - banco de questões]] | não verificado | Validar Edge Function `mentor-ia` com Deno/Supabase |
| Site Mentoria ENEM v2 | ativo, pendente de verificação local | `/Volumes/KINGSTON/apps/apps/site mentoria enem v2` | não verificado | não verificado | não verificado | Confirmar stack e deploy |
| Site xtri.online v2 | ativo, pendente de verificação local | `/Volumes/KINGSTON/apps/apps/site xtri.online v2` | não verificado | não verificado | não verificado | Confirmar stack e deploy |
| Dashboard 2026 | ativo, pendente de verificação local | `/Volumes/KINGSTON/apps/apps/dashboard2026` | não verificado | não verificado | não verificado | Confirmar função operacional |
| Pixel Art Dash 2027 | arquivado ou limpo localmente, pendente de verificação | `/Volumes/KINGSTON/apps/apps/pixel art dash 2027` | não verificado | não verificado | não verificado | Confirmar se permanece ativo ou arquivar |

## Separação de evidência

### Fatos verificados neste ciclo

- O repositório Git do vault atual é `xtribr/xtri-memoria-obsidian`.
- O volume `/Volumes/KINGSTON` não estava montado na revisão de 2026-05-12.
- As notas Supabase canônicas existem em `04 - Dados e Fontes`.

### Hipóteses operacionais

- Os caminhos em `/Volumes/KINGSTON/apps/apps` refletem o ambiente de trabalho usado anteriormente.
- Projetos PROVAS, Ranking ENEM, SISU e Cronogramas dependem de Supabase, mas os vínculos exatos precisam de confirmação por `.env`, deploy ou código.

### Pendências

- Montar Kingston e reexecutar inventário Git.
- Preencher URLs GitHub com `git remote -v`.
- Preencher deploys reais somente após verificar Hostinger/Coolify/Vercel ou configuração equivalente.
- Registrar decisões relevantes em [[Decisões Arquiteturais]].

## Notas relacionadas

- [[Projetos Ativos]]
- [[Supabase - Inventário de Projetos]]
- [[Stack Oficial da XTRI]]
- [[Convenções de Status e Evidência]]

