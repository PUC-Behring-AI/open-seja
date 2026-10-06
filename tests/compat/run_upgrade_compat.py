#!/usr/bin/env python3
"""run_upgrade_compat.py -- Prove that upgrading by tag leaves existing projects alone (plan-000015, Step 9).

Invocation: user-cli, test
Lifecycle: active

Usage:
    python3 tests/compat/run_upgrade_compat.py --from v0.10.1 --to working-tree --remote <local-clone>
    python3 tests/compat/run_upgrade_compat.py --from v0.10.1 --to v0.11.0 --remote <local-clone>

Exit 0 when all four projects pass; 1 when a criterion fails; 2 on a setup error. Offline: `--remote` is a
local git repository (the repo itself or a clone); nothing is fetched, pushed or tagged in it.

The "to" side. `--to <tag>` uses a tag that already exists in `--remote`. `--to working-tree` is for a version
that is not tagged yet (and must not be tagged by this script): the runner makes a throw-away clone of `--remote`
in a temp dir, copies the working tree of `--remote` over it (tracked and untracked files, not ignored ones),
commits there and creates the tag named in the working tree's `.seja-version` **inside that temp clone only**.
That clone is then the remote of the upgrade, so the flow is the real one: `resolve_seja_version.py --remote`,
`git clone --branch <tag>`, `upgrade_harness.py --from <clone> --new-version <tag>`.

The four projects (all synthetic; nothing copied from a real project):
  (i)   new project: no `features/`, v1 plans, no test-first plugin.
  (ii)  third-party `features/` without `intent.md`, v1 plans, plugin installed at an older revision.
  (iii) mid-cycle: approved `features/<slug>/`, v2 plan, frozen M1; generated with the NEW version, then
        upgraded again (and force-re-run twice) to prove idempotence (M1 hash unchanged, empty diff).
  (iv)  shape of a long-lived archive: `.seja-version` old, own `conventions.md`, own settings, own rule,
        plugin copy edited by hand. Generated from `--legacy-from` (default v0.9.1).

The upgrade is driven by the same deterministic pieces `/seja-setup --upgrade` drives: the project's own
`resolve_seja_version.py` and `upgrade_harness.py`, then step 5b (decision 6 = C): when the project already has
`tests/scenario_report.py`, `build_checks.py install-plugin <project>` updates it; it never creates it.
Backups (`.claude-backup-*`) are the upgrade's own side effect and are not project files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"
FOUR = ("check_intent.py", "check_features.py", "check_specify.py", "check_plan_scenarios.py")
ROW = re.compile(r"^(check_\S+\.py)\s+(PASS|FAIL|ERROR)\s", re.MULTILINE)
PLUGIN = "tests/scenario_report.py"
PLUGIN_FILES = (PLUGIN, "tests/.scenario_report.sha256", "tests/conftest.py")
SLUG = "contas-da-semana"
AT = "2026-10-06T18:00:00Z"
GIT_ENV = {
    **os.environ,
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_AUTHOR_NAME": "compat", "GIT_AUTHOR_EMAIL": "compat@example.invalid",
    "GIT_COMMITTER_NAME": "compat", "GIT_COMMITTER_EMAIL": "compat@example.invalid",
}


class SetupError(Exception):
    """The proof could not be set up (not a failed criterion)."""


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 300, check: bool = True) -> subprocess.CompletedProcess:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                         stdin=subprocess.DEVNULL, env=GIT_ENV, check=False)
    if check and res.returncode != 0:
        raise SetupError(f"{' '.join(cmd)} -> exit {res.returncode}\n{res.stdout[-800:]}{res.stderr[-800:]}")
    return res


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root: Path, skip: tuple[str, ...] = ()) -> dict[str, str]:
    """sha256 of every file under root, except the upgrade's backups and any path under `skip`."""
    out: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if not p.is_file() or rel.split("/")[0].startswith(".claude-backup-") or "__pycache__" in p.parts:
            continue
        if any(rel == s or rel.startswith(s.rstrip("/") + "/") for s in skip):
            continue
        out[rel] = sha(p)
    return out


def project_files(root: Path, extra_skip: tuple[str, ...] = ()) -> dict[str, str]:
    """Project files: everything except the harness (`.claude/`), the pin and the backups."""
    return hashes(root, skip=(".claude", ".seja-version", *extra_skip))


def diff(a: dict[str, str], b: dict[str, str]) -> list[str]:
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def drop_backups(project: Path) -> None:
    for backup in project.glob(".claude-backup-*"):
        shutil.rmtree(backup)


