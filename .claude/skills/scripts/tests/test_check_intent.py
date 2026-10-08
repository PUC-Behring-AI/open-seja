"""Tests for check_intent.py -- the grill stop rule (P1 to P6) and the D0 index.

Invocation: test
Lifecycle: active

Rules: .claude/references/general/grill-phase.md (GRL-006, GRL-010, GRL-015).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from check_intent import Finding, brief_residue, check_intent

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
_SCRIPT = _SCRIPTS_DIR / "check_intent.py"
_TEMPLATE = _SCRIPTS_DIR.parent.parent / "references" / "template" / "intent.md"

VALID = _TEMPLATE.read_text(encoding="utf-8")

REQ1_CRIT = (
    "Quando você abre a tela inicial, o sistema mostra as contas que vencem "
    "nos próximos 7 dias."
)

MINIMAL_000007 = """---
slug: task-list
status: approved
---

# Lista de tarefas

## Nas suas palavras

"Quero anotar o que preciso fazer e riscar o que já fiz."

## Requisitos

| REQ | Texto | Critério |
|---|---|---|
| REQ-task-list-001 | Eu posso acrescentar uma tarefa à lista. | Depois de acrescentar, a tarefa aparece na lista. |
| REQ-task-list-002 | Eu posso marcar uma tarefa como feita. | Uma tarefa marcada continua na lista e aparece como feita. |

## Fora do escopo

- Prazos e lembretes.

## Premissas

