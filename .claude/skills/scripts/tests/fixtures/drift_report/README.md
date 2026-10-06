# Fixtures do relatorio de divergencia

> **Simuladas.** Arvores fictícias de projeto, escritas pelo executor do plano. Nenhum dado real, nenhum nome de pessoa ou organizacao. Regras: `.claude/references/general/drift-report.md` (DRP-NNN). Teste: `test_drift_report.py`.

Cada caso e uma raiz de projeto com `features/contas-da-semana/` (intent.md, .feature, runner/, gate.json, drift/), um `plan.md`, um `status.txt` (resultado simulado de `check_specify.py --status`, lido por um stub nos testes) e um `esperado.json` com o que o relatorio traz: `degraus` completos, as `leituras` e `ressalvas` que o caso exercita e, quando houver, `delta`. As contagens foram escritas a mao, pelo cenario, e nao geradas pelo calculador.

| Caso | O que prova |
|---|---|
| `ok-m1` | feature completa no fim do IMPLEMENT: tudo coberto, 2 linhas tocadas sem teste de cenario |
| `ok-m2-deriva` | M2 depois da entrega: K3 vermelho e mais codigo tocado sem teste; M1 congelado ao lado |
| `stale` | status diz stale e o frontmatter diz scenarios: approved; D1 nao medido, o resto medido com ressalva |
| `sem-runner` | sem relatorio do runner: D2 e D3a nao medidos; D3b medido |
| `sem-adaptador-runner` | stack sem executor de cenarios: razao de adaptador, nao de relatorio |
| `sem-gate` | sem gate.json: D3a e D3b nao medidos |
| `sem-adaptador-gate` | stack sem portao (gate.json com adapter false) |
| `sem-registro-vermelho` | sem registro de vermelho: D3a nao medido com ressalva |
| `sem-cobertura` | coverage.json sem touched_uncovered: D3b nao medido por cobertura |
| `sem-base-diff` | sem coverage.json: D3b sem base do diff |
| `baseline-aceito` | gate PASS com baseline aceito: D3a descoberto com ressalva |
| `skip-xfail` | skip e xfail sao descobertos em D2 |
| `disabled` | cenario com tag @skip e omitido pelo runner: descoberto em D2 |
| `outline-pior` | Scenario Outline com duas linhas: vale o pior estado |
| `specify-pulado` | plano com Specify: skipped: nao aplicavel |
| `plano-v1` | plano v1 (sem plan_format_version): nao aplicavel, nada mais e lido |
| `sem-features` | projeto sem features/: nao aplicavel, uma linha |
| `denominador-zero` | unico REQ retirado e sem cenarios: todo D e n/a, nunca 0 |
| `denominador-muda` | REQ novo entre M1 e M2: o denominador muda de 3 para 4 |
| `auditoria` | audit.json com um nao: nenhum D muda, a coluna fica a parte |
| `escada-fechada` | D1, D2 e D3a zero e a auditoria diz nao: leitura de alerta |
| `oraculo` | oracle-result.json: O1 aparece em leituras |
| `d0-residuo` | frase F6 do pedido sem requisito: D0 lista o residuo |
| `retraducao-pos-codigo` | retradução depois do código: três textos lado a lado por REQ |
| `leitura-reversa` | intencao nascida depois da adocao e sem feature aparece; a anterior nao |
| `entrada-corrompida` | gate.json invalido: erro de leitura com o nome do arquivo (exit 2) |
