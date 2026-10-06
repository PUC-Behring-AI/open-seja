---
designer_description: "When one execution of the control protocol finishes, I'm the record of that run -- arm, order, replica, versions, oracle hash, timestamps, matrices, per-step report, O1 and the designer's words -- so the pilot can compare runs without guessing what happened."
---

# Template: Pilot Run Record

Registro de **uma execução** do protocolo de controle (`.claude/references/general/drift-control-protocol.md`). Um arquivo por execução, em `features/<slug>/pilot/<braco>-r<N>.md` do repositório do piloto, ou no caminho que o plan-000016 fixar. Os termos de medida vêm de `.claude/references/general/drift-metric.md`.

Idioma: pt-BR (prosa), identificadores em en-US. As palavras do designer são registradas literalmente (verbatim), atribuídas.

## Campos

| Campo | Conteúdo | Fonte |
|---|---|---|
| `feature` | slug da feature | brief |
| `braco` | `A` (padrão) ou `B` (estendido) | sorteio registrado |
| `ordem` | posição do braço entre os dois da feature (`1` ou `2`) | sorteio registrado |
| `replica` | `r1`, `r2` ou `r3` | protocolo seção 5 |
| `commit_inicial` | SHA do commit de partida | git |
| `versao_harness` | tag do harness (`v0.10.x` no A) | `.seja-version` |
| `versao_modelo` | identificador do modelo | sessão |
| `hash_oraculo` | SHA-256 do oráculo congelado | protocolo seção 3 |
| `t0` | primeira mensagem com o brief (UTC) | `conversation-trace.jsonl` ou `briefs.md` |
| `t_verde` | primeiro `gate full` PASS (UTC) | `gate.json` `ts`; sem portão: campo manual |
| `t_aprovada` | aceitação explícita do designer (UTC) | **campo manual** |
| `eventos_designer` | lista de timestamps UTC das falas do designer entre `t0` e `t_aprovada` | `conversation-trace.jsonl`; sem fonte: campo manual |
| `tempo_parede_min` | `t_aprovada - t0` | calculado |
| `tempo_atendido_min` | soma dos intervalos entre eventos do designer menores que 10 min | calculado |
| `iteracoes_ate_pass` | por step e total | progress file |
| `perguntas_grill` | número de perguntas do grill (só B) | `intent.md` / conversa |
| `matriz_M1`, `matriz_M2` | caminhos das matrizes congeladas | plan-000014 |
| `relatorio_D` | D1, D2, D3a, D3b com `cobertos/descobertos/não medido` e razão | `drift-metric.md` DRM-007 |
| `O1` | `falham/n` dos testes do oráculo no código final | protocolo seção 4 |
| `auditoria` | contagens `sim/parcial/nao` e REQs não auditados | `audit.json` |
| `medidores_citizen` | ajustes no specify; escapes antes vs depois; mutantes virados em REQ (só B) | `drift-metric.md` DRM-010 |
| `execucao_completa` | `sim` ou `nao` (motivo da parada) | protocolo seção 10 |
| `notas_designer` | palavras literais do designer, atribuídas | `/reflect` |

Regra de tempo: a fonte de `t_aprovada` não existe no harness. Quando `eventos_designer` não puder ser montado a partir do `conversation-trace.jsonl`, o `tempo_atendido_min` desta execução é `t_aprovada - t0` e o registro escreve isso em `notas_designer`.

## Modelo

```markdown
---
feature: <slug>
braco: A | B
ordem: 1 | 2
replica: r1 | r2 | r3
commit_inicial: <sha>
versao_harness: <tag>
versao_modelo: <id>
hash_oraculo: <sha256>
t0: YYYY-MM-DDTHH:MM:SSZ
t_verde: YYYY-MM-DDTHH:MM:SSZ | nao_medido
t_aprovada: YYYY-MM-DDTHH:MM:SSZ
eventos_designer: [YYYY-MM-DDTHH:MM:SSZ, ...]
tempo_parede_min: <n>
tempo_atendido_min: <n>
iteracoes_ate_pass: {total: <n>, por_step: {...}}
perguntas_grill: <n> | n/a
matriz_M1: <caminho> | nao_medido
matriz_M2: <caminho> | nao_medido
O1: {n: <n>, falham: <n>}
execucao_completa: sim | nao
---

## Relatório de D

| Degrau | n | cobertos | descobertos | não medido (razão) | D |
|---|---|---|---|---|---|
| D1 | | | | | |
| D2 | | | | | |
| D3a | | | | | |
| D3b | | | | | |

## Auditoria semântica

## Medidores do citizen (só B)

## Notas do designer (verbatim)
```

## Registro de exemplo (dados fictícios)

```markdown
---
feature: task-list
braco: B
ordem: 2
replica: r1
commit_inicial: 0000000000000000000000000000000000000000
versao_harness: v0.0.0-exemplo
versao_modelo: modelo-exemplo
hash_oraculo: 0000000000000000000000000000000000000000000000000000000000000000
t0: 2026-01-01T10:00:00Z
t_verde: 2026-01-01T10:52:00Z
t_aprovada: 2026-01-01T11:20:00Z
eventos_designer: [2026-01-01T10:00:00Z, 2026-01-01T10:04:00Z, 2026-01-01T10:09:00Z, 2026-01-01T10:30:00Z, 2026-01-01T10:34:00Z, 2026-01-01T10:41:00Z, 2026-01-01T11:20:00Z]
tempo_parede_min: 80
tempo_atendido_min: 20
iteracoes_ate_pass: {total: 5, por_step: {"1": 1, "2": 2, "3": 2}}
perguntas_grill: 6
matriz_M1: nao_medido
matriz_M2: nao_medido
O1: {n: 5, falham: 1}
execucao_completa: sim
---

## Relatório de D

| Degrau | n | cobertos | descobertos | não medido (razão) | D |
|---|---|---|---|---|---|
| D1 | 4 | 4 | 0 | 0 | 0.0 |
| D2 | 5 | 5 | 0 | 0 | 0.0 |
| D3a | 5 | 4 | 1 | 0 | 0.2 |
| D3b | 12 | 9 | 3 | 0 | 0.25 |
```

Conta do tempo atendido do exemplo: os intervalos entre eventos consecutivos do designer são 4, 5, 21, 4, 7 e 39 minutos. Os de 21 e de 39 minutos têm 10 minutos ou mais e não entram. Soma: 4 + 5 + 4 + 7 = 20 minutos. O relógio de parede é 10:00 até 11:20 = 80 minutos.
