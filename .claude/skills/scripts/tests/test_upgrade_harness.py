"""Tests for upgrade_harness.

Covers:
- _regenerate_reference_files (plan-000291)
- .seja-version read/write pin path (plan-000380)
"""
from __future__ import annotations

import stat
import sys
from pathlib import Path

import pytest

import upgrade_harness


def _make_scripts_dir(target: Path) -> Path:
    scripts_dir = target / ".claude" / "skills" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    return scripts_dir


def _write_generator(scripts_dir: Path, name: str, body: str) -> Path:
    script = scripts_dir / name
    script.write_text(body, encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


def _sentinel_generator_body(sentinel_rel_path: str) -> str:
    return (
        "import sys\n"
        "from pathlib import Path\n"
        "sentinel = Path.cwd() / r'" + sentinel_rel_path + "'\n"
        "sentinel.parent.mkdir(parents=True, exist_ok=True)\n"
        "sentinel.write_text('generated', encoding='utf-8')\n"
        "sys.exit(0)\n"
    )


def test_regenerate_reference_files_invokes_present_generators(tmp_path, capsys):
    scripts_dir = _make_scripts_dir(tmp_path)
    _write_generator(scripts_dir, "generate_harness_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/harness-reference.md"))
    _write_generator(scripts_dir, "generate_skills_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/skills.md"))
    _write_generator(scripts_dir, "generate_perspectives_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/perspectives.md"))

    report: list[str] = []
    upgrade_harness._regenerate_reference_files(tmp_path, dry_run=False, report_updated=report)

    assert (tmp_path / "seja-public/docs/reference/harness-reference.md").is_file()
    assert (tmp_path / "seja-public/docs/reference/skills.md").is_file()
    assert (tmp_path / "seja-public/docs/reference/perspectives.md").is_file()
    assert len(report) == 3
    assert all("Regenerated" in line for line in report)


def test_regenerate_reference_files_skips_missing_generators(tmp_path, capsys):
    scripts_dir = _make_scripts_dir(tmp_path)
    _write_generator(scripts_dir, "generate_harness_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/harness-reference.md"))
    # skills + perspectives generators intentionally missing

    report: list[str] = []
    upgrade_harness._regenerate_reference_files(tmp_path, dry_run=False, report_updated=report)

    captured = capsys.readouterr()
    assert "Skipped skills reference" in captured.out
    assert "Skipped perspectives reference" in captured.out
    assert len(report) == 1
    assert "harness-reference" in report[0]


def test_regenerate_reference_files_dry_run_logs_without_executing(tmp_path, capsys):
    scripts_dir = _make_scripts_dir(tmp_path)
    _write_generator(scripts_dir, "generate_harness_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/harness-reference.md"))
    _write_generator(scripts_dir, "generate_skills_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/skills.md"))
    _write_generator(scripts_dir, "generate_perspectives_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/perspectives.md"))

    report: list[str] = []
    upgrade_harness._regenerate_reference_files(tmp_path, dry_run=True, report_updated=report)

    assert not (tmp_path / "seja-public/docs/reference/harness-reference.md").exists()
    assert not (tmp_path / "seja-public/docs/reference/skills.md").exists()
    assert not (tmp_path / "seja-public/docs/reference/perspectives.md").exists()
    assert report == []
    captured = capsys.readouterr()
    assert captured.out.count("Would regenerate") == 3


def test_regenerate_reference_files_continues_on_generator_failure(tmp_path, capsys):
    scripts_dir = _make_scripts_dir(tmp_path)
    # Generator exits non-zero
    _write_generator(scripts_dir, "generate_harness_reference.py",
                     "import sys\nsys.stderr.write('boom\\n')\nsys.exit(1)\n")
    _write_generator(scripts_dir, "generate_skills_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/skills.md"))
    _write_generator(scripts_dir, "generate_perspectives_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/perspectives.md"))

    report: list[str] = []
    upgrade_harness._regenerate_reference_files(tmp_path, dry_run=False, report_updated=report)

    captured = capsys.readouterr()
    assert "harness-reference regeneration failed" in captured.out
    # The other two generators still ran
    assert (tmp_path / "seja-public/docs/reference/skills.md").is_file()
    assert (tmp_path / "seja-public/docs/reference/perspectives.md").is_file()
    assert len(report) == 2
    assert not any("harness-reference" == line.replace("Regenerated ", "") for line in report)


