"""Seam test: the end of a v2 plan in /implement freezes M1 (CYC-031, emenda 000015).

Invocation: test
Lifecycle: active

The orchestrator is scripted (as in the plan-000013 rehearsal): it follows the
section "Congelar o M1 (emenda 000015)" of implement-test-first.md, reads the
command from that section, and treats the result as the table there says. The
command runs the real drift_report.py over a copy of a fixture project.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from check_plan_scenarios import parse_header

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPTS = _TESTS_DIR.parent
_NORM = _TESTS_DIR.parents[2] / "references" / "general" / "implement-test-first.md"
_FIX = _TESTS_DIR / "fixtures" / "drift_report"
SLUG = "contas-da-semana"
AT = "2026-10-06T18:00:00Z"


def _command_template() -> str:
    text = _NORM.read_text(encoding="utf-8")
    section = text.split("## Congelar o M1 (emenda 000015)", 1)[1].split("\n## ", 1)[0]
    block = re.search(r"```bash\n(.+?)\n```", section, re.DOTALL)
    assert block, "a seção do M1 perdeu o bloco do comando"
    return block.group(1).strip()


def freeze_m1(root: Path, plan: Path, scripts: Path = _SCRIPTS) -> tuple[str, str]:
    """What the /implement does at the end of the plan. Returns (outcome, message); never raises."""
    header = parse_header(plan.read_text(encoding="utf-8"))
    specify = header.specifies[0][1] if header.specifies else ""
    if header.version != "2" or not header.features or not specify.startswith("approved"):
        return "skipped", "plano sem M1 (v1, sem Feature: ou Specify: skipped)"
    slug = header.features[0][1]
    script = scripts / "drift_report.py"
    if not script.is_file():
        return "warned", "não congelei o M1: drift_report.py não encontrado"
    cmd = (_command_template().replace("python ", f"{sys.executable} ", 1)
           .replace(".claude/skills/scripts/drift_report.py", str(script))
           .replace("<slug>", slug).replace("<plano>", str(plan)).replace("<UTC>", AT))
    run = subprocess.run(cmd.split(), cwd=root, capture_output=True, text=True, timeout=60, check=False)
    if run.returncode == 0 and "Congelei M1" in run.stdout:
        return "frozen", f"- m1: features/{slug}/drift/M1.json"
    if run.returncode == 0:
        return "skipped", run.stdout.strip()
    first = (run.stderr.strip().splitlines() or ["?"])[0]
    if "já foi congelado" in first:
        return "warned", "M1 já congelado; não sobrescrevo"
    return "warned", f"não congelei o M1: {first}"


def _project(case: str, tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / case
    shutil.copytree(_FIX / case, root)
    return root, root / "plan.md"


def test_norm_command_is_the_freeze_of_m1() -> None:
    cmd = _command_template()
    assert cmd.startswith("python .claude/skills/scripts/drift_report.py ")
    for part in ("--feature <slug>", "--plan <plano>", "--moment M1", "--freeze", "--at <UTC>"):
        assert part in cmd


def test_v2_plan_with_feature_creates_m1_with_input_hashes(tmp_path: Path) -> None:
    root, plan = _project("ok-m1", tmp_path)
    m1 = root / "features" / SLUG / "drift" / "M1.json"
    assert not m1.exists()
    outcome, message = freeze_m1(root, plan)
    assert (outcome, message) == ("frozen", f"- m1: features/{SLUG}/drift/M1.json")
    data = json.loads(m1.read_text(encoding="utf-8"))
    assert (data["momento"], data["at"], data["feature"]) == ("M1", AT, SLUG)
    assert data["entradas"] and all(re.fullmatch(r"[0-9a-f]{64}", h) for h in data["entradas"].values())


def test_second_freeze_warns_and_keeps_m1_byte_for_byte(tmp_path: Path) -> None:
    root, plan = _project("ok-m1", tmp_path)
    assert freeze_m1(root, plan)[0] == "frozen"
    m1 = root / "features" / SLUG / "drift" / "M1.json"
    before = m1.read_bytes()
    assert freeze_m1(root, plan) == ("warned", "M1 já congelado; não sobrescrevo")
    assert m1.read_bytes() == before


def test_v1_plan_creates_nothing_in_drift(tmp_path: Path) -> None:
    root, _ = _project("ok-m1", tmp_path)
    v1 = root / "plan-v1.md"
    shutil.copy(_FIX / "plano-v1" / "plan.md", v1)
    drift = root / "features" / SLUG / "drift"
    before = sorted(p.name for p in drift.iterdir())
    assert freeze_m1(root, v1)[0] == "skipped"
    assert sorted(p.name for p in drift.iterdir()) == before


def test_without_drift_report_the_flow_ends_with_a_warning(tmp_path: Path) -> None:
    root, plan = _project("ok-m1", tmp_path)
    outcome, message = freeze_m1(root, plan, scripts=tmp_path / "sem-scripts")
    assert outcome == "warned" and "não congelei o M1" in message
    assert not (root / "features" / SLUG / "drift" / "M1.json").exists()


def test_plan_specify_skipped_freezes_nothing(tmp_path: Path) -> None:
    root, plan = _project("ok-m1", tmp_path)
    text = plan.read_text(encoding="utf-8").replace("Feature: contas-da-semana\n", "")
    text = text.replace("Specify: approved (rev 1)", "Specify: skipped -- tarefa sem código de comportamento")
    plan.write_text(text, encoding="utf-8")
    assert freeze_m1(root, plan)[0] == "skipped"
    assert not (root / "features" / SLUG / "drift" / "M1.json").exists()
