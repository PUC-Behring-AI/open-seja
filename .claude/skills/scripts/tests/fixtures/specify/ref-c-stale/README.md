# Execução de referência (c) -- mudança de intenção depois da aprovação

> **Simulada.** Nenhuma pessoa real respondeu.

| Versão | O que é | Esperado |
|---|---|---|
| `v1-aprovado/` | specify aprovada (lock gravado) | `--status`: `approved` |
| `v2-intencao-mudou/` | o citizen voltou à grill: o REQ 002 agora diz que o desfazer vale por 1 dia (`rev` 2), e a intenção foi reaprovada | `--status`: `stale` (`req-rev`; REQ 002); a checagem completa não acha erro: o cenário antigo ainda cobre o REQ, mas a aprovação é velha |
| `v3-reescrito/` | a fase reescreve só os cenários e o item do REQ 002, mantém os nomes dos outros cenários, sobe a retradução para `rev: 2` e reaprova | `--approve` sai 0; o lock é regravado com o REQ 002 em `rev` 2; depois, `approved` |

Varredura (`check_specify.py` sem argumentos) sobre `v2-intencao-mudou`: sai 1 ("aprovação velha"), porque o frontmatter ainda diz `scenarios: approved`.
