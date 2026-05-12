# Supabase - Projeto qgqliquusdkkwnfuzdwi

## Classificação

- Tipo: projeto Supabase crítico
- Nome: `banco de dados INEP ENEM SISU`
- Status: ativo a confirmar
- Importância: um dos projetos mais importantes da XTRI
- Project ref: `qgqliquusdkkwnfuzdwi`
- URL pública do projeto: https://qgqliquusdkkwnfuzdwi.supabase.co
- Organização: `eazfgctzojzsbojaxgdo`
- Região: South America (São Paulo)
- Status técnico: `ACTIVE_HEALTHY`
- Criado em UTC: 2026-03-28 09:59:05
- Banco: PostgreSQL 17 / 17.6.1.084
- Host do banco: `db.qgqliquusdkkwnfuzdwi.supabase.co`

## Regra de segurança

Esta nota deve guardar contexto operacional e arquitetura, não dados sensíveis.

Nunca registrar aqui:

- `service_role key`
- JWT secret
- tokens de API
- senhas
- dados pessoais de alunos
- dumps de tabelas com informações identificáveis
- respostas, notas ou históricos individuais sem anonimização e autorização explícita

Pode registrar aqui:

- nome e finalidade do projeto
- schemas e tabelas
- descrição de campos
- políticas de RLS
- Edge Functions
- Storage buckets
- variáveis de ambiente por nome, sem valor
- integrações
- decisões técnicas
- procedimentos de manutenção

## Finalidade do projeto

Pendente de detalhamento pelo Professor Xandão.

Perguntas para completar:

- Qual produto ou sistema usa este Supabase?
- Quais usuários dependem dele?
- Quais fluxos críticos passam por ele?
- Quais dados são oficiais neste projeto?
- Existe repositório vinculado?

## Inventário técnico

### Banco de dados

- Schemas:
- Tabelas críticas:
- Views:
- Funções SQL:
- Triggers:
- Extensões:

### Autenticação

- Provedores ativos:
- Regras de cadastro:
- Perfis ou papéis:
- Fluxos sensíveis:

### RLS

- Tabelas com RLS ativo:
- Políticas críticas:
- Pontos pendentes de auditoria:

### Edge Functions

- Funções:
- Variáveis necessárias:
- Chamadas internas:
- Chamadas externas:

### Storage

- Buckets:
- Tipo de arquivo:
- Política de acesso:
- Retenção:

### Integrações

- Frontend:
- Backend externo:
- Baserow:
- WordPress:
- APIs de terceiros:

## Modelo de documentação de tabela

Use este formato para cada tabela relevante:

```text
Tabela:
Finalidade:
Dados sensíveis: sim/não
Campos principais:
RLS:
Relacionamentos:
Origem dos dados:
Consumidores:
Observações:
```

## Procedimentos recomendados

- Manter migrations versionadas no repositório associado.
- Documentar qualquer alteração de schema nesta nota ou em nota de decisão relacionada.
- Auditar RLS antes de expor novas telas ou endpoints.
- Registrar nomes de variáveis de ambiente, mas nunca seus valores.
- Evitar exportar dados reais para o Obsidian.

## Decisões e histórico

- 2026-05-12: projeto registrado na memória da XTRI como ativo Supabase crítico.
- 2026-05-12: metadados técnicos adicionados a partir de `supabase projects list --output json`.

## Notas relacionadas

- [[Fontes de Dados Oficiais]]
- [[Supabase - Inventário de Projetos]]
- [[Projetos Ativos]]
- [[Stack Oficial da XTRI]]
- [[Decisões Arquiteturais]]
