# DESIGN STANDARDS -- open-seja

> Instanciado por `/design` em 2026-10-05. O open-seja não tem interface gráfica: a interface é a **conversa no Claude Code** (perguntas, relatórios, notas) e os artefatos que ela deixa. Por isso a maior parte de um design-standards convencional (navegação, formulários, tokens de cor, tipografia) é N/A. O que se aplica é o padrão de conversa e a voz.

---

## UX patterns

### 1. App Type & Default Pattern Set

Harness conversacional para CLI (Claude Code). Os padrões abaixo são os de `product-design-as-intended.md §8`, aqui como regra para quem escreve skills.

### 2. Padrões de conversa

| Padrão | Regra | Origem |
|---|---|---|
| Decisão com justificativa | Toda `AskUserQuestion` traz, por opção, quando é recomendada e quando não é; nenhuma opção pré-aceita por enquadramento | reflexão-na-ação (1.2.4) |
| Files for review | Antes de qualquer pergunta que cite artefato já gerado, listar os arquivos para revisão | P-005 |
| Espelho oferecido | `/communicate` ao fim do PLAN e `/explain drift` ao fim do BUILD são oferecidos, nunca impostos; o `/reflect` registra quando não foram medidos | H-008, D-002 |
| PASS como resultado | Resultado do portão é mostrado como achados por função, nunca resumido em prosa | H-008 |
| Nota por step | A nota de reflexão-sobre-a-ação é mostrada quando escrita, não só no `/reflect` | 1.2.4 |
| Verbatim | Palavras do designer registradas literalmente, atribuídas | P-003, `/reflect` |
| `não medido` visível | O que não foi medido aparece ao lado do que foi | constituição Q4 |
| [intended] Grill e specify | Rodadas curtas, uma ideia por pergunta; aprovação em voz controlada; o citizen aprova a mensagem, o power dev o contrato | D-004 |

### 3. Voz

- A voz do harness para quem lê está em `.claude/references/general/designer-copy-voice.md`.
- Mensagem de metacomunicação: "eu" é o designer, "você" é o usuário; nunca terceira pessoa nem voz passiva.
- [intended] Voz controlada (STE100) para o citizen: até 25 palavras por frase, até 6 frases por parágrafo, termos fixos; nenhum número técnico no registro do citizen.

### 4. Error Handling UX

- Erro de script: mensagem curta em stderr, código de saída por categoria (ver `standards.md § Backend > 5`).
- Recusa do portão ou de hook: dizer o que foi recusado e quem pode mudar (o humano), nunca contornar.

### 5. Seções N/A

Navegação, formulários, empty states, responsividade, auditoria de acessibilidade de UI e governança de design system: **N/A**.

---

## Graphic / visual design

**N/A** -- sem identidade visual nem tokens. O que se aplica:

- HTML autocontido (`--html` [intended], SPO via `generate_spo.py`): um arquivo, sem recurso externo obrigatório, legível offline.
- Diagramas em Mermaid ou ASCII dentro do Markdown; figuras de origem em `docs/`.
