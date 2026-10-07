**What it does**: Conduz a revisão semanal do GTD em ~15 minutos e produz a nota da semana em `logs/Resumos/YYYY-Www.md`, com commit no fim.

- **Inbox** -- invoca `process-inbox` (ou avisa que está vazio).
- **Objetivos e projetos** -- confere status e próximo passo em `Objetivos.md` e nos projetos do seu arquivo.
- **Resumo** -- lê os diários da semana e escreve a nota com links, decisões, aprendizados e "Fora do resumo".
- **Fechamento** -- propõe até 3 links entre notas, atualiza `index.md` e faz commit.

**Examples**:
> `revisão semanal`
> Delimita a semana, processa o inbox, revisa objetivos/projetos e escreve a nota da semana.

**When to use**: Fim de semana, ou quando uma semana encerrada ficou sem nota.

**Not for**: Gerar resumos de períodos passados (use `compress`); resumir um único dia (use `daily-log`); decidir pelo usuário.

**Next step**: No fim do mês ou trimestre, `/compress`.
