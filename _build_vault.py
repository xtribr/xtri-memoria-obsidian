#!/usr/bin/env python3
"""
Build the 'Questões ENEM' Obsidian vault from api.questoes.xtri.online.

v2 — adds curated discipline classification per the Simulados 2026 xtri taxonomy:
 - Linguagens:  Português · Literatura · Arte · Educação Física · Inglês · Espanhol
 - Humanas:     Filosofia · Geografia · História · Sociologia
 - Natureza:    Biologia · Física · Química
 - Matemática:  + sub-tema (Geom Plana/Espacial/Analítica · Álgebra · Aritmética · Funções · Estatística · Probabilidade · Proporcionalidade · Unidades de medida)

Classification confidence:
 - 'alta'          → derivada de API determinística OU label de habilidade inequívoca
 - 'media'         → label da habilidade aponta probabilidade > 70% mas tem alternativa
 - 'indeterminada' → impossível inferir sem OCR; campo `disciplina_candidatos` lista as opções
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

VAULT = Path("/Users/home/Library/Mobile Documents/com~apple~CloudDocs/OBSIDIAN - QUESTÕES ENEM/Questões ENEM")
BASE = "https://api.questoes.xtri.online/api"

AREA_LABELS = {
    "CH": "Ciências Humanas e suas Tecnologias",
    "CN": "Ciências da Natureza e suas Tecnologias",
    "LC": "Linguagens, Códigos e suas Tecnologias",
    "MT": "Matemática e suas Tecnologias",
}

# discipline string returned by API → area sigla
DISCIPLINE_TO_AREA = {
    "ciencias-humanas-e-suas-tecnologias": "CH",
    "ciencias-da-natureza-e-suas-tecnologias": "CN",
    "linguagens-codigos-e-suas-tecnologias": "LC",
    "matematica-e-suas-tecnologias": "MT",
    "ciencias-humanas": "CH",
    "ciencias-natureza": "CN",
    "linguagens": "LC",
    "matematica": "MT",
}

# Candidate disciplines per area (used when classification is indeterminada)
CANDIDATES = {
    "LC": ["Português", "Literatura", "Arte", "Educação Física"],  # Inglês/Espanhol resolvem via language
    "CH": ["Filosofia", "Geografia", "História", "Sociologia"],
    "CN": ["Biologia", "Física", "Química"],
    "MT": ["Matemática"],
}

# ---------------------------------------------------------------------------
# CURATED SKILL → DISCIPLINE MAPPING
# Built from manual reading of the 120 INEP skill labels (BNCC/Matriz ENEM)
# Use only when the label INEQUIVOCALLY points to a discipline.
# ---------------------------------------------------------------------------
SKILL_MAP: dict[tuple[str, str], dict] = {
    # ---- LC: Linguagens ----
    ("LC", "H5"):  {"disciplina": "LEM",  "confianca": "alta", "nota": "LEM — desambigua via language=ingles|espanhol"},
    ("LC", "H6"):  {"disciplina": "LEM",  "confianca": "alta"},
    ("LC", "H7"):  {"disciplina": "LEM",  "confianca": "alta"},
    ("LC", "H8"):  {"disciplina": "LEM",  "confianca": "alta"},
    ("LC", "H9"):  {"disciplina": "Educação Física", "confianca": "alta"},
    ("LC", "H10"): {"disciplina": "Educação Física", "confianca": "alta"},
    ("LC", "H11"): {"disciplina": "Educação Física", "confianca": "alta"},
    ("LC", "H12"): {"disciplina": "Arte", "confianca": "alta"},
    ("LC", "H13"): {"disciplina": "Arte", "confianca": "alta"},
    ("LC", "H14"): {"disciplina": "Arte", "confianca": "alta"},
    ("LC", "H15"): {"disciplina": "Literatura", "confianca": "alta"},
    ("LC", "H16"): {"disciplina": "Literatura", "confianca": "alta"},
    ("LC", "H17"): {"disciplina": "Literatura", "confianca": "alta"},
    ("LC", "H18"): {"disciplina": "Português", "confianca": "media", "nota": "gêneros — pode ser Literatura também"},
    ("LC", "H19"): {"disciplina": "Português", "confianca": "alta"},
    ("LC", "H20"): {"disciplina": "Português", "confianca": "alta"},
    ("LC", "H21"): {"disciplina": "Português", "confianca": "media"},
    ("LC", "H22"): {"disciplina": "Português", "confianca": "media"},
    ("LC", "H23"): {"disciplina": "Português", "confianca": "alta"},
    ("LC", "H24"): {"disciplina": "Português", "confianca": "alta"},
    ("LC", "H25"): {"disciplina": "Português", "confianca": "alta"},
    ("LC", "H26"): {"disciplina": "Português", "confianca": "alta"},
    ("LC", "H27"): {"disciplina": "Português", "confianca": "alta"},
    # LC H1, H2, H3, H4, H28, H29, H30 — ambíguos sem OCR

    # ---- CH: Humanas ----
    ("CH", "H6"):  {"disciplina": "Geografia", "confianca": "alta"},
    ("CH", "H8"):  {"disciplina": "Geografia", "confianca": "alta"},
    ("CH", "H10"): {"disciplina": "Sociologia", "confianca": "alta"},
    ("CH", "H12"): {"disciplina": "Sociologia", "confianca": "alta"},
    ("CH", "H17"): {"disciplina": "Geografia", "confianca": "alta"},
    ("CH", "H18"): {"disciplina": "Geografia", "confianca": "media"},
    ("CH", "H19"): {"disciplina": "Geografia", "confianca": "alta"},
    ("CH", "H21"): {"disciplina": "Sociologia", "confianca": "media"},
    ("CH", "H23"): {"disciplina": "Filosofia", "confianca": "media", "nota": "valores éticos — pode ser Sociologia"},
    ("CH", "H26"): {"disciplina": "Geografia", "confianca": "alta"},
    ("CH", "H27"): {"disciplina": "Geografia", "confianca": "alta"},
    ("CH", "H28"): {"disciplina": "Geografia", "confianca": "media"},
    ("CH", "H29"): {"disciplina": "Geografia", "confianca": "alta"},
    ("CH", "H30"): {"disciplina": "Geografia", "confianca": "media"},
    # CH H1-H5, H7, H9, H11, H13-H16, H20, H22, H24, H25 — ambíguos (Hist/Geo/Soc/Filo)

    # ---- CN: Natureza ----
    ("CN", "H1"):  {"disciplina": "Física", "confianca": "alta"},
    ("CN", "H5"):  {"disciplina": "Física", "confianca": "alta"},
    ("CN", "H20"): {"disciplina": "Física", "confianca": "alta"},
    ("CN", "H4"):  {"disciplina": "Biologia", "confianca": "alta"},
    ("CN", "H9"):  {"disciplina": "Biologia", "confianca": "alta"},
    ("CN", "H11"): {"disciplina": "Biologia", "confianca": "alta"},
    ("CN", "H13"): {"disciplina": "Biologia", "confianca": "alta"},
    ("CN", "H14"): {"disciplina": "Biologia", "confianca": "alta"},
    ("CN", "H15"): {"disciplina": "Biologia", "confianca": "alta"},
    ("CN", "H16"): {"disciplina": "Biologia", "confianca": "alta"},
    ("CN", "H28"): {"disciplina": "Biologia", "confianca": "alta"},
    ("CN", "H29"): {"disciplina": "Biologia", "confianca": "alta"},
    ("CN", "H24"): {"disciplina": "Química", "confianca": "alta"},
    ("CN", "H25"): {"disciplina": "Química", "confianca": "alta"},
    ("CN", "H27"): {"disciplina": "Química", "confianca": "alta"},
    # CN H2, H3, H6-H8, H10, H12, H17-H19, H21-H23, H26, H30 — ambíguos

    # ---- MT: Matemática (disciplina única; sub_tema quando label permite) ----
    ("MT", "H1"):  {"disciplina": "Matemática", "sub_tema": "Aritmética", "confianca": "alta"},
    ("MT", "H2"):  {"disciplina": "Matemática", "sub_tema": "Aritmética", "confianca": "alta"},
    ("MT", "H3"):  {"disciplina": "Matemática", "sub_tema": "Aritmética", "confianca": "media"},
    ("MT", "H4"):  {"disciplina": "Matemática", "sub_tema": "Aritmética", "confianca": "media"},
    ("MT", "H5"):  {"disciplina": "Matemática", "sub_tema": "Aritmética", "confianca": "media"},
    ("MT", "H6"):  {"disciplina": "Matemática", "sub_tema": "Geometria Espacial", "confianca": "alta"},
    ("MT", "H7"):  {"disciplina": "Matemática", "sub_tema": "Geometria", "confianca": "media", "nota": "Plana OU Espacial"},
    ("MT", "H8"):  {"disciplina": "Matemática", "sub_tema": "Geometria", "confianca": "media"},
    ("MT", "H9"):  {"disciplina": "Matemática", "sub_tema": "Geometria", "confianca": "media"},
    ("MT", "H10"): {"disciplina": "Matemática", "sub_tema": "Unidades de medida", "confianca": "alta"},
    ("MT", "H11"): {"disciplina": "Matemática", "sub_tema": "Unidades de medida", "confianca": "alta"},
    ("MT", "H12"): {"disciplina": "Matemática", "sub_tema": "Unidades de medida", "confianca": "media"},
    ("MT", "H13"): {"disciplina": "Matemática", "sub_tema": "Unidades de medida", "confianca": "media"},
    ("MT", "H14"): {"disciplina": "Matemática", "sub_tema": "Geometria", "confianca": "media"},
    ("MT", "H15"): {"disciplina": "Matemática", "sub_tema": "Proporcionalidade", "confianca": "alta"},
    ("MT", "H16"): {"disciplina": "Matemática", "sub_tema": "Proporcionalidade", "confianca": "alta"},
    ("MT", "H17"): {"disciplina": "Matemática", "sub_tema": "Proporcionalidade", "confianca": "media"},
    ("MT", "H18"): {"disciplina": "Matemática", "sub_tema": "Proporcionalidade", "confianca": "media"},
    ("MT", "H19"): {"disciplina": "Matemática", "sub_tema": "Álgebra", "confianca": "alta"},
    ("MT", "H20"): {"disciplina": "Matemática", "sub_tema": "Funções", "confianca": "alta", "nota": "gráfico cartesiano — pode ser Analítica"},
    ("MT", "H21"): {"disciplina": "Matemática", "sub_tema": "Álgebra", "confianca": "alta"},
    ("MT", "H22"): {"disciplina": "Matemática", "sub_tema": "Álgebra", "confianca": "media"},
    ("MT", "H23"): {"disciplina": "Matemática", "sub_tema": "Álgebra", "confianca": "media"},
    ("MT", "H24"): {"disciplina": "Matemática", "sub_tema": "Estatística", "confianca": "alta"},
    ("MT", "H25"): {"disciplina": "Matemática", "sub_tema": "Estatística", "confianca": "alta"},
    ("MT", "H26"): {"disciplina": "Matemática", "sub_tema": "Estatística", "confianca": "alta"},
    ("MT", "H27"): {"disciplina": "Matemática", "sub_tema": "Estatística", "confianca": "alta"},
    ("MT", "H28"): {"disciplina": "Matemática", "sub_tema": "Probabilidade", "confianca": "alta"},
    ("MT", "H29"): {"disciplina": "Matemática", "sub_tema": "Probabilidade", "confianca": "alta"},
    ("MT", "H30"): {"disciplina": "Matemática", "sub_tema": "Probabilidade", "confianca": "media"},
}


def classify(q: dict) -> dict:
    """Return classification dict: area, disciplina, sub_tema, confianca, fonte, candidatos."""
    discipline_api = (q.get("discipline") or "").strip().lower()
    area = DISCIPLINE_TO_AREA.get(discipline_api, "")
    language = q.get("language")
    skill_obj = q.get("skill") if isinstance(q.get("skill"), dict) else None
    skill_code = skill_obj.get("code") if skill_obj else None

    # 1. LEM via language (alta)
    if area == "LC" and language == "ingles":
        return {"area": area, "disciplina": "Inglês", "sub_tema": None,
                "confianca": "alta", "fonte": "language=ingles", "candidatos": None}
    if area == "LC" and language == "espanhol":
        return {"area": area, "disciplina": "Espanhol", "sub_tema": None,
                "confianca": "alta", "fonte": "language=espanhol", "candidatos": None}

    # 2. Mapping via skill label
    if area and skill_code:
        m = SKILL_MAP.get((area, skill_code))
        if m:
            d = m["disciplina"]
            # special-case "LEM" → resolve to Inglês/Espanhol via language; if no language, indeterminado
            if d == "LEM":
                if language == "ingles":
                    d = "Inglês"
                elif language == "espanhol":
                    d = "Espanhol"
                else:
                    return {"area": area, "disciplina": "indeterminada", "sub_tema": None,
                            "confianca": "indeterminada", "fonte": f"skill={skill_code} LEM sem language",
                            "candidatos": ["Inglês", "Espanhol"]}
            return {"area": area, "disciplina": d, "sub_tema": m.get("sub_tema"),
                    "confianca": m["confianca"], "fonte": f"skill={skill_code}", "candidatos": None}

    # 3. Matemática sem skill mapeado → ainda determinístico na disciplina
    if area == "MT":
        return {"area": area, "disciplina": "Matemática", "sub_tema": None,
                "confianca": "alta", "fonte": "discipline=matematica",
                "candidatos": None}

    # 4. Indeterminada
    return {"area": area or "?", "disciplina": "indeterminada", "sub_tema": None,
            "confianca": "indeterminada", "fonte": "sem-skill-ou-skill-ambigua",
            "candidatos": CANDIDATES.get(area, [])}


def fetch(url: str, retries: int = 3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "vault-builder/2.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  retry {attempt+1}/{retries} after error: {e}", file=sys.stderr)
            time.sleep(1 + attempt)


def safe_slug(s: str, max_len: int = 60) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return s[:max_len] or "item"


def skill_code_of(raw) -> str | None:
    if isinstance(raw, dict):
        v = raw.get("code")
        if isinstance(v, str) and v:
            return v
    return None


# ---------------------------------------------------------------------------
print("→ fetching skills/")
skills = fetch(f"{BASE}/skills/")
print(f"  {len(skills)} habilidades")

print("→ fetching exams/")
exams_payload = fetch(f"{BASE}/exams/")
exams = exams_payload.get("results", exams_payload) if isinstance(exams_payload, dict) else exams_payload
print(f"  {len(exams)} exames")

print("→ fetching questions/")
questions: list[dict] = []
page = 1
while True:
    payload = fetch(f"{BASE}/questions/?page={page}")
    results = payload.get("results", [])
    questions.extend(results)
    if not payload.get("next"):
        break
    page += 1
print(f"  {len(questions)} questões")

# Normalize skill on every question (preserve dict for classification, also store code)
for q in questions:
    q["_skill_code"] = skill_code_of(q.get("skill"))
    q["_class"] = classify(q)

# ---------------------------------------------------------------------------
# Inventory of classification
# ---------------------------------------------------------------------------
from collections import Counter
inv = Counter()
for q in questions:
    c = q["_class"]
    key = (c["area"], c["disciplina"], c["confianca"])
    inv[key] += 1

print("\n=== Classificação resultante ===")
totals_by_disc = Counter()
totals_by_conf = Counter()
for (area, disc, conf), n in sorted(inv.items(), key=lambda x: -x[1]):
    print(f"  {area:3} · {disc:18} · {conf:14} → {n:>4}")
    totals_by_disc[disc] += n
    totals_by_conf[conf] += n
print(f"\n  Confiança: {dict(totals_by_conf)}")
print(f"  Por disciplina: {dict(totals_by_disc)}")

# Sub-temas MT
mt_sub = Counter(q["_class"].get("sub_tema") for q in questions if q["_class"]["area"] == "MT")
print(f"\n  MT sub-temas: {dict(mt_sub)}")

# ---------------------------------------------------------------------------
print(f"\n→ writing to vault: {VAULT}")
assert VAULT.exists()

(VAULT / "Exams").mkdir(exist_ok=True)
(VAULT / "Disciplines").mkdir(exist_ok=True)
(VAULT / "Skills").mkdir(exist_ok=True)
for area in AREA_LABELS:
    (VAULT / "Skills" / area).mkdir(exist_ok=True)
(VAULT / "Questions").mkdir(exist_ok=True)

# Group questions
by_year: dict[int, list[dict]] = defaultdict(list)
by_area: dict[str, list[dict]] = defaultdict(list)
by_skill: dict[str, list[dict]] = defaultdict(list)
by_disc: dict[str, list[dict]] = defaultdict(list)
for q in questions:
    yr = q.get("year")
    if yr:
        by_year[yr].append(q)
    by_area[q["_class"]["area"]].append(q)
    if q["_skill_code"]:
        by_skill[q["_skill_code"]].append(q)
    by_disc[q["_class"]["disciplina"]].append(q)

for yr in by_year:
    (VAULT / "Questions" / str(yr)).mkdir(exist_ok=True)


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


# 1. _index.md
print("→ writing _index.md")
api_skill_pop = sum(1 for q in questions if q.get("skill"))
api_param_pop = sum(1 for q in questions if q.get("param_b") is not None)
classif_alta = totals_by_conf.get("alta", 0)
classif_media = totals_by_conf.get("media", 0)
classif_ind = totals_by_conf.get("indeterminada", 0)

write(VAULT / "_index.md", f"""---
type: Note
---
# Questões ENEM — Memória completa