# ---------------------------------------------------------------- sources


def make_remote(remote: Path, to: str, workdir: Path) -> tuple[Path, str]:
    """Return (remote_for_the_upgrade, target_tag)."""
    if to != "working-tree":
        if to not in run(["git", "tag", "--list", to], cwd=remote).stdout.split():
            raise SetupError(f"tag {to} not found in {remote}")
        return remote, to
    version = (remote / ".seja-version").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"v\d+\.\d+\.\d+", version):
        raise SetupError(f".seja-version of the working tree is not a SemVer tag: {version!r}")
    if version in run(["git", "tag", "--list", version], cwd=remote).stdout.split():
        raise SetupError(f"{version} is already tagged in {remote}; use --to {version}")
    clone = workdir / "remote-clone"
    run(["git", "clone", "-q", str(remote), str(clone)])
    files = run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=remote).stdout
    for rel in sorted({f for f in files.split("\0") if f}):
        src, dst = remote / rel, clone / rel
        if src.is_symlink():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.unlink(missing_ok=True)
            dst.symlink_to(os.readlink(src))
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    for rel in run(["git", "ls-files", "-z"], cwd=clone).stdout.split("\0"):
        if rel and not (remote / rel).exists() and not (remote / rel).is_symlink():
            (clone / rel).unlink(missing_ok=True)
    run(["git", "add", "-A"], cwd=clone)
    run(["git", "commit", "-q", "--allow-empty", "-m", "compat: working tree snapshot"], cwd=clone)
    run(["git", "tag", version], cwd=clone)  # in the throw-away clone only
    return clone, version


def checkout(remote: Path, tag: str, dest: Path) -> Path:
    run(["git", "clone", "-q", "--branch", tag, str(remote), str(dest)])
    if not (dest / ".claude").is_dir():
        raise SetupError(f"{tag} has no .claude/")
    return dest


def install(source: Path, tag: str, project: Path, *, conventions: Path, settings: Path,
            claude_md: str | None = None) -> None:
    """What /seja-setup installs, reduced to the deterministic part: harness, pin, project files."""
    project.mkdir(parents=True)
    shutil.copytree(source / ".claude", project / ".claude", symlinks=True)
    (project / ".seja-version").write_text(tag + "\n", encoding="utf-8")
    (project / "product-design").mkdir()
    shutil.copy(conventions, project / "product-design" / "conventions.md")
    shutil.copy(settings, project / ".claude" / "settings.json")
    if claude_md:
        shutil.copy(FIX / claude_md, project / "CLAUDE.md")
    plans = project / "_output" / "plans"
    plans.mkdir(parents=True)
    for plan in sorted((FIX / "plans").glob("*.md")):
        shutil.copy(plan, plans / plan.name)


# ---------------------------------------------------------------- upgrade


@dataclass
class UpgradeResult:
    noop: bool = False
    dry_run_changed: list[str] = field(default_factory=list)
    plugin: str = ""
    log: str = ""


def upgrade(project: Path, remote: Path, workdir: Path) -> UpgradeResult:
    """/seja-setup --upgrade, step by step (see _internal/seja-setup/upgrade/SKILL.md)."""
    res = UpgradeResult()
    pin = (project / ".seja-version").read_text(encoding="utf-8").strip()
    tag = run([sys.executable, str(project / ".claude/skills/seja-setup/resolve_seja_version.py"),
               "--remote", str(remote)]).stdout.strip()
    if tag == pin:
        res.noop = True
        res.log = f"Harness already up to date at {tag}"
        return res
    src = checkout(remote, tag, workdir / f"src-{project.name}-{tag}")
    script = src / ".claude/skills/scripts/upgrade_harness.py"  # the new release's script (upgrade SKILL step 5)
    base = [sys.executable, str(script), "--from", str(src), "--target", str(project), "--new-version", tag]
    before = hashes(project)
    dry = run(base + ["--dry-run"])
    res.dry_run_changed = diff(before, hashes(project))
    if "[DRY-RUN]" not in dry.stdout:
        raise SetupError("dry-run output has no [DRY-RUN] banner")
    res.log = run(base).stdout
    if (project / PLUGIN).is_file():  # step 5b, decision 6 = C: update only if already installed
        out = run([sys.executable, str(project / ".claude/skills/scripts/build_checks.py"), "install-plugin",
                   str(project)], check=False)
        res.plugin = "updated" if out.returncode == 0 else "refused (edited by hand)"
    else:
        res.plugin = "not installed; not created"
    drop_backups(project)
    return res