def test_regenerate_reference_files_handles_timeout(tmp_path, capsys, monkeypatch):
    scripts_dir = _make_scripts_dir(tmp_path)
    # Generator sleeps longer than the monkeypatched timeout
    _write_generator(
        scripts_dir, "generate_harness_reference.py",
        "import time\ntime.sleep(5)\n",
    )

    # Monkeypatch subprocess.run to raise TimeoutExpired for the first call,
    # simulating a generator that exceeds the timeout without actually waiting.
    import subprocess as _subprocess
    real_run = _subprocess.run

    def fake_run(cmd, *args, **kwargs):
        if "generate_harness_reference.py" in " ".join(str(c) for c in cmd):
            raise _subprocess.TimeoutExpired(cmd=cmd, timeout=1)
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(upgrade_harness.subprocess, "run", fake_run)

    report: list[str] = []
    upgrade_harness._regenerate_reference_files(tmp_path, dry_run=False, report_updated=report)

    captured = capsys.readouterr()
    assert "timed out" in captured.out
    # The helper did not raise and report remains empty for the timed-out generator
    assert not any("harness-reference" in line for line in report)


# ---------------------------------------------------------------------------
# .seja-version pin path (plan-000380)
# ---------------------------------------------------------------------------


def test_read_seja_version_missing(tmp_path):
    assert upgrade_harness.read_seja_version(tmp_path) is None


def test_read_seja_version_present(tmp_path):
    (tmp_path / ".seja-version").write_text("v0.1.0\n", encoding="utf-8")
    assert upgrade_harness.read_seja_version(tmp_path) == "v0.1.0"


def test_read_seja_version_empty_string_is_none(tmp_path):
    (tmp_path / ".seja-version").write_text("   \n", encoding="utf-8")
    assert upgrade_harness.read_seja_version(tmp_path) is None


def test_write_seja_version_creates_file(tmp_path):
    summary = upgrade_harness.write_seja_version(tmp_path, "v0.2.0", dry_run=False)
    assert "Pinned v0.2.0" in summary
    assert (tmp_path / ".seja-version").read_text(encoding="utf-8").strip() == "v0.2.0"


def test_write_seja_version_dry_run_does_not_touch_file(tmp_path):
    summary = upgrade_harness.write_seja_version(tmp_path, "v0.2.0", dry_run=True)
    assert "Would pin v0.2.0" in summary
    assert not (tmp_path / ".seja-version").exists()


def test_write_seja_version_overwrites_existing(tmp_path):
    (tmp_path / ".seja-version").write_text("v0.1.0\n", encoding="utf-8")
    upgrade_harness.write_seja_version(tmp_path, "v0.2.0", dry_run=False)
    assert (tmp_path / ".seja-version").read_text(encoding="utf-8").strip() == "v0.2.0"


def test_collect_source_files_includes_skill_siblings(tmp_path):
    """plan-000466 Step 6b: /seja-setup --upgrade must ship SKILL-*.md
    siblings alongside SKILL.md, otherwise upgraded consumers end up with
    dangling pointers.
    """
    skills_dir = tmp_path / ".claude" / "skills"
    demo = skills_dir / "demo"
    demo.mkdir(parents=True)
    (demo / "SKILL.md").write_text(
        "---\nname: demo\n---\n\n"
        "> Overview: see [./SKILL-quickguide.md](./SKILL-quickguide.md)\n\n"
        "# Demo\n",
        encoding="utf-8",
    )
    (demo / "SKILL-quickguide.md").write_text(
        "Quick guide body.\n", encoding="utf-8"
    )
    (demo / "SKILL-rationale.md").write_text(
        "Rationale body.\n", encoding="utf-8"
    )
    # A file that does NOT start with SKILL must be excluded.
    (demo / "NOTES.md").write_text("not a sibling", encoding="utf-8")

    files = upgrade_harness.collect_source_files(tmp_path)
    names = sorted(p.name for p in files if p.parent == demo)
    assert "SKILL.md" in names
    assert "SKILL-quickguide.md" in names
    assert "SKILL-rationale.md" in names
    assert "NOTES.md" not in names


