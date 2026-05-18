#!/usr/bin/env python3
"""
Fase 7 step 1: regenera _index.md a partir do estado real do vault.

Lê o frontmatter de cada nota em Questions/*/*.md e compõe um _index.md
honesto, refletindo o estado pós-Fase 6 (text-perfect).

Princípio (alinhado com AGENTS.md da XTRI):
- Nunca inventar dados.
- Distribuições sempre derivadas dos arquivos reais.
- Idempotente: re-rodar = mesmo resultado (até que os .md mudem).

Uso:
    cd <vault root>
    python3 _phase7_index_refresh.py
    # ou para output em arquivo diferente:
    python3 _phase7_index_refresh.py --out _index_preview.md

Saída padrão: sobrescreve _index.md.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

VAULT = Path(__file__).resolve().parent
QUESTIONS_DIR = VAULT / "Questions"
DEFAULT_OUT = VAULT / "_index.md"

AREA_FULL = {
    "LC": "Linguagens, Códigos e suas Tecnologias",
    "CH": "Ciências Humanas e suas Tecnologias",
    "CN": "Ciências da Natureza e suas Tecnologias",
    "MT": "Matemática e suas Tecnologias",
}

# Ordem canônica de disciplinas para exibição (alinhada com _taxonomia.md)
DISC_ORDER = [
    "Matemática",
    "Português",
    "História",
    "Biologia",
    "Geografia",
    "Química",
    "Física",
    "Literatura",
    "Sociologia",
    "Filosofia",
    "Arte",
    "Espanhol",
    "Inglês",
    "Educação Física",
    "indeterminada",
]

# ---------------------------------------------------------------------------
# Parser de frontmatter
# ---------------------------------------------------------------------------

# IMPORTANTE: usar [ \t]* (não \s*) após o ":" para não engolir \n e
# pular campos imediatamente depois de campos com valor vazio.
FRONTMATTER_RE = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*\n", re.DOTALL)
FIELD_RE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*):[ \t]*(.*)$", re.MULTILINE)


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Retorna um dict com os campos do frontmatter. Strings já trim-adas."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[warn] não consegui ler {path}: {e}", file=sys.stderr)
        return {}
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fields: dict[str, str] = {}
    for field_match in FIELD_RE.finditer(m.group(1)):
        key, value = field_match.group(1), field_match.group(2).strip()
        fields[key] = value
    return fields


def collect_questions() -> list[dict[str, str]]:
    """Carrega todas as questões com frontmatter parseado."""
    if not QUESTIONS_DIR.is_dir():
        print(f"[erro] diretório não existe: {QUESTIONS_DIR}", file=sys.stderr)
        sys.exit(1)
    out: list[dict[str, str]] = []
    for md in sorted(QUESTIONS_DIR.glob("*/*.md")):
        fm = parse_frontmatter(md)
        if fm.get("type") == "Question":
            out.append(fm)
    return out


# ---------------------------------------------------------------------------
# Estatísticas
# ---------------------------------------------------------------------------

def compute_stats(qs: list[dict[str, str]]) -> dict:
    total = len(qs)
    disc = Counter(q.get("disciplina", "indeterminada") for q in qs)
    area = Counter(q.get("area", "") for q in qs)
    conf = Counter(q.get("disciplina_confianca", "") for q in qs)

    by_year: dict[str, Counter] = defaultdict(Counter)
    for q in qs:
        y = q.get("year", "")
        a = q.get("area", "")
        by_year[y][a] += 1
        by_year[y]["TOTAL"] += 1

    num_re = re.compile(r"^-?\d+(\.\d+)?$")
    with_skill = sum(1 for q in qs if re.match(r"^H\d+$", q.get("skill", "")))
    with_b = sum(1 for q in qs if num_re.match(q.get("param_b", "")))
    with_a = sum(1 for q in qs if num_re.match(q.get("param_a", "")))
    with_c = sum(1 for q in qs if num_re.match(q.get("param_c", "")))
    with_gabarito = sum(1 for q in qs if q.get("correctAlternative", "") in "ABCDE")

    return {
        "total": total,
        "disc": disc,
        "area": area,
        "conf": conf,
        "by_year": dict(sorted(by_year.items())),
        "with_skill": with_skill,
        "with_b": with_b,
        "with_a": with_a,
        "with_c": with_c,
        "with_gabarito": with_gabarito,
    }


# ---------------------------------------------------------------------------
# Renderização do _index.md
# ---------------------------------------------------------------------------

def fmt_int(n: int) -> str:
    """Format como '3.123' (pt-BR)."""
    return f"{n:,}".replace(",", ".")


def pct(num: int, denom: int) -> str:
    if denom == 0:
        return "0,0%"
    return f"{(num / denom * 100):.1f}%".replace(".", ",")


def render_index(s: dict) -> str:
    lines: list[str] = []
    today = date.today().isoformat()

    lines.append("---")
    lines.append("type: Note")
    lines.append(f"generated_at: {today}")
    lines.append("generator: _phase7_index_refresh.py")
    lines.append("canonical_source: phase6-text-claude")
    lines.append("---")
    lines.append("# Questões ENEM — Memória completa")
    lines.append("")
    lines.append(
        f"Vault com **{fmt_int(s['total'])} questões** de **{len(s['by_year'])} edições** "
        f"do ENEM, sincronizadas com [`api.questoes.xtri.online`]"
        f"(https://api.questoes.xtri.online/api/docs/)."
    )
    lines.append("")
    lines.append("> **Fonte canônica**: classificação Fase 6 (Claude lendo "
                 "`context + alternativesIntroduction + alternatives` do detail endpoint). "
                 "Esta é a versão definitiva — sobrescreve Fases 1–5.")
    lines.append("")

    # Estrutura
    lines.append("## Estrutura")
    lines.append("")
    lines.append("- [[Exams/_index|Exams]] — edições")
    lines.append("- [[Disciplines/_index|Disciplines]] — 4 áreas")
    lines.append("- [[Skills/_index|Skills]] — 120 habilidades INEP")
    lines.append(f"- `Questions/` — {fmt_int(s['total'])} notas")
    lines.append("- [[_taxonomia]] — taxonomia de disciplinas")
    lines.append("- [[_api-spec]] — contrato da API XTRI")
    lines.append("")

    # Confiança
    lines.append("## Status da classificação (real)")
    lines.append("")
    lines.append("| Confiança | Qtd | % |")
    lines.append("|---|---:|---:|")
    emoji = {
        "text-high": "🟢",
        "text-medium": "🟡",
        "text-low": "🟠",
        "text-impossivel": "🔴",
        "alta": "⚪",
        "media": "⚪",
    }
    for k, v in s["conf"].most_common():
        e = emoji.get(k, "⚪")
        lines.append(f"| {e} `{k or '(vazio)'}` | {fmt_int(v)} | {pct(v, s['total'])} |")
    lines.append(f"| **Total** | **{fmt_int(s['total'])}** | **100,0%** |")
    lines.append("")

    # Distribuição por disciplina
    lines.append("## Distribuição por disciplina")
    lines.append("")
    lines.append("| Disciplina | Questões | % |")
    lines.append("|---|---:|---:|")
    seen = set()
    for d in DISC_ORDER:
        if d in s["disc"]:
            lines.append(f"| {d} | {fmt_int(s['disc'][d])} | {pct(s['disc'][d], s['total'])} |")
            seen.add(d)
    for d, v in s["disc"].items():
        if d not in seen:
            lines.append(f"| {d} | {fmt_int(v)} | {pct(v, s['total'])} |")
    lines.append(f"| **Total** | **{fmt_int(s['total'])}** | **100,0%** |")
    lines.append("")

    # Distribuição por área
    lines.append("## Distribuição por área")
    lines.append("")
    lines.append("| Área | Questões | % |")
    lines.append("|---|---:|---:|")
    for a, v in s["area"].most_common():
        full = AREA_FULL.get(a, a)
        lines.append(f"| {a} — {full} | {fmt_int(v)} | {pct(v, s['total'])} |")
    lines.append("")

    # Cobertura por ano
    lines.append("## Cobertura por ano")
    lines.append("")
    lines.append("| Ano | Questões | LC | CH | CN | MT |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    tot_lc = tot_ch = tot_cn = tot_mt = 0
    for y, counters in s["by_year"].items():
        t = counters.get("TOTAL", 0)
        lc, ch, cn, mt = counters.get("LC", 0), counters.get("CH", 0), counters.get("CN", 0), counters.get("MT", 0)
        tot_lc += lc; tot_ch += ch; tot_cn += cn; tot_mt += mt
        lines.append(f"| [[enem-{y}|{y}]] | {t} | {lc} | {ch} | {cn} | {mt} |")
    lines.append(f"| **Total** | **{fmt_int(s['total'])}** | **{tot_lc}** | **{tot_ch}** | **{tot_cn}** | **{tot_mt}** |")
    lines.append("")

    # Cobertura de campos
    lines.append("## Cobertura de campos críticos")
    lines.append("")
    lines.append("| Campo | Preenchidos | % |")
    lines.append("|---|---:|---:|")
    lines.append(f"| `correctAlternative` (gabarito) | {fmt_int(s['with_gabarito'])} | {pct(s['with_gabarito'], s['total'])} |")
    lines.append(f"| `skill` (habilidade INEP) | {fmt_int(s['with_skill'])} | {pct(s['with_skill'], s['total'])} |")
    lines.append(f"| `param_b` (dificuldade TRI) | {fmt_int(s['with_b'])} | {pct(s['with_b'], s['total'])} |")
    lines.append(f"| `param_a` (discriminação TRI) | {fmt_int(s['with_a'])} | {pct(s['with_a'], s['total'])} |")
    lines.append(f"| `param_c` (acerto ao acaso) | {fmt_int(s['with_c'])} | {pct(s['with_c'], s['total'])} |")
    lines.append("")

    lines.append("## Sincronização")
    lines.append("")
    lines.append(f"Índice regenerado em **{today}** por `_phase7_index_refresh.py`.")
    lines.append("Para re-rodar: `python3 _phase7_index_refresh.py` na raiz do vault.")
    lines.append("Para preview sem sobrescrever: `python3 _phase7_index_refresh.py --out _index_preview.md`.")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Regenera _index.md a partir dos frontmatters reais.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Caminho de saída (default: _index.md)")
    parser.add_argument("--dry-run", action="store_true", help="Só imprime, não grava.")
    args = parser.parse_args()

    qs = collect_questions()
    if not qs:
        print("[erro] nenhuma questão encontrada em Questions/*/*.md", file=sys.stderr)
        return 1

    print(f"[info] {len(qs)} questões coletadas")
    stats = compute_stats(qs)
    content = render_index(stats)

    if args.dry_run:
        sys.stdout.write(content)
        return 0

    args.out.write_text(content, encoding="utf-8")
    print(f"[ok] escrito: {args.out}")
    print(f"[stats] disciplinas: {len(stats['disc'])} | áreas: {len(stats['area'])} | anos: {len(stats['by_year'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
