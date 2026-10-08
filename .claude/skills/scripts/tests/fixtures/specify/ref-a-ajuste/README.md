# Execução de referência (a) -- feature com código, uma rodada de ajuste

> **Simulada.** Roteiro escrito pelo executor do plan-000011; nenhuma pessoa real respondeu. "usuario" é um papel (citizen e, em outro papel, quem lê código).

Entrada: o `intent.md` aprovado de contas da semana (3 REQs, um `restrição`). Saída: `.feature` e retradução aprovados, lock gravado.

| Versão | O que é | `check_specify.py --feature contas-da-semana` |
|---|---|---|
| `v1-proposta/` | primeira escrita do agente: um step com endereço (termo técnico) e o REQ 002 sem cenário nem item | exit 1: SPC-003 (REQ 002), SPC-008 (GHK-013 aviso), SPC-017 (REQ 002 fora da retradução) |
| `v2-mostrada/` | depois de **uma** autocorreção do agente; é o que o citizen vê | exit 0, `draft` |
| `v3-sem-mudanca/` | ajuste pedido pelo citizen, mas o agente esqueceu a linha em Mudanças | exit 1: SPC-011 |
| `v3-ajustada/` | ajuste com a linha em Mudanças; aprovação com `--approve` | exit 0; grava `intent-final.md` e `lock-final.json` |

## Transcrição (resumo)

1. O agente escreve `v1-proposta`. Roda `check_specify.py`. Saída: 3 achados (ver `v1-proposta/esperado.json`).
2. O agente corrige sozinho: troca "Quando eu abro https://app.local/contas" por "Quando eu abro a tela inicial", escreve os dois cenários do REQ 002 e o item da retradução com o exemplo. Roda de novo: nenhum achado (`v2-mostrada`). Uma autocorreção.
3. O agente mostra ao citizen a retradução de `v2-mostrada` (nunca o `.feature`) e pergunta: Aprovar / Ajustar / Voltar à entrevista / Descartar.
4. Citizen: "Ajustar. No primeiro exemplo, segunda-feira não importa. Para mim a semana é de hoje até daqui a sete dias." É um ajuste de **como se diz**: o REQ 001 já diz "próximos 7 dias".
5. O agente reescreve o exemplo do REQ 001, sobe `rev: 2` e registra `Retradução rev 2` em Mudanças (`v3-ajustada`). O `.feature` não muda: o contrato já dizia isso.
6. Citizen: Aprovar. Quem lê código (o mesmo usuário, em outro papel) vê o `.feature` e a saída do verificador: Aprovar o contrato.
7. `check_specify.py --feature contas-da-semana --approve --at 2026-10-06T15:00Z --by usuario --contract-by usuario`: exit 0.

Desvio em relação ao roteiro do plano: o plano usava o ajuste "o limite é 3 segundos, não 2". Esse pedido muda **o que** se quer (o critério do REQ 003), e pela SPC-011 volta à grill; não é ajuste da specify. O ajuste foi trocado por um de forma.

Calibração (roteiro, não sessão observada): 1 rodada de ajuste; 1 autocorreção antes do resumo; 1 aviso de voz/estilo na proposta (GHK-013), 0 na versão mostrada. Entendimento do citizen sem pedir reformulação: **não medido** (não houve pessoa).
