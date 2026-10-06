#!/usr/bin/env python3
# designer: Before you approve any scenario, I read the .feature files that
#   /plan wrote next to your intent.md and tell you, rule by rule, what is
#   wrong: a scenario with no link to what you asked for, a requirement with no
#   scenario, a tag that points to nothing, a step that repeats or confuses, a
#   scenario that tries to do two things. I decide nothing by impression: the
#   same files always give the same answer, and I say what I did not measure.
"""
check_features.py -- Validator for features/<slug>/*.feature (GHK-001 to GHK-019).

Invocation: skill-invoked, user-cli, hook-ci
Lifecycle: active

Rules: .claude/references/general/gherkin-spec-format.md (GHK-NNN, CYC-003, CYC-027).
Layout: .claude/references/template/feature-layout.md. The intent.md is read with
the parser of check_intent.py (one parser for intent.md).

Scope: only folders features/<slug>/ that have an intent.md are validated; a
folder with .feature files and no intent.md gets one info; any other features/
layout (for example behave-style files) is left alone. With no
features/<slug>/intent.md the script prints a line and exits 0.

Severity: error (exit 1), warning (exit 1 only with --strict), info (never).
No LLM, no network, standard library only. Output is sorted and identical for the
same files. The validator does not compute divergence (D1, D2, D3): it delivers
the REQ -> scenarios matrix (--matrix) and the findings that feed D1 and D2.

Exit codes: 0 = no errors (warnings and infos do not fail); 1 = errors, or
warnings with --strict; 2 = usage error, unreadable root, or internal failure.

Usage
-----
    python .claude/skills/scripts/check_features.py
    python .claude/skills/scripts/check_features.py <root> --feature <slug>
    python .claude/skills/scripts/check_features.py <root> --json --matrix
    python .claude/skills/scripts/check_features.py <root> --steps <dir> --strict

CHECK_PLUGIN_MANIFEST:
  name: Gherkin Spec Format
  stack:
    backend: [any]
    frontend: [any]
  scope: features
  critical: false
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

from check_intent import _norm
from check_intent import parse as parse_intent
from check_intent import table as intent_table

SCHEMA_VERSION = 1

# ---------------------------------------------------------------------------
# Constants (gherkin-spec-format.md)
# ---------------------------------------------------------------------------

RESERVED_SLUGS = ("ent", "perm", "ux", "mc", "jm", "i18n", "val", "delta")
DISABLE_TAGS = ("skip", "wip", "xfail", "ignore")
NAO_FAZ_TAG = "nao-faz"
MAX_STEPS = 10
MAX_BACKGROUND_STEPS = 3

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REQ_TAG_RE = re.compile(r"^@REQ-[a-z][a-z0-9]*(-[a-z0-9]+)*-[0-9]{3,}$")
REQ_TAG_PARTS = re.compile(r"^@REQ-(.+)-([0-9]{3,})$")
REQ_ID_RE = re.compile(r"^REQ-([a-z0-9]+(?:-[a-z0-9]+)*)-(\d{3,})$")
JM_RE = re.compile(r"JM-TB-\d{3}")
PLACEHOLDER_RE = re.compile(r"<([^<>\s][^<>]*)>")

_HEADERS = {
    "en": {
        "feature": ("Feature", "Business Need", "Ability"),
        "rule": ("Rule",),
        "background": ("Background",),
        "outline": ("Scenario Outline", "Scenario Template"),
        "scenario": ("Scenario", "Example"),
        "examples": ("Examples", "Scenarios"),
    },
    "pt": {
        "feature": ("Funcionalidade", "Característica", "Caracteristica"),
        "rule": ("Regra",),
        "background": ("Contexto", "Cenário de Fundo", "Cenario de Fundo", "Fundo"),
        "outline": ("Esquema do Cenário", "Esquema do Cenario"),
        "scenario": ("Cenário", "Cenario", "Exemplo"),
        "examples": ("Exemplos",),
    },
}
_STEPS = {
    "en": {"given": ("Given",), "when": ("When",), "then": ("Then",), "and": ("And",), "but": ("But",)},
    "pt": {
        "given": ("Dado", "Dada", "Dados", "Dadas"),
        "when": ("Quando",),
        "then": ("Então", "Entao"),
        "and": ("E",),
        "but": ("Mas",),
    },
}
LANGUAGES = tuple(_HEADERS)


def _compile(lang: str) -> tuple[list[tuple[str, re.Pattern[str]]], list[tuple[str, re.Pattern[str]]]]:
    headers = []
    for kind, names in _HEADERS[lang].items():
        ordered = sorted(names, key=len, reverse=True)
        headers.append((kind, re.compile(r"^(?:" + "|".join(re.escape(n) for n in ordered) + r")\s*:\s*(.*)$")))
    # Longest header first so "Scenario Outline" wins over "Scenario".
    headers.sort(key=lambda item: 0 if item[0] in ("outline", "background") else 1)
    steps = []
    for kind, names in _STEPS[lang].items():
        steps.append((kind, re.compile(r"^(?:" + "|".join(re.escape(n) for n in names) + r")\s+(.*)$")))
    steps.append(("star", re.compile(r"^\*\s+(.*)$")))
    return headers, steps


_PATTERNS = {lang: _compile(lang) for lang in LANGUAGES}
# Unambiguous keywords of the other language (used to explain a missing "# language: pt").
_FOREIGN_STEP = re.compile(r"^(?:Dado|Dada|Dados|Dadas|Quando|Então|Entao)\s")


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


class ParseError(Exception):
    def __init__(self, line: int, message: str) -> None:
        super().__init__(message)
        self.line = line
        self.message = message


class Finding(NamedTuple):
    rule: str
    severity: str
    file: str
    line: int
    scenario: str
    message: str
    hint: str


@dataclass
class Tag:
    name: str  # with the leading "@"
    line: int

    @property
    def bare(self) -> str:
        return self.name[1:]


@dataclass
class Step:
    kind: str  # given, when, then, and, but, star
    text: str
    line: int
    type: str | None  # effective type: given, when, then (None: leading and/but)
    extra: list[str] = field(default_factory=list)


@dataclass
class Examples:
    line: int
    tags: list[Tag] = field(default_factory=list)
    header: list[str] = field(default_factory=list)
    header_line: int = 0
    rows: list[list[str]] = field(default_factory=list)


@dataclass
class RuleInfo:
    name: str
    line: int
    tags: list[Tag] = field(default_factory=list)
    description: list[str] = field(default_factory=list)


@dataclass
class Scenario:
    kind: str  # scenario or outline
    name: str
    line: int
    tags: list[Tag] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)
    examples: list[Examples] = field(default_factory=list)
    rule: RuleInfo | None = None
    description: list[str] = field(default_factory=list)


@dataclass
class Feature:
    language: str
    name: str
    line: int
    tags: list[Tag] = field(default_factory=list)
    background: list[Step] = field(default_factory=list)
    background_line: int = 0
    scenarios: list[Scenario] = field(default_factory=list)
    rules: list[RuleInfo] = field(default_factory=list)


@dataclass
class FeatureFile:
    path: str
    feature: Feature | None = None
    error: ParseError | None = None


@dataclass
class ReqInfo:
    line: int
    active: bool


@dataclass
class Intent:
    slug: str
    status: str
    scenarios_approved: bool | None
    reqs: dict[str, ReqInfo]
    terms: list[str] | None
    serve: list[str]
    out_of_scope: int
    out_line: int
    reqs_line: int
    invalid_rows: int


@dataclass
class FeatureDir:
    slug: str
    path: str
    intent_path: str | None = None
    intent: Intent | None = None
    files: list[FeatureFile] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Gherkin parser (subset: Feature, Rule, Background, Scenario, Scenario Outline,
# Examples, tags, comments, doc strings, data tables, "# language:" en/pt)
# ---------------------------------------------------------------------------

_LANG_COMMENT = re.compile(r"^\s*#\s*language\s*:\s*(\S+)\s*$")
_DOC_DELIMS = ('"""', "```")