def run_all(project: Path) -> dict[str, str]:
    out = run([sys.executable, str(project / ".claude/skills/scripts/run_all_checks.py"), "--root", str(project)],
              cwd=project, timeout=300, check=False)
    rows = dict(ROW.findall(out.stdout))
    if not rows:
        raise SetupError("run_all_checks produced no rows:\n" + out.stdout[-600:] + out.stderr[-600:])
    return rows


def one_check(project: Path, script: str) -> tuple[int, str]:
    out = run([sys.executable, str(project / ".claude/skills/scripts" / script)], cwd=project, check=False)
    return out.returncode, out.stdout + out.stderr


# ---------------------------------------------------------------- criteria


@dataclass
class Report:
    name: str
    compared: int = 0
    findings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.findings

    def need(self, cond: bool, message: str) -> None:
        if not cond:
            self.findings.append(message)


def v1_plans_accepted(project: Path, rep: Report) -> None:
    """The v1 plans stay valid: routed by /implement, not read as a v2 plan."""
    for plan in sorted((project / "_output/plans").glob("plan-0000*v1*.md")):
        route = run([sys.executable, str(project / ".claude/skills/scripts/build_checks.py"), "route", str(plan),
                     "--json"], cwd=project, check=False)
        data = json.loads(route.stdout) if route.stdout.strip().startswith("{") else {}
        rep.need(route.returncode == 0 and data.get("refusal") is None, f"{plan.name}: /implement route refused a v1 plan")
        rep.need(all(s.get("scenarios") == [] for s in data.get("steps", [])), f"{plan.name}: v1 plan got scenarios")
    code, _ = one_check(project, "check_plan_scenarios.py")
    rep.need(code == 0, "check_plan_scenarios failed on v1 plans")


def cycle_checks_say_nothing(project: Path, rep: Report) -> None:
    for script in FOUR:
        code, out = one_check(project, script)
        rep.need(code == 0 and "nada a verificar" in out,
                 f"{script}: expected exit 0 and 'nada a verificar', got {code}: {out.strip()[:120]}")


def check_set(rep: Report, before: dict[str, str], after: dict[str, str]) -> None:
    fails_before = {k for k, v in before.items() if v != "PASS"}
    fails_after = {k for k, v in after.items() if v != "PASS"}
    rep.need(fails_before == fails_after, f"failure set changed: {sorted(fails_before ^ fails_after)}")
    rep.need(all(after.get(c) == "PASS" for c in FOUR), "a cycle check is not PASS after the upgrade")
    rep.need(not any(c in before for c in FOUR), "the four checks already existed before (wrong 'from'?)")
    rep.notes.append(f"run_all_checks: {len(before)} -> {len(after)} checks; failures {len(fails_before)} -> "
                     f"{len(fails_after)} (same set: {fails_before == fails_after}); "
                     f"added: {', '.join(sorted(set(after) - set(before))) or 'none'}")


def plugin_old_copy(project: Path, new_plugin: Path, *, hand_edited: bool) -> None:
    """A previously installed plugin: an older revision, stamped (updatable) or edited by hand (not)."""
    tests = project / "tests"
    tests.mkdir(exist_ok=True)
    old = new_plugin.read_bytes() + b"\n# older revision\n"
    (tests / "scenario_report.py").write_bytes(old)
    stamped = old if not hand_edited else new_plugin.read_bytes() + b"\n# something else\n"
    (tests / ".scenario_report.sha256").write_text(hashlib.sha256(stamped).hexdigest() + "\n", encoding="utf-8")
    (tests / "conftest.py").write_text('pytest_plugins = ["scenario_report"]\n', encoding="utf-8")


# ---------------------------------------------------------------- projects


@dataclass
class Ctx:
    frm: str
    legacy: str
    to: str
    remote: Path
    work: Path
    old_src: Path
    legacy_src: Path
    new_src: Path

    @property
    def new_plugin(self) -> Path:
        return self.new_src / ".claude/references/template/bdd/python/scenario_report.py.example"


