---
name: process-inbox
description: Processa o inbox do arquivo (GTD esclarecer → organizar), item por item, propondo destino na estrutura real do arquivo com justificativa e movendo só com confirmação. Use quando o usuário pedir para processar, esvaziar ou organizar o inbox, ou quando o inbox estiver cheio ou antigo.
metadata:
  last-updated: 2026-10-04 00:51 UTC
  version: 1.0.0
  category: utility
  context_budget: standard
  references: []
---

> Overview: see [./SKILL-quickguide.md](./SKILL-quickguide.md)

# process-inbox

Transforma `inbox/` em zero itens, um de cada vez, sem decidir pelo usuário.

## Destinos

Este arquivo não usa pastas PARA; a classificação é por acionabilidade para a **estrutura real do
arquivo**:

- **Projeto** (tem fim e prazo, mais de um passo): nota de projeto na pasta de projetos do seu arquivo (nova ou existente). Ao criar, use `Templates/Projeto.md` e peça o primeiro passo concreto.
- **Referência / recurso** (não acionável, útil): a pasta de referências do seu arquivo (por assunto ou
  disciplina), ou uma linha numa lista de links, se você mantém uma.
- **Próxima ação** (um passo, <2 min): sugerir fazer agora; senão virar próximo passo de um objetivo
  (`Objetivos.md`) ou projeto.
- **Talvez um dia**: linha no `Objetivos.md` ou numa nota de "algum dia".
- **Descarte**: só com confirmação explícita; `git rm` preserva no histórico (Q2).

## Pré-condições
- Há ao menos um item em `inbox/`. Se não houver, diga "Inbox vazio" e pare.

## Passos

1. **Liste** os itens do inbox em ordem cronológica (mais antigo primeiro), numerados, com título e
   data de captura. Diga quantos são.
2. **Para cada item**, leia a nota e responda em três linhas:
   - **O que é**: uma frase.
   - **É acionável?** Não → referência, algum dia ou descarte. Sim → projeto, próxima ação ou fazer
     agora.
   - **Proposta**: destino exato (pasta e, se for o caso, nota-alvo) e o `tipo` que a nota vai receber
     (`leitura` ou `permanente`; ela deixa de ser `transitoria`).
3. **Espere a decisão** do usuário. Aceite respostas em lote ("tudo ok menos o 3", "3 vai para o
   projeto X"). Se ele pedir, discuta o item; não passe ao próximo sem decisão.
4. **Execute** o que foi aprovado, item a item:
   - Mover a nota (ou acrescentar a linha na nota-alvo, quando é uma próxima ação).
   - Atualizar `tipo` e `origem` no frontmatter; se reescrever o conteúdo com as próprias palavras,
     marcar `origem: usuario+assistente`.
   - Adicionar `[[links]]` para notas relacionadas que você conhece pelo `index.md`. Não invente
     relações: só linke o que você leu.
   - Atualizar `index.md`.
5. **Descartar** só com confirmação explícita daquele item. Descartar = `git rm`; o histórico preserva.
6. **Relate** em até 5 linhas: quantos processados, para onde foram, o que ficou pendente.
7. **Registre** em `logs/log.md`: `## [YYYY-MM-DD] skill | process-inbox: N itens (P projetos, R
   referências, A ações, D descartados)`.

## O que esta skill não faz
- Não move nada sem confirmação.
- Não cria projeto novo sem próximo passo definido. Se o item é um projeto, pergunte "qual é o primeiro
  passo concreto?" antes de criar a nota.
- Não elabora o conteúdo da nota além do necessário para classificar. Elaborar é trabalho de outra
  sessão.
- Não processa itens capturados hoje se o usuário preferir deixá-los "assentar"; pergunte uma vez,
  respeite a resposta.

## Formato da nota de projeto (quando criar uma)

Use `Templates/Projeto.md` (preenchendo `{{date}}` e `{{title}}`). Se o template não existir, este é o
formato:

```markdown
---
tipo: permanente
origem: usuario+assistente
tags: []
data: YYYY-MM-DD
status: ativo
---
# Título do projeto

**Objetivo**: 
**Resultado esperado**: 
**Prazo**: 
**Próximo passo**: 

## Notas relacionadas
- 
```