def _parse_tags(raw: str, line: int) -> list[Tag]:
    body = raw.split(" #", 1)[0]
    return [Tag(token, line) for token in body.split() if token.startswith("@")]


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _effective_type(kind: str, previous: str | None) -> str | None:
    if kind in ("given", "when", "then"):
        return kind
    return previous


class _Parser:
    def __init__(self, text: str) -> None:
        self.lines = text.splitlines()
        self.language = "en"
        self.feature: Feature | None = None
        self.rule: RuleInfo | None = None
        self.target: str | None = None  # feature, rule, background, scenario, examples, step
        self.scenario: Scenario | None = None
        self.examples: Examples | None = None
        self.step: Step | None = None
        self.sink: list[Step] | None = None
        self.pending_tags: list[Tag] = []
        self.in_doc: str | None = None
        self.last_type: str | None = None
        self.seen_content = False

    def run(self) -> Feature:
        for number, raw in enumerate(self.lines, start=1):
            self._line(number, raw)
        if self.feature is None:
            raise ParseError(1, "Não encontrei a linha Feature: neste arquivo.")
        return self.feature

    # -- dispatch -----------------------------------------------------------

    def _line(self, number: int, raw: str) -> None:
        line = raw.strip()
        if self.in_doc is not None:
            self._doc_line(line)
            return
        if not line:
            return
        if line.startswith("#"):
            self._comment(number, line)
            return
        if line.startswith("@"):
            self.pending_tags += _parse_tags(line, number)
            self.seen_content = True
            return
        if line.startswith(_DOC_DELIMS):
            self._doc_open(number, line)
            return
        if line.startswith("|"):
            self._table_row(number, line)
            return
        header = self._match(line, 0)
        if header is not None:
            self._header(number, *header)
            return
        step = self._match(line, 1)
        if step is not None:
            self._step(number, *step)
            return
        self._text(number, line)

    def _comment(self, number: int, line: str) -> None:
        match = _LANG_COMMENT.match(line)
        if match and self.feature is None and not self.seen_content:
            lang = match.group(1).lower()
            if lang not in LANGUAGES:
                raise ParseError(number, f"O idioma {lang} não é suportado. Use en ou pt.")
            self.language = lang

    def _match(self, line: str, which: int) -> tuple[str, str] | None:
        for kind, pattern in _PATTERNS[self.language][which]:
            match = pattern.match(line)
            if match:
                return kind, match.group(1).strip()
        return None

    # -- structure ----------------------------------------------------------

    def _header(self, number: int, kind: str, name: str) -> None:
        self.seen_content = True
        tags, self.pending_tags = self.pending_tags, []
        if kind == "feature":
            if self.feature is not None:
                raise ParseError(number, "Há mais de uma linha Feature: neste arquivo.")
            self.feature = Feature(self.language, name, number, tags)
            self.target = "feature"
            return
        if self.feature is None:
            raise ParseError(number, "Não encontrei a linha Feature: antes desta linha.")
        feature = self.feature
        if kind == "examples":
            if self.scenario is None or self.scenario.kind != "outline":
                raise ParseError(number, "Esta linha de exemplos não está dentro de um esquema de cenário.")
            self.examples = Examples(number, tags)
            self.scenario.examples.append(self.examples)
            self.step, self.sink, self.target = None, None, "examples"
            return
        self.scenario = self.examples = self.step = self.sink = None
        self.last_type = None
        self.target = kind
        if kind == "rule":
            self.rule = RuleInfo(name, number, tags)
            feature.rules.append(self.rule)
        elif kind == "background":
            feature.background_line = number
            self.sink = feature.background
        else:
            self.scenario = Scenario(kind, name, number, tags, rule=self.rule)
            feature.scenarios.append(self.scenario)
            self.sink = self.scenario.steps
            self.target = "scenario"

    def _step(self, number: int, kind: str, text: str) -> None:
        self.seen_content = True
        if self.feature is None:
            raise ParseError(number, "Não encontrei a linha Feature: antes deste step.")
        if self.sink is None:
            raise ParseError(number, "Este step não está dentro de um cenário nem de um contexto.")
        eff = _effective_type(kind, self.last_type)
        self.last_type = eff
        self.step = Step(kind, text, number, eff)
        self.sink.append(self.step)
        self.target = "step"

    def _doc_open(self, number: int, line: str) -> None:
        if self.step is None:
            raise ParseError(number, "Um bloco de texto precisa vir logo depois de um step.")
        delim = line[:3]
        if not line[3:].strip().endswith(delim):
            self.in_doc = delim

    def _doc_line(self, line: str) -> None:
        if line.startswith(self.in_doc or ""):
            self.in_doc = None
        elif self.step is not None:
            self.step.extra.append(line)

    def _table_row(self, number: int, line: str) -> None:
        cells = _split_row(line)
        if self.target == "examples" and self.examples is not None:
            if not self.examples.header:
                self.examples.header, self.examples.header_line = cells, number
            else:
                self.examples.rows.append(cells)
        elif self.target == "step" and self.step is not None:
            self.step.extra.extend(cells)
        else:
            raise ParseError(number, "Uma tabela precisa vir depois de um step ou de Examples.")

    def _foreign(self, line: str) -> bool:
        if self.language != "en":
            return False
        return bool(_FOREIGN_STEP.match(line) or any(p.match(line) for _, p in _PATTERNS["pt"][0]))

    def _text(self, number: int, line: str) -> None:
        if self._foreign(line):
            raise ParseError(number, "Esta palavra-chave é do português e falta a linha # language: pt no início.")
        if self.feature is None:
            raise ParseError(number, "Não encontrei a linha Feature: antes desta linha.")
        if self.target == "rule" and self.rule is not None:
            self.rule.description.append(line)
        elif self.target == "scenario" and self.scenario is not None:
            self.scenario.description.append(line)
        elif self.target not in ("feature", "background", "examples"):
            raise ParseError(number, f"Não entendi esta linha: {line[:40]}")