def test_collect_source_files_rejects_nonsibling_skill_names(tmp_path):
    """The sibling glob must not match files that happen to start with SKILL
    but do not follow the SKILL.md / SKILL-<facet>.md shape.
    """
    skills_dir = tmp_path / ".claude" / "skills"
    demo = skills_dir / "only-skill"
    demo.mkdir(parents=True)
    (demo / "SKILL.md").write_text(
        "---\nname: only\n---\n# Only\n", encoding="utf-8"
    )
    # An ill-named file that would slip past a loose prefix filter.
    (demo / "SKILLS-plan.md").write_text("not a sibling", encoding="utf-8")

    files = upgrade_harness.collect_source_files(tmp_path)
    names = sorted(p.name for p in files if p.parent == demo)
    assert "SKILL.md" in names
    assert "SKILLS-plan.md" not in names


# ---------------------------------------------------------------------------
# _internal skills enumeration (plan-000553)
# ---------------------------------------------------------------------------


def test_collect_source_files_includes_internal_skills(tmp_path):
    """_internal skill directories (nested >1 level) must be discovered."""
    skills_dir = tmp_path / ".claude" / "skills"

    # Top-level skill (should still work)
    top = skills_dir / "critique"
    top.mkdir(parents=True)
    (top / "SKILL.md").write_text("---\nname: check\n---\n# Check\n", encoding="utf-8")

    # Nested _internal skill
    internal = skills_dir / "_internal" / "plan" / "standard"
    internal.mkdir(parents=True)
    (internal / "SKILL.md").write_text(
        "---\nname: plan-standard\n---\n# Plan Standard\n", encoding="utf-8"
    )

    # Another nested _internal skill with SKILL-quickguide.md sibling
    internal2 = skills_dir / "_internal" / "design" / "interview"
    internal2.mkdir(parents=True)
    (internal2 / "SKILL.md").write_text(
        "---\nname: design-interview\n---\n# Design Interview\n", encoding="utf-8"
    )
    (internal2 / "SKILL-quickguide.md").write_text("Quick guide.\n", encoding="utf-8")

    files = upgrade_harness.collect_source_files(tmp_path)
    rel_paths = {f.relative_to(tmp_path).as_posix() for f in files}

    assert ".claude/skills/critique/SKILL.md" in rel_paths
    assert ".claude/skills/_internal/plan/standard/SKILL.md" in rel_paths
    assert ".claude/skills/_internal/design/interview/SKILL.md" in rel_paths
    assert ".claude/skills/_internal/design/interview/SKILL-quickguide.md" in rel_paths


def test_collect_source_files_excludes_scripts_from_recursive_scan(tmp_path):
    """The scripts/ directory must not be treated as a skill directory."""
    skills_dir = tmp_path / ".claude" / "skills"
    scripts = skills_dir / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "upgrade_harness.py").write_text("# script\n", encoding="utf-8")

    # A real skill to ensure the function doesn't return empty
    demo = skills_dir / "demo"
    demo.mkdir(parents=True)
    (demo / "SKILL.md").write_text("---\nname: demo\n---\n# Demo\n", encoding="utf-8")

    files = upgrade_harness.collect_source_files(tmp_path)
    # scripts/*.py should be collected via the scripts enumeration, not skill enumeration
    skill_files = [f for f in files if "_internal" in str(f) or (f.parent.name != "scripts" and f.name.startswith("SKILL"))]
    # No SKILL*.md from scripts/
    assert not any(f.parent == scripts and f.name.startswith("SKILL") for f in files)


# ---------------------------------------------------------------------------
# Co-located skill scripts (plan-000553)
# ---------------------------------------------------------------------------


