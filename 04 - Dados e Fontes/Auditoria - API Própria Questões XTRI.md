# Auditoria - API Própria Questões XTRI

## Escopo

- API: [[API Própria - Questões XTRI]]
- Documentação: https://api.questoes.xtri.online/api/docs/
- OpenAPI: https://api.questoes.xtri.online/api/schema/
- Data da auditoria: 2026-05-12
- Método: chamadas públicas controladas com `GET` e `OPTIONS`.

## Regra da auditoria

Foram feitas chamadas pequenas, sem varrer toda a base e sem baixar volume grande de questões. A auditoria registrou estrutura, contagens, filtros, headers e riscos de contrato. Não foram salvos enunciados completos, alternativas completas nem arquivos de imagem.

## Resultado executivo

A API está ativa, documentada por OpenAPI 3.0.3 e responde de forma consistente para anos, provas, questões, habilidades, detalhe por ID e detalhe por ano/slug.

Ela deve ser tratada como ativo crítico da XTRI porque já expõe uma interface mais limpa que o schema bruto do Supabase:

- questões paginadas;
- provas por ano;
- habilidades ENEM;
- alternativas estruturadas;
- parâmetros TRI `param_a`, `param_b`, `param_c`;
- filtros por ano, disciplina, habilidade e dificuldade.

Principais riscos:

- A API expõe `correctAlternative` em listagens e detalhes.
- O detalhe da questão expõe `isCorrect` dentro de cada alternativa.
- CORS não libera `https://xtri.online` nem `https://www.xtri.online` nos testes feitos.
- Não foi observado `Cache-Control`.
- Não foi observado rate limit nos headers.
- Algumas questões recentes podem estar sem `skill` e `param_b`.

## Chamadas controladas realizadas

### Documentação e schema

| Endpoint | Status | Achado |
|---|---:|---|
| `/api/docs/` | 200 | Swagger UI carregando schema de `/api/schema/` |
| `/api/schema/` | 200 | OpenAPI `3.0.3`, título `ENEM API`, versão `1.0.0` |

### Metadados

| Endpoint | Status | Achado |
|---|---:|---|
| `/api/years/` | 200 | Retornou anos de 2009 a 2025 |
| `/api/exams/?page=1` | 200 | `count = 17`, todos os anos em uma página |
| `/api/skills/` | 200 | `120` habilidades |

### Questões

| Endpoint | Status | Achado |
|---|---:|---|
| `/api/questions/?page=1` | 200 | `count = 3123`, página com `50` resultados |
| `/api/exams/2025/questions/?page=1` | 200 | `count = 182`, página com `50` resultados |
| `/api/questions/17488/` | 200 | Detalhe por ID funcionando |
| `/api/questions/2025/1-espanhol/` | 200 | Detalhe por ano e slug funcionando |

### Filtros testados

| Filtro | Resultado |
|---|---:|
| `year=2025` | `182` questões |
| `year=2024` | `184` questões |
| `year=2023` | `183` questões |
| `discipline=linguagens` | `787` questões |
| `skill_code=H1` | `106` questões |
| `skill_area=CH` | `674` questões |
| `skill=CH:H1` | `30` questões |
| `param_b_min=0&param_b_max=1` | `887` questões |
| `param_b_min=1&param_b_max=2` | `899` questões |

Observação:

- O filtro `skill=CH:H1` é mais específico que `skill_code=H1`, porque `H1` existe em mais de uma área.

## Campos reais observados

### Listagem de questões

Campos observados em `/api/questions/`:

- `id`
- `title`
- `index`
- `year`
- `slug`
- `discipline`
- `language`
- `skill`
- `image`
- `correctAlternative`
- `param_b`

### Detalhe de questão

Campos observados em `/api/questions/{id}/`:

- `id`
- `title`
- `index`
- `year`
- `slug`
- `discipline`
- `language`
- `skill`
- `image`
- `correctAlternative`
- `param_b`
- `context`
- `contextLocal`
- `files`
- `alternativesIntroduction`
- `alternatives`
- `param_a`
- `param_c`
- `in_item_aban`

### Alternativas

O detalhe da questão retorna alternativas estruturadas com:

- `letter`
- `text`
- `image`
- `file`
- `localFile`
- `isCorrect`

## Exposição de gabarito

Achado:

- `correctAlternative` aparece na listagem.
- `correctAlternative` aparece no detalhe.
- `isCorrect` aparece em cada alternativa no detalhe.

Impacto:

- Excelente para consulta, estudo, explicação e revisão.
- Inadequado para modo simulado, prova, ranking ou qualquer fluxo em que o aluno não deva ver o gabarito antes de responder.

Ação recomendada:

