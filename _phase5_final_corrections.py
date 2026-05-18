#!/usr/bin/env python3
"""Aplica as 2 últimas correções nomeadas do Spot-Check Fase 5."""
import re
from pathlib import Path

VAULT = Path("/Users/home/Library/Mobile Documents/com~apple~CloudDocs/OBSIDIAN - QUESTÕES ENEM/Questões ENEM")

CORRECTIONS = {
    16193: ("Arte", "LC"),
    16794: ("Matemática", "MT"),
}

def safe_slug(s):
    return re.sub(r"[^\w-]", "-", s.lower().replace("ç","c").replace("ã","a")
                  .replace("á","a").replace("é","e").replace("í","i")
                  .replace("ó","o").replace("ú","u"))

for qid, (disc, area) in CORRECTIONS.items():
    matches = list((VAULT / "Questions").glob(f"*/*-{qid}.md"))
    if not matches:
        print(f"  ! id {qid} não encontrado")
        continue
    p = matches[0]
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"^area:.*$", f"area: {area}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina:.*$", f"disciplina: {disc}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_confianca:.*$", "disciplina_confianca: humano-revisado", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^disciplina_fonte:.*$", "disciplina_fonte: correcao-usuario-spotcheck-fase5", text, count=1, flags=re.MULTILINE)
    BODY = re.compile(r"\*\*Disciplina\*\*:\s*\*\*[^*]+\*\*\s*\(`confiança:\s*[^`]+`\)")
    text = BODY.sub(f"**Disciplina**: **{disc}** (`confiança: humano-revisado`)", text, count=1)
    text = re.sub(r"\*\*Área\*\*:\s*\[\[discipline-[a-z]+\|[A-Z]+\]\]",
                  f"**Área**: [[discipline-{area.lower()}|{area}]]", text, count=1)
    new_tag = safe_slug(disc)
    new_area = area.lower()
    def fix_tags(m):
        items = [t.strip() for t in m.group(1).split(",")]
        items = [t for t in items if t not in (
            "ch","cn","lc","mt","precisa-ocr","classificado-ia",
            "classificado-vision","classificado-vision-livre","indeterminada",
            "português","matemática","biologia","física","química","geografia",
            "historia","história","sociologia","filosofia","literatura","arte",
            "educacao-fisica","inglês","espanhol")]
        if new_area not in items: items.append(new_area)
        if new_tag not in items: items.append(new_tag)
        items.append("humano-revisado")
        return f"tags: [{', '.join(items)}]"
    text = re.sub(r"^tags:\s*\[(.*?)\]", fix_tags, text, count=1, flags=re.MULTILINE)
    p.write_text(text, encoding="utf-8")
    print(f"  ✓ id {qid} → {area}/{disc}")
print("✓ done")
