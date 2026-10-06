"""Tests for build_brief.py (implement-test-first.md, ITF-012 and ITF-013).

Invocation: test
Lifecycle: active
"""

from __future__ import annotations

import json
from pathlib import Path

import build_brief as bb
import pytest

# Contract written before the code (plan-000013 step 3); removed when the module goes green (steps 4-6).
pytestmark = pytest.mark.xfail(reason="plan-000013 step 3: contrato antes do codigo", strict=False)


_TESTS = Path(__file__).resolve().parent
_FX = _TESTS / "fixtures" / "build"
_PLAN = (_TESTS / "fixtures" / "plan_scenarios" / "v2-completo" / "plan.md").read_text(encoding="utf-8")
_ROOT = _TESTS / "fixtures" / "plan_scenarios" / "_raizes" / "aprovada"
_STEPS = _FX / "project" / "tests"
_SRC = _FX / "project"
OTHER_STEPS = ("Criar a tabela de contas", "Marcar e desfazer o pagamento", "Manter a lista rápida", "Refatorar o módulo de datas")


def _tool(name: str) -> dict:
    return json.loads((_FX / "brief" / name).read_text(encoding="utf-8"))


def _brief(role: str, **kw) -> dict:
    kw.setdefault("root", _ROOT)
    kw.setdefault("feature", "contas-da-semana")
    return bb.build_brief(role, _PLAN, 2, **kw)


def test_tester_sees_the_owned_gherkin_and_the_step_index() -> None:
    brief = _brief("tester", steps_dir=_STEPS)
    text = brief["text"]
    assert "Ver as contas que vencem nos próximos 7 dias" in text
    assert "Listar as contas da semana" in text
    assert "que a lista de tarefas está vazia" in text  # index of existing step definitions
    assert "esqueleto" in text.lower()
    for title in OTHER_STEPS:
        assert title not in text
    assert "Marcar uma conta como paga" not in text  # scenario of another step


def test_tester_does_not_see_code_bodies() -> None:
    text = _brief("tester", steps_dir=_STEPS, source_root=_SRC)["text"]
    assert "self.tasks[title] = done" not in text


def test_coder_sees_the_red_check_message_and_the_frozen_files() -> None:
    text = _brief("coder", tool_output=_tool("red-check-output.json"))["text"]
    assert "O teste falhou no passo Então" in text
    assert "tests/steps_defs.py" in text and "features/task-list/manage-tasks.feature" in text
    assert "pragma" not in text and "CRAP" not in text  # no rule of the other roles
    for title in OTHER_STEPS:
        assert title not in text


def test_cleaner_sees_only_crap_and_function_bodies() -> None:
    text = _brief("cleaner", tool_output=_tool("crap-output.json"), source_root=_SRC)["text"]
    assert "CRAP(src/tasks.py::TaskList.mark_done)=26.4 (CC=26, cov=0.92) > 8" in text
    assert "def mark_done(self, title):" in text
    assert "Scenarios" not in text and "Cenário" not in text and "Ver as contas" not in text
    assert "Listar as contas da semana" not in text
    for title in OTHER_STEPS:
        assert title not in text


def test_hardener_sees_survivors_and_the_pragma_rule() -> None:
    text = _brief("hardener", tool_output=_tool("survivors-output.json"), source_root=_SRC)["text"]
    assert "mark_done__mutmut_2" in text and "self.tasks[title] = False" in text
    assert "# pragma: no mutate  # equivalent:" in text
    assert "pergunta" in text.lower()
    assert "Ver as contas" not in text


def test_manifest_lists_sizes() -> None:
    brief = _brief("tester", steps_dir=_STEPS)
    assert brief["manifest"] and all(isinstance(m["chars"], int) and m["chars"] > 0 for m in brief["manifest"])
    assert brief["truncated"] is False
    assert sum(m["chars"] for m in brief["manifest"] if m["included"]) <= len(brief["text"])


def test_cap_cuts_optional_context_and_keeps_the_scope_rule() -> None:
    brief = _brief("tester", steps_dir=_STEPS, max_chars=900)
    assert brief["truncated"] is True
    assert "Escopo" in brief["text"]
    assert any(not m["included"] for m in brief["manifest"])


def test_unknown_role_is_a_usage_error() -> None:
    with pytest.raises(ValueError):
        bb.build_brief("architect", _PLAN, 2)
    assert bb.main(["--role", "architect", "--plan", "x.md", "--step", "1"]) == 2


def test_cli_writes_the_brief(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    plan = tmp_path / "plan-000900-x.md"
    plan.write_text(_PLAN, encoding="utf-8")
    code = bb.main(["--role", "tester", "--plan", str(plan), "--step", "2", "--feature", "contas-da-semana",
                    "--root", str(_ROOT), "--out-dir", str(tmp_path / "out"), "--json"])
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert Path(out["path"]).is_file() and out["schema_version"] == 1
    assert Path(out["path"]).name == "brief-plan-000900-step-2-tester.md"


def test_cli_missing_plan_is_exit_2(tmp_path: Path) -> None:
    assert bb.main(["--role", "coder", "--plan", str(tmp_path / "none.md"), "--step", "1"]) == 2