def parse_feature(text: str) -> Feature:
    """Parse one .feature text. Raises ParseError(line, message) on a syntax problem."""
    return _Parser(text).run()


# ---------------------------------------------------------------------------
# intent.md (read with the parser of check_intent.py)
# ---------------------------------------------------------------------------


def _first_cell(row) -> str:
    return next(iter(row.cells.values()), "").strip().strip("`")


def _count_items(section) -> int:
    if section is None:
        return 0
    items = [ln.strip()[1:].strip() for _, ln in section.lines if ln.strip().startswith("- ")]
    return sum(1 for item in items if _norm(item) not in ("", "nenhuma", "nenhum", "none"))


def load_intent(text: str, folder_slug: str) -> Intent:
    """Read the facts GHK needs from an intent.md text (REQs, status, terms, serve)."""
    doc = parse_intent(text)
    section = doc.sections.get("requisitos")
    reqs: dict[str, ReqInfo] = {}
    invalid = 0
    for row in intent_table(section):
        raw = _first_cell(row)
        match = REQ_ID_RE.match(raw)
        if not match or match.group(1) != folder_slug:
            invalid += 1
            continue
        active = _norm(row.cells.get("estado", "")) != "retirado"
        reqs.setdefault(raw, ReqInfo(row.line, active))
    terms = None
    model = doc.sections.get("modelo e termos")
    if model is not None:
        terms = [row.cells.get("termo", "").strip() for row in intent_table(model)]
        terms = [t for t in terms if t]
    serve_raw = doc.frontmatter.get("serve", "").strip().strip("[]")
    scenarios = doc.frontmatter.get("scenarios")
    out_section = doc.sections.get("fora do escopo")
    return Intent(
        slug=doc.frontmatter.get("slug", ""),
        status=doc.frontmatter.get("status", ""),
        scenarios_approved=None if scenarios is None else scenarios == "approved",
        reqs=reqs,
        terms=terms,
        serve=[i.strip() for i in serve_raw.split(",") if i.strip()],
        out_of_scope=_count_items(out_section),
        out_line=out_section.line if out_section is not None else 1,
        reqs_line=section.line if section is not None else 1,
        invalid_rows=invalid,
    )


# ---------------------------------------------------------------------------
# Helpers over parsed features
# ---------------------------------------------------------------------------


def _find(rule: str, severity: str, file: str, line: int, message: str, hint: str = "",
          scenario: str = "") -> Finding:
    return Finding(rule, severity, file, line, scenario, message, hint)


def _is_req_tag(tag: Tag) -> bool:
    return tag.name.lower().startswith("@req-")


def scenario_tags(feature: Feature, scenario: Scenario) -> list[Tag]:
    """Tags that disable or mark a scenario at any level (feature, rule, scenario, examples)."""
    tags = list(feature.tags)
    if scenario.rule is not None:
        tags += scenario.rule.tags
    tags += scenario.tags
    for block in scenario.examples:
        tags += block.tags
    return tags


def is_disabled(feature: Feature, scenario: Scenario) -> bool:
    return any(t.bare.lower() in DISABLE_TAGS for t in scenario_tags(feature, scenario))


def cited_reqs(fd_slug: str, scenario: Scenario) -> list[str]:
    """REQ ids cited by the scenario with a well-formed tag of this feature folder."""
    ids = []
    for tag in scenario.tags:
        match = REQ_TAG_PARTS.match(tag.name)
        if REQ_TAG_RE.match(tag.name) and match and match.group(1) == fd_slug:
            ids.append(f"REQ-{match.group(1)}-{match.group(2)}")
    return ids


def _parsed(fd: FeatureDir) -> list[FeatureFile]:
    return [ff for ff in fd.files if ff.feature is not None]


# ---------------------------------------------------------------------------
# Structure and traceability rules
# ---------------------------------------------------------------------------


def _level_tags(ff: FeatureFile, tags: list[Tag], where: str) -> list[Finding]:
    out = []
    for tag in tags:
        if _is_req_tag(tag):
            out.append(_find("GHK-003", "error", ff.path, tag.line,
                             f"A tag {tag.name} não pode ficar em {where}. Ela vai em cada cenário.",
                             "Mova a tag para a linha acima do cenário."))
        elif tag.bare.lower() == NAO_FAZ_TAG:
            out.append(_find("GHK-019", "error", ff.path, tag.line,
                             f"A tag @{NAO_FAZ_TAG} vale só em cenário, não em {where}.",
                             "Mova a tag para a linha acima do cenário."))
    return out


def _disable_findings(ff: FeatureFile, tags: list[Tag], scenario: str = "") -> list[Finding]:
    return [
        _find("GHK-014", "warning", ff.path, tag.line,
              f"Este cenário está desligado ({tag.name}) e conta como não coberto.",
              "Tire a tag quando o cenário voltar a valer.", scenario)
        for tag in tags
        if tag.bare.lower() in DISABLE_TAGS
    ]


