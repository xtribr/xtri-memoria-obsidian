#!/usr/bin/env python3
"""
Fase 6 step 4: aplica classificações Fase 6 (text-perfect) às notas .md.

Sobrescreve TODAS as classificações anteriores (alta/media/ai-*/vision-*)
para as 3.123 questões. Esta é a fonte canônica final.

Também atualiza param_a, param_b, param_c no frontmatter quando disponíveis.
"""
import json
import re
from collections import Counter
from pathlib import Path

VAULT = Path("/Users/home/Library/Mobile Documents/com~apple~CloudDocs/OBSIDIAN - QUESTÕES ENEM/Questões ENEM")
CACHE = Path.home() / "phase6-cache"

VALID_DISCS = {"Português","Literatura","Arte","Educação Física","Inglês","Espanhol",
               "Filosofia","Geografia","História","Sociologia",
               "Biologia","Física","Química","Matemática","indeterminada"}
VALID_AREAS = {"LC","CH","CN","MT"}
VALID_CONF = {"text-high","text-medium","text-low","text-impossivel"}

# Normalize agent typos (sem acento → com acento; sem prefixo → com text-)
DISC_NORMALIZE = {
    "Matematica": "Matemática", "Portugues": "Português", "Fisica": "Física",
    "Quimica": "Química", "Historia": "História",
    "EducacaoFisica": "Educação Física", "EdFísica": "Educação Física",
    "Ingles": "Inglês",
}
CONF_NORMALIZE = {"medium": "text-medium", "high": "text-high",
                  "low": "text-low", "impossivel": "text-impossivel"}


def safe_slug(s):
    return re.sub(r"[^\w-]", "-", s.lower().replace("ç","c").replace("ã","a")
                  .replace("á","a").replace("é","e").replace("í","i")
                  .replace("ó","o").replace("ú","u").replace("õ","o"))

DISC_TO_AREA = {
    "Português":"LC","Literatura":"LC","Arte":"LC","Educação Física":"LC",
    "Inglês":"LC","Espanhol":"LC",
    "Filosofia":"CH","Geografia":"CH","História":"CH","Sociologia":"CH",
    "Biologia":"CN","Física":"CN","Química":"CN",
    "Matemática":"MT",
}

# Load classifications
all_class = {}
invalid = 0
for f in sorted(CACHE.glob("phase6-classified-*.jsonl")):
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            invalid += 1
            continue
        # Normalize variants
        r["disciplina"] = DISC_NORMALIZE.get(r.get("disciplina"), r.get("disciplina"))
        r["confianca"] = CONF_NORMALIZE.get(r.get("confianca"), r.get("confianca"))
        # Validação
        if r.get("disciplina") not in VALID_DISCS:
            invalid += 1
            continue
        if r.get("confianca") not in VALID_CONF:
            invalid += 1
            continue
        # Derive area do disciplina
        if r["disciplina"] != "indeterminada":
            r["area"] = DISC_TO_AREA[r["disciplina"]]
        else:
            r["area"] = r.get("area", "?")
        all_class[r["id"]] = r

print(f"loaded {len(all_class)} valid (invalid={invalid})")

# Load detail cache for TRI params
details = {}
for line in (CACHE / "questions-detail.jsonl").read_text(encoding="utf-8").splitlines():
    if not line.strip(): continue
    d = json.loads(line)
    if not d.get("_error"):
        details[d["id"]] = d
print(f"loaded {len(details)} details for TRI enrichment")

# Index notes
note_by_id = {}
for p in (VAULT / "Questions").glob("*/*.md"):
    text = p.read_text(encoding="utf-8")
    m = re.search(r"^id:\s*(\d+)", text, re.MULTILINE)
    if m:
        note_by_id[int(m.group(1))] = p

