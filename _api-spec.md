---
type: Note
---
# API · Contrato

**Base**: `https://api.questoes.xtri.online/api/`
**Docs**: <https://api.questoes.xtri.online/api/docs/>
**Stack**: Django REST Framework

## Endpoints

| Método | Path | Retorna | Paginação |
|---|---|---|---|
| GET | `/api/exams/` | 17 edições | sem paginação |
| GET | `/api/skills/` | 120 habilidades | sem paginação |
| GET | `/api/questions/` | 3,123 questões | `?page=N` · 50/página |

### Schema `questions[]`
```json
{
  "id": int, "title": str, "index": int, "year": int, "slug": str,
  "discipline": str, "language": str|null,
  "skill": { "area": "CH|CN|LC|MT", "code": "H1..H30", "label": str } | null,
  "image": str|null, "correctAlternative": "A".."E",
  "param_b": float|null
}
```

**Cobertura observada**: `skill` 2,849 (91.2%) · `param_b` 2,523 (80.8%).

### Schema `skills[]`
```json
{ "area": "CH|CN|LC|MT", "code": "H1..H30", "label": str }
```

### Schema `exams[]`
```json
{ "title": str, "year": int, "disciplines": [...], "languages": [...] }
```

## Gaps
- Sem `/openapi.json` · sem `/swagger.json`
- Sem endpoint de auth · sem rate-limiting documentado
- Sem versionamento (`/api/v1/...`)
