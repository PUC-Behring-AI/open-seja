# Fixtures golden do drift-metric

Contrato de teste do calculador de divergência (plan-000014). Regras em `.claude/references/general/drift-metric.md`. Feature fictícia; nenhum dado real.

`casos.json` tem seis casos, cada um com `entrada` (matriz) e `esperado` (relatório do DRM-007).

- `normal`: 10 REQs, 12 cenários; mistura de cobertos e descobertos nos quatro degraus (D1 8/2, D2 10/2, D3a 8/2, D3b 43/7).
- `nada-medido`: sem `gate.json`; D3a e D3b `não medido`, `D = "n/a"`.
- `specify-pulado`: `Specify: skipped`; relatório "não aplicável" (`NM-SPECIFY-PULADA`).
- `orfao-e-sem-tag`: um cenário sem tag e uma tag sem REQ; contados fora do D.
- `escada-fechada`: D1 = D2 = D3a = 0 e O1 > 0; liga o alerta `escada_fechou_sem_capturar`.
- `amostra-pequena`: 5 REQs; ressalva `amostra pequena`.
