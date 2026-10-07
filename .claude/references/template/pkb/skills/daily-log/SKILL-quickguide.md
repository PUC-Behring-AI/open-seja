**What it does**: Cria ou atualiza a nota de diário do dia em `logs/YYYY/YYYY-MM-DD.md` e, no fim do dia, extrai itens acionáveis para `inbox/`.

- **Abrir o dia** -- cria a nota de hoje (se não existe) e preenche o "Foco de hoje" a partir do próximo passo prioritário.
- **Registrar** -- acrescenta uma linha com hora ao "Registro"; se algo for acionável, oferece capturar no inbox.
- **Fechar o dia** -- transforma as capturas em notas no `inbox/`, preenche o "Próximo passo" de amanhã e oferece commit.

**Examples**:
> `log de hoje`
> Cria a nota do dia e mostra o foco de hoje.

> `registra que terminei o levantamento da arquitetura`
> Acrescenta a linha ao registro do dia.

> `fecha o dia`
> Move capturas para o inbox e oferece commit.

**When to use**: Manter um diário, registrar um evento do dia, ou fechar o dia e preparar o próximo passo.

**Not for**: Resumir períodos (use `weekly-review`/`compress`); responder perguntas sobre o arquivo; editar diários de dias anteriores.

**Next step**: No fim da semana, `/weekly-review`.
