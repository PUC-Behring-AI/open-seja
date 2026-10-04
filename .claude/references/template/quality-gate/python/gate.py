"""Quality gate core for Python projects (stdlib only).

Pure functions: CRAP score, radon/coverage join, touched functions from a
git diff, CRAP ratchet, marker ratchet and exit code. The executor
(CLI, subprocess orchestration) is layered on top of this core; every
external command goes through one injectable `run(cmd, env, cwd, timeout)`.
"""
from __future__ import annotations

import argparse
import ast
import datetime
import json
import os
import re
import subprocess
import sys
import time
from collections import namedtuple
import shutil
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set

# Exit categories, lowest failing one wins (1 always precedes).
CAT_CONFIG = 1
CAT_STATIC = 2
CAT_TESTS = 3
CAT_CRAP = 4
CAT_ARCH = 5
CAT_MUTATION = 6
CAT_MARKERS = 7

JOIN_MISS_LIMIT = 0.05
_EPS = 1e-9


@dataclass
class Finding:
    category: int
    key: str
    message: str
    value: Optional[float] = None
    limit: Optional[float] = None
    severity: str = "error"  # "error" or "warning"


@dataclass
class FunctionMetric:
    file: str
    qualname: str
    lineno: int
    endline: int
    cc: int
    cov: float
    crap: float
    joined: bool = True

    @property
    def key(self) -> str:
        return make_key(self.file, self.qualname)


def make_key(file: str, qualname: str) -> str:
    return "%s::%s" % (file, qualname)


def crap(cc: int, cov: float) -> float:
    """CRAP = cc^2 * (1 - cov)^3 + cc."""
    return cc ** 2 * (1.0 - cov) ** 3 + cc


def _norm(path: str, root: str) -> str:
    absolute = path if os.path.isabs(path) else os.path.join(root, path)
    return os.path.relpath(os.path.abspath(absolute), os.path.abspath(root)).replace(os.sep, "/")


def _flatten(entry: dict, prefix: str) -> Iterable[tuple]:
    """Yield (qualname, entry) for a radon entry and its closures."""
    qual = prefix + entry["name"]
    yield qual, entry
    for child in entry.get("closures", []) or []:
        for item in _flatten(child, qual + "."):
            yield item


def _radon_functions(entries: List[dict]) -> Iterable[tuple]:
    for entry in entries:
        etype = entry.get("type")
        if etype == "class":
            # The class itself is ignored; its methods are scored on their own.
            for meth in entry.get("methods", []) or []:
                for item in _flatten(meth, entry["name"] + "."):
                    yield item
            continue
        prefix = entry["classname"] + "." if entry.get("classname") else ""
        for item in _flatten(entry, prefix):
            yield item


def _region_cov(region: Optional[dict]) -> tuple:
    """Return (cov, found) for a coverage `functions` region."""
    if region is None:
        return 0.0, False
    summ = region.get("summary", {})
    denom = summ.get("num_statements", 0) + summ.get("num_branches", 0)
    if denom == 0:
        return 1.0, True
    num = summ.get("covered_lines", 0) + summ.get("covered_branches", 0)
    return num / float(denom), True


def join_metrics(radon_json: dict, coverage_json: dict, root: str = ".") -> Dict[str, FunctionMetric]:
    """Join radon cc with per-function coverage (coverage >= 7.5)."""
    cov_files = {
        _norm(path, root): data for path, data in (coverage_json.get("files") or {}).items()
    }
    metrics: Dict[str, FunctionMetric] = {}
    for path, entries in radon_json.items():
        if isinstance(entries, dict):  # radon error payload for a file
            continue
        rel = _norm(path, root)
        functions = (cov_files.get(rel) or {}).get("functions") or {}
        for qual, entry in _radon_functions(entries):
            cov, found = _region_cov(functions.get(qual))
            cc = int(entry["complexity"])
            metric = FunctionMetric(
                file=rel,
                qualname=qual,
                lineno=int(entry["lineno"]),
                endline=int(entry.get("endline") or entry["lineno"]),
                cc=cc,
                cov=cov,
                crap=crap(cc, cov),
                joined=found,
            )
            metrics[metric.key] = metric
    return metrics


