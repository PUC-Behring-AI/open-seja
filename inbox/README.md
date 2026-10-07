---
tipo: permanente
origem: assistente
tags: [inbox, pkb]
---
# Inbox

Captura rapida (GTD): tudo entra aqui antes de ser classificado. Eu escrevo uma nota nova a cada skill
que roda, com as palavras que voce me disse, a data, a skill e o artefato que nasceu delas. Voce revisa
depois (`process-inbox`) e move cada nota para o lugar certo.

## Frontmatter esperado

```yaml
---
origem: usuario | assistente | usuario+assistente
tipo: transitoria | leitura | permanente
tags: []
data: YYYY-MM-DD
---
```

Notas capturadas pelo harness acrescentam `fonte` (evt_ids e brief), `skill` e `artefato`.

## Regras

- Nome do arquivo: `YYYY-MM-DD-<slug>.md`. Datas sempre `YYYY-MM-DD`.
- `_live.md` e **gerado** (indice cronologico com links); nao edite a mao, a proxima captura o reescreve.
- Apagar esta pasta ou este README desliga a captura automatica.

## Origem

A pratica (GTD, PARA, Zettelkasten) e os templates vem do bootstrap publico
`https://github.com/PUC-Behring-AI/personal_knowledge_base_bootstrap.git`.