- Criar modos de resposta:
  - `study`: pode expor gabarito e `isCorrect`.
  - `assessment`: não expõe `correctAlternative` nem `isCorrect`.
  - `admin`: expõe tudo com autenticação.

## Completude de TRI e habilidade

Achado:

- Amostra de 2025 retornou `skill = null` e `param_b = null`.
- Amostra de 2024 retornou `skill` preenchido e `param_b` preenchido.

Interpretação:

- A API suporta habilidade e parâmetros TRI.
- Nem todos os anos ou itens parecem estar completos nesses campos.

Ação recomendada:

- Criar monitor de completude por ano:
  - percentual de questões com `skill`;
  - percentual com `param_a`, `param_b`, `param_c`;
  - percentual com imagem;
  - percentual com alternativas completas.

## CORS

Teste com `Origin`:

| Origin | `Access-Control-Allow-Origin` |
|---|---|
| `https://xtri.online` | ausente |
| `https://www.xtri.online` | ausente |
| `https://questoes.xtri.online` | ausente |
| `https://api.questoes.xtri.online` | ausente |
| `http://localhost:3000` | presente |
| `http://127.0.0.1:3000` | ausente |

Preflight `OPTIONS`:

- Para `http://localhost:3000`, retornou métodos e headers permitidos.
- Para `https://xtri.online`, não retornou `Access-Control-Allow-Origin`.

Impacto:

- Um frontend em produção em `xtri.online` pode ser bloqueado pelo navegador se consumir essa API diretamente.
- O consumo server-side não sofre a mesma restrição de CORS.

Ação recomendada:

- Definir domínios oficiais consumidores.
- Liberar CORS para os domínios necessários.
- Evitar liberar `*` se houver endpoints futuros autenticados.

## Headers observados

Headers positivos:

- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: same-origin`
- `Vary: Accept, Cookie, origin`

Pontos não observados:

- `Cache-Control`
- headers aparentes de rate limit

Ação recomendada:

- Definir cache para endpoints públicos estáveis, especialmente anos, provas, habilidades e questões oficiais.
- Definir rate limit ou proteção equivalente.

## Comportamento de erro

| Chamada | Status | Resposta |
|---|---:|---|
| `/api/questions/999999999/` | 404 | JSON com `detail` |
| `/api/exams/1800/` | 404 | JSON com `detail` |

Avaliação:

- Erros são previsíveis e retornam JSON.

## Comparação com requisitos XTRI

| Requisito | Status na API | Observação |
|---|---|---|
| Questões listáveis | bom | Paginado, com filtros |
| Detalhe da questão | bom | Contrato rico |
| Alternativas estruturadas | bom | Melhor que o JSON bruto do Supabase |
| Habilidades ENEM | bom | 120 habilidades expostas |
| Parâmetros TRI | parcial | Campos existem, mas há nulos |
| Caderno/cor | ausente no contrato testado | Só há `index` |
| Suporte visual | parcial | Há `image/files`, mas sem descrição acessível |
| Gabarito protegido | ausente | Gabarito público em listagem e detalhe |
| Cache/rate limit | não confirmado | Não apareceu nos headers |
| CORS produção | lacuna | `xtri.online` não liberado nos testes |

## Decisões necessárias

- A API será a interface oficial de consulta para produtos XTRI?
- `correctAlternative` deve aparecer em listagem pública?
- Deve existir endpoint de modo simulado sem gabarito?
- Quais domínios devem ter CORS liberado?
- A API deve adotar versionamento por path, como `/api/v1/`?
- Quais endpoints devem ter cache?
- Quais limites de uso devem ser aplicados?

## Recomendações

### P0

- Definir política de exposição de gabarito.
- Corrigir ou configurar CORS para domínios oficiais.
- Confirmar se todos os endpoints são intencionalmente públicos.

### P1

- Criar endpoint ou parâmetro de modo `assessment` sem gabarito.
- Criar monitor de completude por ano para `skill` e parâmetros TRI.
- Definir cache e rate limit.
- Criar testes de contrato da API.

### P2

- Criar versão `/api/v1/`.
- Adicionar metadados de suporte visual acessível.
- Documentar SLA interno e política de breaking changes.

## Próximas ações

1. Registrar decisão sobre exposição de gabarito.
2. Registrar decisão sobre API como interface oficial.
3. Criar [[Roadmap - Banco de Questões]] incluindo correções da API.
4. Validar CORS com o ambiente real do frontend consumidor.

## Notas relacionadas

- [[API Própria - Questões XTRI]]
- [[Backlog - Banco de Questões]]
- [[Requisitos - Banco de Questões XTRI]]
- [[Auditoria - Schema Real Banco de Questões]]
- [[Supabase - banco de questões]]