def _check_req_tags(fd: FeatureDir, ff: FeatureFile, scenario: Scenario) -> list[Finding]:
    out: list[Finding] = []
    intent = fd.intent
    req_tags = [t for t in scenario.tags if _is_req_tag(t)]
    if not req_tags:
        out.append(_find("GHK-002", "error", ff.path, scenario.line,
                         f"O cenário {scenario.name} não tem tag @REQ-.",
                         "Ponha a tag @REQ-<slug>-NNN do requisito na linha acima.", scenario.name))
    for tag in req_tags:
        match = REQ_TAG_PARTS.match(tag.name)
        if not REQ_TAG_RE.match(tag.name) or not match:
            out.append(_find("GHK-003", "error", ff.path, tag.line,
                             f"A tag {tag.name} não tem a forma @REQ-<slug>-NNN.",
                             f"Escreva, por exemplo, @REQ-{fd.slug}-001.", scenario.name))
        elif match.group(1) != fd.slug:
            out.append(_find("GHK-003", "error", ff.path, tag.line,
                             f"A tag {tag.name} usa o slug {match.group(1)}, e a pasta usa {fd.slug}.",
                             f"Use @REQ-{fd.slug}-{match.group(2)}.", scenario.name))
        elif intent is not None and f"REQ-{match.group(1)}-{match.group(2)}" not in intent.reqs:
            out.append(_find("GHK-004", "error", ff.path, tag.line,
                             f"A tag {tag.name} cita um requisito que não existe em intent.md.",
                             "Confira o número na tabela de requisitos.", scenario.name))
    return out


def _check_placeholders(ff: FeatureFile, scenario: Scenario) -> list[Finding]:
    blocks = [b for b in scenario.examples if b.header]
    if not blocks:
        return []
    columns = {c for b in blocks for c in b.header}
    used: set[str] = set(PLACEHOLDER_RE.findall(scenario.name))
    out = []
    for step in scenario.steps:
        for name in PLACEHOLDER_RE.findall(" ".join([step.text, *step.extra])):
            used.add(name)
            if name not in columns:
                out.append(_find("GHK-009", "error", ff.path, step.line,
                                 f"A coluna {name} não existe em Examples.",
                                 "Acrescente a coluna ou tire o <...> do step.", scenario.name))
    for block in blocks:
        for column in block.header:
            if column not in used:
                out.append(_find("GHK-009", "error", ff.path, block.header_line,
                                 f"A coluna {column} de Examples não é usada em nenhum step.",
                                 "Use <coluna> num step ou tire a coluna.", scenario.name))
    return out


def _check_outline(ff: FeatureFile, scenario: Scenario) -> list[Finding]:
    if scenario.kind != "outline":
        return []
    if not scenario.examples:
        return [_find("GHK-011", "error", ff.path, scenario.line,
                      f"O esquema de cenário {scenario.name} não tem Examples.",
                      "Acrescente Examples com ao menos uma linha.", scenario.name)]
    return [
        _find("GHK-011", "error", ff.path, block.line,
              f"Os exemplos de {scenario.name} não têm linhas.",
              "Acrescente ao menos uma linha de dados.", scenario.name)
        for block in scenario.examples
        if not block.rows
    ]


def _check_scenarios(fd: FeatureDir, ff: FeatureFile) -> list[Finding]:
    feature = ff.feature
    assert feature is not None
    out = _level_tags(ff, feature.tags, "Feature") + _disable_findings(ff, feature.tags)
    for rule in feature.rules:
        out += _level_tags(ff, rule.tags, "Rule") + _disable_findings(ff, rule.tags)
        out += _check_rule(fd, ff, rule)
    names: dict[str, int] = {}
    for scenario in feature.scenarios:
        out += _check_req_tags(fd, ff, scenario)
        out += _disable_findings(ff, scenario.tags, scenario.name)
        out += _check_outline(ff, scenario)
        for block in scenario.examples:
            out += _level_tags(ff, block.tags, "Examples") + _disable_findings(ff, block.tags, scenario.name)
        if scenario.steps and scenario.steps[0].type is None:
            first = scenario.steps[0]
            out.append(_find("GHK-009", "error", ff.path, first.line,
                             "O primeiro step não pode começar com And, But, E ou Mas.",
                             "Comece com Given, When ou Then.", scenario.name))
        out += _check_placeholders(ff, scenario)
        key = " ".join(scenario.name.casefold().split())
        if key in names:
            out.append(_find("GHK-010", "error", ff.path, scenario.line,
                             f"O nome {scenario.name} já foi usado na linha {names[key]}.",
                             "Dê um nome diferente: o relatório liga o cenário pelo nome.", scenario.name))
        else:
            names[key] = scenario.line
    return out


def _check_rule(fd: FeatureDir, ff: FeatureFile, rule: RuleInfo) -> list[Finding]:
    text = " ".join([rule.name, *rule.description])
    cited = JM_RE.findall(text)
    if not cited:
        return [_find("GHK-018", "error", ff.path, rule.line,
                      f"O grupo {rule.name} não diz de qual jornada JM-TB-NNN ele é.",
                      "Cite a jornada no nome ou na descrição do Rule, por exemplo (JM-TB-001).")]
    serve = fd.intent.serve if fd.intent is not None else []
    if serve:
        return [
            _find("GHK-018", "warning", ff.path, rule.line,
                  f"A jornada {jm} não consta em serve do intent.md.",
                  "Acrescente a jornada em serve ou corrija o ID.")
            for jm in cited
            if jm not in serve
        ]
    return []


def _check_dir_slug(fd: FeatureDir) -> list[Finding]:
    intent = fd.intent
    assert intent is not None and fd.intent_path is not None
    path = fd.intent_path
    out = []
    if not SLUG_RE.match(fd.slug):
        out.append(_find("GHK-016", "error", path, 1, f"O nome da pasta {fd.slug} não é kebab-case.",
                         "Use letras minúsculas, números e hífens."))
    elif fd.slug in RESERVED_SLUGS:
        out.append(_find("GHK-016", "error", path, 1, f"O nome {fd.slug} não pode ser usado.",
                         f"Os nomes {', '.join(RESERVED_SLUGS)} são reservados ao design."))
    if intent.slug and intent.slug != fd.slug:
        out.append(_find("GHK-016", "error", path, 1,
                         f"O slug {intent.slug} do intent.md é diferente do nome da pasta {fd.slug}.",
                         "Use o mesmo nome nos dois."))
    if not intent.reqs:
        out.append(_find("GHK-016", "error", path, intent.reqs_line,
                         f"O intent.md não tem nenhum requisito REQ-{fd.slug}-NNN.",
                         "Preencha a tabela de requisitos; o REQ vai na primeira coluna."))
    return out


