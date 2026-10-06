"""Tests for check_features.py -- GHK-001 to GHK-019 over the golden fixtures.

Invocation: test
Lifecycle: active

Rules: .claude/references/general/gherkin-spec-format.md (GHK-NNN).
Fixtures: fixtures/features/<case>/ (esperado.json per case).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from check_features import (
    ParseError,
    build_matrix,
    discover,
    light_key,
    load_intent,
    load_step_defs,
    normalize_step,
    parse_feature,
    term_candidates,
    validate,
)

_TESTS_DIR = Path(__file__).resolve().parent
_FIXTURES = _TESTS_DIR / "fixtures" / "features"
_SPEC = _TESTS_DIR.parents[2] / "references" / "general" / "gherkin-spec-format.md"

STRUCTURE_RULES = {"GHK-001", "GHK-002", "GHK-003", "GHK-004", "GHK-005", "GHK-009", "GHK-010", "GHK-011",
                   "GHK-014", "GHK-016", "GHK-018", "GHK-019"}

CASES = sorted(p.name for p in _FIXTURES.iterdir() if p.is_dir())


def _expected(case: str) -> dict:
    return json.loads((_FIXTURES / case / "esperado.json").read_text(encoding="utf-8"))


def _findings(root: Path, rules: set[str], args: list[str] | None = None) -> list[list]:
    steps = None
    if args and "--steps" in args:
        steps = load_step_defs(Path(args[args.index("--steps") + 1].replace("{root}", str(root))), root)
    found = validate(discover(root), steps)
    return sorted([f.rule, f.severity, f.file, f.line] for f in found if f.rule in rules)


def _write(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


INTENT = """---
slug: login
status: {status}
---

## Requisitos

| REQ | Requisito | Critério |
|---|---|---|
| REQ-login-001 | Você entra. | Quando você entra, o sistema abre. |
| REQ-login-002 | Você sai. | Quando você sai, o sistema fecha. |
| REQ-login-003 | Você volta. | Quando você volta, o sistema lembra. |
"""

SCENARIO = """Feature: Entrar

  {tag}
  Scenario: Entrar
    Given o usuário tem uma conta
    When o usuário informa a senha
    Then o sistema abre a conta
"""


ALL_RULES = {f"GHK-{n:03d}" for n in range(1, 20)}

# ---------------------------------------------------------------------------
# Golden cases (all rules)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", CASES)
def test_structure_golden(case: str) -> None:
    expected = _expected(case)
    want = sorted(f for f in expected["findings"] if f[0] in STRUCTURE_RULES)
    assert _findings(_FIXTURES / case, STRUCTURE_RULES) == want


@pytest.mark.parametrize("case", CASES)
def test_steps_golden_all_rules(case: str) -> None:
    expected = _expected(case)
    got = _findings(_FIXTURES / case, ALL_RULES, expected["args"])
    assert got == sorted(expected["findings"])


def test_every_rule_has_a_golden_case() -> None:
    cited = {f[0] for case in CASES for f in _expected(case)["findings"]}
    documented = set(re.findall(r"^\| (GHK-\d{3}) \|", _SPEC.read_text(encoding="utf-8"), re.MULTILINE))
    assert documented and cited == documented


@pytest.mark.parametrize("case", [c for c in CASES if "matrix" in _expected(c)])
def test_matrix_golden(case: str) -> None:
    matrix = build_matrix(discover(_FIXTURES / case))
    got = {slug: {"scenarios_approved": data["scenarios_approved"],
                  "reqs": {req: len(info["scenarios"]) for req, info in data["reqs"].items()}}
           for slug, data in matrix.items()}
    assert got == _expected(case)["matrix"]


def test_sem_features_and_terceiros_are_not_validated() -> None:
    for case in ("sem-features", "features-de-terceiros"):
        assert discover(_FIXTURES / case) == []


def test_counts_that_feed_plan_000008() -> None:
    sem_tag = [f for f in _expected("ghk-002-sem-tag")["findings"] if f[0] == "GHK-002"]
    orfa = [f for f in _expected("ghk-004-orfa")["findings"] if f[0] == "GHK-004"]
    assert len(sem_tag) == 1 and len(orfa) == 1


# ---------------------------------------------------------------------------
# Unit tests of the plan (structure, matrix)
# ---------------------------------------------------------------------------


def test_scenario_without_tag_returns_ghk002_with_scenario_line(tmp_path: Path) -> None:
    text = SCENARIO.format(tag="")
    root = _write(tmp_path, {"features/login/intent.md": INTENT.format(status="approved"),
                             "features/login/a.feature": text})
    found = [f for f in validate(discover(root)) if f.rule == "GHK-002"]
    assert [(f.file, f.line) for f in found] == [("features/login/a.feature", 4)]


def test_tag_to_missing_req_returns_ghk004(tmp_path: Path) -> None:
    root = _write(tmp_path, {"features/login/intent.md": INTENT.format(status="approved"),
                             "features/login/a.feature": SCENARIO.format(tag="@REQ-login-009")})
    assert [f.rule for f in validate(discover(root)) if f.rule == "GHK-004"] == ["GHK-004"]


def test_req_without_scenario_is_error_when_approved_and_info_in_grilling(tmp_path: Path) -> None:
    feature = SCENARIO.format(tag="@REQ-login-001")
    for status, severity in (("approved", "error"), ("grilling", "info")):
        root = _write(tmp_path / status, {"features/login/intent.md": INTENT.format(status=status),
                                          "features/login/a.feature": feature})
        found = [f for f in validate(discover(root)) if f.rule == "GHK-005"]
        assert {f.severity for f in found} == {severity}
        assert len(found) == 2  # REQ 002 and 003


def test_feature_level_req_tag_returns_ghk003(tmp_path: Path) -> None:
    text = "@REQ-login-001\n" + SCENARIO.format(tag="@REQ-login-001")
    root = _write(tmp_path, {"features/login/intent.md": INTENT.format(status="approved"),
                             "features/login/a.feature": text})
    assert any(f.rule == "GHK-003" and f.line == 1 for f in validate(discover(root)))


def test_portuguese_file_parses_with_effective_types() -> None:
    feature = parse_feature(
        "# language: pt\nFuncionalidade: X\n\n  @REQ-x-001\n  Cenário: Y\n    Dado a\n    E b\n"
        "    Quando c\n    Então d\n    E e\n"
    )
    assert [s.type for s in feature.scenarios[0].steps] == ["given", "given", "when", "then", "then"]


def test_outline_placeholder_without_column_returns_ghk009(tmp_path: Path) -> None:
    text = """Feature: X

  @REQ-login-001
  Scenario Outline: Y
    Given o valor <x>
    When o usuário age
    Then o sistema responde

    Examples:
      | y |
      | 1 |
