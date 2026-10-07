# Logs

Diarios e resumos de periodo, mantidos pelo assistente (skills `daily-log`, `weekly-review`, `compress`).

## Estrutura

```
logs/
├── README.md          # este arquivo
├── log.md             # log operacional das skills
├── YYYY/              # uma pasta por ano
│   └── YYYY-MM-DD.md  # um diario por dia; o nome e so a data
└── Resumos/
    ├── YYYY-Www.md    # semana ISO
    ├── YYYY-MM.md     # mes
    └── YYYY-Qn.md     # trimestre
```

## Frontmatter

- Diario: `tipo: diario`, `data: YYYY-MM-DD`, `origem: usuario+assistente`.
- Resumo: `tipo: resumo-semanal | resumo-mensal | resumo-trimestral`, `periodo`, `inicio`, `fim`,
  `origem: assistente`.

## Convencoes

- Datas sempre `YYYY-MM-DD` em nome de arquivo e no corpo (ordem alfabetica = cronologica).
- Um arquivo por dia; diario e imutavel depois do dia. Correcoes vao no dia seguinte ou no resumo.
- Camadas de compressao: semana vem dos diarios, mes das semanas, trimestre dos meses. Cada camada tem
  uma secao "Fora do resumo" listando o que ficou de fora.