def join_findings(metrics: Dict[str, FunctionMetric]) -> List[Finding]:
    """Category 1 `join-miss` when more than 5% of functions lack a coverage region."""
    if not metrics:
        return []
    missed = [m for m in metrics.values() if not m.joined]
    ratio = len(missed) / float(len(metrics))
    if ratio > JOIN_MISS_LIMIT:
        return [Finding(CAT_CONFIG, "join-miss",
                        "%d of %d functions have no coverage region" % (len(missed), len(metrics)),
                        ratio, JOIN_MISS_LIMIT)]
    return []


_FILE_RE = re.compile(r"^\+\+\+ (?:b/)?(.+?)\s*$")
_HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def touched_functions(diff_text: str, untracked: Iterable[str],
                      metrics: Dict[str, FunctionMetric]) -> Set[str]:
    """Keys of functions touched by a `git diff -U0` plus untracked files.

    An added/changed hunk `+c,d` touches functions containing lines c..c+d-1;
    a removal-only hunk (d == 0) touches the function containing line c.
    Untracked files touch all of their functions.
    """
    by_file: Dict[str, List[FunctionMetric]] = {}
    for metric in metrics.values():
        by_file.setdefault(metric.file, []).append(metric)
    touched: Set[str] = set()
    for path in untracked:
        for metric in by_file.get(path.replace(os.sep, "/"), []):
            touched.add(metric.key)
    current: Optional[str] = None
    for line in diff_text.splitlines():
        fm = _FILE_RE.match(line)
        if fm:
            current = None if fm.group(1) == "/dev/null" else fm.group(1)
            continue
        hm = _HUNK_RE.match(line)
        if hm and current:
            start = int(hm.group(1))
            count = 1 if hm.group(2) is None else int(hm.group(2))
            last = start + count - 1 if count > 0 else start
            for metric in by_file.get(current, []):
                if metric.lineno <= last and start <= metric.endline:
                    touched.add(metric.key)
    return touched


def evaluate_crap(metrics: Dict[str, FunctionMetric], baseline: dict, touched: Set[str],
                  max_touched: float, max_abs: float) -> List[Finding]:
    """Apply the CRAP ratchet. Category 4 findings, plus `over-ceiling` warnings."""
    base = (baseline or {}).get("functions", {})
    findings: List[Finding] = []
    for key in sorted(metrics):
        value = metrics[key].crap
        entry = base.get(key)
        if key in touched or entry is None:
            if value > max_touched + _EPS:
                why = "touched" if key in touched else "new"
                m = metrics[key]
                hint = ("reduce complexity, not just add tests" if m.cc > max_touched
                        else "add tests or simplify")
                findings.append(Finding(
                    CAT_CRAP, key,
                    "CRAP(%s)=%.2f > %s (%s function; cc=%d, cov=%.0f%%): %s"
                    % (key, value, max_touched, why, m.cc, m.cov * 100, hint),
                    value, max_touched))
            continue
        base_crap = float(entry["crap"])
        if value > base_crap + _EPS:
            findings.append(Finding(CAT_CRAP, key,
                                    "CRAP(%s)=%.2f rose above baseline %.2f" % (key, value, base_crap),
                                    value, base_crap))
        elif base_crap > max_abs and value > max_abs + _EPS:
            findings.append(Finding(CAT_CRAP, key + "#over-ceiling",
                                    "CRAP(%s)=%.2f above ceiling %s (legacy baseline %.2f)"
                                    % (key, value, max_abs, base_crap),
                                    value, max_abs, severity="warning"))
    return findings


def ratchet_markers(counts_now: dict, counts_base: dict) -> List[Finding]:
    """Evasion markers (skip, xfail, no cover, no mutate).

    Counts are `{kind: {"total": n, "unjustified": m}}`; markers lacking
    `reason=`/`reason:`/`equivalent:` must not exceed the baseline.
    """
    findings: List[Finding] = []
    for kind in sorted(counts_now):
        now = counts_now[kind].get("unjustified", 0)
        base = (counts_base or {}).get(kind, {}).get("unjustified", 0)
        if now > base:
            findings.append(Finding(CAT_MARKERS, kind,
                                    "%d new '%s' marker(s) without reason/equivalent" % (now - base, kind),
                                    now, base))
    return findings


def exit_code(findings: Iterable[Finding]) -> int:
    """0 PASS; 1 precedes; otherwise the lowest failing category 2..7. Warnings ignored."""
    cats = {f.category for f in findings if f.severity != "warning"}
    if CAT_CONFIG in cats:
        return CAT_CONFIG
    failing = [c for c in cats if CAT_STATIC <= c <= CAT_MARKERS]
    return min(failing) if failing else 0


