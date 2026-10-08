# Fixtures do teste-primeiro (plan-000013)

> **Ficticias.** Escritas pelo executor do plano; nenhum dado real, nenhum nome de pessoa ou organizacao. Regras: `.claude/references/general/implement-test-first.md` (ITF-NNN). Ferramentas: `build_checks.py`, `build_brief.py`, plugin `scenario_report.py.example`. Testes: `test_build_checks.py`, `test_build_brief.py`, `test_scenario_report.py`.

| Pasta | O que prova |
|---|---|
| `project/` | mini projeto: a feature de exemplo do plan-000010, `src/tasks.py` (codigo do step) e `tests/steps_defs.py` (step definitions com asserção real, constante, `raise` e condicional, para R4) |
| `reports/red-*.json` | relatorios do plugin para cada caso do `red-check` (R1..R8); `suite-base.json` e a linha de base de R6 |
| `reports/green-*.json` | relatorios para o `green-check` (ITF-009) |
| `cucumber/` | o mesmo vermelho lido do Cucumber JSON (CYC-027) e do JUnit (step indefinido, `@skip`) |
| `coverage/` | cobertura da rodada vermelha que exerce e que nao exerce o corpo de `src/tasks.py` (R7) |
| `skeleton/` | esqueleto valido e invalido (ITF-004) |
| `scope/cases.json` | um caso por papel, com e sem violacao (ITF-007, ITF-008) |
| `uncovered/` | diff `-U0` e cobertura so de cenarios (ITF-018) |
| `baseline/` | `quality-baseline.json` igual e movido (ITF-017) |
| `gate/` | saidas do portao e um `gate.json` com chave desconhecida (ITF-015) |
| `brief/` | saidas de ferramenta que entram nos briefings (ITF-012) |
| `plans/v1-hashes.json` | hash dos dois planos v1 de `plan_format/` (copias do plan-000007): o golden de `route` exige que nao mudem |
