---
designer_description: "I'm your project's immutable principles -- the non-negotiable lines on identity, architecture, quality, security, and compliance that every skill and agent loads before anything else, and that nothing else in your references can override. When a proposal would cross one of these lines, it is blocked here before it ever reaches a plan or a commit."
---

# PROJECT CONSTITUTION -- open-seja

> Este arquivo declara princípios imutáveis que prevalecem sobre toda outra orientação. Agentes nunca os violam sem override explícito do humano.
>
> A constituição é carregada primeiro pelo pre-skill, antes das convenções e de qualquer outro arquivo de referência.

---

## Project Identity

open-seja -- distribuição de acesso aberto do SEJA; um harness para o Claude Code que trata desenvolvimento assistido por IA como comunicação projetada, com ciclo PLAN -> BUILD -> REFLECT, portão determinístico por passo e caminho de volta ao humano.

Usuário primário: desenvolvedores ao longo da escala citizen <-> power (H-001). Secundário: pesquisadores que estudam o harness como objeto.

---

## Technical Principles

| # | Principle | Rationale |
|---|-----------|-----------|
| T1 | PASS é resultado de ferramenta, não frase. Nenhum passo de BUILD conta como feito sem o portão determinístico (ou sem a declaração explícita de que o projeto não tem portão). | Prosa no prompt não é plano de controle (H-008). |
| T2 | Sem as-intended não há ciclo. `/design` precede o primeiro `/plan`; `/plan` recusa partir sem `product-design-as-intended.md`. | A deriva precisa de referência (D-002, H-002). |
| T3 | Artefatos em `_output/` são imutáveis; correção é por apensamento com motivo (revoked / superseded), nunca por reescrita. | História de design é evidência de pesquisa (P-004, SigniFYI). |
| T4 | Arquivos Human (markers) recebem de agentes apenas marcadores, via `apply_marker.py`, após confirmação no mesmo turno. | A voz pertence a quem a emitiu (P-004, Q-007). |
| T5 | Skill orquestra, agente executa, em contexto isolado; o usuário nunca invoca agente diretamente. | P-006, P-007, H-004. |
| T6 | Fronteira agnóstica de stack: o harness consome contratos (JSON do portão com códigos de saída por categoria; relatório do runner) e nunca a ferramenta; stack sem adaptador degrada para `não medido`, nunca para falha. | O ciclo roda em qualquer linguagem e diz o que não mediu. |

---

## Quality Principles

| # | Principle | Rationale |
|---|-----------|-----------|
| Q1 | Mudança no harness só entra com `pytest .claude/skills/scripts/tests/` verde e `run_all_checks.py` sem falha nova em relação ao baseline. | O harness exige dos projetos o que exige de si. |
| Q2 | `/critique` sempre precede `/document` e `/communicate`. | Validar antes de comunicar (P-005). |
| Q3 | Toda hipótese registrada carrega o que a confirmaria e o que a refutaria; limiares de medida são fixados antes de ver os dados. | Raciocínio abdutivo aplicado a si mesmo (1.2.4, H-008). |
| Q4 | O que não foi medido é dito como `não medido`, ao lado do que foi, nunca escondido em média ou número único. | Honestidade do instrumento (H-009, D-004). |

---

## Security Invariants

| # | Invariant | Rationale |
|---|-----------|-----------|
| S1 | O portão roda sem rede e sem chave de API no ambiente filho. | Centenas de rodadas mutadas multiplicariam qualquer vazamento. |
| S2 | O agente não move o ratchet nem pula o portão: `--accept-baseline` e `git commit --no-verify` negados por permissão; hooks `Stop` e `PreToolUse` ativos. | O humano é o dono das restrições (H-008). |
| S3 | Nenhum segredo em fonte ou em `_output/`; `.env` gitignored. | Chave commitada é chave comprometida. |

---

## Compliance Requirements

| # | Requirement | Regulation/Contract |
|---|-------------|---------------------|
| C1 | Atribuição ao SEJA original e licença CC BY-NC 4.0 preservadas em toda distribuição; nome usado conforme `TRADEMARKS.md`. | Licença e marca. |
| C2 | Nenhum nome de parceiro, instituição conveniada ou pessoa nos artefatos de `_output/` e de `product-design/`; dados de instâncias ficam nos repositórios das instâncias. Citações bibliográficas de obras publicadas não contam como nome de pessoa. | Confidencialidade de convênios; o open-seja é visível à organização e tende ao público. |
| C3 | `main` só recebe o que o `tools/publish-manifest.txt` inclui (sem `_output/**`, sem `conventions.md` do próprio open-seja). | Separar distribuição de desenvolvimento. |

---

## Enforcement

- Estes princípios são carregados em todo contexto de agente pelo pre-skill.
- `/critique validate` verifica conformidade contra as restrições derivadas deste documento (`product-design/agent/constraints.yaml`).
- Violações descobertas em `/critique review` ou `/critique preflight` são **bloqueantes**: precisam ser resolvidas antes do commit.
- Emendas exigem aprovação explícita do designer e registro no changelog abaixo.

---

## Changelog

### v1 -- 2026-10-05 00:00 UTC
- Constituição inicial criada via `/design` a partir de `_output/tmp/design-rascunho-as-intended-2026-10-05.md` (Parte B). C2 ganha a ressalva sobre citações bibliográficas, porque a fundamentação fundida no as-intended cita autores publicados.