# ==========================================================================
# Executor
# ==========================================================================

RunResult = namedtuple("RunResult", "returncode stdout stderr")

SECRET_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN")
_SECRET_RE = re.compile(r".*_(API_KEY|TOKEN|SECRET)$")
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "mutants", "_output", "build",
             "dist", "__pycache__", ".tox", ".mypy_cache", ".ruff_cache"}
BASELINE_NAME = "quality-baseline.json"
DEFAULT_MAX_TOUCHED = 10.0
DEFAULT_MAX_ABS = 30.0
SEP = "\u01c1"  # mutmut 3 separator for methods


def scrub_env(parent: Dict[str, str], passthrough: Iterable[str] = ()) -> Dict[str, str]:
    """Child environment without credentials (unless explicitly passed through)."""
    keep = set(passthrough)
    out = {}
    for name, value in parent.items():
        if name in keep:
            out[name] = value
        elif name in SECRET_ENV or _SECRET_RE.match(name):
            continue
        else:
            out[name] = value
    return out


def default_run(cmd, env, cwd, timeout):
    try:
        res = subprocess.run(list(cmd), env=env, cwd=cwd, capture_output=True,
                             text=True, timeout=timeout)
        return RunResult(res.returncode, res.stdout, res.stderr)
    except subprocess.TimeoutExpired:
        return RunResult(124, "", "timeout after %ss" % timeout)
    except OSError as err:
        return RunResult(127, "", str(err))


class ConfigFail(Exception):
    def __init__(self, key, message):
        Exception.__init__(self, message)
        self.key = key
        self.message = message


def read_config(root: str) -> dict:
    """Read [tool.seja-gate] and [tool.mutmut] from pyproject.toml."""
    path = os.path.join(root, "pyproject.toml")
    if not os.path.isfile(path):
        raise ConfigFail("no-pyproject", "pyproject.toml not found in %s" % root)
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
        except ImportError:
            raise ConfigFail("no-toml-reader", "Python >= 3.11 (or tomli) is required to read pyproject.toml")
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    tool = data.get("tool", {})
    cfg = dict(tool.get("seja-gate", {}))
    cfg["_mutmut"] = tool.get("mutmut", {})
    cfg["_has_contract"] = bool(tool.get("importlinter")) or os.path.isfile(os.path.join(root, ".importlinter"))
    return cfg


def detect_package(root: str, cfg: dict) -> str:
    """Package name: [tool.seja-gate] package, else the single dir under src/."""
    if cfg.get("package"):
        return os.path.basename(str(cfg["package"]).rstrip("/")).replace("-", "_")
    src = os.path.join(root, "src")
    if os.path.isdir(src):
        cands = [d for d in sorted(os.listdir(src))
                 if os.path.isdir(os.path.join(src, d)) and not d.startswith((".", "_"))
                 and not d.endswith(".egg-info")]
        if len(cands) == 1:
            return cands[0]
    raise ConfigFail("no-package", "cannot detect the package; set [tool.seja-gate] package")


def package_dir(root: str, package: str) -> str:
    for cand in (os.path.join(root, "src", package), os.path.join(root, package)):
        if os.path.isdir(cand):
            return cand
    raise ConfigFail("no-package", "package directory for %r not found" % package)


def iter_py(root: str, top: Optional[str] = None) -> Iterable[str]:
    base = top or root
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name.endswith(".py"):
                yield os.path.join(dirpath, name)


# ---- static test lint ----------------------------------------------------

def _has_assertion(func: ast.AST) -> bool:
    for node in ast.walk(func):
        if isinstance(node, ast.Assert):
            return True
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if attr == "raises" or attr.startswith("assert"):
                return True
    return False


def lint_tests(root: str) -> List[Finding]:
    """Every `def test_*` needs an assert or pytest.raises (AST)."""
    findings: List[Finding] = []
    tdir = os.path.join(root, "tests")
    if not os.path.isdir(tdir):
        return findings
    for path in iter_py(root, tdir):
        base = os.path.basename(path)
        if not (base.startswith("test_") or base.endswith("_test.py")):
            continue
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        try:
            with open(path, encoding="utf-8") as fh:
                tree = ast.parse(fh.read(), filename=path)
        except (SyntaxError, UnicodeDecodeError) as err:
            findings.append(Finding(CAT_TESTS, rel + "::<parse>", "cannot parse %s: %s" % (rel, err)))
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                if not _has_assertion(node):
                    findings.append(Finding(CAT_TESTS, "%s::%s" % (rel, node.name),
                                            "test %s has no assert or pytest.raises" % node.name))
    return findings