def _check_coverage(fd: FeatureDir) -> list[Finding]:
    intent = fd.intent
    assert intent is not None and fd.intent_path is not None
    files = _parsed(fd)
    if len(files) != len(fd.files):
        return []  # a file did not parse: the coverage is unknown, not zero
    covered: set[str] = set()
    nao_faz = False
    for ff in files:
        assert ff.feature is not None
        for scenario in ff.feature.scenarios:
            covered.update(cited_reqs(fd.slug, scenario))
            nao_faz |= any(t.bare.lower() == NAO_FAZ_TAG for t in scenario.tags)
    severity = "error" if intent.status == "approved" else "info"
    out = []
    for req, info in intent.reqs.items():
        if info.active and req not in covered:
            note = "" if severity == "error" else " Isto ainda não foi medido: a entrevista não terminou."
            out.append(_find("GHK-005", severity, fd.intent_path, info.line,
                             f"O requisito {req} não tem cenário.{note}",
                             "Escreva um cenário com a tag desse requisito, ou retire o requisito."))
    if intent.out_of_scope and not nao_faz and files:
        out.append(_find("GHK-019", "info", fd.intent_path, intent.out_line,
                         f"Fora do escopo tem {_plural(intent.out_of_scope, 'item', 'itens')} e nenhum cenário @{NAO_FAZ_TAG}.",
                         "Opcional: um cenário @nao-faz prova o que o sistema não faz."))
    return out


def validate_structure(fd: FeatureDir) -> list[Finding]:
    """GHK-001..005, 009..011, 014, 016, 018, 019 for one features/<slug>/ folder."""
    if fd.intent is None:
        return [_find("GHK-016", "info", fd.path, 1,
                      "Esta pasta tem .feature e não tem intent.md; não foi validada.",
                      "Rode a grill do /plan para criar o intent.md.")]
    out = _check_dir_slug(fd)
    for ff in fd.files:
        if ff.error is not None:
            out.append(_find("GHK-001", "error", ff.path, ff.error.line, ff.error.message,
                             "Corrija a linha e rode de novo."))
        else:
            out += _check_scenarios(fd, ff)
    out += _check_coverage(fd)
    return sort_findings(out)


def sort_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(set(findings), key=lambda f: (f.file, f.line, f.rule, f.message))


# ---------------------------------------------------------------------------
# Matrix REQ -> scenarios (input of D1 and of the divergence report)
# ---------------------------------------------------------------------------


def scenario_key(slug: str, path: str, name: str) -> str:
    return f"{slug}/{Path(path).name}::{name}"


def build_matrix(fds: list[FeatureDir]) -> dict:
    """Matrix per feature: every REQ of intent.md (empty list when uncovered) with its scenarios."""
    matrix: dict = {}
    for fd in fds:
        if fd.intent is None:
            continue
        reqs = {req: {"state": "ativo" if info.active else "retirado", "scenarios": []}
                for req, info in fd.intent.reqs.items()}
        for ff in _parsed(fd):
            feature = ff.feature
            assert feature is not None
            order: dict[int, int] = {}
            for scenario in feature.scenarios:
                entry = _matrix_entry(fd, ff, feature, scenario, order)
                for req in cited_reqs(fd.slug, scenario):
                    if req in reqs:
                        reqs[req]["scenarios"].append(entry)
        matrix[fd.slug] = {"status": fd.intent.status, "scenarios_approved": fd.intent.scenarios_approved,
                           "reqs": reqs}
    return matrix


def _matrix_entry(fd: FeatureDir, ff: FeatureFile, feature: Feature, scenario: Scenario,
                  order: dict[int, int]) -> dict:
    journey = None
    if scenario.rule is not None:
        rule = scenario.rule
        key = id(rule)
        order[key] = order.get(key, 0) + 1
        found = JM_RE.findall(" ".join([rule.name, *rule.description]))
        journey = {"rule": rule.name, "jm": found[0] if found else None, "order": order[key]}
    rows = sum(len(b.rows) for b in scenario.examples) if scenario.kind == "outline" else None
    return {
        "key": scenario_key(fd.slug, ff.path, scenario.name),
        "file": ff.path,
        "name": scenario.name,
        "line": scenario.line,
        "rows": rows,
        "disabled": is_disabled(feature, scenario),
        "nao_faz": any(t.bare.lower() == NAO_FAZ_TAG for t in scenario.tags),
        "journey": journey,
    }


# ---------------------------------------------------------------------------
# Step rules: duplicate, ambiguity, near-duplicate, size, style, vocabulary
# ---------------------------------------------------------------------------

_VALUE_RE = re.compile(r'"[^"]*"|\d+(?:[.,]\d+)?')

# GHK-013: fixed list of implementation-detail patterns (documented in gherkin-spec-format.md).
_DETAIL_PATTERNS = (
    ("uma URL", re.compile(r"https?://|\bwww\.", re.IGNORECASE)),
    ("um caminho de arquivo", re.compile(r"(?:[\w.-]+/)+[\w-]+\.\w{1,5}\b|\b[A-Za-z]:\\|\\\w+\\")),
    ("SQL", re.compile(r"\bSELECT\b.+\bFROM\b|\bINSERT\s+INTO\b|\bUPDATE\b.+\bSET\b|\bDELETE\s+FROM\b",
                       re.IGNORECASE)),
    ("um seletor", re.compile(r"(?:^|\s)#[A-Za-z][\w-]*|(?:^|\s)\.[A-Za-z][\w-]*")),
    ("uma chamada de função", re.compile(r"\b[a-z_][a-z0-9_]*\(\)")),
    ("um nome de classe", re.compile(r"\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+\b")),
)


def light_key(text: str) -> str:
    """Case and spacing only: two steps with the same light key are the same text."""
    return " ".join(text.casefold().split())


def normalize_step(text: str) -> str:
    """Aggressive form for near-duplicates: no case, no punctuation, values replaced by <v>."""
    value = _VALUE_RE.sub("\x00", text.casefold())
    value = re.sub(r"[^\w\s<>\x00]", "", value)
    return " ".join(value.split()).replace("\x00", "<v>")


def step_values(text: str) -> tuple[str, ...]:
    return tuple(re.sub(r"[^\w\s]", "", v.casefold()).strip() for v in _VALUE_RE.findall(text))


