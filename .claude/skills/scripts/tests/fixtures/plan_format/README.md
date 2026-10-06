# Fixtures de formato de plano

Documentam a regra de versao de `plan_format_version` (ver `## Compatibilidade` em `.claude/references/general/extended-cycle-contract.md`, CYC-018). Nenhum validador le estas fixtures hoje; o validador e do plan-000012.

| Arquivo | O que prova |
|---|---|
| `v1-plan-with-tests.md` | Plano v1 real, com steps de codigo e `Tests:`. Nao tem `Scenarios:` e continua valido para sempre. |
| `v1-plan-doc-only.md` | Plano v1 real, de documentacao (`Tests: N/A`). Tambem valido sem `Scenarios:`. |
| `v2-valid.md` | Plano v2 ficticio valido: step com `Tests:` nao-N/A tem `Scenarios:`; step com `Tests: N/A` usa `Scenarios: N/A (motivo)`. |
| `v2-invalid-missing-scenarios.md` | Plano v2 ficticio INVALIDO: Step 1 tem `Tests:` nao-N/A sem `Scenarios:`. O `/implement` para a execucao neste caso. |

Os dois planos v1 sao copias literais de planos do ledger; nao editar.