Vault com **{len(questions):,} questões** de **{len(exams)} edições** do ENEM (2009–2025), sincronizadas com [`api.questoes.xtri.online`](https://api.questoes.xtri.online/api/docs/).

## Estrutura

- [[Exams/_index|Exams]] — {len(exams)} edições
- [[Disciplines/_index|Disciplines]] — 4 áreas
- [[Skills/_index|Skills]] — 120 habilidades INEP
- `Questions/` — {len(questions):,} notas (uma por questão, agrupadas por ano)
- [[_taxonomia]] — taxonomia de disciplinas alinhada com `SIMULADOS 2026 xtri`

## Classificação por disciplina (Fase 1 + 2)

| Confiança | Qtd | % |
|---|---|---|
| 🟢 alta (determinístico) | {classif_alta:,} | {classif_alta/len(questions)*100:.1f}% |
| 🟡 média (skill aponta mas tem ruído) | {classif_media:,} | {classif_media/len(questions)*100:.1f}% |
| 🔴 indeterminada (precisa OCR) | {classif_ind:,} | {classif_ind/len(questions)*100:.1f}% |

### Distribuição por disciplina

| Disciplina | Questões |
|---|---|
""" + "\n".join(
    f"| {d} | {totals_by_disc[d]:,} |"
    for d in sorted(totals_by_disc, key=lambda x: -totals_by_disc[x])
) + f"""

## Cobertura por ano

| Ano | Questões | LC | CH | CN | MT |
|---|---|---|---|---|---|
""" + "\n".join(
    f"| [[enem-{yr}|{yr}]] | {len(by_year[yr])} | "
    + " | ".join(
        str(sum(1 for q in by_year[yr] if q["_class"]["area"] == a))
        for a in ["LC", "CH", "CN", "MT"]
    )
    + " |"
    for yr in sorted(by_year)
) + f"""

## Cobertura da API (verificada na geração)

- `skill` populado em **{api_skill_pop:,} / {len(questions):,}** ({api_skill_pop/len(questions)*100:.1f}%)
- `param_b` (TRI) populado em **{api_param_pop:,} / {len(questions):,}** ({api_param_pop/len(questions)*100:.1f}%)

## Próximos passos

- **Fase 3 (pendente de aprovação)**: OCR + LLM para resolver as {classif_ind:,} questões indeterminadas. Custo estimado: ~US$ {classif_ind*0.005:.0f}, ~2h de execução.
- Veja [[_api-spec]] para o contrato completo

## Sincronização

Vault gerado em {time.strftime("%Y-%m-%d")} via `_build_vault.py` (idempotente — re-rodar = re-sincronizar).
""")

# 2. _api-spec.md
print("→ writing _api-spec.md")
write(VAULT / "_api-spec.md", f"""---
type: Note
---
# API · Contrato

**Base**: `{BASE}/`
**Docs**: <https://api.questoes.xtri.online/api/docs/>
**Stack**: Django REST Framework

## Endpoints

| Método | Path | Retorna | Paginação |
|---|---|---|---|
| GET | `/api/exams/` | {len(exams)} edições | sem paginação |
| GET | `/api/skills/` | {len(skills)} habilidades | sem paginação |
| GET | `/api/questions/` | {len(questions):,} questões | `?page=N` · 50/página |

### Schema `questions[]`
```json
{{
  "id": int, "title": str, "index": int, "year": int, "slug": str,
  "discipline": str, "language": str|null,
  "skill": {{ "area": "CH|CN|LC|MT", "code": "H1..H30", "label": str }} | null,
  "image": str|null, "correctAlternative": "A".."E",
  "param_b": float|null
}}
```

**Cobertura observada**: `skill` {api_skill_pop:,} ({api_skill_pop/len(questions)*100:.1f}%) · `param_b` {api_param_pop:,} ({api_param_pop/len(questions)*100:.1f}%).

### Schema `skills[]`
```json
{{ "area": "CH|CN|LC|MT", "code": "H1..H30", "label": str }}
```

### Schema `exams[]`
```json
{{ "title": str, "year": int, "disciplines": [...], "languages": [...] }}
```

## Gaps
- Sem `/openapi.json` · sem `/swagger.json`
- Sem endpoint de auth · sem rate-limiting documentado
- Sem versionamento (`/api/v1/...`)
""")

# 3. _taxonomia.md
print("→ writing _taxonomia.md")
write(VAULT / "_taxonomia.md", f"""---
type: Note
---
# Taxonomia de disciplinas — alinhada com `SIMULADOS 2026 xtri`

Esta é a nomenclatura canônica usada no campo `disciplina` de cada questão.

## Linguagens, Códigos e suas Tecnologias (LC)
- **Português** — interpretação, gramática, gêneros textuais, argumentação, variedades linguísticas
- **Literatura** — texto literário, escolas literárias, patrimônio literário nacional
- **Arte** — produção artística, manifestações culturais, diversidade estética
- **Educação Física** — manifestações corporais, cultura de movimento, esporte e saúde
- **Inglês** — LEM Inglês (idioma escolhido pelo aluno)
- **Espanhol** — LEM Espanhol (idioma escolhido pelo aluno)

## Ciências Humanas e suas Tecnologias (CH)
- **Filosofia** — ética, política, epistemologia, filosofia clássica/moderna/contemporânea
- **Geografia** — espaço, território, climatologia, geopolítica, urbanização, agropecuária
- **História** — Brasil colonial/império/república, ditadura, civilizações, história geral
- **Sociologia** — instituições sociais, movimentos sociais, cidadania, cultura, trabalho

## Ciências da Natureza e suas Tecnologias (CN)
- **Biologia** — ecossistemas, genética, evolução, fisiologia, saúde
- **Física** — mecânica, termodinâmica, eletromagnetismo, ondas, eletricidade
- **Química** — orgânica, inorgânica, físico-química, ambiental

## Matemática e suas Tecnologias (MT)

Disciplina única; sub-temas:
- **Aritmética** — números, operações, contagem
- **Álgebra** — equações, sistemas, expressões algébricas
- **Geometria** (genérico — quando plana/espacial não é distinguível pela habilidade)
- **Geometria Plana** — figuras planas, áreas
- **Geometria Espacial** — sólidos, volumes (3D)
- **Geometria Analítica** — pontos, retas, cônicas em plano cartesiano
- **Funções** — gráficos cartesianos, modelagem
- **Proporcionalidade** — razão, proporção direta/inversa
- **Unidades de medida** — escalas, grandezas
- **Estatística** — média, mediana, gráficos, tabelas
- **Probabilidade** — eventos, combinatória

## Confiança de classificação

Cada questão tem `disciplina_confianca` no frontmatter:
- **alta** — derivada de campo determinístico (idioma, área única) ou habilidade INEP cuja label aponta inequivocamente
- **media** — habilidade INEP indica probabilidade > 70% mas existe alternativa
- **indeterminada** — não dá pra inferir sem ler o enunciado (precisa OCR); `disciplina_candidatos` lista as opções viáveis

> Origem do mapping habilidade → disciplina: leitura curada das 120 labels da Matriz INEP em 2026-05-17.
""")

# 4. Disciplines
print("→ writing Disciplines/")
write(VAULT / "Disciplines" / "_index.md", f"""---
type: Note
---
# Disciplines

| Sigla | Área | Questões | Disciplinas filhas |
|---|---|---|---|
""" + "\n".join(
    f"| [[discipline-{a.lower()}|{a}]] | {AREA_LABELS[a]} | {len(by_area.get(a, []))} | "
    + ", ".join(CANDIDATES[a] + (["Inglês", "Espanhol"] if a == "LC" else []))
    + " |"
    for a in AREA_LABELS
))

for area, label in AREA_LABELS.items():
    qs = by_area.get(area, [])
    skills_in_area = [s for s in skills if s["area"] == area]
    disc_breakdown = Counter(q["_class"]["disciplina"] for q in qs)
    breakdown_md = "\n".join(
        f"- **{d}** — {n:,} questões"
        for d, n in sorted(disc_breakdown.items(), key=lambda x: -x[1])
    )
    write(VAULT / "Disciplines" / f"discipline-{area.lower()}.md", f"""---
type: Discipline
area: {area}
---
# {label} ({area})

**{len(qs):,} questões** · **{len(skills_in_area)} habilidades**

## Distribuição por disciplina

{breakdown_md}

## Habilidades

Ver [[Skills/_index]]. Subset desta área:
""" + "\n".join(
        f"- [[{s['code']}|{s['code']}]] — {s['label']}"
        for s in sorted(skills_in_area, key=lambda x: int(x["code"][1:]))
    ) + f"""

## Cobertura por ano

| Ano | Questões |
|---|---|
""" + "\n".join(
        f"| [[enem-{yr}|{yr}]] | {sum(1 for q in by_year[yr] if q['_class']['area'] == area)} |"
        for yr in sorted(by_year)
    ))

# 5. Skills
print("→ writing Skills/")
write(VAULT / "Skills" / "_index.md", f"""---
type: Note
---
# Skills — Matriz de Referência ENEM

**120 habilidades** organizadas em 4 áreas (30 por área).

""" + "\n".join(
    f"## {AREA_LABELS[a]} ({a})\n\n"
    + "\n".join(
        f"- [[{s['code']}|{s['code']}]] — {s['label']}"
        for s in sorted([sk for sk in skills if sk["area"] == a], key=lambda x: int(x["code"][1:]))
    )
    + "\n"
    for a in AREA_LABELS
))

for s in skills:
    area = s["area"]
    code = s["code"]
    refs = sorted(by_skill.get(code, []), key=lambda x: (-(x.get("year") or 0), x.get("index") or 0))
    mapping = SKILL_MAP.get((area, code))
    mapping_md = ""
    if mapping:
        nota = f" — {mapping.get('nota')}" if mapping.get("nota") else ""
        sub = f" · sub-tema: **{mapping['sub_tema']}**" if mapping.get("sub_tema") else ""
        mapping_md = f"\n\n**Mapeamento curado**: disciplina → **{mapping['disciplina']}** (confiança: {mapping['confianca']}){sub}{nota}\n"

    if refs:
        by_yr = defaultdict(list)
        for q in refs:
            by_yr[q.get("year")].append(q)
        body = f"**{len(refs)} questões** mapeadas pela API.\n\n"
        for yr in sorted(by_yr, reverse=True):
            body += f"### ENEM {yr} ({len(by_yr[yr])})\n\n"
            for q in by_yr[yr]:
                gab = q.get("correctAlternative") or "?"
                idx = q.get("index", "?")
                d = q["_class"]["disciplina"]
                body += f"- Q{idx} · gab `{gab}` · {d} · [[{safe_slug(q['slug'])}-{q['id']}|{(q.get('title') or 'questão').strip()[:50]}]]\n"
            body += "\n"
    else:
        body = "_Nenhuma questão mapeada por esta habilidade na API consultada._"

    write(VAULT / "Skills" / area / f"{code}.md", f"""---
type: Skill
area: {area}
code: {code}
n_questions: {len(refs)}
---
# {code} — {AREA_LABELS[area]}

> {s['label']}

**Área**: [[discipline-{area.lower()}|{AREA_LABELS[area]} ({area})]]
{mapping_md}
## Questões que testam esta habilidade

{body}
""")

# 6. Exams
print("→ writing Exams/")
write(VAULT / "Exams" / "_index.md", f"""---
type: Note
---
# Exams — Edições ENEM

{len(exams)} edições.

| Ano | Questões | LC | CH | CN | MT |
|---|---|---|---|---|---|
""" + "\n".join(
    f"| [[enem-{yr}|{yr}]] | {len(by_year[yr])} | "
    + " | ".join(
        str(sum(1 for q in by_year[yr] if q["_class"]["area"] == a))
        for a in ["LC", "CH", "CN", "MT"]
    )
    + " |"
    for yr in sorted(by_year)
))

for ex in exams:
    yr = ex.get("year")
    if not yr:
        continue
    qs = sorted(by_year.get(yr, []), key=lambda x: (x["_class"]["area"], x.get("index") or 0))
    disciplines_list = ex.get("disciplines") or []
    languages_list = ex.get("languages") or []
    rows = "\n".join(
        f"| {q.get('index', '?')} | {q['_class']['area']} | {q['_class']['disciplina']} | "
        f"{q['_class']['confianca']} | `{q.get('correctAlternative','?')}` | "
        f"[[{safe_slug(q['slug'])}-{q['id']}|{(q.get('title') or 'questão').strip()[:50]}]] |"
        for q in qs
    )
    write(VAULT / "Exams" / f"enem-{yr}.md", f"""---
type: Exam
year: {yr}
title: ENEM {yr}
---
# {ex.get('title', f'ENEM {yr}')}

**{len(qs)} questões no vault**

## Disciplinas (no payload da API)
{chr(10).join(f"- `{d.get('value','?')}` — {d.get('label','?')}" for d in disciplines_list) if disciplines_list else '_(não informado)_'}

## Idiomas (LC)
{chr(10).join(f"- `{l.get('value','?')}` — {l.get('label','?')}" for l in languages_list) if languages_list else '_(sem variante)_'}

## Questões

| Nº | Área | Disciplina | Confiança | Gabarito | Título |
|---|---|---|---|---|---|
{rows}
""")

# 7. Questions
print(f"→ writing Questions/ ({len(questions):,} notes)")
for q in questions:
    yr = q.get("year")
    if not yr:
        continue
    cls = q["_class"]
    area = cls["area"]
    disc = cls["disciplina"]
    sub = cls["sub_tema"]
    conf = cls["confianca"]
    cands = cls.get("candidatos") or []
    skill_code = q["_skill_code"] or ""
    param_b = q.get("param_b")
    slug = safe_slug(q.get("slug") or "questao")
    qid = q["id"]
    idx = q.get("index", 0)
    fname = f"{slug}-{qid}.md"

    # tags — alinhadas com Simulados 2026 (lowercase, hyphenated)
    tags = ["questao", f"ano-{yr}", area.lower()]
    if disc and disc != "indeterminada":
        tags.append(safe_slug(disc).replace("ç", "c").replace("ã", "a"))
    if sub:
        tags.append(safe_slug(sub))
    if conf == "indeterminada":
        tags.append("precisa-ocr")

    fm = [
        "---",
        "type: Question",
        f"id: {qid}",
        f"year: {yr}",
        f"index: {idx}",
        f"area: {area}",
        f"disciplina: {disc}",
    ]
    if sub:
        fm.append(f"sub_tema: {sub}")
    fm += [
        f"disciplina_confianca: {conf}",
    ]
    if cands:
        fm.append(f"disciplina_candidatos: [{', '.join(cands)}]")
    if cls.get("fonte"):
        fm.append(f"disciplina_fonte: {cls['fonte']}")
    fm += [
        f"language: {q.get('language') or ''}",
        f"skill: {skill_code}",
        f"correctAlternative: {q.get('correctAlternative') or ''}",
        f"param_b: {param_b if param_b is not None else ''}",
        f"tags: [{', '.join(tags)}]",
        "---",
        f"# {q.get('title') or f'Questão {idx} — ENEM {yr}'}",
        "",
        f"**Edição**: [[enem-{yr}]] · **Área**: [[discipline-{area.lower()}|{area}]] · **Disciplina**: **{disc}**"
        + (f" — sub-tema: **{sub}**" if sub else "")
        + f" (`confiança: {conf}`)",
        "",
        f"**Posição no caderno**: {idx}"
        + (f" · **Idioma**: {q['language']}" if q.get('language') else "")
        + f" · **Gabarito**: `{q.get('correctAlternative') or '?'}`"
        + (f" · **TRI** (`param_b`): `{param_b:+.4f}`" if isinstance(param_b, (int, float)) else ""),
    ]
    if conf == "indeterminada" and cands:
        fm += ["", f"> ⚠️ Disciplina não determinável a partir do payload da API. Candidatos: **{', '.join(cands)}**. Resolver via OCR + LLM (Fase 3)."]
    if q.get("image"):
        fm += ["", "## Enunciado", "", f"![enunciado]({q['image']})"]
    if skill_code:
        fm += ["", "## Habilidade testada", "", f"[[{skill_code}]] — `{cls.get('fonte','')}`"]
    fm += [
        "",
        "## Metadados",
        "",
        f"- **ID na API**: `{qid}`",
        f"- **Slug**: `{q.get('slug') or ''}`",
        f"- **API**: ver [[_api-spec]]",
        f"- **Taxonomia**: ver [[_taxonomia]]",
    ]
    write(VAULT / "Questions" / str(yr) / fname, "\n".join(fm) + "\n")

print(f"\n✓ done · {len(questions):,} question notes written")