# ---- markers -------------------------------------------------------------

_MARKERS = (
    ("skip", re.compile(r"pytest\.mark\.skip(?!if)|pytest\.skip\(|unittest\.skip(?!If)")),
    ("xfail", re.compile(r"pytest\.mark\.xfail|pytest\.xfail\(")),
    ("no cover", re.compile(r"#\s*pragma:\s*no\s+cover")),
    ("no mutate", re.compile(r"#\s*pragma:\s*no\s+mutate")),
)
_JUSTIFIED = re.compile(r"reason\s*[=:]|equivalent\s*:")


def count_markers(root: str) -> dict:
    counts = {kind: {"total": 0, "unjustified": 0} for kind, _ in _MARKERS}
    for path in iter_py(root):
        if os.path.abspath(path) == os.path.abspath(__file__):
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line in lines:
            for kind, rx in _MARKERS:
                if rx.search(line):
                    counts[kind]["total"] += 1
                    if not _JUSTIFIED.search(line):
                        counts[kind]["unjustified"] += 1
    return counts


# ---- mutation helpers ----------------------------------------------------

def module_name(file: str, roots: Iterable[str]) -> str:
    rel = file.replace(os.sep, "/")
    for r in list(roots) + ["src/"]:
        r = r.replace(os.sep, "/").strip()
        if r and r != ".":
            r = r.rstrip("/") + "/"
            if rel.startswith(r):
                rel = rel[len(r):]
                break
    rel = rel[:-3] if rel.endswith(".py") else rel
    mod = rel.replace("/", ".")
    if mod.endswith(".__init__"):
        mod = mod[: -len(".__init__")]
    return mod


def mutation_globs(keys: Iterable[str], roots: Iterable[str]) -> List[str]:
    """Per-function mutmut 3 globs: `<mod>.x_<fn>__mutmut_*`, methods `<mod>.x<SEP><Cls><SEP><m>__mutmut_*`."""
    globs = []
    for key in sorted(keys):
        file, qual = key.split("::", 1)
        mod = module_name(file, roots)
        if "." in qual:
            globs.append("%s.x%s%s__mutmut_*" % (mod, SEP, qual.replace(".", SEP)))
        else:
            globs.append("%s.x_%s__mutmut_*" % (mod, qual))
    return globs


def mutant_to_key(name: str, files: Iterable[str], roots: Iterable[str] = ()) -> Optional[str]:
    """Map a mutmut mutant name to `<file>::<qualname>`, or None if unknown."""
    if "." not in name or "__mutmut_" not in name:
        return None
    mod, rest = name.rsplit(".", 1)
    rest = rest.split("__mutmut_")[0]
    if rest.startswith("x" + SEP):
        qual = rest[1:].strip(SEP).replace(SEP, ".")
    elif rest.startswith("x_"):
        qual = rest[2:]
    else:
        return None
    for f in files:
        if module_name(f, roots) == mod:
            return make_key(f, qual)
    return None


def parse_mutmut_results(text: str) -> List[tuple]:
    """Parse `mutmut results --all true` into (mutant_name, status) pairs."""
    rows = []
    for line in text.splitlines():
        m = re.match(r"^\s*([\w.%s]+__mutmut_\d+)\s*:\s*(\w[\w ]*?)\s*$" % SEP, line)
        if m:
            rows.append((m.group(1), m.group(2).lower()))
    return rows


# ---- orchestration -------------------------------------------------------

class Report:
    def __init__(self, level):
        self.level = level
        self.stages = []
        self.findings: List[Finding] = []
        self.baseline_path = ""

    def stage(self, name, status, started):
        self.stages.append({"name": name, "status": status,
                            "seconds": round(time.time() - started, 3)})

    def failed(self):
        return any(f.severity != "warning" for f in self.findings)

    def code(self):
        return exit_code(self.findings)

    def payload(self):
        code = self.code()
        status = "PASS" if code == 0 else ("ERROR" if code == CAT_CONFIG else "FAIL")
        return {"version": 1, "level": self.level, "status": status, "exit_code": code,
                "stages": self.stages,
                "findings": [vars(f).copy() for f in self.findings],
                "baseline": self.baseline_path}