def _all_steps(feature: Feature) -> list[tuple[Step, Scenario | None]]:
    pairs: list[tuple[Step, Scenario | None]] = [(st, None) for st in feature.background]
    for scenario in feature.scenarios:
        pairs += [(st, scenario) for st in scenario.steps]
    return pairs


def _check_duplicates(ff: FeatureFile, feature: Feature) -> list[Finding]:
    out = []
    for scenario in feature.scenarios:
        seen: dict[tuple[str, str], int] = {}
        for step in scenario.steps:
            if step.type is None:
                continue
            key = (step.type, light_key(step.text))
            if key in seen:
                out.append(_find("GHK-006", "error", ff.path, step.line,
                                 f"Este step repete o da linha {seen[key]} no mesmo cenário.",
                                 "Tire o step repetido.", scenario.name))
            else:
                seen[key] = step.line
    return out


def _check_ambiguity(ff: FeatureFile, feature: Feature) -> list[Finding]:
    by_text: dict[str, dict[str, int]] = {}
    for step, _ in _all_steps(feature):
        if step.type is not None:
            by_text.setdefault(light_key(step.text), {}).setdefault(step.type, step.line)
    out = []
    for kinds in by_text.values():
        if len(kinds) < 2:
            continue
        ordered = sorted(kinds.items(), key=lambda item: item[1])
        for kind, line in ordered[1:]:
            out.append(_find("GHK-007", "error", ff.path, line,
                             f"Este texto aparece como {ordered[0][0]} e como {kind} nesta feature.",
                             "Escreva um texto diferente para cada tipo de step."))
    return out


def _check_near_duplicates(ff: FeatureFile, feature: Feature) -> list[Finding]:
    groups: dict[tuple, dict[str, int]] = {}
    for step, _ in _all_steps(feature):
        if step.type is None:
            continue
        key = (step.type, normalize_step(step.text), step_values(step.text))
        groups.setdefault(key, {}).setdefault(step.text.strip(), step.line)
    out = []
    for variants in groups.values():
        if len(variants) < 2:
            continue
        ordered = sorted(variants.values())
        for line in ordered[1:]:
            out.append(_find("GHK-008", "warning", ff.path, line,
                             f"Este step só difere do da linha {ordered[0]} por caixa ou pontuação.",
                             "Use exatamente o mesmo texto."))
    return out


def _check_size(ff: FeatureFile, feature: Feature) -> list[Finding]:
    out = []
    if feature.background and (len(feature.background) > MAX_BACKGROUND_STEPS
                               or any(st.type == "when" for st in feature.background)):
        out.append(_find("GHK-012", "warning", ff.path, feature.background_line,
                         f"O contexto tem mais de {MAX_BACKGROUND_STEPS} steps ou tem uma ação (When).",
                         "Deixe no contexto só o que é comum e curto, sem ação."))
    for scenario in feature.scenarios:
        seen_then = False
        flagged = False
        for step in scenario.steps:
            if step.type == "then":
                seen_then = True
            elif step.type == "when" and seen_then and not flagged:
                flagged = True
                out.append(_find("GHK-012", "warning", ff.path, step.line,
                                 "Este cenário parece ter mais de um comportamento.",
                                 "Divida em dois cenários: um When por cenário.", scenario.name))
        if len(scenario.steps) > MAX_STEPS:
            out.append(_find("GHK-012", "warning", ff.path, scenario.line,
                             f"Este cenário tem {len(scenario.steps)} steps. O limite é {MAX_STEPS}.",
                             "Divida o cenário ou tire o que não muda o resultado.", scenario.name))
    return out


def _check_style(ff: FeatureFile, feature: Feature) -> list[Finding]:
    out = []
    for step, scenario in _all_steps(feature):
        for what, pattern in _DETAIL_PATTERNS:
            if pattern.search(step.text):
                out.append(_find("GHK-013", "warning", ff.path, step.line,
                                 f"O step fala de {what}. Diga o que o usuário vê, não como o sistema faz.",
                                 "Troque o detalhe técnico por uma frase do domínio.",
                                 scenario.name if scenario else ""))
                break
    return out


def term_candidates(text: str) -> list[str]:
    """Words GHK-017 checks: quoted text without digits, and capitalized words after the first."""
    text = PLACEHOLDER_RE.sub(" ", text)
    out = [q for q in re.findall(r'"([^"]+)"', text) if q.strip() and not re.search(r"\d", q)]
    rest = re.sub(r'"[^"]*"', " ", text)
    words = re.findall(r"[^\W\d_][\w-]*", rest)
    out += [w for i, w in enumerate(words) if i > 0 and w[0].isupper()]
    return out


def _stem(value: str) -> str:
    return value[:-1] if value.endswith("s") and len(value) > 3 else value


def _covered(candidate: str, terms: list[str]) -> bool:
    cand = _stem(_norm(candidate))
    for term in terms:
        norm = _stem(_norm(term))
        if (len(norm) >= 3 and norm in cand) or (len(cand) >= 3 and cand in norm):
            return True
    return False


def _check_vocabulary(fd: FeatureDir) -> list[Finding]:
    intent = fd.intent
    assert intent is not None and fd.intent_path is not None
    out: list[Finding] = []
    measured = False
    for ff in _parsed(fd):
        assert ff.feature is not None
        for scenario, steps in _steps_by_scenario(ff.feature):
            reported: set[str] = set()
            for step in steps:
                if any(pattern.search(step.text) for _, pattern in _DETAIL_PATTERNS):
                    continue  # already reported as an implementation detail (GHK-013)
                for cand in term_candidates(step.text):
                    measured = True
                    key = _norm(cand)
                    if intent.terms and not _covered(cand, intent.terms) and key not in reported:
                        reported.add(key)
                        out.append(_find("GHK-017", "warning", ff.path, step.line,
                                         f"A palavra {cand} não está em Modelo e termos.",
                                         "Acrescente o termo ao Modelo e termos ou use a palavra do pedido.",
                                         scenario))
    if measured and not intent.terms:
        out.append(_find("GHK-017", "info", fd.intent_path, 1,
                         "O intent.md não tem Modelo e termos; eu não conferi o vocabulário dos steps.",
                         "Preencha o Modelo e termos na grill."))
    return out