def test_collect_source_files_includes_colocated_py_scripts(tmp_path):
    """Co-located .py files in skill directories must be collected."""
    skills_dir = tmp_path / ".claude" / "skills"

    check_dir = skills_dir / "critique"
    check_dir.mkdir(parents=True)
    (check_dir / "SKILL.md").write_text("---\nname: check\n---\n# Check\n", encoding="utf-8")
    (check_dir / "check_docs.py").write_text("# check docs\n", encoding="utf-8")
    (check_dir / "check_git_freshness.py").write_text("# git freshness\n", encoding="utf-8")

    setup_dir = skills_dir / "seja-setup"
    setup_dir.mkdir(parents=True)
    (setup_dir / "SKILL.md").write_text("---\nname: seja-setup\n---\n# Setup\n", encoding="utf-8")
    (setup_dir / "resolve_seja_version.py").write_text("# resolve\n", encoding="utf-8")

    files = upgrade_harness.collect_source_files(tmp_path)
    rel_paths = {f.relative_to(tmp_path).as_posix() for f in files}

    assert ".claude/skills/critique/check_docs.py" in rel_paths
    assert ".claude/skills/critique/check_git_freshness.py" in rel_paths
    assert ".claude/skills/seja-setup/resolve_seja_version.py" in rel_paths


def test_collect_source_files_excludes_non_py_colocated_files(tmp_path):
    """Only .py files (and SKILL*.md) should be collected from skill dirs."""
    skills_dir = tmp_path / ".claude" / "skills"
    demo = skills_dir / "demo"
    demo.mkdir(parents=True)
    (demo / "SKILL.md").write_text("---\nname: demo\n---\n# Demo\n", encoding="utf-8")
    (demo / "helper.py").write_text("# helper\n", encoding="utf-8")
    (demo / "NOTES.md").write_text("random notes", encoding="utf-8")
    (demo / "data.json").write_text("{}", encoding="utf-8")

    files = upgrade_harness.collect_source_files(tmp_path)
    names = {f.name for f in files if f.parent == demo}

    assert "SKILL.md" in names
    assert "helper.py" in names
    assert "NOTES.md" not in names
    assert "data.json" not in names


# ---------------------------------------------------------------------------
# plan-20261020-688kjs Step 12: retire what v0.11.0 installed for the ladder
# ---------------------------------------------------------------------------

import hashlib
import json
import subprocess

_RETIRED_JSON = Path(upgrade_harness.__file__).resolve().parent / "retired-files.json"
_LADDER_SCRIPT = ".claude/skills/scripts/check_specify.py"


def _entry(path: str) -> dict:
    data = json.loads(_RETIRED_JSON.read_text(encoding="utf-8"))
    return next(e for e in data["files"] if e["path"] == path)


def _git_show_v0110(path: str) -> bytes | None:
    try:
        proc = subprocess.run(
            ["git", "show", f"v0.11.0:{path}"],
            capture_output=True, check=False, cwd=_RETIRED_JSON.parent,
        )
    except OSError:
        return None
    return proc.stdout if proc.returncode == 0 else None


def _fake_identical(target: Path, path: str, monkeypatch) -> Path:
    """Write a file whose sha256 is the one recorded for `path`."""
    dest = target / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    content = b"ladder file as installed by v0.11.0\n"
    dest.write_bytes(content)
    entries = [{"path": path, "sha256_v0_11_0": hashlib.sha256(content).hexdigest()}]
    monkeypatch.setattr(upgrade_harness, "load_retired_files", lambda *a, **k: entries)
    return dest


def test_retired_file_identical_to_v0110_is_removed(tmp_path, monkeypatch, capsys):
    dest = _fake_identical(tmp_path, _LADDER_SCRIPT, monkeypatch)
    removed, kept = upgrade_harness.remove_retired_files(tmp_path, dry_run=False)
    assert not dest.exists()
    assert removed == [_LADDER_SCRIPT] and kept == []
    assert f"removido {_LADDER_SCRIPT}" in capsys.readouterr().out


def test_retired_file_edited_by_client_is_kept(tmp_path, monkeypatch, capsys):
    dest = _fake_identical(tmp_path, _LADDER_SCRIPT, monkeypatch)
    dest.write_text("edited by the client\n", encoding="utf-8")
    removed, kept = upgrade_harness.remove_retired_files(tmp_path, dry_run=False)
    assert dest.read_text(encoding="utf-8") == "edited by the client\n"
    assert removed == [] and kept == [_LADDER_SCRIPT]
    assert f"mantido (editado) {_LADDER_SCRIPT}" in capsys.readouterr().out


