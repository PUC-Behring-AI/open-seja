# Fixtures -- fase grill (plan-000009, Step 6)

> **Simuladas.** As três entrevistas são fictícias, escritas pelo executor do plano. Nenhuma pessoa real respondeu; o "citizen" é um papel. Nenhum dado real, nenhum nome de pessoa ou organização. Os números de calibração (rodadas, perguntas) são do roteiro, não de uma sessão observada.

Regras: `.claude/references/general/grill-phase.md`. Verificador: `.claude/skills/scripts/check_intent.py`. Teste: `test_check_intent.py` (lê `esperado.json`).

| Pasta | Situação (GRL-012) | Versões | Esperado com `--require-approved` |
|---|---|---|---|
| `a-feature-com-codigo/` | feature com código, 3 rodadas | `intent-rodada-1.md`, `intent-rodada-2.md`, `intent-final.md` | rodada 1: P1, P3, P6; rodada 2: P2, P3, P6; final: nenhum error |
| `b-tarefa-sem-codigo/` | tarefa sem código, entrevista curta | `plano-trecho.md` (seção `## Intenção` e `Specify: skipped`) | sem `intent.md`; `check_intent.py` não se aplica |
| `c-brief-detalhado/` | brief já detalhado, 1 rodada de confirmação | `intent-rodada-0.md`, `intent-final.md` | rodada 0: P1, P3, P6; final: nenhum error |

D0 (`--d0`): na rodada 1 de (a), F2 ainda não virou requisito; em (c), F3 ficou só em premissa nas duas versões. É leitura, não portão (DRM-010).

## Roteiro de execução manual

1. Num projeto de teste com `/design` feito, rode `/plan --grill` com o brief de `a-feature-com-codigo/transcricao.md`.
2. Responda como o citizen da transcrição. Depois de cada rodada, compare `features/reserva-de-sala/intent.md` com a versão da rodada.
3. Rode `python3 .claude/skills/scripts/check_intent.py features/reserva-de-sala/intent.md --require-approved` e confira as regras da tabela acima.
4. Anote: rodadas, perguntas por rodada, avisos de voz e quantas perguntas o citizen pediu para reformular.
5. Repita com (b) usando `/plan` e confira que o plano tem `## Intenção` e `Specify: skipped`, e que nenhuma pasta `features/` foi criada.
