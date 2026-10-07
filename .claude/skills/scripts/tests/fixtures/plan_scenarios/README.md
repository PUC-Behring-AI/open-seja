# Fixtures de plano a partir de cenarios (plan-000012)

> **Simuladas.** Todos os casos sao ficticios, escritos pelo executor do plano. Os dois planos v1 reais (`v1-real-1`, `v1-real-2`) sao copias literais das fixtures de `plan_format/` (nao editar). Nenhum dado real, nenhum nome de pessoa ou organizacao.

Regras: `.claude/references/general/plan-from-scenarios.md` (PFS-NNN). Verificador: `.claude/skills/scripts/check_plan_scenarios.py`. Teste: `test_check_plan_scenarios.py` (le `esperado.json`).

Cada caso e uma pasta com `plan.md` e `esperado.json`:

- `root`: raiz de projeto (relativa a esta pasta) onde `features/<slug>/` mora, ou `null` quando o plano nao usa feature. As raizes ficam em `_raizes/` (copias das fixtures de `specify/`): `aprovada` (lock bate), `rev2` (a mesma, com `rev: 2` no lock), `stale` (rev de um REQ subiu depois da aprovacao), `draft` (sem lock), `missing` (sem `.feature`).
- `status`: estado SPC-013 que o `check_specify.py --status` devolve para a raiz (o teste usa um stub com esse valor; o Step 7 confere contra o script real).
- `exit_code`, `findings` (`[regra, gravidade, linha]` exatos, ordenados por linha e regra) e `matrix` (chave -> numeros dos steps; `null` quando nao se aplica).

Linha de cada achado: campo do step (`Scenarios:` ou `Tests:`) quando o achado e do campo; titulo `### Step N:` quando o campo falta; linha `Feature:` para cenario sem step (PFS-009); linha `Specify:` para PFS-011, PFS-012 e PFS-014; linha `plan_format_version:` para PFS-001; linha 1 quando falta `Specify:`.