def test_retired_file_dry_run_does_not_remove(tmp_path, monkeypatch):
    dest = _fake_identical(tmp_path, _LADDER_SCRIPT, monkeypatch)
    removed, _ = upgrade_harness.remove_retired_files(tmp_path, dry_run=True)
    assert dest.exists() and removed == [_LADDER_SCRIPT]


def test_absent_retired_file_is_ignored(tmp_path):
    removed, kept = upgrade_harness.remove_retired_files(tmp_path, dry_run=False)
    assert removed == [] and kept == []


def test_real_hash_of_check_specify_matches_v0110(tmp_path, capsys):
    blob = _git_show_v0110(_LADDER_SCRIPT)
    if blob is None:
        pytest.skip("tag v0.11.0 not available in this checkout")
    dest = tmp_path / _LADDER_SCRIPT
    dest.parent.mkdir(parents=True)
    dest.write_bytes(blob)
    removed, _ = upgrade_harness.remove_retired_files(tmp_path, dry_run=False)
    assert _LADDER_SCRIPT in removed and not dest.exists()


def test_features_folder_stays_byte_for_byte_and_warns(tmp_path):
    feat = tmp_path / "features" / "contas"
    feat.mkdir(parents=True)
    (feat / "intent.md").write_text("# intent\n", encoding="utf-8")
    (feat / "contas.feature").write_bytes(b"Feature: contas\n")
    before = {p: p.read_bytes() for p in feat.rglob("*") if p.is_file()}
    upgrade_harness.remove_retired_files(tmp_path, dry_run=False)
    warnings = upgrade_harness.ladder_warnings(tmp_path)
    assert {p: p.read_bytes() for p in feat.rglob("*") if p.is_file()} == before
    assert upgrade_harness.FEATURES_WARNING in warnings


def test_pkb_dir_filled_keeps_pkb_inbox_and_warns(tmp_path):
    (tmp_path / "product-design").mkdir()
    (tmp_path / "product-design" / "conventions.md").write_text(
        "| `PKB_DIR` | `00-Inbox` | Pasta de captura |\n", encoding="utf-8"
    )
    inbox = tmp_path / ".claude" / "skills" / "scripts" / "pkb_inbox.py"
    inbox.parent.mkdir(parents=True)
    inbox.write_text("# pkb\n", encoding="utf-8")
    upgrade_harness.remove_retired_files(tmp_path, dry_run=False)
    assert inbox.exists()
    assert upgrade_harness.PKB_WARNING in upgrade_harness.ladder_warnings(tmp_path)


def test_no_warnings_without_features_or_pkb(tmp_path):
    (tmp_path / "product-design").mkdir()
    (tmp_path / "product-design" / "conventions.md").write_text(
        "| `PKB_DIR` |  | vazio desliga |\n", encoding="utf-8"
    )
    assert upgrade_harness.ladder_warnings(tmp_path) == []


def test_retired_list_never_names_pkb_or_retired_tokens():
    paths = {e["path"] for e in upgrade_harness.load_retired_files()}
    assert not any("pkb" in p for p in paths)
    assert ".claude/skills/scripts/check_retired_tokens.py" not in paths


def test_retired_list_covers_every_ladder_file_added_in_v0110():
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-status", "v0.10.1", "v0.11.0", "--", ".claude/"],
            capture_output=True, text=True, check=False, cwd=_RETIRED_JSON.parent,
        )
    except OSError:
        pytest.skip("git not available")
    if proc.returncode != 0:
        pytest.skip("tags v0.10.1/v0.11.0 not available in this checkout")
    added = [ln.split("\t")[1] for ln in proc.stdout.splitlines() if ln.startswith("A\t")]
    not_ladder = (
        "/tests/",
        "/template/pkb/",
        "scripts/artifact_id.py",
        "scripts/check_ledger_ids.py",
        "scripts/pkb_inbox.py",
    )
    ladder = {p for p in added if not any(m in p for m in not_ladder)}
    listed = {e["path"] for e in upgrade_harness.load_retired_files()}
    assert ladder - listed == set()