- Há uma única lista por usuário.
"""


def _errors(findings: list[Finding], rule: str | None = None) -> list[Finding]:
    return [
        f for f in findings
        if f.severidade == "error" and (rule is None or f.regra == rule)
    ]


def _line_of(text: str, needle: str) -> int:
    for i, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return i
    raise AssertionError(needle)


# --- the valid model --------------------------------------------------------


def test_template_passes_with_require_approved():
    assert _errors(check_intent(VALID, require_approved=True)) == []


def test_minimal_000007_schema_passes_without_require_approved():
    assert _errors(check_intent(MINIMAL_000007)) == []


def test_minimal_000007_schema_fails_with_require_approved():
    findings = check_intent(MINIMAL_000007, require_approved=True)
    rules = {f.regra for f in _errors(findings)}
    assert {"P1", "P6"} <= rules


# --- P2 criterion -----------------------------------------------------------


def test_req_without_criterion_is_p2_error_on_req_line():
    text = VALID.replace(REQ1_CRIT, "")
    errs = _errors(check_intent(text), "P2")
    assert errs
    assert errs[0].linha == _line_of(text, "REQ-contas-da-semana-001 |")


def test_vague_word_without_number_is_p2_error():
    text = VALID.replace(
        REQ1_CRIT, "Quando você abre a tela inicial, o sistema deve ser rápido."
    )
    errs = _errors(check_intent(text), "P2")
    assert any("rápido" in f.mensagem for f in errs)


def test_criterion_without_when_form_is_p2_error():
    text = VALID.replace(REQ1_CRIT, "O sistema deve ser rápido.")
    assert _errors(check_intent(text), "P2")


def test_vague_word_with_number_passes():
    text = VALID.replace(
        REQ1_CRIT,
        "Quando você abre a tela inicial, o sistema responde rápido, em até 2 segundos.",
    )
    assert _errors(check_intent(text), "P2") == []


def test_english_when_form_passes():
    text = VALID.replace(
        REQ1_CRIT, "When you open the home screen, the system shows the bills due in 7 days."
    )
    assert _errors(check_intent(text), "P2") == []


# --- P1 dimensions ----------------------------------------------------------


def test_empty_dimension_is_p1_error_naming_it():
    text = VALID.replace("| gatilho | A pessoa abre o aplicativo. | A3 |", "| gatilho |  | A3 |")
    errs = _errors(check_intent(text), "P1")
    assert errs and "gatilho" in errs[0].mensagem


def test_missing_dimension_row_is_p1_error():
    text = VALID.replace("| gatilho | A pessoa abre o aplicativo. | A3 |\n", "")
    errs = _errors(check_intent(text), "P1")
    assert errs and "gatilho" in errs[0].mensagem


def test_out_of_scope_with_reason_is_not_p1():
    text = VALID.replace(
        "| gatilho | A pessoa abre o aplicativo. | A3 |",
        "| gatilho | fora do escopo: a lista só existe quando abre | A3 |",
    )
    assert _errors(check_intent(text), "P1") == []


def test_out_of_scope_without_reason_is_p1_error():
    text = VALID.replace(
        "| gatilho | A pessoa abre o aplicativo. | A3 |", "| gatilho | fora do escopo: | A3 |"
    )
    assert _errors(check_intent(text), "P1")


# --- P3 open questions and assumptions -------------------------------------


def test_open_question_is_p3_error_and_require_approved_fails(tmp_path):
    text = VALID.replace("- nenhuma", "- A lista mostra contas atrasadas?")
    assert _errors(check_intent(text), "P3")
    path = tmp_path / "intent.md"
    path.write_text(text, encoding="utf-8")
    proc = _run(str(path), "--require-approved", "--strict")
    assert proc.returncode == 1


def test_unconfirmed_assumption_is_p3_error():
    text = VALID.replace("| A2 | sim |", "| A2 | não |")
    assert _errors(check_intent(text), "P3")


# --- P4 ids -----------------------------------------------------------------


def test_duplicate_id_is_p4_error():
    text = VALID.replace("REQ-contas-da-semana-002", "REQ-contas-da-semana-001")
    assert _errors(check_intent(text), "P4")


def test_slug_mismatch_is_p4_error():
    text = VALID.replace("REQ-contas-da-semana-003", "REQ-outra-coisa-003")
    errs = _errors(check_intent(text), "P4")
    assert any("outra-coisa" in f.mensagem for f in errs)


def test_gap_in_numbering_is_p4_error():
    text = VALID.replace("REQ-contas-da-semana-003", "REQ-contas-da-semana-004")
    assert _errors(check_intent(text), "P4")


def test_retired_req_counts_as_used_and_passes():
    text = VALID.replace("| 1 | ativo |\n| REQ-contas-da-semana-002", "| 1 | retirado |\n| REQ-contas-da-semana-002")
    text = text.replace(
        "| Data | REQ | O que mudou | rev |\n|---|---|---|---|\n",
        "| Data | REQ | O que mudou | rev |\n|---|---|---|---|\n"
        "| 2026-10-07 | REQ-contas-da-semana-001 | retirado a pedido | 1 |\n",
    )
    assert _errors(check_intent(text), "P4") == []


def test_rev_above_one_without_change_row_is_p4_error():
    text = VALID.replace("| 1 | ativo |\n| REQ-contas-da-semana-002", "| 2 | ativo |\n| REQ-contas-da-semana-002")
    errs = _errors(check_intent(text), "P4")
    assert any("Mudanças" in f.mensagem for f in errs)


# --- P5 origin --------------------------------------------------------------


def test_req_without_origin_is_p5_error():
    text = VALID.replace("| comportamento | F2, A5 |", "| comportamento |  |")
    assert _errors(check_intent(text), "P5")


def test_req_citing_missing_index_is_p5_error():
    text = VALID.replace("| comportamento | F2, A5 |", "| comportamento | F9 |")
    assert _errors(check_intent(text), "P5")


def test_derived_from_existing_req_passes():
    text = VALID.replace("| restrição | F5, A4 |", "| restrição | derivado de: REQ-contas-da-semana-001 |")
    assert _errors(check_intent(text), "P5") == []


# --- P6 approval ------------------------------------------------------------


def test_approved_without_approved_by_is_p6_error():
    text = VALID.replace("approved_by: usuario\n", "")
    assert _errors(check_intent(text), "P6")


def test_grilling_fails_only_with_require_approved():
    text = VALID.replace("status: approved", "status: grilling")
    assert _errors(check_intent(text)) == []
    assert _errors(check_intent(text, require_approved=True), "P6")


# --- voice ------------------------------------------------------------------


def test_requirement_sentence_of_26_words_is_voice_warning():
    long = " ".join(["palavra"] * 25) + " final."
    text = VALID.replace("Você vê as contas que vencem nos próximos 7 dias.", long)
    findings = check_intent(text)
    assert any(f.regra == "VOZ" and f.severidade == "warning" for f in findings)
    assert _errors(findings) == []


def test_verbatim_quote_of_40_words_is_ignored():
    quote = " ".join(["palavra"] * 40)
    text = VALID.replace("Quero ver as contas que vencem nesta semana.", quote)
    assert [f for f in check_intent(text) if f.regra == "VOZ"] == []


def test_more_than_six_sentences_in_a_cell_is_voice_warning():
    many = " ".join(["Frase curta."] * 7)
    text = VALID.replace("Você não paga a mesma conta duas vezes.", many)
    assert any(f.regra == "VOZ" for f in check_intent(text))


# --- determinism and CLI ----------------------------------------------------


def test_same_text_gives_identical_output():
    text = VALID.replace("- nenhuma", "- Uma pergunta?").replace("approved_by: usuario\n", "")
    assert check_intent(text) == check_intent(text)


def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_SCRIPT), *args],
        capture_output=True, text=True, cwd=cwd, check=False,
    )


def test_strict_exit_codes(tmp_path):
    good = tmp_path / "good.md"
    good.write_text(VALID, encoding="utf-8")
    bad = tmp_path / "bad.md"
    bad.write_text(VALID.replace(REQ1_CRIT, ""), encoding="utf-8")
    assert _run(str(good), "--require-approved", "--strict").returncode == 0
    assert _run(str(bad), "--strict").returncode == 1
    assert _run(str(bad)).returncode == 0


def test_missing_file_is_usage_error(tmp_path):
    assert _run(str(tmp_path / "absent.md")).returncode == 2


def test_json_output_has_schema_and_voice_caveat(tmp_path):
    good = tmp_path / "good.md"
    good.write_text(VALID, encoding="utf-8")
    data = json.loads(_run(str(good), "--json").stdout)
    assert data["schema_version"] == 1
    assert data["findings"] == []
    assert any("voz: não verificada" in r for r in data["ressalvas"])


def test_scan_mode_without_features_dir_passes(tmp_path):
    proc = _run(cwd=tmp_path)
    assert proc.returncode == 0


def test_scan_mode_fails_on_incomplete_approved_intent(tmp_path):
    feat = tmp_path / "features" / "contas-da-semana"
    feat.mkdir(parents=True)
    (feat / "intent.md").write_text(VALID.replace(REQ1_CRIT, ""), encoding="utf-8")
    assert _run(cwd=tmp_path).returncode == 1


def test_scan_mode_tolerates_grilling_intent(tmp_path):
    feat = tmp_path / "features" / "contas-da-semana"
    feat.mkdir(parents=True)
    text = VALID.replace(REQ1_CRIT, "").replace("status: approved", "status: grilling")
    (feat / "intent.md").write_text(text, encoding="utf-8")
    assert _run(cwd=tmp_path).returncode == 0


# --- size and D0 ------------------------------------------------------------


def test_more_than_twelve_reqs_is_warning():
    row = VALID.splitlines()[_line_of(VALID, "REQ-contas-da-semana-001 |") - 1]
    extra = "\n".join(
        row.replace("-001", f"-{n:03d}") for n in range(4, 14)
    )
    text = VALID.replace(row, row + "\n" + extra)
    findings = check_intent(text)
    assert any(f.regra == "TAMANHO" and f.severidade == "warning" for f in findings)


def test_d0_empty_for_template():
    d0 = brief_residue(VALID)
    assert d0 == {"estado": "medido", "frases": 5, "residuo": []}


def test_d0_lists_sentence_without_req_or_out_of_scope():
    text = VALID.replace("- Aviso no celular antes do vencimento (F3).", "- Aviso no celular antes do vencimento.")
    assert brief_residue(text)["residuo"] == [{"frase": "F3", "nota": ""}]


def test_d0_marks_sentence_only_in_assumption():
    text = VALID.replace("- Aviso no celular antes do vencimento (F3).", "- Aviso no celular antes do vencimento.")
    text = text.replace("| A2 | sim |", "| A2, F3 | sim |")
    assert brief_residue(text)["residuo"] == [{"frase": "F3", "nota": "só em premissa"}]


def test_d0_without_index_is_not_measured():
    d0 = brief_residue(MINIMAL_000007)
    assert d0 == {"estado": "nao_medido", "razao_nm": ["NM-SEM-INDICE-BRIEF"]}


@pytest.mark.parametrize("flag", ["--d0"])
def test_d0_cli_prints_json(tmp_path, flag):
    good = tmp_path / "good.md"
    good.write_text(VALID, encoding="utf-8")
    data = json.loads(_run(str(good), flag).stdout)
    assert data["d0"]["estado"] == "medido"


# --- reference interviews (Step 6 fixtures; simulated) ----------------------

_GRILL = Path(__file__).resolve().parent / "fixtures" / "grill"
_EXPECTED = json.loads((_GRILL / "esperado.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", sorted(_EXPECTED["intent"]))
def test_fixture_errors_match_expected_rules(name):
    text = (_GRILL / name).read_text(encoding="utf-8")
    rules = sorted({f.regra for f in _errors(check_intent(text, require_approved=True))})
    assert rules == _EXPECTED["intent"][name]["erros"]


@pytest.mark.parametrize("name", sorted(_EXPECTED["intent"]))
def test_fixture_d0_matches_expected(name):
    residue = brief_residue((_GRILL / name).read_text(encoding="utf-8"))["residuo"]
    assert [r["frase"] for r in residue] == _EXPECTED["intent"][name]["d0"]


@pytest.mark.parametrize("name", sorted(_EXPECTED["intent"]))
def test_fixture_strict_exit_code(name):
    expected = 1 if _EXPECTED["intent"][name]["erros"] else 0
    proc = _run(str(_GRILL / name), "--require-approved", "--strict")
    assert proc.returncode == expected


def test_fixture_task_without_code_has_short_intent_and_skip_line():
    text = (_GRILL / _EXPECTED["sem_codigo"]).read_text(encoding="utf-8")
    assert "\nSpecify: skipped -- " in text
    section = text.split("## Intenção\n", 1)[1].split("\n\n", 1)[0].splitlines()
    labels = [line.split(":", 1)[0] for line in section]
    assert labels == ["- Objetivo", "- O que você vê no fim", "- Não faz", "- Pronto quando"]
    assert not list((_GRILL / "b-tarefa-sem-codigo").glob("intent*.md"))


# --- review fixes (plan 000009) ---------------------------------------------


def test_bom_utf8_frontmatter_is_read(tmp_path):
    path = tmp_path / "bom.md"
    path.write_bytes(b"\xef\xbb\xbf" + VALID.encode("utf-8"))
    proc = _run(str(path), "--require-approved", "--strict")
    assert proc.returncode == 0, proc.stdout
    assert "slug" not in proc.stdout


def test_undecodable_file_is_exit_2_in_single_file_mode(tmp_path):
    path = tmp_path / "bad.md"
    path.write_bytes(b"---\nslug: \xff\xfe\n---\n")
    proc = _run(str(path))
    assert proc.returncode == 2
    assert "Traceback" not in proc.stderr


def test_scan_continues_after_unreadable_file(tmp_path):
    for name, data in (("a-bad", b"\xff\xfe\x00"), ("b-good", VALID.encode("utf-8"))):
        feat = tmp_path / "features" / name
        feat.mkdir(parents=True)
        (feat / "intent.md").write_bytes(data)
    proc = _run(cwd=tmp_path)
    assert proc.returncode == 2
    assert "Traceback" not in proc.stderr
    assert "a-bad" in proc.stdout + proc.stderr
    assert "b-good" in proc.stdout


def test_split_row_keeps_escaped_and_backticked_pipes():
    from check_intent import _split_row

    assert _split_row(r"| a \| b | `c|d` | e |") == [r"a \| b", "`c|d`", "e"]


def test_fenced_heading_does_not_open_section():
    from check_intent import parse

    text = "---\nslug: x\nstatus: grilling\n---\n\n## Requisitos\n\n```\n## Premissas\n```\n"
    doc = parse(text)
    assert "premissas" not in doc.sections
    text = text.replace("```", "~~~")
    assert "premissas" not in parse(text).sections


def test_d0_without_path_is_usage_error(tmp_path):
    proc = _run("--d0", cwd=tmp_path)
    assert proc.returncode == 2
    assert "--d0" in proc.stderr


@pytest.mark.parametrize("flag", ["--strict", "--require-approved"])
def test_d0_with_strict_or_require_is_usage_error(tmp_path, flag):
    path = tmp_path / "i.md"
    path.write_text(VALID, encoding="utf-8")
    assert _run(str(path), "--d0", flag).returncode == 2


def test_require_approved_demands_change_row_in_minimal_file():
    text = (
        "---\nslug: t\nstatus: approved\n---\n\n## Requisitos\n\n"
        "| REQ | Texto | Critério | rev |\n|---|---|---|---|\n"
        "| REQ-t-001 | Texto. | Quando eu abro, o sistema mostra 3 itens. | 2 |\n"
    )
    assert any("Mudanças" in f.mensagem for f in _errors(check_intent(text, require_approved=True), "P4"))
    assert not any("Mudanças" in f.mensagem for f in _errors(check_intent(text), "P4"))