| Caso | O que prova |
|---|---|
| `v1-real-1` | plano v1 real, com steps de codigo e Tests: (copia literal) |
| `v1-real-2` | plano v1 real, de documentacao (copia literal) |
| `v1-minimo` | plano sem plan_format_version (v1 implicito); Tests nao-N/A sem Scenarios nao e achado |
| `v1-corpo-quebrado` | v1 nunca e lido alem do cabecalho (PFS-001): corpo invalido sai 0 |
| `v2-completo` | v2 valido: 4 cenarios, 5 steps (3 com chaves, 1 migracao N/A, 1 refactor N/A); cada cenario em um step so |
| `v2-outline` | v2 valido: o Scenario Outline (A lista abre logo com muitas contas) e uma chave so, citada uma vez |
| `v2-skipped` | v2 pulado: documentacao; todos Tests: N/A; Scenarios ausente ou N/A |
| `v2-cabecalho-livre` | v2 valido: linhas do cabecalho em outra ordem e com bloco Origem no meio (cabecalho = antes da primeira secao) |
| `pfs-006-na-com-testes` | Tests nao-N/A com N/A (motivo): valido pelo contrato; achado info para o piloto (nao bloqueia) |
| `pfs-001-versao-3` | versao desconhecida: exit 2 |
| `pfs-002-sem-specify` | v2 sem Specify: |
| `pfs-002-approved-sem-feature` | approved sem Feature: |
| `pfs-002-skipped-com-feature` | skipped com Feature: |
| `pfs-002-skipped-sem-motivo` | skipped sem motivo |
| `pfs-002-feature-sem-pasta` | Feature: sem pasta features/<slug>/ |
| `pfs-002-specify-duplicada` | Specify: duas vezes (a segunda e o achado) |
| `pfs-003-sem-campo` | step com Tests: N/A e sem Scenarios: |
| `pfs-004-sem-crases` | chave sem crases: nao conta como citada (PFS-009 tambem) |
| `pfs-004-tag-req` | @REQ- no lugar da chave (decisao 3 = A): dica 'use o nome do cenario' |
| `pfs-004-slug-diferente` | slug da chave diferente do Feature: |
| `pfs-004-duplicata` | mesma chave duas vezes no mesmo step |
| `pfs-005-renomeado` | cenario renomeado (chave fora do index): PFS-005 e o original fica sem step (PFS-009) |
| `pfs-006-sem-campo-com-testes` | Tests nao-N/A e Scenarios ausente (o cenario do step 4 foi para o step 2) |
| `pfs-007-na-enchimento` | N/A (n/a) |
| `pfs-007-na-curto` | motivo com menos de 3 palavras |
| `pfs-007-na-sem-motivo` | N/A sem parenteses |
| `pfs-008-chave-sem-teste` | chave citada com Tests: N/A |
| `pfs-009-cenario-sem-step` | cenario aprovado que nenhum step cita; o step com Tests nao-N/A e N/A (motivo) so da info |
| `pfs-010-dois-donos` | o mesmo cenario em dois steps com teste (dono unico, decisao 2 = A) |
| `pfs-011-stale` | estado dos cenarios stale: refaca a specify |
| `pfs-011-draft` | estado dos cenarios draft: refaca a specify |
| `pfs-011-missing` | estado dos cenarios missing: refaca a specify |
| `pfs-012-rev-velho` | cabecalho rev 1 com lock rev 2: plano velho em relacao a ultima aprovacao |
| `pfs-012-rev-igual` | cabecalho rev 2 com lock rev 2 (negativo de PFS-012) |
| `pfs-013-skipped-com-testes` | skipped e step com Tests nao-N/A sem Scenarios N/A (motivo) |
| `pfs-013-skipped-na-com-motivo` | skipped com Tests nao-N/A e N/A (motivo): passa com info |
| `pfs-013-skipped-com-chave` | plano pulado nao tem cenario para citar |
| `pfs-014-nenhum-step` | aprovado e nenhum step cita cenario: 4x PFS-009 e dica PFS-014 |
| `pfs-002-opt-out-sem-motivo` | opt-out sem motivo: erro, nunca legado (emenda 000022) |
| `pfs-002-opt-out-motivo-curto` | opt-out com motivo que nao passa no PFS-007 |
| `pfs-002-default-off-com-cabecalho-on` | default off com `Specify default: on`: incoerencia do cabecalho |
| `pfs-002-default-off-sem-linha` | default off sem a linha `Specify default:` (ausente = on): incoerencia do cabecalho |
| `pfs-002-opt-out-com-default-off` | opt-out com `Specify default: off`: com off o `--without-specify` nao faz nada |
| `pfs-002-opt-out-maiusculo` | `Opt-out: <motivo>` com maiuscula: grafia proxima da classe e erro, nunca legado |
| `pfs-002-default-off-hifen` | `default-off` com hifen: grafia proxima da classe e erro, nunca legado |
| `pfs-002-specify-default-invalido` | `Specify default:` com valor fora de on e off |
| `pfs-002-specify-default-duplicado` | `Specify default:` duas vezes (a segunda e o achado) |
| `pfs-013-sem-classe-legado` | motivo sem classe e sem acento (legado = tarefa sem codigo): Tests nao-N/A sem Scenarios continua erro |
| `pfs-013-legado-parenteses-na-com-motivo` | legado com parenteses: Tests nao-N/A com N/A (motivo) continua info |
| `pfs-013-default-off-sem-na` | default off: step de teste sem `Scenarios: N/A (motivo)` e step com chave sao erro, com a dica da specify desligada |
| `pfs-016-opt-out-com-testes` | opt-out com `Specify default: on` e teste real com N/A (motivo): so o info PFS-016, sai 0 |
| `pfs-016-opt-out-sem-linha` | opt-out sem a linha `Specify default:` (ausente = on): info PFS-016 |
| `pfs-016-approved-com-default-off` | approved com `Specify default: off`: info PFS-016 |
| `pfs-016-default-off-com-testes` | default off com off e teste real com N/A (motivo): segue o braco, nenhum achado (negativo de PFS-016 e do info do PFS-013) |

## Execucoes de referencia (plan-000012, Step 7; SIMULADAS)

Tres execucoes do `/plan` em modo descartavel, feitas pelo executor do plano (nenhuma pessoa real). Cada pasta `ref-*/NN-*/` e uma versao do plano, com a saida esperada do verificador:

| Pasta | O que mostra |
|---|---|
| `ref-a-feature-com-codigo/01-rascunho` -> `02-final` | feature com codigo: o rascunho tem um cenario sem step e um step sem cenario (PFS-009, PFS-006); uma correcao e o plano sai 0 |
| `ref-b-sem-codigo/01-final` | tarefa sem codigo (README): `Specify: skipped -- <motivo>`, sai 0 |
| `ref-b-sem-codigo/02-variante-recusada` | a mesma tarefa com um step de teste: PFS-013 |
| `ref-c-cenarios-reaprovados/01..03` | o `.feature` muda (stale, PFS-011); reaprovado com rev 2 e cenario renomeado (PFS-012, PFS-005, PFS-009); plano atualizado a mao sai 0 |

Raizes novas: `_raizes/editada` (o `.feature` editado e o `intent.md` com rev 2 e linhas em Mudancas, sem reaprovar: `stale`) e `_raizes/reaprovada` (a anterior depois de `check_specify.py --approve`: lock com `rev: 2`, chave renomeada).