def _steps_by_scenario(feature: Feature) -> list[tuple[str, list[Step]]]:
    pairs = [("", list(feature.background))] if feature.background else []
    pairs += [(sc.name, sc.steps) for sc in feature.scenarios]
    return pairs


def validate_steps(fd: FeatureDir) -> list[Finding]:
    """GHK-006, 007, 008, 012, 013 and 017 for one features/<slug>/ folder."""
    if fd.intent is None:
        return []
    out: list[Finding] = []
    for ff in _parsed(fd):
        feature = ff.feature
        assert feature is not None
        out += (_check_duplicates(ff, feature) + _check_ambiguity(ff, feature)
                + _check_near_duplicates(ff, feature) + _check_size(ff, feature) + _check_style(ff, feature))
    out += _check_vocabulary(fd)
    return sort_findings(out)


# ---------------------------------------------------------------------------
# Step definitions (--steps): read with ast, never executed (GHK-015)
# ---------------------------------------------------------------------------


@dataclass
class StepDef:
    type: str  # given, when, then, any
    kind: str  # literal, parse, unverified
    pattern: str
    file: str
    line: int
    regex: re.Pattern[str] | None = None


_DEF_TYPES = {"given": "given", "when": "when", "then": "then", "step": "any"}
_PARSE_NAMES = ("parse",)


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _parse_to_regex(pattern: str) -> re.Pattern[str]:
    parts = re.split(r"\{[^{}]*\}", pattern)
    return re.compile("(.+?)".join(re.escape(part) for part in parts))


def _decorator_def(node: ast.expr, file: str) -> StepDef | None:
    if not isinstance(node, ast.Call):
        return None
    step_type = _DEF_TYPES.get(_call_name(node.func))
    if step_type is None:
        return None
    arg = node.args[0] if node.args else None
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return StepDef(step_type, "literal", arg.value, file, node.lineno)
    if (isinstance(arg, ast.Call) and _call_name(arg.func) in _PARSE_NAMES and arg.args
            and isinstance(arg.args[0], ast.Constant) and isinstance(arg.args[0].value, str)):
        pattern = arg.args[0].value
        return StepDef(step_type, "parse", pattern, file, node.lineno, _parse_to_regex(pattern))
    return StepDef(step_type, "unverified", ast.unparse(arg) if arg is not None else "", file, node.lineno)