def common(ctx: Ctx, rep: Report, p: Path, *, plugin_expected: str, skip: tuple[str, ...] = ()) -> Report:
    files_before = project_files(p, skip)
    plans_before = hashes(p / "_output")
    checks_before = run_all(p)
    first = upgrade(p, ctx.remote, ctx.work)
    rep.need(not first.noop, "first upgrade was a no-op")
    rep.need(not first.dry_run_changed, f"dry-run changed files: {first.dry_run_changed[:5]}")
    rep.need(first.plugin == plugin_expected, f"plugin: expected '{plugin_expected}', got '{first.plugin}'")
    rep.compared = len(files_before)
    changed = diff(files_before, project_files(p, skip))
    rep.need(not changed, f"project files changed: {changed[:8]}")
    rep.need(diff(plans_before, hashes(p / "_output")) == [], "_output/ changed")
    rep.need((p / ".seja-version").read_text(encoding="utf-8").strip() == ctx.to, ".seja-version is not the new tag")
    rep.need((p / ".claude/references/template/bdd/python/scenario_report.py.example").is_file(),
             "the plugin template did not reach the upgraded project")
    check_set(rep, checks_before, run_all(p))
    cycle_checks_say_nothing(p, rep)
    v1_plans_accepted(p, rep)
    again = upgrade(p, ctx.remote, ctx.work)
    rep.need(again.noop, "second upgrade was not 'already up to date'")
    settled = hashes(p)
    forced = run([sys.executable, str(ctx.new_src / ".claude/skills/scripts/upgrade_harness.py"), "--from", str(ctx.new_src),
                  "--target", str(p), "--new-version", ctx.to])
    drop_backups(p)
    rep.need(diff(settled, hashes(p)) == [], f"forced re-run changed files: {diff(settled, hashes(p))[:8]}")
    rep.notes.append(f"plugin: {first.plugin}; second upgrade: '{again.log}'; forced re-run: empty diff over "
                     f"{len(settled)} files (exit {forced.returncode})")
    return rep


def project_i(ctx: Ctx) -> Report:
    rep = Report("(i) new project, no features/, v1 plans")
    p = ctx.work / "p1"
    install(ctx.old_src, ctx.frm, p, conventions=FIX / "conventions-basic.md", settings=FIX / "settings-basic.json")
    rep = common(ctx, rep, p, plugin_expected="not installed; not created")
    rep.need(not (p / "tests").exists(), "the upgrade created tests/")
    return rep


def project_ii(ctx: Ctx) -> Report:
    rep = Report("(ii) third-party features/ without intent.md, v1 plans, older plugin installed")
    p = ctx.work / "p2"
    install(ctx.old_src, ctx.frm, p, conventions=FIX / "conventions-basic.md", settings=FIX / "settings-basic.json")
    shutil.copytree(FIX / "third-party-features" / "features", p / "features")
    plugin_old_copy(p, ctx.new_plugin, hand_edited=False)
    features = hashes(p / "features")
    rep = common(ctx, rep, p, plugin_expected="updated", skip=PLUGIN_FILES)
    rep.need(hashes(p / "features") == features, "third-party features/ changed")
    rep.need((p / PLUGIN).read_bytes() == ctx.new_plugin.read_bytes(), "installed plugin was not brought to the new revision")
    rep.need(not (p / "features" / "login" / "intent.md").exists(), "the upgrade created an intent.md")
    return rep


def project_iii(ctx: Ctx) -> Report:
    rep = Report("(iii) mid-cycle: approved feature, v2 plan, frozen M1; upgraded again")
    p = ctx.work / "p3"
    install(ctx.new_src, ctx.to, p, conventions=FIX / "conventions-basic.md", settings=FIX / "settings-basic.json")
    shutil.copytree(FIX / "feature-m1" / "features", p / "features")
    plan = p / "_output" / "plans" / "plan-000900-fixture.md"
    shutil.copy(FIX / "feature-m1" / "plan-000900-fixture.md", plan)
    freeze = run([sys.executable, str(p / ".claude/skills/scripts/drift_report.py"), "--feature", SLUG, "--plan",
                  str(plan), "--moment", "M1", "--freeze", "--at", AT], cwd=p, check=False)
    m1 = p / "features" / SLUG / "drift" / "M1.json"
    rep.need(freeze.returncode == 0 and m1.is_file(), f"M1 was not frozen: {freeze.stderr.strip()[:160]}")
    if not m1.is_file():
        return rep
    m1_hash = sha(m1)
    files_before = project_files(p)
    checks_before = run_all(p)
    first = upgrade(p, ctx.remote, ctx.work)
    rep.need(first.noop, f"the project is already at {ctx.to}: the upgrade must be 'already up to date'")
    for round_ in (1, 2):
        before = hashes(p)
        run([sys.executable, str(ctx.new_src / ".claude/skills/scripts/upgrade_harness.py"), "--from", str(ctx.new_src),
             "--target", str(p), "--new-version", ctx.to])
        drop_backups(p)
        changed = diff(before, hashes(p))
        rep.need(not changed, f"forced upgrade {round_} changed files: {changed[:8]}")
    rep.compared = len(files_before)
    rep.need(sha(m1) == m1_hash, "M1.json hash changed")
    rep.need(diff(files_before, project_files(p)) == [], "project files changed")
    checks_after = run_all(p)
    rep.need(checks_before == checks_after, "run_all_checks results changed on the second upgrade")
    rep.need(all(checks_after.get(c) == "PASS" for c in FOUR), "a cycle check is not PASS with an approved feature")
    code, out = one_check(p, "check_plan_scenarios.py")
    rep.need(code == 0, f"check_plan_scenarios fails on the v2 plan: {out.strip()[:120]}")
    rep.notes.append(f"M1.json sha256 {m1_hash[:12]} unchanged; upgrade 'already up to date'; two forced re-runs: "
                     f"empty diff ({len(files_before)} project files)")
    return rep


