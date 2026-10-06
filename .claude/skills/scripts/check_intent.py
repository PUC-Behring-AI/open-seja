#!/usr/bin/env python3
# designer: Before /plan moves from the interview to the scenarios, I read
#   the intent.md it wrote and tell you, rule by rule, what is still missing:
#   a dimension nobody answered, a requirement without a sentence that says
#   how you will see it working, an open question, an assumption you did not
#   confirm, an ID out of place, or an approval that was never recorded. I
#   decide nothing by impression: the same file always gives the same answer.
"""
check_intent.py -- Grill stop rule (P1 to P6) for features/<slug>/intent.md.

Invocation: skill-invoked, user-cli, hook-ci
Lifecycle: active

Rules: .claude/references/general/grill-phase.md (GRL-006, GRL-010, GRL-015).
Schema: .claude/references/template/intent.md (superset of the minimal schema
in .claude/references/template/feature-layout.md).

| Rule | Condition |
|------|-----------|
| P1   | the six dimensions answered, or `fora do escopo: <reason>` |
| P2   | every active REQ has a criterion "Quando ..., o sistema ..." with no vague word lacking a number |
| P3   | no open question; every assumption `Confirmado: sim` |
| P4   | REQ-<slug>-NNN with the frontmatter slug, unique, contiguous, never reused; rev history in "Mudanças" |
| P5   | every active REQ has text and an origin (F<n>/A<n> index, quote, or `derivado de: REQ-...`) |
| P6   | `status: approved` with `approved_at` and `approved_by` |

Severity: `error` for P1 to P6 (and schema problems); `warning` for voice
(VOZ), size (TAMANHO), and `serve:` format (SERVE). Without
--require-approved, a file with only the minimal schema of feature-layout.md gets only
the minimal rules plus a warning that the stop rule was not evaluated.

No clock, no network, no LLM. Output is sorted and identical for the same text.

Exit codes: 0 = done (always, unless --strict); 1 = --strict and an error was
found, or scan mode found an error in an approved intent; 2 = usage error.

Usage
-----
    python .claude/skills/scripts/check_intent.py features/<slug>/intent.md
    python .claude/skills/scripts/check_intent.py <intent.md> --require-approved --strict
    python .claude/skills/scripts/check_intent.py <intent.md> --json
    python .claude/skills/scripts/check_intent.py <intent.md> --d0
    python .claude/skills/scripts/check_intent.py            # scan features/*/intent.md

CHECK_PLUGIN_MANIFEST:
  name: Intent Stop Rule
  stack:
    backend: [any]
    frontend: [any]
  scope: intent
  critical: false
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import NamedTuple

# ---------------------------------------------------------------------------
# Constants (grill-phase.md)
# ---------------------------------------------------------------------------

GRILL_MAX_ROUNDS = 5
GRILL_MAX_QUESTIONS_PER_ROUND = 4
GRILL_DIMENSIONS = ("quem", "o_que", "gatilho", "resultado", "nao_faz", "erros_limites")
GRILL_MAX_REQS = 12

DIMENSION_LABELS = {
    "quem": "quem",
    "o_que": "o que faz",
    "gatilho": "gatilho",
    "resultado": "resultado",
    "nao_faz": "não faz",
    "erros_limites": "erros e limites",
}

_DIMENSION_ALIASES = {
    "quem": "quem",
    "o que faz": "o_que",
    "o que": "o_que",
    "o_que": "o_que",
    "gatilho": "gatilho",
    "resultado": "resultado",
    "nao faz": "nao_faz",
    "nao_faz": "nao_faz",
    "erros e limites": "erros_limites",
    "erros_limites": "erros_limites",
}

VAGUE_WORDS = (
    "rapido", "rapidamente", "facil", "facilmente", "bom", "boa", "simples",
    "seguro", "segura", "adequado", "adequada", "intuitivo", "intuitiva",
    "amigavel", "eficiente", "robusto", "melhor", "etc",
    "fast", "quick", "easy", "good", "simple", "secure", "intuitive",
    "friendly", "efficient",
)

REQ_TYPES = ("comportamento", "restricao")
REQ_STATES = ("ativo", "retirado")
STATUSES = ("grilling", "approved")

try:  # plan 000074 (controlled language), when delivered in this harness
    import lint_controlled_language as _voice_lint  # type: ignore[import-not-found]

    MAX_SENTENCE_WORDS = int(getattr(_voice_lint, "MAX_SENTENCE_WORDS", 25))
    MAX_SENTENCES_PER_PARAGRAPH = int(getattr(_voice_lint, "MAX_SENTENCES_PER_PARAGRAPH", 6))
    VOICE_LINTER = True
except ImportError:
    MAX_SENTENCE_WORDS = 25
    MAX_SENTENCES_PER_PARAGRAPH = 6
    VOICE_LINTER = False

VOICE_CAVEAT = (
    "voz: não verificada -- eu só conferi o tamanho das frases e dos parágrafos; "
    "uma ideia por frase e os termos fixos não foram conferidos."
)

_REQ_ID = re.compile(r"^REQ-([a-z0-9]+(?:-[a-z0-9]+)*)-(\d{3})$")
_REQ_ANY = re.compile(r"REQ-[a-z0-9]+(?:-[a-z0-9]+)*-\d{3}")
_INDEX_ITEM = re.compile(r"^\s*-\s*([FA]\d+)\b")
_INDEX_REF = re.compile(r"\b([FA]\d+)\b")
_WHEN_FORM = re.compile(r"^\s*(quando\b.+,\s*o sistema\b|when\b.+,\s*the system\b).+", re.IGNORECASE)
_APPROVED_AT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?Z$")
_SERVE_ID = re.compile(r"^(REQ-[A-Z0-9]+-\d{3}|JM-TB-\d{3}|D-\d{3})$")
_QUOTED = re.compile(r'"[^"]*"|`[^`]*`')
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?;])\s+")
_EMPTY_LIST = ("", "nenhuma", "nenhum", "none")


class Finding(NamedTuple):
    regra: str
    linha: int
    mensagem: str
    severidade: str


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _norm(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(stripped.lower().split())


def _blank_comments(text: str) -> list[str]:
    """Replace HTML comments with blanks, keeping line numbers."""
    blanked = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.DOTALL)
    return blanked.splitlines()


class Row(NamedTuple):
    line: int
    cells: dict[str, str]


class Section(NamedTuple):
    line: int
    lines: list[tuple[int, str]]


class Doc(NamedTuple):
    frontmatter: dict[str, str]
    sections: dict[str, Section]


def _parse_frontmatter(lines: list[str]) -> tuple[dict[str, str], int]:
    if not lines or lines[0].strip() != "---":
        return {}, 0
    meta: dict[str, str] = {}
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return meta, idx + 1
        key, sep, value = lines[idx].partition(":")
        if sep and not lines[idx].startswith((" ", "\t")):
            meta[key.strip()] = value.strip().strip('"')
    return meta, 0


def parse(text: str) -> Doc:
    lines = _blank_comments(text)
    meta, start = _parse_frontmatter(lines)
    sections: dict[str, Section] = {}
    current: list[tuple[int, str]] | None = None
    for number, line in enumerate(lines[start:], start=start + 1):
        if line.startswith("## "):
            current = []
            sections[_norm(line[3:])] = Section(number, current)
        elif current is not None:
            current.append((number, line))
    return Doc(meta, sections)


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def table(section: Section | None) -> list[Row]:
    if section is None:
        return []
    rows = [(n, ln) for n, ln in section.lines if ln.strip().startswith("|")]
    if len(rows) < 2:
        return []
    header = [_norm(cell) for cell in _split_row(rows[0][1])]
    result = []
    for number, line in rows[2:]:
        cells = _split_row(line)
        result.append(Row(number, {h: (cells[i] if i < len(cells) else "") for i, h in enumerate(header)}))
    return result


def _list_items(section: Section | None) -> list[tuple[int, str]]:
    if section is None:
        return []
    return [(n, ln.strip()[1:].strip()) for n, ln in section.lines if ln.strip().startswith("- ")]


def _section_text(section: Section | None) -> str:
    return "" if section is None else "\n".join(ln for _, ln in section.lines)


def _cell(row: Row, *names: str) -> str:
    for name in names:
        if name in row.cells:
            return row.cells[name]
    return ""


def _index(doc: Doc) -> set[str]:
    return {m.group(1) for _, ln in _section_lines(doc, "nas suas palavras") if (m := _INDEX_ITEM.match(ln))}


def _section_lines(doc: Doc, name: str) -> list[tuple[int, str]]:
    section = doc.sections.get(name)
    return [] if section is None else section.lines


def _is_extended(doc: Doc, reqs: list[Row]) -> bool:
    grill_sections = ("dimensoes", "perguntas abertas", "mudancas", "modelo e termos")
    has_column = bool(reqs) and "nas suas palavras" in reqs[0].cells
    has_meta = "approved_at" in doc.frontmatter or "approved_by" in doc.frontmatter
    return any(s in doc.sections for s in grill_sections) or has_column or has_meta


def _is_active(row: Row) -> bool:
    return _norm(_cell(row, "estado")) != "retirado"


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------


def _err(rule: str, line: int, msg: str) -> Finding:
    return Finding(rule, line, msg, "error")


def _warn(rule: str, line: int, msg: str) -> Finding:
    return Finding(rule, line, msg, "warning")


def _check_frontmatter(doc: Doc) -> list[Finding]:
    meta = doc.frontmatter
    out = []
    if not meta.get("slug"):
        out.append(_err("ESQUEMA", 1, "Falta o campo slug no início do arquivo."))
    if meta.get("status") not in STATUSES:
        out.append(_err("ESQUEMA", 1, "O status precisa ser grilling ou approved."))
    if "requisitos" not in doc.sections:
        out.append(_err("ESQUEMA", 1, "Falta a seção Requisitos."))
    return out


def _check_ids(doc: Doc, reqs: list[Row], extended: bool) -> list[Finding]:
    slug = doc.frontmatter.get("slug", "")
    out: list[Finding] = []
    seen: dict[int, int] = {}
    for row in reqs:
        raw = _cell(row, "req").strip("`")
        match = _REQ_ID.match(raw)
        if not match:
            out.append(_err("P4", row.line, f"O ID {raw or '(vazio)'} não tem a forma REQ-<slug>-NNN."))
            continue
        if match.group(1) != slug:
            out.append(_err("P4", row.line, f"O ID {raw} usa o slug {match.group(1)}, e o arquivo usa {slug}."))
        number = int(match.group(2))
        if number in seen:
            out.append(_err("P4", row.line, f"O ID {raw} aparece duas vezes."))
        seen.setdefault(number, row.line)
        out.extend(_check_rev(row, raw, doc, extended))
    out.extend(_check_contiguous(seen))
    return out


def _check_contiguous(seen: dict[int, int]) -> list[Finding]:
    if not seen:
        return []
    missing = sorted(set(range(1, max(seen) + 1)) - set(seen))
    if not missing:
        return []
    gaps = ", ".join(f"{n:03d}" for n in missing)
    return [_err("P4", min(seen.values()), f"Faltam os números {gaps}. Um requisito retirado fica na tabela.")]


def _check_rev(row: Row, raw: str, doc: Doc, extended: bool) -> list[Finding]:
    rev_text = _cell(row, "rev")
    if "rev" not in row.cells:
        return []
    if not rev_text.isdigit() or int(rev_text) < 1:
        return [_err("P4", row.line, f"O rev de {raw} precisa ser um número a partir de 1.")]
    changed = int(rev_text) > 1 or not _is_active(row)
    if extended and changed and raw not in _section_text(doc.sections.get("mudancas")):
        return [_err("P4", row.line, f"{raw} mudou, mas não tem linha em Mudanças.")]
    return []


def _check_criterion(row: Row, raw: str, full: bool) -> list[Finding]:
    criterion = _cell(row, "criterio")
    if not criterion:
        return [_err("P2", row.line, f"{raw} não tem critério.")]
    if not full:
        return []
    out = []
    if not _WHEN_FORM.match(criterion):
        out.append(_err("P2", row.line, f"O critério de {raw} precisa ter a forma: Quando ..., o sistema ..."))
    if not re.search(r"\d", criterion):
        words = set(re.findall(r"\w+", _norm(criterion)))
        for vague in VAGUE_WORDS:
            if vague in words:
                shown = next((w for w in re.findall(r"\w+", criterion) if _norm(w) == vague), vague)
                out.append(_err("P2", row.line, f"O critério de {raw} usa a palavra {shown} sem um número."))
    return out


def _check_origin(row: Row, raw: str, index: set[str], ids: set[str]) -> list[Finding]:
    origin = _cell(row, "nas suas palavras")
    if not origin:
        return [_err("P5", row.line, f"{raw} não diz de onde veio, nas suas palavras.")]
    if _norm(origin).startswith("derivado de"):
        derived = _REQ_ANY.findall(origin)
        if derived and all(d in ids for d in derived):
            return []
        return [_err("P5", row.line, f"{raw} diz derivado de um requisito que não existe.")]
    refs = _INDEX_REF.findall(origin)
    missing = [r for r in refs if r not in index]
    if missing:
        return [_err("P5", row.line, f"{raw} cita {', '.join(missing)}, que não está em Nas suas palavras.")]
    if refs or '"' in origin:
        return []
    return [_err("P5", row.line, f"{raw} não cita uma frase sua nem diz derivado de.")]


def _check_type(row: Row, raw: str) -> list[Finding]:
    if "tipo" not in row.cells or _norm(_cell(row, "tipo")) in REQ_TYPES:
        return []
    return [_err("ESQUEMA", row.line, f"O tipo de {raw} precisa ser comportamento ou restrição.")]


def _check_state(row: Row, raw: str) -> list[Finding]:
    if "estado" not in row.cells or _norm(_cell(row, "estado")) in REQ_STATES:
        return []
    return [_err("ESQUEMA", row.line, f"O estado de {raw} precisa ser ativo ou retirado.")]


def _check_reqs(doc: Doc, reqs: list[Row], extended: bool, require: bool) -> list[Finding]:
    full = extended or require
    index = _index(doc)
    ids = {_cell(r, "req").strip("`") for r in reqs}
    has_origin_column = bool(reqs) and "nas suas palavras" in reqs[0].cells
    out: list[Finding] = []
    if require and reqs and not has_origin_column:
        out.append(_err("P5", reqs[0].line - 2, "A tabela de requisitos não tem a coluna Nas suas palavras."))
    if require and not reqs:
        out.append(_err("P2", doc.sections["requisitos"].line if "requisitos" in doc.sections else 1,
                        "Não há nenhum requisito."))
    for row in reqs:
        raw = _cell(row, "req").strip("`")
        out.extend(_check_type(row, raw))
        out.extend(_check_state(row, raw))
        if not _is_active(row):
            continue
        if not _cell(row, "requisito", "texto"):
            out.append(_err("P5", row.line, f"{raw} não tem texto."))
        out.extend(_check_criterion(row, raw, full))
        if has_origin_column:
            out.extend(_check_origin(row, raw, index, ids))
    return out


def _dimension_rows(doc: Doc) -> dict[str, Row]:
    found: dict[str, Row] = {}
    for row in table(doc.sections.get("dimensoes")):
        key = _DIMENSION_ALIASES.get(_norm(_cell(row, "dimensao")))
        if key:
            found.setdefault(key, row)
    return found


def _check_dimensions(doc: Doc, require: bool) -> list[Finding]:
    section = doc.sections.get("dimensoes")
    if section is None:
        return [_err("P1", 1, "Falta a seção Dimensões.")] if require else []
    found = _dimension_rows(doc)
    out = []
    for key in GRILL_DIMENSIONS:
        label = DIMENSION_LABELS[key]
        row = found.get(key)
        if row is None:
            out.append(_err("P1", section.line, f"Falta a dimensão {label}."))
            continue
        answer = _cell(row, "resposta")
        if not answer:
            out.append(_err("P1", row.line, f"A dimensão {label} não tem resposta."))
        elif _norm(answer).startswith("fora do escopo") and not answer.partition(":")[2].strip():
            out.append(_err("P1", row.line, f"A dimensão {label} está fora do escopo sem motivo."))
    return out


def _check_open_questions(doc: Doc, require: bool) -> list[Finding]:
    section = doc.sections.get("perguntas abertas")
    if section is None:
        return [_err("P3", 1, "Falta a seção Perguntas abertas.")] if require else []
    return [
        _err("P3", n, f"Há uma pergunta aberta: {item}")
        for n, item in _list_items(section)
        if _norm(item) not in _EMPTY_LIST
    ]


def _check_assumptions(doc: Doc, require: bool) -> list[Finding]:
    section = doc.sections.get("premissas")
    if section is None:
        return [_err("P3", 1, "Falta a seção Premissas.")] if require else []
    rows = table(section)
    out = [
        _err("P3", row.line, "Esta premissa ainda não foi confirmada.")
        for row in rows
        if _norm(_cell(row, "confirmado")) != "sim"
    ]
    for n, item in _list_items(section):
        if _norm(item) not in _EMPTY_LIST:
            out.append(_err("P3", n, "Esta premissa não tem a coluna Confirmado."))
    return out


def _check_approval(doc: Doc, require: bool) -> list[Finding]:
    meta = doc.frontmatter
    out = []
    if require and meta.get("status") != "approved":
        out.append(_err("P6", 1, "Você ainda não aprovou esta intenção."))
    if meta.get("status") == "approved":
        if not _APPROVED_AT.match(meta.get("approved_at", "")):
            out.append(_err("P6", 1, "Falta approved_at com data e hora UTC."))
        if not meta.get("approved_by"):
            out.append(_err("P6", 1, "Falta approved_by: quem aprovou."))
    return out


def _check_serve(doc: Doc) -> list[Finding]:
    raw = doc.frontmatter.get("serve", "").strip()
    if not raw:
        return []
    items = [i.strip() for i in raw.strip("[]").split(",") if i.strip()]
    bad = [i for i in items if not _SERVE_ID.match(i)]
    if not bad:
        return []
    return [_warn("SERVE", 1, f"serve tem IDs fora da forma REQ-XX-NNN, JM-TB-NNN ou D-NNN: {', '.join(bad)}.")]


def _check_size(reqs: list[Row]) -> list[Finding]:
    active = [r for r in reqs if _is_active(r)]
    if len(active) <= GRILL_MAX_REQS:
        return []
    return [_warn("TAMANHO", active[0].line,
                  f"Há {len(active)} requisitos. Pense em dividir em duas features.")]


# ---------------------------------------------------------------------------
# Voice (GRL-010)
# ---------------------------------------------------------------------------


def _voice(line: int, text: str) -> list[Finding]:
    plain = _QUOTED.sub("", text).strip()
    if not plain:
        return []
    sentences = [s for s in _SENTENCE_SPLIT.split(plain) if re.search(r"\w", s)]
    out = []
    for sentence in sentences:
        words = [w for w in sentence.split() if re.search(r"\w", w)]
        if len(words) > MAX_SENTENCE_WORDS:
            out.append(_warn("VOZ", line, f"Uma frase tem {len(words)} palavras. O limite é {MAX_SENTENCE_WORDS}."))
    if len(sentences) > MAX_SENTENCES_PER_PARAGRAPH:
        out.append(_warn("VOZ", line,
                         f"Um trecho tem {len(sentences)} frases. O limite é {MAX_SENTENCES_PER_PARAGRAPH}."))
    return out


def _agent_texts(doc: Doc, reqs: list[Row]) -> list[tuple[int, str]]:
    texts: list[tuple[int, str]] = []
    for row in reqs:
        texts.extend((row.line, _cell(row, name)) for name in ("requisito", "texto", "criterio", "para que"))
    texts.extend((row.line, _cell(row, "resposta")) for row in table(doc.sections.get("dimensoes")))
    texts.extend((row.line, _cell(row, "o que quer dizer")) for row in table(doc.sections.get("modelo e termos")))
    texts.extend((row.line, _cell(row, "premissa")) for row in table(doc.sections.get("premissas")))
    texts.extend(_list_items(doc.sections.get("fora do escopo")))
    return texts


def _check_voice(doc: Doc, reqs: list[Row]) -> list[Finding]:
    out: list[Finding] = []
    for line, text in _agent_texts(doc, reqs):
        out.extend(_voice(line, text))
    return out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def check_intent(text: str, *, require_approved: bool = False) -> list[Finding]:
    """Return the findings of the stop rule P1 to P6 for one intent.md text."""
    doc = parse(text)
    reqs = table(doc.sections.get("requisitos"))
    extended = _is_extended(doc, reqs)
    findings = _check_frontmatter(doc)
    findings += _check_ids(doc, reqs, extended)
    findings += _check_reqs(doc, reqs, extended, require_approved)
    if extended or require_approved:
        findings += _check_dimensions(doc, require_approved)
        findings += _check_open_questions(doc, require_approved)
        findings += _check_assumptions(doc, require_approved)
        findings += _check_approval(doc, require_approved)
    else:
        findings.append(_warn("ESQUEMA", 1, "Este arquivo usa só o esquema mínimo. Eu não avaliei a regra de parada."))
    if require_approved and "modelo e termos" not in doc.sections:
        findings.append(_warn("ESQUEMA", 1, "Falta a seção Modelo e termos."))
    findings += _check_serve(doc) + _check_size(reqs) + _check_voice(doc, reqs)
    return sorted(set(findings), key=lambda f: (f.linha, f.regra, f.severidade, f.mensagem))


def ressalvas() -> list[str]:
    """Caveats that always travel with the result."""
    return [] if VOICE_LINTER else [VOICE_CAVEAT]


def brief_residue(text: str) -> dict:
    """D0 reading (DRM-010): brief sentences F<n> with no active REQ and no out-of-scope item."""
    doc = parse(text)
    sentences = sorted((r for r in _index(doc) if r.startswith("F")), key=lambda r: int(r[1:]))
    if not sentences:
        return {"estado": "nao_medido", "razao_nm": ["NM-SEM-INDICE-BRIEF"]}
    reqs = table(doc.sections.get("requisitos"))
    cited = {ref for row in reqs if _is_active(row) for ref in _INDEX_REF.findall(_cell(row, "nas suas palavras"))}
    cited |= set(_INDEX_REF.findall(_section_text(doc.sections.get("fora do escopo"))))
    in_assumption = set(_INDEX_REF.findall(_section_text(doc.sections.get("premissas"))))
    residue = [
        {"frase": s, "nota": "só em premissa" if s in in_assumption else ""}
        for s in sentences
        if s not in cited
    ]
    return {"estado": "medido", "frases": len(sentences), "residuo": residue}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_text(path: str, findings: list[Finding]) -> None:
    for f in findings:
        print(f"{path}:{f.linha}: {f.severidade} {f.regra}: {f.mensagem}")
    errors = sum(1 for f in findings if f.severidade == "error")
    print(f"{path}: {errors} error(s), {len(findings) - errors} warning(s)")
    for caveat in ressalvas():
        print(f"{path}: ressalva: {caveat}")


def _as_json(path: str, findings: list[Finding]) -> dict:
    return {
        "schema_version": 1,
        "path": path,
        "findings": [f._asdict() for f in findings],
        "ressalvas": ressalvas(),
    }


def _scan(root: Path, as_json: bool) -> int:
    paths = sorted((root / "features").glob("*/intent.md"))
    if not paths:
        print("check_intent: nenhum features/*/intent.md; nada a verificar.")
        return 0
    failed = False
    reports = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        approved = parse(text).frontmatter.get("status") == "approved"
        findings = check_intent(text, require_approved=approved)
        failed |= approved and any(f.severidade == "error" for f in findings)
        rel = str(path.relative_to(root))
        if as_json:
            reports.append(_as_json(rel, findings))
        else:
            _print_text(rel, findings)
    if as_json:
        print(json.dumps({"schema_version": 1, "reports": reports}, ensure_ascii=False, indent=2))
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Grill stop rule (P1 to P6) for intent.md.")
    parser.add_argument("path", nargs="?", help="intent.md to check; omit to scan features/*/intent.md")
    parser.add_argument("--require-approved", action="store_true", help="apply P1 to P6 in full")
    parser.add_argument("--strict", action="store_true", help="exit 1 when an error is found")
    parser.add_argument("--json", action="store_true", help="JSON output with schema_version")
    parser.add_argument("--d0", action="store_true", help="print the D0 reading (brief residue) as JSON")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="project root for scan mode")
    args = parser.parse_args(argv)

    if args.path is None:
        return _scan(args.root, args.json)
    path = Path(args.path)
    if not path.is_file():
        print(f"check_intent: arquivo não encontrado: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    if args.d0:
        print(json.dumps({"schema_version": 1, "path": str(path), "d0": brief_residue(text)},
                         ensure_ascii=False, indent=2))
        return 0
    findings = check_intent(text, require_approved=args.require_approved)
    if args.json:
        print(json.dumps(_as_json(str(path), findings), ensure_ascii=False, indent=2))
    else:
        _print_text(str(path), findings)
    has_error = any(f.severidade == "error" for f in findings)
    return 1 if args.strict and has_error else 0


if __name__ == "__main__":
    sys.exit(main())
