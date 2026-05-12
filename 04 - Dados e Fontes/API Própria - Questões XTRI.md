# API Própria - Questões XTRI

## Classificação

- Tipo: API própria da XTRI
- Nome público na documentação: `ENEM API`
- URL da documentação: https://api.questoes.xtri.online/api/docs/
- OpenAPI schema: https://api.questoes.xtri.online/api/schema/
- Versão informada: `1.0.0`
- Status: ativo em produção a confirmar
- Importância: ativo crítico da XTRI para consulta de provas, questões, alternativas e habilidades ENEM

## Descrição oficial da API

API para consultar provas, questões, alternativas e habilidades da matriz de referência do ENEM.

## Regra de segurança

Esta nota deve registrar contrato público, endpoints e decisões de integração. Não registrar tokens, cookies, credenciais, dumps ou dados sensíveis.

## Endpoints mapeados

| Método | Endpoint | Finalidade |
|---|---|---|
| `GET` | `/api/exams/` | Lista as provas |
| `GET` | `/api/exams/{year}/` | Detalha uma prova pelo ano |
| `GET` | `/api/exams/{year}/questions/` | Lista questões de uma prova |
| `GET` | `/api/questions/` | Lista questões |
| `GET` | `/api/questions/{id}/` | Detalha uma questão pelo ID |
| `GET` | `/api/questions/{year}/{slug}/` | Detalha uma questão pelo ano e slug |
| `GET` | `/api/skills/` | Lista todas as habilidades do ENEM |
| `GET` | `/api/skills/{id}/` | Detalha uma habilidade |
| `GET` | `/api/years/` | Lista os anos disponíveis |

## Filtros úteis

### Questões

Endpoints:

- `/api/questions/`
- `/api/exams/{year}/questions/`

Filtros:

- `year`: filtra questões pelo ano da prova.
- `discipline`: aceita `linguagens`, `matematica`, `ciencias-humanas` ou `ciencias-natureza`.
- `index`: filtra pelo número/posição da questão na prova.
- `language`: aceita `ingles`, `espanhol` ou `null`.
- `skill`: atalho para habilidade. Exemplos aceitos: `LC:H1`, `LC-H1`, `LC_H1` ou `H1`.
- `skill_area`: filtra pela área da habilidade.
- `skill_code`: aceita `H1` ou `1`.
- `param_b_min`: filtra questões com dificuldade IRT acima ou igual ao valor.
- `param_b_max`: filtra questões com dificuldade IRT abaixo ou igual ao valor.
- `page`: paginação.

### Habilidades

Endpoint:

- `/api/skills/`

Filtros:

- `area`: filtra habilidades por área.
- `code`: aceita `H1` ou `1`.

## Schemas principais

### `QuestionList`

Campos:

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

### `QuestionDetail`

Campos:

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

### `Alternative`

Campos:

- `letter`
- `text`
- `image`
- `file`
- `localFile`
- `isCorrect`

### `EnemSkill`

Campos:

- `area`
- `code`
- `label`

### `Exam`

Campos:

- `title`
- `year`
- `disciplines`
- `languages`

## Relação com o banco Supabase

Provável relação direta com [[Supabase - banco de questões]], especialmente com:

- `itens`
- `itens_prova`
- `questoes_externas`
- `habilidades`
- `competencias`
- `areas_conhecimento`
- buckets `questoes-enem` e `questoes-externas`

Inferência técnica:

- A API já expõe parte do contrato ideal definido em [[Requisitos - Banco de Questões XTRI]], principalmente questão, prova, habilidade, alternativa, parâmetros TRI e imagem.
- A API parece mais organizada para consumo externo do que o schema bruto do Supabase, porque normaliza `QuestionDetail`, `Alternative`, `Exam` e `EnemSkill`.

## Pontos fortes

- OpenAPI público disponível.
- Endpoints claros para anos, provas, questões e habilidades.
- Filtros por área, disciplina, habilidade, ano, posição e dificuldade `param_b`.
- Detalhe da questão inclui parâmetros TRI `param_a`, `param_b`, `param_c`.
- Alternativas aparecem como lista estruturada no contrato da API.
- Suporte a imagens e arquivos associados.

## Lacunas a auditar

- Auditoria inicial realizada: [[Auditoria - API Própria Questões XTRI]]
- Confirmar origem exata dos dados: Supabase, banco próprio, arquivos estáticos ou outra fonte.
- Confirmar política de cache, paginação e limites de uso.
- Confirmar se todos os endpoints são intencionalmente públicos.
- Confirmar se `isCorrect` deve ser exposto em todos os contextos públicos.
- Confirmar se questões abandonadas (`in_item_aban`) aparecem por padrão ou exigem filtro.
- Confirmar se há rate limit.
- Confirmar CORS e domínios autorizados.
- Confirmar se existe autenticação opcional ou chaves internas para endpoints administrativos.
- Confirmar se a API expõe apenas dados de questões, sem dados de usuário.

## Auditoria controlada

- Relatório: [[Auditoria - API Própria Questões XTRI]]
- Resultado: API ativa, paginada e funcional para anos, provas, questões, habilidades, detalhe por ID e detalhe por ano/slug.
- Ponto crítico: `correctAlternative` e `isCorrect` são expostos publicamente.
- Ponto técnico: CORS liberou `http://localhost:3000`, mas não liberou `https://xtri.online` nos testes.
- Ponto de dados: algumas questões recentes podem retornar `skill` e `param_b` nulos.

## Conexão com requisitos do banco de questões

| Requisito | API atual | Observação |
|---|---|---|
| Questão | Parcial bom | `QuestionList` e `QuestionDetail` expõem contrato claro |
| Alternativas | Bom | `Alternative` é estruturado na API |
| Habilidade | Bom | `EnemSkill` expõe área, código e descrição |
| Prova/ano | Bom | `Exam` e endpoints por ano |
| Caderno/posição | Parcial | Há `index`, mas não caderno/cor no contrato observado |
| Suporte visual | Parcial | Há `image`, `files`, `file`, `localFile`, mas sem descrição acessível |
| TRI | Parcial bom | `param_a`, `param_b`, `param_c`, `in_item_aban` |
| Desempenho agregado | Ausente | Não aparece no contrato público |
| Revisão pedagógica | Ausente | Não aparece no contrato público |
| IA/PLN | Ausente | Não aparece no contrato público |

## Próximas ações técnicas

1. Registrar decisão sobre exposição de gabarito público (`correctAlternative` e `isCorrect`).
2. Registrar decisão sobre a API como interface oficial de consulta para produtos XTRI.
3. Corrigir ou configurar CORS para domínios oficiais consumidores.
4. Definir política de cache e rate limit para endpoints públicos.
5. Planejar endpoint, parâmetro ou modo `assessment` sem exposição de gabarito.
6. Planejar versionamento futuro por path, como `/api/v1/`, antes de breaking changes.

## Notas relacionadas

- [[Supabase - banco de questões]]
- [[Auditoria - API Própria Questões XTRI]]
- [[Requisitos - Banco de Questões XTRI]]
- [[Auditoria - Schema Real Banco de Questões]]
- [[Checklist - Auditoria do Schema Banco de Questões]]
- [[Síntese - Artigos TRI e ENEM para XTRI]]