def _tail(res: RunResult, n: int = 600) -> str:
    return ((res.stdout or "") + (res.stderr or "")).strip()[-n:]


def _load_json(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _coverage_stale(cov: dict, pkg_dir: str) -> bool:
    stamp = (cov.get("meta") or {}).get("timestamp")
    if not stamp:
        return True
    try:
        when = datetime.datetime.fromisoformat(stamp)
    except ValueError:
        return True
    cov_time = when.timestamp()  # naive stamps are local time, as coverage writes them
    newest = 0.0
    for path in iter_py(pkg_dir):
        newest = max(newest, os.path.getmtime(path))
    return newest > cov_time + 1.0


def _measure(run, env, root, pkg, cfg, rep, files=None):
    """Run pytest with coverage and radon; return (metrics, pkg_dir) or None on failure."""
    pdir = package_dir(root, pkg)
    started = time.time()
    res = run(["pytest", "--cov=%s" % pkg, "--cov-branch", "--cov-report=json",
               "--timeout=30"], env, root, 1800)
    if res.returncode != 0 and "unrecognized arguments: --timeout" in _tail(res, 2000):
        rep.stage("pytest", "fail", started)
        rep.findings.append(Finding(CAT_CONFIG, "missing-pytest-timeout",
                                    "pytest-timeout is not installed. Install with: uv add --dev pytest-timeout"))
        return None
    if res.returncode != 0:
        rep.stage("pytest", "fail", started)
        rep.findings.append(Finding(CAT_TESTS, "pytest", "pytest failed (exit %d): %s" % (res.returncode, _tail(res))))
        return None
    rep.stage("pytest", "pass", started)
    covpath = os.path.join(root, "coverage.json")
    started = time.time()
    if not os.path.isfile(covpath):
        rep.stage("coverage", "fail", started)
        rep.findings.append(Finding(CAT_CONFIG, "no-coverage", "coverage.json was not produced"))
        return None
    cov = _load_json(covpath)
    if _coverage_stale(cov, pdir):
        rep.stage("coverage", "fail", started)
        rep.findings.append(Finding(CAT_CONFIG, "stale-coverage",
                                    "coverage.json is older than the newest source file; rerun the tests"))
        return None
    rep.stage("coverage", "pass", started)
    started = time.time()
    res = run(["radon", "cc", "-j", os.path.relpath(pdir, root)], env, root, 300)
    try:
        radon = json.loads(res.stdout)
    except ValueError:
        radon = None
    if res.returncode != 0 or not isinstance(radon, dict):
        rep.stage("crap", "fail", started)
        rep.findings.append(Finding(CAT_CONFIG, "radon-failed", "radon cc failed: %s" % _tail(res)))
        return None
    metrics = join_metrics(radon, cov, root)
    rep.findings.extend(join_findings(metrics))
    return metrics


def _git_touched(run, env, root, diff_base, metrics, rep):
    res = run(["git", "merge-base", "HEAD", diff_base], env, root, 60)
    if res.returncode != 0 or not res.stdout.strip():
        rep.findings.append(Finding(CAT_CONFIG, "no-diff-base",
                                    "cannot resolve diff base %r; fetch it or set [tool.seja-gate] diff_base" % diff_base))
        return None
    base = res.stdout.strip().splitlines()[0]
    diff = run(["git", "diff", "-U0", base], env, root, 60)
    untracked = run(["git", "ls-files", "--others", "--exclude-standard"], env, root, 60)
    return touched_functions(diff.stdout or "", (untracked.stdout or "").split(), metrics)


def _write_baseline(path, metrics, markers, survived_total=0):
    data = {"version": 1,
            "functions": {k: {"cc": m.cc, "cov": round(m.cov, 4), "crap": round(m.crap, 4), "survived": 0}
                          for k, m in sorted(metrics.items())},
            "markers": markers, "mutation": {"survived_total": survived_total}}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")


def _required_tools(level, cfg):
    tools = ["ruff", "pyright", "pytest", "radon"]
    if cfg.get("_has_contract"):
        tools.append("lint-imports")
    if level == "full":
        tools.append("mutmut")
    return tools


def execute(args, run, which, root, parent_env, rep) -> None:
    cfg = read_config(root)
    pkg = detect_package(root, cfg)
    env = scrub_env(parent_env, cfg.get("env_passthrough", []))
    missing = [t for t in _required_tools(rep.level, cfg) if not which(t)]
    if missing:
        rep.findings.append(Finding(CAT_CONFIG, "missing-tools",
                                    "missing tools: %s. Install with: uv add --dev %s"
                                    % (", ".join(missing), " ".join(missing))))
        return
    bpath = os.path.join(root, BASELINE_NAME)
    rep.baseline_path = bpath
    max_touched = float(cfg.get("crap_max_touched", DEFAULT_MAX_TOUCHED))
    max_abs = float(cfg.get("crap_max_abs", DEFAULT_MAX_ABS))
    diff_base = cfg.get("diff_base", "origin/main")
    only = None
    if args.files:
        only = {_norm(f, root) for f in args.files}

    init_mode = args.init_baseline or args.accept_baseline
    if args.accept_baseline and not args.yes:
        rep.findings.append(Finding(CAT_CONFIG, "needs-yes", "--accept-baseline requires --yes (human only)"))
        return
    if args.init_baseline and not args.accept_baseline and os.path.isfile(bpath):
        rep.stage("baseline", "skip", time.time())
        return
    if not init_mode and not os.path.isfile(bpath):
        rep.findings.append(Finding(CAT_CONFIG, "no-baseline",
                                    "%s not found; run `python gate.py --init-baseline`" % BASELINE_NAME))
        return

    if init_mode:
        metrics = _measure(run, env, root, pkg, cfg, rep)
        if metrics is None or rep.failed():
            return
        _write_baseline(bpath, metrics, count_markers(root))
        rep.stage("baseline", "pass", time.time())
        return

    # 1. static: ruff then pyright (category 2)
    for name, cmd in (("ruff", ["ruff", "check", "."]),
                      ("ruff-format", ["ruff", "format", "--check", "."]),
                      ("pyright", ["pyright"])):
        started = time.time()
        res = run(cmd, env, root, 600)
        if res.returncode != 0:
            rep.stage(name, "fail", started)
            rep.findings.append(Finding(CAT_STATIC, name, "%s failed (exit %d): %s" % (name, res.returncode, _tail(res))))
            return
        rep.stage(name, "pass", started)
    # 2. test AST lint (category 3), then pytest + coverage
    started = time.time()
    lint = lint_tests(root)
    rep.stage("test-lint", "fail" if lint else "pass", started)
    if lint:
        rep.findings.extend(lint)
        return
    metrics = _measure(run, env, root, pkg, cfg, rep)
    if metrics is None or rep.failed():
        return
    # 3. CRAP (category 4)
    started = time.time()
    touched = _git_touched(run, env, root, diff_base, metrics, rep)
    if touched is None:
        rep.stage("crap", "fail", started)
        return
    baseline = _load_json(bpath)
    scoped = metrics
    if only is not None:
        scoped = {k: m for k, m in metrics.items() if m.file in only}
    crap_findings = evaluate_crap(scoped, baseline, touched, max_touched, max_abs)
    rep.findings.extend(crap_findings)
    rep.stage("crap", "fail" if any(f.severity != "warning" for f in crap_findings) else "pass", started)
    if rep.failed():
        return
    # 4. import contracts (category 5)
    if cfg.get("_has_contract"):
        started = time.time()
        res = run(["lint-imports"], env, root, 300)
        if res.returncode != 0:
            rep.stage("lint-imports", "fail", started)
            rep.findings.append(Finding(CAT_ARCH, "lint-imports", "import contract broken: %s" % _tail(res)))
            return
        rep.stage("lint-imports", "pass", started)
    # 5. markers (category 7)
    started = time.time()
    mark = ratchet_markers(count_markers(root), baseline.get("markers", {}))
    rep.stage("markers", "fail" if mark else "pass", started)
    rep.findings.extend(mark)
    if mark:
        return
    # 6. mutation (category 6, --full only)
    if rep.level == "full":
        _mutation(run, env, root, cfg, metrics, touched, only, baseline, rep)


def _mutation(run, env, root, cfg, metrics, touched, only, baseline, rep):
    started = time.time()
    roots = cfg["_mutmut"].get("paths_to_mutate", ["src/"])
    if isinstance(roots, str):
        roots = [roots]
    if only is not None:
        targets = [k for k, m in metrics.items() if m.file in only]
    else:
        targets = sorted(touched)
    if not targets:
        rep.stage("mutation", "skip", started)
        return
    globs = mutation_globs(targets, roots)
    res = run(["mutmut", "run"] + globs, env, root, 3600)
    out = run(["mutmut", "results", "--all", "true"], env, root, 300)
    if out.returncode != 0 and not (out.stdout or "").strip():
        rep.stage("mutation", "fail", started)
        rep.findings.append(Finding(CAT_CONFIG, "mutmut-failed", "mutmut failed (exit %d): %s" % (res.returncode, _tail(res))))
        return
    files = {m.file for m in metrics.values()}
    survivors = [name for name, status in parse_mutmut_results(out.stdout or "") if status == "survived"]
    target_set = set(targets)
    for name in survivors:
        key = mutant_to_key(name, files, roots)
        if key in target_set:
            rep.findings.append(Finding(CAT_MUTATION, key,
                                        "surviving mutant %s in a touched function; kill it or mark "
                                        "`# pragma: no mutate  # equivalent: <reason>`" % name))
    base_total = (baseline.get("mutation") or {}).get("survived_total")
    if base_total is not None and len(survivors) > base_total and not rep.failed():
        rep.findings.append(Finding(CAT_MUTATION, "survived_total",
                                    "%d surviving mutants exceed baseline %d" % (len(survivors), base_total),
                                    len(survivors), base_total))
    rep.stage("mutation", "fail" if rep.failed() else "pass", started)


def build_parser():
    ap = argparse.ArgumentParser(prog="gate.py", allow_abbrev=False,
                                 description="Deterministic quality gate (ruff, pyright, pytest, CRAP, mutation).")
    level = ap.add_mutually_exclusive_group()
    level.add_argument("--fast", action="store_true", help="default: static checks, tests, CRAP, contracts, markers")
    level.add_argument("--full", action="store_true", help="--fast plus mutation testing (mutmut)")
    ap.add_argument("--files", nargs="+", metavar="PATH", help="restrict CRAP and mutation to these files")
    ap.add_argument("--json", action="store_true", help="print the JSON report on stdout")
    ap.add_argument("--init-baseline", action="store_true", help="write %s if absent" % BASELINE_NAME)
    ap.add_argument("--accept-baseline", action="store_true", help="overwrite the baseline (requires --yes; humans only)")
    ap.add_argument("--yes", action="store_true", help="confirm --accept-baseline")
    ap.add_argument("--out-dir", metavar="DIR", help="report directory (default: $SEJA_QUALITY_DIR or _output/quality)")
    return ap


def _emit(rep, args, root, parent_env, anchored):
    payload = rep.payload()
    if anchored:
        out_dir = args.out_dir or parent_env.get("SEJA_QUALITY_DIR") or os.path.join(root, "_output", "quality")
        try:
            os.makedirs(out_dir, exist_ok=True)
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            with open(os.path.join(out_dir, "gate-%s.json" % stamp), "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
        except OSError as err:
            sys.stderr.write("warning: cannot write report: %s\n" % err)
    if args.json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        for st in payload["stages"]:
            sys.stderr.write("[%s] %s (%.1fs)\n" % (st["status"], st["name"], st["seconds"]))
        for f in rep.findings:
            sys.stderr.write("[%d] %s: %s\n" % (f.category, f.key, f.message))
        sys.stderr.write("%s (exit %d)\n" % (payload["status"], payload["exit_code"]))
    return payload["exit_code"]


def main(argv=None, run=None, which=None, cwd=None, env=None) -> int:
    args = build_parser().parse_args(argv)
    root = os.path.abspath(cwd or os.getcwd())
    parent_env = dict(os.environ if env is None else env)
    rep = Report("full" if args.full else "fast")
    anchored = True
    try:
        execute(args, run or default_run, which or shutil.which, root, parent_env, rep)
    except ConfigFail as err:
        rep.findings.append(Finding(CAT_CONFIG, err.key, err.message))
        anchored = err.key != "no-pyproject"
    return _emit(rep, args, root, parent_env, anchored)


if __name__ == "__main__":
    sys.exit(main())
