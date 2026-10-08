#!/usr/bin/env python3
# designer: When I hand one part of a step to a fresh agent, I give it only what its job
#   needs -- the tester sees the scenarios, the coder sees why the test failed, the cleaner
#   sees only the tangled functions, the hardener sees only the mutants that survived -- and
#   I cut the extras before the scope rule, so no agent works from the whole plan or the chat.
"""
build_brief -- short briefing per role of the test-first branch (implement-test-first.md, ITF-012, ITF-013).

Invocation: skill-invoked (/implement)
Lifecycle: active

Writes one Markdown briefing to <out-dir> (default _output/tmp/) and prints its path (or a JSON
manifest with --json). Each briefing has a manifest of what went in and a cap in characters
(default 24 000, PIPELINE_BRIEF_MAX): above the cap the optional context is cut, never the rules or
the scope. Standard library only.

Exit codes: 0 written, 2 usage error or unreadable input.

Usage:
    python3 .claude/skills/scripts/build_brief.py --role <tester|coder|cleaner|hardener> --plan <plan.md>
        --step N [--feature <slug>] [--root <project>] [--steps-dir <dir>] [--source-root <dir>]
        [--tool-output <json>] [--out-dir <dir>] [--max-chars N] [--json]
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_features as cf
from artifact_id import ARTIFACT_ID

SCHEMA_VERSION = 1
PIPELINE_BRIEF_MAX = 24000
ROLES = ("tester", "coder", "cleaner", "hardener")
_STEP_RE = re.compile(r"^###\s+Step\s+(\d+)\s*:")
_KEY_RE = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)*/[^/:`]+\.feature::[^`]+)`")
_STEP_DECOS = {"given", "when", "then", "step"}

CLOSING = ("## Resultado\n\nO resultado é o que a ferramenta devolver, não o que você escrever. "
           "Qualquer arquivo fora do escopo é violação e a ferramenta o recusa.")

SCOPE = {
    "tester": ("## Escopo\n\nVocê só cria ou muda: arquivos de teste, definições de passo, `conftest.py` e "
               "esqueleto nos arquivos de código do step. Você não muda `.feature`, portão, hooks, settings, "
               "`quality-baseline.json` nem `conventions.md`."),
    "coder": ("## Escopo\n\nVocê muda código-fonte e testes que não estão congelados. Você não muda `features/**`, "
              "os arquivos congelados abaixo, portão, hooks, settings, `quality-baseline.json` nem `conventions.md`."),
    "cleaner": ("## Escopo\n\nVocê só muda código-fonte. Nenhum arquivo de teste, nenhum `.feature`, nada do portão. "
                "O comportamento não muda: os testes continuam verdes e a interface do step fica igual."),
    "hardener": ("## Escopo\n\nVocê só cria testes novos (ou muda testes não congelados) e acrescenta linhas de "
                 "pragma com motivo no código. Nenhuma outra mudança de código-fonte."),
}

RULES = {
    "tester": ("## Regras do vermelho\n\n"
               "- Escreva um teste por cenário, ligado pela chave de cenário, antes de qualquer código.\n"
               "- No código do step, só esqueleto: assinatura e corpo `pass`, `...`, docstring, `return` de literal "
               "ou `raise NotImplementedError`. Sem lógica (ITF-004).\n"
               "- O teste falha no passo Então, por asserção sobre o resultado (R2, R3).\n"
               "- Nada de asserção constante: `assert False`, `raise AssertionError` sem condição, `pytest.fail` (R4).\n"
               "- O teste chama o esqueleto do step (R7). O resto da suíte continua como estava (R6).\n"
               "- Reuse as definições de passo que já existem; definição duplicada é erro (GHK-015)."),
    "coder": ("## Regras do verde\n\n"
              "- Escreva o mínimo de código para os cenários do step passarem.\n"
              "- Só `passed` conta: skip, xfail e erro não são verde (ITF-009).\n"
              "- Depois do verde, o portão rápido precisa passar nos arquivos tocados."),
    "cleaner": ("## Regras da limpeza\n\n"
                "- Reduza a complexidade das funções listadas até o alvo, sem mudar o comportamento.\n"
                "- Não crie funções de uma linha só para baixar o número.\n"
                "- Os testes não mudam e continuam verdes; o portão rápido precisa passar."),
    "hardener": ("## Regras do endurecimento\n\n"
                 "- Para cada mutante sobrevivente, escreva um teste que o mate.\n"
                 "- Se o mutante for equivalente (não muda o comportamento), anote a linha com "
                 "`# pragma: no mutate  # equivalent: <motivo>`. Pragma sem motivo falha o portão.\n"
                 "- Para cada sobrevivente, escreva também uma pergunta curta ao usuário, em português, sem número "
                 "técnico: \"Se <o código fizesse outra coisa>, nenhum teste perceberia. Isso importa para você?\"\n"
                 "- Não se mede por percentual: o alvo é zero sobrevivente sem explicação."),
}


# ---------------------------------------------------------------------------
# Readers (pure)
# ---------------------------------------------------------------------------


def step_block(plan_text: str, step: int) -> str:
    lines = plan_text.splitlines()
    out, inside = [], False
    for line in lines:
        m = _STEP_RE.match(line)
        if m:
            if inside:
                break
            inside = int(m.group(1)) == step
        elif inside and line.startswith(("## ", "### ")):
            break
        if inside:
            out.append(line)
    if not out:
        raise ValueError(f"step {step} não existe no plano")
    return "\n".join(out).strip()


def owned_keys(block: str) -> list[str]:
    for line in block.splitlines():
        if "**Scenarios**" in line:
            return _KEY_RE.findall(line)
    return []


def scenario_texts(root: Path, slug: str, keys) -> dict[str, str]:
    """Raw Gherkin of each owned scenario (tags, title, steps, examples)."""
    out: dict[str, str] = {}
    wanted = set(keys)
    for path in sorted((Path(root) / "features" / slug).glob("*.feature")):
        text = path.read_text(encoding="utf-8-sig")
        lines = text.splitlines()
        feature = cf.parse_feature(text)
        starts = []
        for sc in feature.scenarios:
            first = min([t.line for t in sc.tags] + [sc.line])
            starts.append((first, sc))
        starts.sort(key=lambda x: x[0])
        for i, (first, sc) in enumerate(starts):
            key = cf.scenario_key(slug, str(path), sc.name)
            if key not in wanted:
                continue
            end = starts[i + 1][0] - 1 if i + 1 < len(starts) else len(lines)
            chunk = lines[first - 1:end]
            while chunk and not chunk[-1].strip():
                chunk.pop()
            out[key] = "\n".join(chunk)
    return out


def _deco_pattern(deco: ast.expr) -> tuple[str, str] | None:
    if not isinstance(deco, ast.Call) or not deco.args:
        return None
    func = deco.func
    name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else ""
    if name not in _STEP_DECOS:
        return None
    arg = deco.args[0]
    if isinstance(arg, ast.Call) and arg.args:
        arg = arg.args[0]
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return name, arg.value
    return None


def step_index(steps_dir: Path) -> list[str]:
    rows = []
    for path in sorted(Path(steps_dir).rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for deco in node.decorator_list:
                    found = _deco_pattern(deco)
                    if found:
                        rows.append(f"- {found[0]}: `{found[1]}` ({path.name}:{node.lineno})")
    return rows


def function_source(source_root: Path, key: str) -> str | None:
    """Source of `<file>::<Class.method>` (or `<file>::<function>`)."""
    if "::" not in key:
        return None
    rel, qual = key.split("::", 1)
    try:
        text = (Path(source_root) / rel).read_text(encoding="utf-8-sig")
        tree = ast.parse(text)
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None

    def walk(nodes, prefix):
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = prefix + node.name
                if name == qual and not isinstance(node, ast.ClassDef):
                    segment = ast.get_source_segment(text, node) or ""
                    return textwrap.dedent(" " * node.col_offset + segment)
                found = walk(node.body, name + ".")
                if found:
                    return found
        return None

    return walk(tree.body, "")


def test_files(source_root: Path) -> list[str]:
    root = Path(source_root)
    return sorted(str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("test_*.py"))


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def _assemble(sections: list[tuple[str, str, bool]], max_chars: int) -> dict:
    required = sum(len(text) + 2 for _n, text, req in sections if req)
    budget = max_chars - required
    manifest, parts, truncated = [], [], required > max_chars
    for name, text, req in sections:
        include = req or len(text) + 2 <= budget
        if not req:
            if include:
                budget -= len(text) + 2
            else:
                truncated = True
        manifest.append({"item": name, "chars": len(text), "required": req, "included": include})
        if include:
            parts.append(text)
    text = "\n\n".join(parts) + "\n"
    return {"schema_version": SCHEMA_VERSION, "text": text, "manifest": manifest, "truncated": truncated,
            "chars": len(text)}


def build_brief(role: str, plan_text: str, step: int, *, root: Path | None = None, feature: str | None = None,
                steps_dir: Path | None = None, source_root: Path | None = None, tool_output: dict | None = None,
                max_chars: int = PIPELINE_BRIEF_MAX) -> dict:
    if role not in ROLES:
        raise ValueError(f"papel desconhecido: {role}")
    tool_output = tool_output or {}
    head = f"# Briefing -- {role}, step {step}\n\nUm trabalho, depois destruído. Leia só isto."
    sections: list[tuple[str, str, bool]] = [("cabeçalho", head, True), ("regras", RULES[role], True)]
    if role in ("tester", "coder"):
        block = step_block(plan_text, step)
        sections.append(("step", "## O step\n\n" + block, True))
        keys = owned_keys(block)
        if root is not None and feature and keys:
            texts = scenario_texts(Path(root), feature, keys)
            gherkin = "\n\n".join(f"```gherkin\n{texts[k]}\n```" for k in keys if k in texts)
            if gherkin:
                sections.append(("gherkin", "## Os cenários deste step\n\n" + gherkin, True))
    if role == "tester" and steps_dir is not None:
        rows = step_index(Path(steps_dir))
        if rows:
            sections.append(("índice de passos", "## Definições de passo que já existem\n\n" + "\n".join(rows), False))
    if role == "coder":
        message = tool_output.get("message") or ""
        if message:
            sections.append(("red-check", "## Por que o teste falhou\n\n" + message, True))
        frozen = tool_output.get("frozen") or []
        if frozen:
            sections.append(("congelados", "## Arquivos congelados\n\n" + "\n".join(f"- `{f}`" for f in frozen), True))
    if role == "cleaner":
        rows = [f"- CRAP({f['key']})={f['crap']:g} (CC={f['cc']}, cov={f['cov']:g}) > {f['target']:g}: dividir"
                for f in tool_output.get("findings", [])]
        sections.append(("crap", "## Funções acima do alvo\n\n" + ("\n".join(rows) or "- nenhuma"), True))
        for f in tool_output.get("findings", []):
            src = function_source(source_root, f["key"]) if source_root else None
            if src:
                sections.append((f"corpo {f['key']}", f"### `{f['key']}`\n\n```python\n{src}\n```", False))
    if role == "hardener":
        rows = []
        for s in tool_output.get("survivors", []):
            rows.append(f"### `{s['mutant']}` em `{s['key']}`\n\n```diff\n{s.get('diff', '')}\n```")
        sections.append(("sobreviventes", "## Mutantes sobreviventes\n\n" + ("\n\n".join(rows) or "- nenhum"), True))
        for key in sorted({s["key"] for s in tool_output.get("survivors", [])}):
            src = function_source(source_root, key) if source_root else None
            if src:
                sections.append((f"corpo {key}", f"### `{key}`\n\n```python\n{src}\n```", False))
        if source_root:
            files = test_files(Path(source_root))
            if files:
                sections.append(("testes", "## Testes que já existem\n\n" + "\n".join(f"- `{t}`" for t in files),
                                 False))
    sections += [("escopo", SCOPE[role], True), ("resultado", CLOSING, True)]
    return _assemble(sections, max_chars)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _plan_id(path: Path) -> str:
    # The lookahead keeps the legacy branch from taking the first six digits of a new ID.
    m = re.match(rf"(plan-{ARTIFACT_ID})(?![0-9A-Za-z])", path.name)
    return m.group(1) if m else path.stem


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="build_brief.py", description="Briefing per role (ITF-012).")
    ap.add_argument("--role", required=True, choices=ROLES)
    ap.add_argument("--plan", required=True, type=Path)
    ap.add_argument("--step", required=True, type=int)
    ap.add_argument("--feature")
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--steps-dir", type=Path)
    ap.add_argument("--source-root", type=Path)
    ap.add_argument("--tool-output", type=Path)
    ap.add_argument("--out-dir", type=Path, default=Path("_output") / "tmp")
    ap.add_argument("--max-chars", type=int, default=PIPELINE_BRIEF_MAX)
    ap.add_argument("--json", action="store_true")
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    try:
        plan_text = args.plan.read_text(encoding="utf-8-sig")
        tool = json.loads(args.tool_output.read_text(encoding="utf-8-sig")) if args.tool_output else None
        brief = build_brief(args.role, plan_text, args.step, root=args.root, feature=args.feature,
                            steps_dir=args.steps_dir, source_root=args.source_root or args.root, tool_output=tool,
                            max_chars=args.max_chars)
        out = args.out_dir / f"brief-{_plan_id(args.plan)}-step-{args.step}-{args.role}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(brief["text"], encoding="utf-8")
    except (OSError, ValueError, UnicodeDecodeError) as err:
        print(f"build_brief: {err}", file=sys.stderr)
        return 2
    if brief["truncated"]:
        print(f"build_brief: briefing cortado no teto de {args.max_chars} caracteres", file=sys.stderr)
    if args.json:
        result = {k: v for k, v in brief.items() if k != "text"}
        result["path"] = str(out)
        sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