def project_iv(ctx: Ctx) -> Report:
    rep = Report("(iv) archive shape: old pin, own conventions/settings/rule, hand-edited plugin")
    p = ctx.work / "p4"
    install(ctx.legacy_src, ctx.legacy, p, conventions=FIX / "conventions-legacy-shape.md",
            settings=FIX / "settings-legacy-shape.json", claude_md="claude-legacy-shape.md")
    shutil.copy(FIX / "rule-local.md", p / ".claude" / "rules" / "meu-projeto.md")
    (p / ".claude" / "settings.local.json").write_text('{"permissions": {"allow": ["Bash(ls:*)"]}}\n', encoding="utf-8")
    plugin_old_copy(p, ctx.new_plugin, hand_edited=True)
    keep = {rel: sha(p / rel) for rel in
            ("product-design/conventions.md", ".claude/settings.json", ".claude/settings.local.json",
             ".claude/rules/meu-projeto.md", "CLAUDE.md", *PLUGIN_FILES)}
    rep = common(ctx, rep, p, plugin_expected="refused (edited by hand)")
    rep.need({rel: sha(p / rel) for rel in keep} == keep,
             "conventions.md, settings, local rule, CLAUDE.md or the hand-edited plugin changed")
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Upgrade-by-tag compatibility proof (see the module docstring).")
    ap.add_argument("--from", dest="frm", required=True, help="previous tag the projects are generated from, e.g. v0.10.1")
    ap.add_argument("--to", required=True, help="new tag, or 'working-tree' for the not-yet-tagged working tree of --remote")
    ap.add_argument("--remote", required=True, type=Path, help="local clone (or the repo itself) used as the remote")
    ap.add_argument("--legacy-from", default="v0.9.1", help="tag project (iv) is generated from (default v0.9.1)")
    ap.add_argument("--workdir", type=Path, default=None, help="keep temp projects here (default: a temp dir, removed)")
    args = ap.parse_args(argv)
    remote = args.remote.resolve()
    own_tmp = args.workdir is None
    work = args.workdir.resolve() if args.workdir else Path(tempfile.mkdtemp(prefix="seja-compat-"))
    work.mkdir(parents=True, exist_ok=True)
    try:
        up_remote, to = make_remote(remote, args.to, work)
        ctx = Ctx(args.frm, args.legacy_from, to, up_remote, work,
                  checkout(up_remote, args.frm, work / "src-from"),
                  checkout(up_remote, args.legacy_from, work / "src-legacy"),
                  checkout(up_remote, to, work / "src-to"))
        reports = [fn(ctx) for fn in (project_i, project_ii, project_iii, project_iv)]
    except SetupError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 2
    finally:
        if own_tmp:
            shutil.rmtree(work, ignore_errors=True)
    print(f"upgrade compat: {args.frm} -> {to} (project iv generated from {args.legacy_from})")
    for rep in reports:
        print(f"\n{'PASS' if rep.ok else 'FAIL'}  {rep.name}")
        print(f"  project files compared: {rep.compared}")
        for note in rep.notes:
            print(f"  {note}")
        for finding in rep.findings:
            print(f"  FINDING: {finding}")
    bad = [r for r in reports if not r.ok]
    print(f"\n{len(reports) - len(bad)}/{len(reports)} projects pass")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