updated = 0
area_changed = 0
stats = Counter()
for qid, rec in all_class.items():
    path = note_by_id.get(qid)
    if not path:
        continue
    text = path.read_text(encoding="utf-8")
    disc = rec["disciplina"]
    area_new = rec["area"]
    conf = rec["confianca"]
    just = rec.get("justificativa", "")

    # Detect area change
    m_old = re.search(r"^area:\s*(\w+)", text, re.MULTILINE)
    if m_old and m_old.group(1) != area_new:
        area_changed += 1

    # Frontmatter
    text = re.sub(r"^area:.*$", f"area: {area_new}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina:.*$", f"disciplina: {disc}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_confianca:.*$", f"disciplina_confianca: {conf}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_candidatos:\s*\[.*?\]\n", "", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_fonte:.*$", "disciplina_fonte: phase6-text-claude", text, count=1, flags=re.MULTILINE)

    # TRI params (do detail cache)
    d = details.get(qid, {})
    for p_field in ("param_a", "param_b", "param_c"):
        v = d.get(p_field)
        v_str = f"{v}" if v is not None else ""
        # Update or add
        if re.search(rf"^{p_field}:", text, re.MULTILINE):
            text = re.sub(rf"^{p_field}:.*$", f"{p_field}: {v_str}", text, count=1, flags=re.MULTILINE)
        else:
            # Insert after disciplina_fonte
            text = re.sub(r"(^disciplina_fonte:.*$)",
                          rf"\1\n{p_field}: {v_str}", text, count=1, flags=re.MULTILINE)

    # Tags
    new_disc_tag = safe_slug(disc) if disc != "indeterminada" else "indeterminada"
    new_area_tag = area_new.lower() if area_new in VALID_AREAS else "outro"
    def fix_tags(m):
        items = [t.strip() for t in m.group(1).split(",")]
        items = [t for t in items if t not in (
            "ch","cn","lc","mt","precisa-ocr","classificado-ia",
            "classificado-vision","classificado-vision-livre","indeterminada",
            "humano-revisado","português","matemática","biologia","física","química",
            "geografia","historia","história","sociologia","filosofia","literatura",
            "arte","educacao-fisica","inglês","espanhol")]
        if new_area_tag not in items: items.append(new_area_tag)
        if new_disc_tag not in items: items.append(new_disc_tag)
        items.append("classificado-text")
        return f"tags: [{', '.join(items)}]"
    text = re.sub(r"^tags:\s*\[(.*?)\]", fix_tags, text, count=1, flags=re.MULTILINE)

    # Body line
    BODY = re.compile(r"\*\*Disciplina\*\*:\s*\*\*[^*]+\*\*(?:\s*—\s*sub-tema:\s*\*\*[^*]+\*\*)?\s*\(`confiança:\s*[^`]+`\)")
    text = BODY.sub(f"**Disciplina**: **{disc}** (`confiança: {conf}`)", text, count=1)
    text = re.sub(r"\*\*Área\*\*:\s*\[\[discipline-[a-z]+\|[A-Z]+\]\]",
                  f"**Área**: [[discipline-{area_new.lower()}|{area_new}]]", text, count=1)

    # Replace previous classification audit section
    prev = re.compile(r"## Classificação Fase [3-5].*?(?=\n## |\Z)", re.DOTALL)
    new_audit = (
        f"## Classificação Fase 6 (texto perfeito)\n\n"
        f"- **Disciplina**: **{disc}**\n"
        f"- **Área**: **{area_new}**\n"
        f"- **Confiança**: `{conf}`\n"
        f"- **Justificativa**: {just}\n"
        f"- **Método**: Claude lendo `context + alternativesIntroduction + alternatives` do detail endpoint da API\n"
        f"- **Data**: 2026-05-17\n"
    )
    if prev.search(text):
        text = prev.sub(new_audit + "\n", text, count=1)
    elif "## Classificação Fase 6" not in text:
        text = re.sub(r"(## Metadados)", new_audit + "\n\\1", text, count=1)

    path.write_text(text, encoding="utf-8")
    updated += 1
    stats[disc] += 1
    stats[f"_conf:{conf}"] += 1
    stats[f"_area:{area_new}"] += 1

print(f"\n✓ updated {updated}/{len(all_class)} · áreas corrigidas: {area_changed}")
print("\nBreakdown:")
for k, v in sorted(stats.items(), key=lambda x: -x[1])[:30]:
    print(f"  {k:30} {v}")
