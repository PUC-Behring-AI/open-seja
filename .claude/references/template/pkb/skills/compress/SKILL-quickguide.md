**What it does**: Compressão progressiva dos diários em camadas em `logs/Resumos/`: semanas faltantes a partir dos diários, meses a partir das semanas, trimestres a partir dos meses.

- Cada camada resume só a camada de baixo e linka para ela.
- Toda camada tem "Fora do resumo" para tornar visível o que foi deixado de fora.
- Diários e semanas existentes nunca são alterados.

**Examples**:
> `resumo do mês`
> Lista os períodos encerrados sem nota e pergunta quais gerar.

> `fecha o trimestre`
> Gera o trimestre a partir dos meses, olhando objetivos e projetos.

**When to use**: Períodos encerrados (semana/mês/trimestre) sem nota, para reduzir o diário às camadas superiores.

**Not for**: A revisão da semana *atual* (use `weekly-review`); alterar diários ou semanas existentes.

**Next step**: Nenhum -- o trimestre é a camada final.
