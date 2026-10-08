#!/usr/bin/env python3
# designer: After you approve the list of requirements, /plan writes the
#   scenarios and, in first person, what it understood. Before anyone sees
#   them, I check both: every requirement has a scenario and a story you can
#   recognize, every limit has a number, nothing technical reaches you, and
#   nothing changed since you last approved. Only when I find nothing do I
#   record your approval; if anything changed later, I say it is out of date.
"""
check_specify.py -- Specify phase checker and approval recorder (SPC-001 to SPC-018).

Invocation: skill-invoked, user-cli, hook-ci
Lifecycle: active

Rules: .claude/references/general/specify-phase.md (SPC-NNN; D-004, CYC-013, CYC-014).
Reads intent.md with the parser of check_intent.py and the .feature files with
check_features.py (both imported; one parser per format).

| Rule    | What I check                                                        | Severity        |
|---------|---------------------------------------------------------------------|-----------------|
| SPC-001 | intent.md exists, `status: approved`, no error in check_intent      | error           |
| SPC-003 | every active REQ has a scenario; no retired REQ has one             | error           |
| SPC-004 | a `restrição` REQ has a number in a Then step or in Examples        | error           |
| SPC-007 | no step longer than MAX_SENTENCE_WORDS (quoted values excluded)     | warning         |
| SPC-008 | check_features errors and warnings for the feature (strict)         | error / warning |
| SPC-011 | Retradução rev > 1 has a line in Mudanças; rev past the cap         | error / info    |
| SPC-012 | an approved scenario name is still there, or Mudanças cites it      | error           |
| SPC-013 | status: missing, draft, approved, stale (against scenarios.lock.json)| --              |
| SPC-017 | Retradução: rev, one item per active REQ with an example, "não faz" | error / warning |
| SPC-018 | Retradução: no technical token, sentence and paragraph size         | warning         |

`--approve` (SPC-010) writes scenarios.lock.json and then the five `scenarios_*`
fields of the intent.md frontmatter. Each file is written atomically (temp file,
then replace, keeping the original mode); the pair is not. A failure between the two
writes leaves a lock without the frontmatter field, which reads as `stale` (reason
`sem-campo`) and is fixed by running --approve again. Writes only when no error and no
warning is found. `--at` comes from the caller: no clock, no network, no LLM.
Output is sorted and identical for the same files.

Exit codes:
  0 = no error and no warning (infos do not fail); --status always 0;
      scan mode (no --feature) fails only on a `scenarios: approved` feature that is stale.
  1 = at least one error or warning (nothing is written by --approve); scan: a stale approval.
      --reconcile never exits 1.
  2 = usage error, unreadable file, missing folder, unknown lock schema_version,
      or the scenario validator (check_features.py) not found. Never a traceback.

Usage
-----
    python .claude/skills/scripts/check_specify.py                      # scan features/*/
    python .claude/skills/scripts/check_specify.py <root> --feature <slug>
    python .claude/skills/scripts/check_specify.py <root> --feature <slug> --status --json
    python .claude/skills/scripts/check_specify.py <root> --feature <slug> --approve \\
        --at 2026-10-06T15:00Z --by usuario --contract-by usuario
    python .claude/skills/scripts/check_specify.py <root> --reconcile [<slug>] [--json]

`--reconcile` (CYC-032, emenda 000015): when the approval is old (`--status` is
`stale`, including an intent.md back in `grilling`), turn `scenarios: approved` into
`scenarios: draft` in that intent.md only; every other byte, the other `scenarios_*`
fields and the lock stay. Atomic, idempotent, confined to features/<slug>/. Without a
slug it sweeps every features/*/intent.md. Exit 0 when nothing to do or reconciled.

CHECK_PLUGIN_MANIFEST:
  name: Specify Approval
  stack:
    backend: [any]
    frontend: [any]
  scope: features
  critical: false
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

from check_intent import (
    MAX_SENTENCE_WORDS,
    MAX_SENTENCES_PER_PARAGRAPH,
    _norm,
    ressalvas,
)
from check_intent import check_intent as run_check_intent
from check_intent import parse as parse_intent
from check_intent import table as intent_table

try:  # scenario validator (check_features.py); SPC-014: without it the phase does not approve
    import check_features as _cf
except ImportError:  # pragma: no cover - exercised by monkeypatching _cf
    _cf = None

# ---------------------------------------------------------------------------
# Constants (specify-phase.md)
# ---------------------------------------------------------------------------

SCHEMA_VERSION = 1
LOCK_SCHEMA_VERSION = 1
SPECIFY_MAX_ROUNDS = 3
LOCK_NAME = "scenarios.lock.json"
CONTRACT_NOBODY = "ninguem"
REASON_ORDER = ("intencao-reaberta", "sem-lock", "sem-campo", "req-novo", "req-retirado", "req-rev",
                "feature", "retraducao")

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
AT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?Z$")
NAME_RE = re.compile(r"^[\w.@-]+$")
REQ_ID_RE = re.compile(r"^REQ-([a-z0-9]+(?:-[a-z0-9]+)*)-(\d{3})$")
REQ_ANY = re.compile(r"REQ-[a-z0-9]+(?:-[a-z0-9]+)*-\d{3}")
REV_LINE = re.compile(r"^\s*rev:\s*(\S*)\s*$")
TECH_TOKENS = re.compile(r"\bPASS\b|\bFAIL\b|%|\b(?:GHK|SPC|CYC|DRM|GRL)-\d|@REQ|\.feature\b")
CITATION = re.compile(r"\(\s*(?:REQ-[a-z0-9-]+-\d{3}|[FA]\d+)(?:\s*,\s*(?:REQ-[a-z0-9-]+-\d{3}|[FA]\d+))*\s*\)")
QUOTED = re.compile(r'"[^"]*"|`[^`]*`')
SENTENCE_SPLIT = re.compile(r"(?<=[.!?;])\s+")
NAO_FAZ_HEADERS = ("o que eu nao vou fazer", "what i will not do")
EXAMPLE_PREFIXES = ("exemplo:", "example:")
FIRST_PERSON = ("eu", "i")
EMPTY_ITEMS = ("", "nenhuma", "nenhum", "none")


class Finding(NamedTuple):
    rule: str
    severity: str
    file: str
    line: int
    message: str
    hint: str


class Status(NamedTuple):
    status: str
    reasons: list[str]
    reqs: list[str]


class Report(NamedTuple):
    slug: str
    findings: list[Finding]
    status: Status


class UsageError(Exception):
    """Exit 2: wrong usage, unreadable file, unknown schema, missing validator."""


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        raise UsageError(f"não consegui ler {path.as_posix()}: {exc.__class__.__name__}") from None


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalized(path: Path) -> bytes:
    """File bytes with the BOM dropped and CRLF turned into LF (same rule as the Retradução hash)."""
    return _read(path).replace("\r\n", "\n").encode("utf-8")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


class Req(NamedTuple):
    id: str
    line: int
    active: bool
    rev: int
    kind: str


def requirements(doc, slug: str) -> list[Req]:
    out = []
    for row in intent_table(doc.sections.get("requisitos")):
        raw = row.cells.get("req", "").strip().strip("`")
        match = REQ_ID_RE.match(raw)
        if not match or match.group(1) != slug:
            continue
        rev = row.cells.get("rev", "").strip()
        out.append(Req(raw, row.line, _norm(row.cells.get("estado", "")) != "retirado",
                       int(rev) if rev.isdigit() else 1, _norm(row.cells.get("tipo", ""))))
    return out


def retraducao_text(doc) -> str | None:
    section = doc.sections.get("retraducao")
    if section is None:
        return None
    lines = [ln.rstrip() for _, ln in section.lines]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def _retraducao_rev(doc) -> tuple[int, int | None]:
    """(line, rev) of the `rev:` line of the Retradução section; rev None when malformed."""
    section = doc.sections.get("retraducao")
    for number, line in [] if section is None else section.lines:
        match = REV_LINE.match(line)
        if match:
            value = match.group(1)
            return number, int(value) if value.isdigit() and int(value) >= 1 else None
    return (section.line if section is not None else 1), None


def _feature_files(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.feature"))


# ---------------------------------------------------------------------------
# SPC-013: status against the lock
# ---------------------------------------------------------------------------


def _load_lock(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(_read(path))
    except json.JSONDecodeError:
        raise UsageError(f"{path.as_posix()} não é JSON válido") from None
    if not isinstance(data, dict) or data.get("schema_version") != LOCK_SCHEMA_VERSION:
        raise UsageError(f"{path.as_posix()}: schema_version desconhecido ({data.get('schema_version') if isinstance(data, dict) else '?'})")
    return data


def _current(folder: Path, doc, slug: str) -> dict:
    """The parts of the lock that can be recomputed from the files on disk."""
    reqs = requirements(doc, slug) if doc is not None else []
    text = retraducao_text(doc) if doc is not None else None
    return {
        "basis": {r.id: r.rev for r in reqs if r.active},
        "files": {p.name: _sha(_normalized(p)) for p in _feature_files(folder)},
        "retraducao": _sha((text or "").encode("utf-8")),
    }


def compute_status(root: Path, slug: str) -> Status:
    """SPC-013: missing, draft, approved or stale, with reasons and affected REQs."""
    folder = root / "features" / slug
    if not _feature_files(folder):
        return Status("missing", [], [])
    intent_path = folder / "intent.md"
    doc = parse_intent(_read(intent_path)) if intent_path.is_file() else None
    meta = doc.frontmatter if doc is not None else {}
    marked = meta.get("scenarios") == "approved"
    lock = _load_lock(folder / LOCK_NAME)
    if lock is None:
        return Status("stale", ["sem-lock"], []) if marked else Status("draft", [], [])
    now = _current(folder, doc, slug)
    reasons: set[str] = set()
    reqs: set[str] = set()
    if meta.get("status") != "approved":
        reasons.add("intencao-reaberta")
    if not marked:
        reasons.add("sem-campo")
    old = {k: int(v) for k, v in lock.get("basis", {}).items()}
    for req in sorted(set(old) | set(now["basis"])):
        if req not in old:
            reasons.add("req-novo")
        elif req not in now["basis"]:
            reasons.add("req-retirado")
        elif old[req] != now["basis"][req]:
            reasons.add("req-rev")
        else:
            continue
        reqs.add(req)
    if lock.get("files") != now["files"]:
        reasons.add("feature")
    if lock.get("retraducao") != now["retraducao"]:
        reasons.add("retraducao")
    ordered = [r for r in REASON_ORDER if r in reasons]
    return Status("stale" if ordered else "approved", ordered, sorted(reqs))


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------


def _f(rule: str, severity: str, file: str, line: int, message: str, hint: str = "") -> Finding:
    return Finding(rule, severity, file, line, message, hint)


def _words(text: str) -> int:
    return sum(1 for w in QUOTED.sub("", text).split() if re.search(r"\w", w))


def _check_entry(intent_rel: str, text: str | None) -> list[Finding]:
    """SPC-001."""
    hint = "Rode /plan --grill para terminar a entrevista."
    if text is None:
        return [_f("SPC-001", "error", intent_rel, 1, "Não encontrei intent.md. A entrevista vem antes.", hint)]
    doc = parse_intent(text)
    if doc.frontmatter.get("status") != "approved":
        return [_f("SPC-001", "error", intent_rel, 1, "A lista de requisitos ainda não foi aprovada.", hint)]
    return [
        _f("SPC-001", "error", intent_rel, max(f.linha, 1), f"intent.md tem um problema ({f.regra}): {f.mensagem}", hint)
        for f in run_check_intent(text, require_approved=True)
        if f.severidade == "error"
    ]


def _check_ghk(fds) -> list[Finding]:
    """SPC-008: errors and warnings of check_features, strict. GHK-005 is left to SPC-003 (same fact)."""
    words = {"error": "erro", "warning": "aviso"}
    return [
        _f("SPC-008", f.severity, f.file, f.line, f"{f.rule} ({words[f.severity]}): {f.message}",
           f.hint or "Corrija o cenário antes de mostrar a alguém.")
        for f in _cf.validate(fds)
        if f.severity in words and f.rule != "GHK-005"
    ]


def _scenarios(fd, slug: str):
    for ff in fd.files:
        if ff.feature is None:
            continue
        for scenario in ff.feature.scenarios:
            yield ff, scenario, _cf.cited_reqs(slug, scenario)


def _check_coverage(fd, slug: str, reqs: list[Req], intent_rel: str) -> list[Finding]:
    """SPC-003 and SPC-004."""
    out: list[Finding] = []
    by_req: dict[str, list] = {}
    for ff, scenario, cited in _scenarios(fd, slug):
        for req in cited:
            by_req.setdefault(req, []).append((ff, scenario))
    for req in reqs:
        found = by_req.get(req.id, [])
        if req.active and not found:
            out.append(_f("SPC-003", "error", intent_rel, req.line, f"O requisito {req.id} não tem cenário.",
                          f"Escreva um cenário com a tag @{req.id}."))
        if not req.active:
            out.extend(_f("SPC-003", "error", ff.path, scenario.line,
                          f"O cenário {scenario.name} cita {req.id}, que foi retirado.",
                          "Tire o cenário e registre a saída em Mudanças.")
                       for ff, scenario in found)
        if req.active and req.kind == "restricao" and found and not any(_has_number(s) for _, s in found):
            ff, scenario = found[0]
            out.append(_f("SPC-004", "error", ff.path, scenario.line,
                          f"O requisito {req.id} é uma restrição e o cenário não tem número.",
                          "Ponha o limite no Então ou em Exemplos. Sem número, volte à entrevista."))
    return out


def _has_number(scenario) -> bool:
    then = any(step.type == "then" and re.search(r"\d", step.text) for step in scenario.steps)
    rows = any(re.search(r"\d", cell) for block in scenario.examples for row in block.rows for cell in row)
    return then or rows


def _check_steps(fd) -> list[Finding]:
    """SPC-007."""
    out = []
    for ff in fd.files:
        if ff.feature is None:
            continue
        steps = list(ff.feature.background) + [s for sc in ff.feature.scenarios for s in sc.steps]
        for step in steps:
            count = _words(step.text)
            if count > MAX_SENTENCE_WORDS:
                out.append(_f("SPC-007", "warning", ff.path, step.line,
                              f"Este step tem {count} palavras. O limite é {MAX_SENTENCE_WORDS}.",
                              "Divida em dois steps, uma ideia em cada."))
    return out


class _Item(NamedTuple):
    line: int
    text: str
    examples: int


def _retraducao_items(section) -> tuple[list[_Item], int | None, list[_Item]]:
    """(REQ items, line of the "não faz" header, "não faz" items)."""
    items: list[_Item] = []
    nao_faz: list[_Item] = []
    header: int | None = None
    for number, line in section.lines:
        stripped = line.strip()
        if header is None and _norm(stripped).startswith(NAO_FAZ_HEADERS):
            header = number
        elif (items and header is None and stripped.startswith("- ")
              and _norm(stripped[2:]).startswith(EXAMPLE_PREFIXES)):
            last = items[-1]
            items[-1] = last._replace(examples=last.examples + 1)
        elif line.startswith("- "):
            target = nao_faz if header is not None else items
            target.append(_Item(number, stripped[2:].strip(), 0))
    return items, header, nao_faz


def _out_of_scope_count(doc) -> int:
    section = doc.sections.get("fora do escopo")
    if section is None:
        return 0
    entries = [ln.strip()[2:].strip() for _, ln in section.lines if ln.strip().startswith("- ")]
    return sum(1 for e in entries if _norm(e) not in EMPTY_ITEMS)


def _check_retraducao(doc, reqs: list[Req], intent_rel: str) -> list[Finding]:
    """SPC-017, SPC-018 and SPC-011."""
    section = doc.sections.get("retraducao")
    if section is None:
        return [_f("SPC-017", "error", intent_rel, 1, "Falta a seção Retradução: o que eu entendi, em primeira pessoa.",
                   "Escreva a retradução antes de pedir a aprovação.")]
    out: list[Finding] = []
    rev_line, rev = _retraducao_rev(doc)
    if rev is None:
        out.append(_f("SPC-017", "error", intent_rel, rev_line, "Falta a linha rev: com um número a partir de 1.",
                      "Escreva rev: 1 logo abaixo do título."))
    items, header, nao_faz = _retraducao_items(section)
    active = {r.id for r in reqs if r.active}
    retired = {r.id for r in reqs if not r.active}
    cited: set[str] = set()
    for item in items:
        ids = set(REQ_ANY.findall(item.text))
        cited |= ids
        if ids & retired:
            out.append(_f("SPC-017", "error", intent_rel, item.line, "Este item fala de um requisito retirado.",
                          "Tire o item da retradução."))
        if ids & active and item.examples == 0:
            out.append(_f("SPC-017", "error", intent_rel, item.line, "Este item não tem exemplo narrado.",
                          "Acrescente uma linha - Exemplo: com uma situação concreta."))
        if ids and not set(re.findall(r"\w+", _norm(CITATION.sub("", item.text)))) & set(FIRST_PERSON):
            out.append(_f("SPC-017", "warning", intent_rel, item.line, "Este item não fala em primeira pessoa.",
                          "Comece com Eu: o que eu vou fazer."))
    out.extend(_f("SPC-017", "error", intent_rel, section.line, f"O requisito {req} não aparece na retradução.",
                  "Acrescente um item com o que eu vou fazer e um exemplo.")
               for req in sorted(active - cited))
    expected = _out_of_scope_count(doc)
    if len(nao_faz) < expected:
        out.append(_f("SPC-017", "error", intent_rel, header or section.line,
                      f"Fora do escopo tem {expected} itens e O que eu não vou fazer tem {len(nao_faz)}.",
                      "Diga ao citizen cada coisa que fica fora."))
    out.extend(_check_citizen_voice(section, intent_rel))
    if rev is not None and rev > 1:
        out.extend(_check_rounds(doc, rev, rev_line, intent_rel))
    return out


def _check_citizen_voice(section, intent_rel: str) -> list[Finding]:
    """SPC-018: surprise test (no confirm-only token) and controlled voice."""
    out = []
    for number, line in section.lines:
        if not line.strip() or REV_LINE.match(line):
            continue
        tokens = sorted(set(TECH_TOKENS.findall(QUOTED.sub("", line))))
        if tokens:
            out.append(_f("SPC-018", "warning", intent_rel, number,
                          f"Este trecho usa {', '.join(tokens)}, que não diz nada que você possa reconhecer.",
                          "Troque por um exemplo do que você vê."))
        plain = CITATION.sub("", QUOTED.sub("", line)).strip().lstrip("-").strip()
        sentences = [s for s in SENTENCE_SPLIT.split(plain) if re.search(r"\w", s)]
        longest = max((_words(s) for s in sentences), default=0)
        if longest > MAX_SENTENCE_WORDS:
            out.append(_f("SPC-018", "warning", intent_rel, number,
                          f"Uma frase tem {longest} palavras. O limite é {MAX_SENTENCE_WORDS}.",
                          "Divida a frase em duas."))
        if len(sentences) > MAX_SENTENCES_PER_PARAGRAPH:
            out.append(_f("SPC-018", "warning", intent_rel, number,
                          f"Este trecho tem {len(sentences)} frases. O limite é {MAX_SENTENCES_PER_PARAGRAPH}.",
                          "Divida em dois itens."))
    return out


def _mudancas_text(doc) -> str:
    section = doc.sections.get("mudancas")
    return "" if section is None else "\n".join(ln for _, ln in section.lines)


def _check_rounds(doc, rev: int, rev_line: int, intent_rel: str) -> list[Finding]:
    """SPC-011."""
    out = []
    if f"retraducao rev {rev}" not in _norm(_mudancas_text(doc)):
        out.append(_f("SPC-011", "error", intent_rel, rev_line, f"A retradução está no rev {rev} sem linha em Mudanças.",
                      f"Acrescente em Mudanças: Retradução rev {rev}: o que mudou."))
    if rev - 1 > SPECIFY_MAX_ROUNDS:
        out.append(_f("SPC-011", "info", intent_rel, rev_line,
                      f"Já houve {rev - 1} ajustes. O teto é {SPECIFY_MAX_ROUNDS}: devolva a decisão ao citizen.",
                      "Pergunte: aprovar como está, voltar à entrevista ou descartar."))
    return out


def _check_names(fd, doc, lock: dict | None, slug: str, lock_rel: str) -> list[Finding]:
    """SPC-012."""
    if lock is None:
        return []
    now = {_cf.scenario_key(slug, ff.path, sc.name) for ff, sc, _ in _scenarios(fd, slug)}
    changes = _mudancas_text(doc)
    out = []
    for key in sorted(lock.get("index", [])):
        name = key.split("::", 1)[1] if "::" in key else key
        if key not in now and name not in changes:
            out.append(_f("SPC-012", "error", lock_rel, 1, f"O cenário aprovado {name} mudou de nome ou sumiu.",
                          "Volte o nome ou registre a mudança em Mudanças, com o nome antigo."))
    return out


def sort_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(set(findings), key=lambda f: (f.file, f.line, f.rule, f.severity, f.message))


def check_specify(root: Path, slug: str) -> Report:
    """All checks for features/<slug>/ (SPC-001 to SPC-018), plus the status."""
    if _cf is None:
        raise UsageError("validador de cenários não encontrado (check_features.py); eu não aprovo sem ele")
    folder = root / "features" / slug
    intent_path = folder / "intent.md"
    intent_rel = _rel(intent_path, root)
    text = _read(intent_path) if intent_path.is_file() else None
    status = compute_status(root, slug)
    entry = _check_entry(intent_rel, text)
    if entry or text is None:
        return Report(slug, sort_findings(entry), status)
    doc = parse_intent(text)
    reqs = requirements(doc, slug)
    fds = _cf.discover(root, slug)
    fd = fds[0]
    lock = _load_lock(folder / LOCK_NAME)
    findings = _check_ghk(fds) + _check_coverage(fd, slug, reqs, intent_rel) + _check_steps(fd)
    findings += _check_retraducao(doc, reqs, intent_rel)
    findings += _check_names(fd, doc, lock, slug, _rel(folder / LOCK_NAME, root))
    return Report(slug, sort_findings(findings), status)


def blocking(findings: list[Finding]) -> bool:
    return any(f.severity in ("error", "warning") for f in findings)


# ---------------------------------------------------------------------------
# SPC-010: approval record
# ---------------------------------------------------------------------------


def build_lock(root: Path, slug: str, *, at: str, by: str, contract_by: str) -> str:
    folder = root / "features" / slug
    doc = parse_intent(_read(folder / "intent.md"))
    fds = _cf.discover(root, slug)
    index = sorted({_cf.scenario_key(slug, ff.path, sc.name) for ff, sc, _ in _scenarios(fds[0], slug)})
    rev = _retraducao_rev(doc)[1]
    lock = {
        **_current(folder, doc, slug),
        "approved_at": at,
        "approved_by": by,
        "contract_by": contract_by,
        "index": index,
        "rev": rev,
        "schema_version": LOCK_SCHEMA_VERSION,
        "slug": slug,
    }
    return json.dumps(lock, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def set_frontmatter(raw: bytes, fields: list[tuple[str, str]]) -> bytes:
    """Replace or insert `key: value` lines in the frontmatter; every other byte stays."""
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise UsageError("intent.md não tem frontmatter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise UsageError("intent.md não fecha o frontmatter")
    for key, value in fields:
        new = f"{key}: {value}{eol}"
        idx = next((i for i in range(1, end) if lines[i].split(":", 1)[0].strip() == key
                    and not lines[i].startswith((" ", "\t"))), None)
        if idx is None:
            lines.insert(end, new)
            end += 1
        else:
            lines[idx] = new
    out = "".join(lines).encode("utf-8")
    return b"\xef\xbb\xbf" + out if bom else out


def _atomic_write(path: Path, data: bytes) -> None:
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        if path.exists():
            shutil.copymode(path, tmp)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def approve(root: Path, slug: str, *, at: str, by: str, contract_by: str) -> Report:
    """Check, and only when nothing blocks, write the lock and then the frontmatter (SPC-010)."""
    report = check_specify(root, slug)
    if blocking(report.findings) or report.status.status == "missing":
        return report
    folder = root / "features" / slug
    lock_text = build_lock(root, slug, at=at, by=by, contract_by=contract_by)
    rev = json.loads(lock_text)["rev"]
    intent_path = folder / "intent.md"
    try:
        raw = intent_path.read_bytes()
    except OSError as exc:
        raise UsageError(f"não consegui ler {intent_path.as_posix()}: {exc.__class__.__name__}") from None
    new_intent = set_frontmatter(raw, [
        ("scenarios", "approved"),
        ("scenarios_approved_at", at),
        ("scenarios_approved_by", by),
        ("scenarios_contract_by", contract_by),
        ("scenarios_rev", str(rev)),
    ])
    _atomic_write(folder / LOCK_NAME, lock_text.encode("utf-8"))
    _atomic_write(intent_path, new_intent)
    return Report(slug, report.findings, compute_status(root, slug))


# ---------------------------------------------------------------------------
# CYC-032: reconcile the field with the status (emenda 000015)
# ---------------------------------------------------------------------------

DRAFT = "draft"
RECONCILE_ALL = "\0all"
_RECONCILE_WORDS = {"reopened": "a intenção foi reaberta", "stale": "os cenários mudaram depois da aprovação"}


def _feature_folder(root: Path, slug: str) -> Path:
    """features/<slug>/ of this root, refusing a slug or a symlink that leads outside features/."""
    if not SLUG_RE.match(slug):
        raise UsageError(f"o nome {slug} não é um slug (letras minúsculas, números e hífen)")
    base = (root / "features").resolve()
    folder = root / "features" / slug
    if not folder.is_dir():
        raise UsageError(f"não há features/{slug}/. A entrevista vem antes: rode /plan --grill.")
    if not folder.resolve().is_relative_to(base):
        raise UsageError(f"features/{slug}/ aponta para fora de features/; não escrevo nada")
    return folder


def reconcile(root: Path, slug: str) -> dict:
    """Turn `scenarios: approved` into `draft` when the status is not approved; nothing else changes."""
    intent_path = _feature_folder(root, slug) / "intent.md"
    if not intent_path.is_file():
        raise UsageError(f"não há features/{slug}/intent.md")
    current = parse_intent(_read(intent_path)).frontmatter.get("scenarios")
    status = compute_status(root, slug)
    result = {"schema_version": SCHEMA_VERSION, "slug": slug, "changed": False, "from": current, "to": current,
              "reason": None, "reasons": status.reasons}
    if current != "approved" or status.status == "approved":
        return result
    try:
        raw = intent_path.read_bytes()
    except OSError as exc:
        raise UsageError(f"não consegui ler {intent_path.as_posix()}: {exc.__class__.__name__}") from None
    _atomic_write(intent_path, set_frontmatter(raw, [("scenarios", DRAFT)]))
    reason = "reopened" if "intencao-reaberta" in status.reasons else "stale"
    result.update({"changed": True, "from": "approved", "to": DRAFT, "reason": reason})
    return result


def _reconcile_line(result: dict) -> str:
    if not result["changed"]:
        return f"features/{result['slug']}: nada a fazer."
    return (f"features/{result['slug']}: os cenários voltaram a rascunho, porque "
            f"{_RECONCILE_WORDS[result['reason']]}. Peça nova aprovação.")


def _run_reconcile(root: Path, slug: str, as_json: bool) -> int:
    if slug != RECONCILE_ALL:
        result = reconcile(root, slug)
        print(json.dumps(result, ensure_ascii=False, indent=2) if as_json else _reconcile_line(result))
        return 0
    folders = sorted(p.parent for p in (root / "features").glob("*/intent.md")) if (root / "features").is_dir() else []
    results = [reconcile(root, folder.name) for folder in folders]
    if as_json:
        print(json.dumps({"schema_version": SCHEMA_VERSION, "features": results}, ensure_ascii=False, indent=2))
    elif not results:
        print("check_specify: nenhum features/<slug>/intent.md; nada a verificar.")
    else:
        for result in results:
            print(_reconcile_line(result))
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_SEVERITY_WORDS = {"error": "erro", "warning": "aviso", "info": "informação"}


def _plural(count: int, one: str, many: str) -> str:
    return f"{count} {one if count == 1 else many}"


def _status_words(status: Status) -> str:
    extra = f" ({', '.join(status.reasons)})" if status.reasons else ""
    reqs = f"; requisitos afetados: {', '.join(status.reqs)}" if status.reqs else ""
    return f"{status.status}{extra}{reqs}"


def _as_json(report: Report, approved: bool | None = None) -> dict:
    data = {
        "schema_version": SCHEMA_VERSION,
        "slug": report.slug,
        "status": report.status.status,
        "reasons": report.status.reasons,
        "reqs": report.status.reqs,
        "findings": [f._asdict() for f in report.findings],
        "ressalvas": ressalvas(),
    }
    if approved is not None:
        data["approved"] = approved
    return data


def _print_report(report: Report, approved: bool | None) -> None:
    for f in report.findings:
        hint = f" Dica: {f.hint}" if f.hint else ""
        print(f"{f.file}:{f.line}: {f.rule} {_SEVERITY_WORDS[f.severity]}: {f.message}{hint}")
    count = {s: sum(1 for f in report.findings if f.severity == s) for s in _SEVERITY_WORDS}
    print(f"check_specify {report.slug}: {_plural(count['error'], 'erro', 'erros')}, "
          f"{_plural(count['warning'], 'aviso', 'avisos')}, "
          f"{_plural(count['info'], 'informação', 'informações')}; "
          f"estado dos cenários: {_status_words(report.status)}")
    if approved is not None:
        print("aprovação registrada." if approved else "aprovação não registrada: corrija os achados acima.")
    for caveat in ressalvas():
        print(f"ressalva: {caveat}")


def _scan(root: Path, as_json: bool) -> int:
    folders = sorted(p.parent for p in (root / "features").glob("*/intent.md")) if (root / "features").is_dir() else []
    if not folders:
        if as_json:
            print(json.dumps({"schema_version": SCHEMA_VERSION, "features": []}, ensure_ascii=False, indent=2))
        else:
            print("check_specify: nenhum features/<slug>/intent.md; nada a verificar.")
        return 0
    failed = unreadable = False
    rows = []
    for folder in folders:
        slug = folder.name
        try:
            marked = parse_intent(_read(folder / "intent.md")).frontmatter.get("scenarios") == "approved"
            status = compute_status(root, slug)
        except UsageError as exc:
            unreadable = True
            print(f"check_specify: {exc}", file=sys.stderr)
            continue
        stale = marked and status.status != "approved"
        failed |= stale
        rows.append({"slug": slug, "status": status.status, "reasons": status.reasons, "reqs": status.reqs,
                     "approved_marked": marked})
        if not as_json:
            note = " -- aprovação velha: peça nova aprovação" if stale else ""
            print(f"features/{slug}: cenários {_status_words(status)}{note}")
    if as_json:
        print(json.dumps({"schema_version": SCHEMA_VERSION, "features": rows}, ensure_ascii=False, indent=2))
    return 2 if unreadable else (1 if failed else 0)


def _run(args: argparse.Namespace) -> int:
    root = Path(args.root)
    if not root.is_dir():
        raise UsageError(f"pasta não encontrada: {root}")
    if args.reconcile is not None:
        if args.approve or args.status:
            raise UsageError("--reconcile não se combina com --approve nem com --status")
        slug = args.reconcile
        if args.feature is not None:
            if slug not in (RECONCILE_ALL, args.feature):
                raise UsageError("--reconcile e --feature citam features diferentes")
            slug = args.feature
        return _run_reconcile(root, slug, args.json)
    if args.feature is None:
        if args.approve or args.status:
            raise UsageError("--approve e --status pedem --feature <slug>")
        return _scan(root, args.json)
    if not SLUG_RE.match(args.feature):
        raise UsageError(f"o nome {args.feature} não é um slug (letras minúsculas, números e hífen)")
    if not (root / "features" / args.feature).is_dir():
        raise UsageError(f"não há features/{args.feature}/. A entrevista vem antes: rode /plan --grill.")
    if args.status:
        status = compute_status(root, args.feature)
        report = Report(args.feature, [], status)
        if args.json:
            print(json.dumps(_as_json(report), ensure_ascii=False, indent=2))
        else:
            print(f"features/{args.feature}: cenários {_status_words(status)}")
        return 0
    approved = None
    if args.approve:
        missing = [flag for flag, value in (("--at", args.at), ("--by", args.by), ("--contract-by", args.contract_by))
                   if not value]
        if missing:
            raise UsageError(f"--approve pede {', '.join(missing)}")
        if not AT_RE.match(args.at):
            raise UsageError("--at precisa ser data e hora UTC, por exemplo 2026-10-06T15:00Z")
        if not NAME_RE.match(args.by) or not NAME_RE.match(args.contract_by):
            raise UsageError("--by e --contract-by são um nome sem espaço (ou ninguem)")
        report = approve(root, args.feature, at=args.at, by=args.by, contract_by=args.contract_by)
        approved = not blocking(report.findings) and report.status.status == "approved"
    else:
        report = check_specify(root, args.feature)
    if args.json:
        print(json.dumps(_as_json(report, approved), ensure_ascii=False, indent=2))
    else:
        _print_report(report, approved)
    return 1 if blocking(report.findings) or approved is False else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Specify phase checker and approval recorder (SPC-001 to SPC-018).")
    parser.add_argument("root", nargs="?", default=".", help="project root (default: current directory)")
    parser.add_argument("--feature", help="check features/<slug>/; omit to scan every features/*/intent.md")
    parser.add_argument("--status", action="store_true", help="print only the status: missing, draft, approved, stale")
    parser.add_argument("--approve", action="store_true", help="record the approval when nothing blocks (SPC-010)")
    parser.add_argument("--at", help="UTC date and time of the approval, given by the caller")
    parser.add_argument("--by", help="who approved the message (the citizen)")
    parser.add_argument("--contract-by", dest="contract_by", help=f"who approved the .feature contract, or {CONTRACT_NOBODY}")
    parser.add_argument("--reconcile", nargs="?", const=RECONCILE_ALL, metavar="SLUG",
                        help="turn an old `scenarios: approved` into `draft` (one slug, or every feature)")
    parser.add_argument("--json", action="store_true", help="one JSON object with schema_version")
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except UsageError as exc:
        print(f"check_specify: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 -- never a raw traceback for the user
        print(f"check_specify: erro interno ({type(exc).__name__}): {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