"""
    root = _write(tmp_path, {"features/login/intent.md": INTENT.format(status="approved"),
                             "features/login/a.feature": text})
    found = [f for f in validate(discover(root)) if f.rule == "GHK-009"]
    assert len(found) == 2  # <x> has no column, and column y is unused


def test_feature_folder_without_intent_returns_only_info(tmp_path: Path) -> None:
    root = _write(tmp_path, {"features/login/a.feature": SCENARIO.format(tag="")})
    found = validate(discover(root))
    assert [f.severity for f in found] == ["info"]


def test_same_files_give_identical_findings(tmp_path: Path) -> None:
    root = _write(tmp_path, {"features/login/intent.md": INTENT.format(status="approved"),
                             "features/login/a.feature": SCENARIO.format(tag="@REQ-login-009")})
    assert validate(discover(root)) == validate(discover(root))


def test_parse_error_carries_line_and_message() -> None:
    with pytest.raises(ParseError) as err:
        parse_feature("Feature: X\n\n  Given um passo solto\n")
    assert err.value.line == 3


def test_load_intent_reads_status_terms_serve_and_scenarios() -> None:
    text = INTENT.format(status="approved").replace(
        "status: approved\n", "status: approved\nscenarios: approved\nserve: [JM-TB-001, D-004]\n"
    ) + "\n## Modelo e termos\n\n| Termo | O que quer dizer | Fonte |\n|---|---|---|\n| conta | Algo. | F1 |\n"
    intent = load_intent(text, "login")
    assert (intent.status, intent.scenarios_approved, intent.serve, intent.terms) == (
        "approved", True, ["JM-TB-001", "D-004"], ["conta"])
    assert list(intent.reqs) == ["REQ-login-001", "REQ-login-002", "REQ-login-003"]


# ---------------------------------------------------------------------------
# Unit tests of the plan (steps and step definitions)
# ---------------------------------------------------------------------------


def _feature_root(tmp_path: Path, body: str, terms: str = "") -> Path:
    intent = INTENT.format(status="approved") + terms
    return _write(tmp_path, {"features/login/intent.md": intent, "features/login/a.feature": body})


def _rules(root: Path, rule: str, defs=None):
    return [f for f in validate(discover(root), defs) if f.rule == rule]


def test_repeated_step_in_a_scenario_returns_ghk006_on_the_second(tmp_path: Path) -> None:
    body = """Feature: X

  @REQ-login-001
  Scenario: Y
    Given o usuário está logado
    And o usuário está logado
    When o usuário age
    Then o sistema responde
