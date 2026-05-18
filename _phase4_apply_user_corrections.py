#!/usr/bin/env python3
"""
Aplica as 21 correções marcadas pelo usuário no Spot-Check Fase 4.
Normaliza nomes (LINGUAGEM → Português via área LC, QUIMICA → Química, etc.)
e atualiza frontmatter, body e tags com `disciplina_confianca: humano-revisado`.
"""
import re
from pathlib import Path
from collections import Counter

VAULT = Path("/Users/home/Library/Mobile Documents/com~apple~CloudDocs/OBSIDIAN - QUESTÕES ENEM/Questões ENEM")

# Map correção do usuário → (disciplina canônica, área correta)
NORMALIZE = {
    "QUIMICA": ("Química", "CN"),
    "QUMICA":  ("Química", "CN"),
    "QUÍMICA": ("Química", "CN"),
    "FISICA":  ("Física", "CN"),
    "FÍSICA":  ("Física", "CN"),
    "BIOLOGIA": ("Biologia", "CN"),
    "MATEMATICA": ("Matemática", "MT"),
    "MATEMÁTICA": ("Matemática", "MT"),
    "HISTORIA": ("História", "CH"),
    "HISTÓRIA": ("História", "CH"),
    "GEOGRAFIA": ("Geografia", "CH"),
    "ARTES": ("Arte", "LC"),
    "ARTE": ("Arte", "LC"),
    "LITERATURA": ("Literatura", "LC"),
    "LINGUAGENS": ("Português", "LC"),
    "LINGUAGEM GENERO PEÇA PUBLICITÁRIA": ("Português", "LC"),  # peça publicitária = Português
}

CORRECTIONS = {
    14575: "LINGUAGEM GENERO PEÇA PUBLICITÁRIA",
    16986: "QUIMICA",
    16769: "QUMICA",
    17506: "FISICA",
    14647: "FISICA",
    15734: "BIOLOGIA",
    16245: "MATEMATICA",
    16759: "QUIMICA",
    17132: "FISICA",
    17175: "MATEMATICA",
    14732: "ARTES",
    15013: "HISTORIA",
    15208: "HISTORIA",
    15628: "BIOLOGIA",
    16312: "ARTES",
    16564: "QUIMICA",
    16794: "MATEMATICA",
    17297: "QUIMICA",
    16950: "GEOGRAFIA",
    14949: "BIOLOGIA",
    16389: "LINGUAGENS",
}


def safe_slug(s):
    return re.sub(r"[^\w-]", "-", s.lower()
                  .replace("ç","c").replace("ã","a").replace("õ","o")
                  .replace("á","a").replace("é","e").replace("í","i")
                  .replace("ó","o").replace("ú","u"))


# Index notes
note_by_id = {}
for p in (VAULT / "Questions").glob("*/*.md"):
    text = p.read_text(encoding="utf-8")
    m = re.search(r"^id:\s*(\d+)", text, re.MULTILINE)
    if m:
        note_by_id[int(m.group(1))] = p

stats = Counter()
for qid, raw in CORRECTIONS.items():
    path = note_by_id.get(qid)
    if not path:
        print(f"  ! id {qid} não encontrado")
        continue
    key = raw.strip().upper()
    if key not in NORMALIZE:
        print(f"  ! id {qid}: correção '{raw}' não reconhecida — pulando")
        stats["unrecognized"] += 1
        continue
    disc, area = NORMALIZE[key]
    text = path.read_text(encoding="utf-8")

    # Update frontmatter
    text = re.sub(r"^area:.*$", f"area: {area}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina:.*$", f"disciplina: {disc}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_confianca:.*$", "disciplina_confianca: humano-revisado", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_fonte:.*$", "disciplina_fonte: correcao-usuario-spotcheck-fase4", text, count=1, flags=re.MULTILINE)

    # Update tags
    new_tag = safe_slug(disc)
    new_area = area.lower()
    def fix_tags(m):
        items = [t.strip() for t in m.group(1).split(",")]
        # remove old area tags + old disciplina tags + old classificado-*
        items = [t for t in items if t not in (
            "ch","cn","lc","mt","precisa-ocr","classificado-ia","classificado-vision",
            "indeterminada","português","matemática","biologia","física","química",
            "geografia","historia","história","sociologia","filosofia","literatura",
            "arte","educacao-fisica","inglês","espanhol")]
        if new_area not in items:
            items.append(new_area)
        if new_tag not in items:
            items.append(new_tag)
        items.append("humano-revisado")
        return f"tags: [{', '.join(items)}]"
    text = re.sub(r"^tags:\s*\[(.*?)\]", fix_tags, text, count=1, flags=re.MULTILINE)

    # Update body
    BODY = re.compile(
        r"\*\*Disciplina\*\*:\s*\*\*[^*]+\*\*(?:\s*—\s*sub-tema:\s*\*\*[^*]+\*\*)?\s*\(`confiança:\s*[^`]+`\)"
    )
    text = BODY.sub(f"**Disciplina**: **{disc}** (`confiança: humano-revisado`)", text, count=1)
    # Update "Área" link in body too
    text = re.sub(r"\*\*Área\*\*:\s*\[\[discipline-[a-z]+\|[A-Z]+\]\]",
                  f"**Área**: [[discipline-{area.lower()}|{area}]]", text, count=1)

    # Append correction audit
    audit = (
        f"\n## Correção manual (Spot-Check Fase 4)\n\n"
        f"- **Área anterior** (da API): possivelmente errada\n"
        f"- **Disciplina anterior** (Vision): possivelmente errada\n"
        f"- **Correção do usuário**: área=**{area}** · disciplina=**{disc}**\n"
        f"- **Justificativa do usuário**: `{raw}`\n"
        f"- **Data**: 2026-05-17\n"
    )
    if "## Correção manual" not in text:
        text = re.sub(r"(## Metadados)", audit + "\n\\1", text, count=1)

    path.write_text(text, encoding="utf-8")
    stats[f"area:{area}"] += 1
    stats[f"disc:{disc}"] += 1

print(f"\n✓ aplicadas {sum(v for k,v in stats.items() if k.startswith('area:'))} correções")
print(f"\nBreakdown:")
for k, v in sorted(stats.items()):
    print(f"  {k:30} {v}")