def parse_step_defs(source: str, file: str) -> list[StepDef]:
    """Step definitions (@given, @when, @then, @step) found in one Python source; never executed."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    defs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defs += [d for d in (_decorator_def(dec, file) for dec in node.decorator_list) if d is not None]
    return sorted(defs, key=lambda d: (d.file, d.line))


def _expanded_texts(step: Step, scenario: Scenario | None) -> list[str]:
    if scenario is None or scenario.kind != "outline":
        return [step.text]
    texts = []
    for block in scenario.examples:
        for row in block.rows:
            text = step.text
            for column, value in zip(block.header, row):
                text = text.replace(f"<{column}>", value)
            texts.append(text)
    return texts or [step.text]


def _matches(definition: StepDef, step: Step, scenario: Scenario | None) -> bool:
    if definition.type not in (step.type, "any") or definition.kind == "unverified":
        return False
    for text in _expanded_texts(step, scenario):
        if definition.kind == "literal" and text.strip() == definition.pattern.strip():
            return True
        if definition.kind == "parse" and definition.regex is not None and definition.regex.fullmatch(text.strip()):
            return True
    return False


def validate_step_defs(fds: list[FeatureDir], defs: list[StepDef]) -> list[Finding]:
    """GHK-015: duplicate definitions (error), unused ones (warning), undefined or unverifiable (info)."""
    out: list[Finding] = []
    first: dict[tuple[str, str, str], StepDef] = {}
    for definition in defs:
        if definition.kind == "unverified":
            out.append(_find("GHK-015", "info", definition.file, definition.line,
                             "Este padrão de step não é um texto nem parsers.parse; não foi verificado.",
                             "Confira à mão se algum step do .feature usa esta definição."))
            continue
        key = (definition.type, definition.kind, definition.pattern)
        if key in first:
            other = first[key]
            out.append(_find("GHK-015", "error", definition.file, definition.line,
                             f"A definição de step {definition.pattern} existe duas vezes "
                             f"({other.file}:{other.line} e {definition.file}:{definition.line}).",
                             "Deixe uma só: a segunda esconde a primeira sem aviso."))
        else:
            first[key] = definition
    used: set[int] = set()
    unverified_types = {d.type for d in defs if d.kind == "unverified"}
    for fd in fds:
        if fd.intent is None:
            continue
        for ff in _parsed(fd):
            assert ff.feature is not None
            for step, scenario in _all_steps(ff.feature):
                hits = [i for i, d in enumerate(defs) if _matches(d, step, scenario)]
                used.update(hits)
                if not hits and "any" not in unverified_types and step.type not in unverified_types:
                    out.append(_find("GHK-015", "info", ff.path, step.line,
                                     "Este step ainda não tem definição. No teste-primeiro isto é normal.",
                                     "Escreva a definição junto do teste do cenário.",
                                     scenario.name if scenario else ""))
    for i, definition in enumerate(defs):
        if definition.kind != "unverified" and i not in used and first.get(
                (definition.type, definition.kind, definition.pattern)) is definition:
            out.append(_find("GHK-015", "warning", definition.file, definition.line,
                             f"A definição {definition.pattern} não casa com nenhum step.",
                             "Tire a definição ou escreva o step que a usa."))
    return sort_findings(out)


# ---------------------------------------------------------------------------
# Discovery (I/O) and CLI
# ---------------------------------------------------------------------------


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def load_dir(root: Path, folder: Path) -> FeatureDir:
    intent_file = folder / "intent.md"
    fd = FeatureDir(slug=folder.name, path=_rel(folder, root))
    if intent_file.is_file():
        fd.intent_path = _rel(intent_file, root)
        text = _read(intent_file)
        fd.intent = load_intent(text or "", folder.name)
    for feature_file in sorted(folder.glob("*.feature")):
        ff = FeatureFile(path=_rel(feature_file, root))
        text = _read(feature_file)
        if text is None:
            ff.error = ParseError(1, "Não consegui ler este arquivo como texto UTF-8.")
        else:
            try:
                ff.feature = parse_feature(text)
            except ParseError as err:
                ff.error = err
        fd.files.append(ff)
    return fd


def discover(root: Path, only: str | None = None) -> list[FeatureDir]:
    """Folders features/<slug>/ that have an intent.md or .feature files; anything else is left alone."""
    base = root / "features"
    if not base.is_dir():
        return []
    found = []
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        if only is not None and folder.name != only:
            continue
        if (folder / "intent.md").is_file() or any(folder.glob("*.feature")):
            found.append(load_dir(root, folder))
    return found


def load_step_defs(steps_dir: Path, root: Path) -> list[StepDef]:
    defs: list[StepDef] = []
    for source in sorted(steps_dir.rglob("*.py")):
        text = _read(source)
        if text is not None:
            defs += parse_step_defs(text, _rel(source, root))
    return defs


def validate(fds: list[FeatureDir], defs: list[StepDef] | None = None) -> list[Finding]:
    out: list[Finding] = []
    for fd in fds:
        out += validate_structure(fd) + validate_steps(fd)
    if defs is not None:
        out += validate_step_defs(fds, defs)
    return sort_findings(out)


_SEVERITY_WORDS = {"error": "erro", "warning": "aviso", "info": "info"}


def _plural(count: int, one: str, many: str) -> str:
    return f"{count} {one if count == 1 else many}"


def summarize(fds: list[FeatureDir], findings: list[Finding], matrix: dict) -> dict:
    """Counts shown in the final line and in the JSON summary."""
    scenarios = sum(len(ff.feature.scenarios) for fd in fds for ff in _parsed(fd) if ff.feature is not None)
    reqs = [info for data in matrix.values() for info in data["reqs"].values() if info["state"] == "ativo"]
    return {
        "errors": sum(1 for f in findings if f.severity == "error"),
        "warnings": sum(1 for f in findings if f.severity == "warning"),
        "infos": sum(1 for f in findings if f.severity == "info"),
        "reqs": len(reqs),
        "scenarios": scenarios,
        "uncovered_reqs": sum(1 for info in reqs if not info["scenarios"]),
    }


def _summary_line(summary: dict) -> str:
    return (
        f"{_plural(summary['errors'], 'erro', 'erros')}, "
        f"{_plural(summary['warnings'], 'aviso', 'avisos')}, "
        f"{_plural(summary['infos'], 'informação', 'informações')}; "
        f"{_plural(summary['reqs'], 'REQ', 'REQs')}, "
        f"{_plural(summary['scenarios'], 'cenário', 'cenários')}, "
        f"{summary['uncovered_reqs']} REQ sem cenário"
    )


def _group(path: str) -> str:
    parts = path.split("/")
    return parts[1] if parts[0] == "features" and len(parts) > 1 else parts[0]


def _print_text(findings: list[Finding], summary: dict, matrix: dict | None, quiet: bool) -> None:
    shown = [f for f in findings if not (quiet and f.severity == "info")]
    current = None
    for f in shown:
        group = _group(f.file)
        if group != current:
            print(f"[{group}]")
            current = group
        hint = f" Dica: {f.hint}" if f.hint else ""
        print(f"{f.file}:{f.line}: {f.rule} {_SEVERITY_WORDS[f.severity]}: {f.message}{hint}")
    if matrix is not None:
        for slug, data in matrix.items():
            aprovado = {True: "sim", False: "não", None: "não declarado"}[data["scenarios_approved"]]
            print(f"matriz {slug}: status {data['status']}, cenários aprovados: {aprovado}")
            for req, info in data["reqs"].items():
                print(f"  {req} ({info['state']}): {len(info['scenarios'])} cenário(s)")
                for entry in info["scenarios"]:
                    print(f"    {entry['key']} (linha {entry['line']})")
    print(_summary_line(summary))


def _report(root: Path, fds: list[FeatureDir], findings: list[Finding], matrix: dict, with_matrix: bool) -> dict:
    report = {
        "schema_version": SCHEMA_VERSION,
        "root": str(root),
        "summary": summarize(fds, findings, matrix),
        "findings": [f._asdict() for f in findings],
        "features": [
            {"slug": fd.slug, "status": fd.intent.status, "scenarios_approved": fd.intent.scenarios_approved}
            for fd in fds
            if fd.intent is not None
        ],
    }
    if with_matrix:
        report["matrix"] = matrix
    return report


def _run(args: argparse.Namespace) -> int:
    root = Path(args.root)
    if not root.is_dir():
        print(f"check_features: pasta não encontrada: {root}", file=sys.stderr)
        return 2
    if args.steps and not Path(args.steps).is_dir():
        print(f"check_features: pasta de definições não encontrada: {args.steps}", file=sys.stderr)
        return 2
    fds = discover(root, args.feature)
    if args.feature and not fds:
        print(f"check_features: não há features/{args.feature}/ neste projeto.", file=sys.stderr)
        return 2
    if not any(fd.intent is not None for fd in fds):
        if args.json:
            print(json.dumps(_report(root, [], [], {}, args.matrix), ensure_ascii=False, indent=2))
        else:
            print("check_features: nenhum features/<slug>/intent.md; nada a verificar.")
        return 0
    defs = load_step_defs(Path(args.steps), root) if args.steps else None
    findings = validate(fds, defs)
    matrix = build_matrix(fds)
    if args.json:
        print(json.dumps(_report(root, fds, findings, matrix, args.matrix), ensure_ascii=False, indent=2))
    else:
        _print_text(findings, summarize(fds, findings, matrix), matrix if args.matrix else None, args.quiet)
    has_error = any(f.severity == "error" for f in findings)
    has_warning = any(f.severity == "warning" for f in findings)
    return 1 if has_error or (args.strict and has_warning) else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate features/<slug>/*.feature (GHK-001 to GHK-019).")
    parser.add_argument("root", nargs="?", default=".", help="project root (default: current directory)")
    parser.add_argument("--feature", help="validate only features/<slug>/")
    parser.add_argument("--steps", help="folder with the step definitions (Python), read with ast")
    parser.add_argument("--json", action="store_true", help="one JSON object with schema_version")
    parser.add_argument("--matrix", action="store_true", help="also print the REQ -> scenarios matrix")
    parser.add_argument("--strict", action="store_true", help="warnings also fail (exit 1)")
    parser.add_argument("--quiet", action="store_true", help="hide informations")
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except Exception as exc:  # noqa: BLE001 -- never a raw traceback for the user
        print(f"check_features: erro interno ({type(exc).__name__}): {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