"""
    found = _rules(_feature_root(tmp_path, body), "GHK-006")
    assert [f.line for f in found] == [6]


def test_same_text_as_given_and_then_returns_ghk007(tmp_path: Path) -> None:
    body = """Feature: X

  @REQ-login-001
  Scenario: Y
    Given o saldo é 10
    When o usuário age
    Then o saldo é 10
"""
    assert [f.line for f in _rules(_feature_root(tmp_path, body), "GHK-007")] == [7]


def test_steps_that_differ_only_by_case_or_punctuation_are_a_warning(tmp_path: Path) -> None:
    body = """Feature: X

  @REQ-login-001
  Scenario: Y
    Given o usuário está logado
    When o usuário age
    Then o sistema responde

  @REQ-login-002
  Scenario: Z
    Given O usuário está logado!
    When o usuário age
    Then o sistema responde
"""
    found = _rules(_feature_root(tmp_path, body), "GHK-008")
    assert [(f.severity, f.line) for f in found] == [("warning", 11)]


def test_when_then_when_returns_ghk012_as_warning(tmp_path: Path) -> None:
    body = """Feature: X

  @REQ-login-001
  Scenario: Y
    Given o usuário está logado
    When o usuário age
    Then o sistema responde
    When o usuário age de novo
    Then o sistema responde de novo
"""
    found = _rules(_feature_root(tmp_path, body), "GHK-012")
    assert [(f.severity, f.line) for f in found] == [("warning", 8)]


@pytest.mark.parametrize("step", ["abre https://exemplo.test/x", "roda SELECT * FROM contas", "clica em #entrar"])
def test_implementation_detail_returns_ghk013_as_warning(tmp_path: Path, step: str) -> None:
    body = f"Feature: X\n\n  @REQ-login-001\n  Scenario: Y\n    Given o usuário {step}\n"
    found = _rules(_feature_root(tmp_path, body), "GHK-013")
    assert [f.severity for f in found] == ["warning"]


def test_normalization_and_candidates() -> None:
    assert normalize_step('O saldo é "10".') == normalize_step("o saldo é 20")
    assert light_key("  Um  Passo ") == "um passo"
    assert term_candidates('o usuário abre a Fatura e vê "Premium" e "1 conta"') == ["Premium", "Fatura"]


def test_term_missing_from_model_returns_ghk017_and_present_term_does_not(tmp_path: Path) -> None:
    body = """Feature: X

  @REQ-login-001
  Scenario: Y
    Given o usuário tem uma conta
    When o usuário abre a Fatura
    Then o sistema mostra "Conta"
"""
    terms = "\n## Modelo e termos\n\n| Termo | O que quer dizer | Fonte |\n|---|---|---|\n| conta | Algo. | F1 |\n"
    found = _rules(_feature_root(tmp_path, body, terms), "GHK-017")
    assert [(f.severity, f.line) for f in found] == [("warning", 6)]


def test_duplicate_step_definitions_return_ghk015_error_with_both_places(tmp_path: Path) -> None:
    root = _feature_root(tmp_path, SCENARIO.format(tag="@REQ-login-001"))
    (root / "steps").mkdir()
    (root / "steps" / "a.py").write_text('from pytest_bdd import given\n\n@given("um usuário")\ndef a(): pass\n')
    (root / "steps" / "b.py").write_text('from pytest_bdd import given\n\n@given("um usuário")\ndef b(): pass\n')
    found = _rules(root, "GHK-015", load_step_defs(root / "steps", root))
    errors = [f for f in found if f.severity == "error"]
    assert len(errors) == 1 and "steps/a.py:3" in errors[0].message and "steps/b.py:3" in errors[0].message


def test_empty_steps_dir_gives_only_info_and_no_error(tmp_path: Path) -> None:
    root = _feature_root(tmp_path, SCENARIO.format(tag="@REQ-login-001"))
    (root / "steps").mkdir()
    found = _rules(root, "GHK-015", load_step_defs(root / "steps", root))
    assert found and {f.severity for f in found} == {"info"}


def test_re_definition_is_not_verified_and_does_not_fail(tmp_path: Path) -> None:
    root = _feature_root(tmp_path, SCENARIO.format(tag="@REQ-login-001"))
    (root / "steps").mkdir()
    (root / "steps" / "a.py").write_text(
        'import re\nfrom pytest_bdd import given, parsers\n\n@given(parsers.re(r"um .+"))\ndef a(): pass\n')
    found = _rules(root, "GHK-015", load_step_defs(root / "steps", root))
    assert any("não foi verificado" in f.message for f in found)
    assert all(f.severity != "error" for f in found)
