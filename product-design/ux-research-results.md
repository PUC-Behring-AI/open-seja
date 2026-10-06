# UX RESEARCH -- open-seja

> **Classification**: `Human (markers)` -- a prosa (personas, cenários de problema, observações de jornada) é de autoria humana. Agentes só escrevem marcadores de forma fixa (`<!-- INCORPORATED: plan-NNNNNN | YYYY-MM-DD -->`) e apensam linhas ao `## CHANGELOG`, via `apply_marker.py` e após confirmação.
>
> **Stable IDs**: personas `R-P-NNN`, cenários de problema `R-PS-NNN`, jornadas descobertas `JM-E-NNN`.
>
> **One-directional flow**: achados de `§5 Discovered User Journeys` informam `product-design/product-design-as-intended.md §15`; não voltam para cá.
>
> **Estado da evidência (2026-10-05)**: as personas e os cenários abaixo são **derivados da fundamentação** (H-001, P-002, H-008 em `product-design-as-intended.md §3`), não de pesquisa de campo. Viram evidência quando uma sessão real (ensaio de primeiro ciclo, piloto do roadmap-000006) os confirmar ou corrigir em §5.

---

## 1. Personas

### Persona Inventory

| ID | Name | Role / Archetype | Goals |
|----|------|-----------------|-------|
| R-P-001 | Power dev | Polo de alta literacia de código da escala H-001 | G-001 construir com validação por passo; G-002 saber o que escapou do portão; G-003 governar o ratchet |
| R-P-002 | Citizen dev | Polo de baixa literacia de código da escala H-001 | G-004 dizer a intenção nas próprias palavras; G-005 reconhecer a própria intenção no que voltou, sem ler código |
| R-P-003 | Pesquisador do harness | Estuda o harness como objeto (engenharia semiótica, engenharia de software) | G-006 reconstruir o que o preposto comunicou e por quê, a partir de artefatos com ID e proveniência |

### R-P-001: Power dev

> **Role / Archetype:** desenvolvedor que lê código fluentemente; o código é o seu sistema de signos primário.
>
> **Bio:** usa o Claude Code para acelerar trabalho que saberia fazer sozinho. Revisa diffs, mas o agente escreve mais rápido do que ele revisa.
>
> **Goals:**
> - G-001: cada passo só conta como feito quando uma ferramenta diz PASS.
> - G-002: saber o que escapou do portão (achados do `/critique` em steps com PASS).
> - G-003: ser o único a mover limiar e baseline.
>
> **Key Frustrations:**
> - Revisão humana como único portão, limitada pela velocidade de leitura.
> - Processo que vira ritual: a forma sem o conteúdo (risco dominante do polo, H-003).
>
> **Relevant Context:**
> - Proficiência técnica: alta.
> - Retradução: eletiva.

### R-P-002: Citizen dev

> **Role / Archetype:** tem a intenção e o domínio do problema; não lê código.
>
> **Bio:** pede ao agente o que quer em linguagem natural e recebe código que não decodifica.
>
> **Goals:**
> - G-004: ser ouvido nas próprias palavras antes de qualquer código.
> - G-005: verificar, sem ler código, se o que foi construído é o que pediu, e saber o que não foi construído.
>
> **Key Frustrations:**
> - A tradução do agente pode estar errada sem estar quebrada, e ele não tem como saber.
> - Aprovar o que não entendeu ("parece bem"): delegação cega, o risco dominante do polo (H-003).
>
> **Relevant Context:**
> - Proficiência técnica: baixa em código; alta no domínio.
> - Retradução: obrigatória (P-003, H-003).

### R-P-003: Pesquisador do harness

> **Role / Archetype:** pesquisador de engenharia semiótica ou de engenharia de software.
>
> **Bio:** lê o ledger (`_output/`), o as-intended e o as-coded para estudar como o sistema comunica ao humano as intenções que realizou.
>
> **Goals:**
> - G-006: reconstruir, a partir de artefatos com ID estável e proveniência, o que foi pretendido, construído, medido e não medido.
>
> **Key Frustrations:**
> - Artefatos reescritos sem rastro; hipóteses tratadas como decisões; medidas sem limiar fixado antes.
>
> **Relevant Context:**
> - Lê pt-BR (fundamentação) e en-US (`docs/`); Q-005 aberta.

---

## 2. Problem Scenarios

### R-PS-001: O agente escreve mais rápido do que eu reviso

- **Persona:** R-P-001 (Power dev)
- **Goals:** G-001, G-002
- **Setting:** um plano de vários steps executado em modo auto, num repositório Python.

O agente conclui steps em sequência e cada um parece certo. O dev revisa por amostragem porque não consegue acompanhar. Um achado crítico aparece só no fim, num step que ninguém olhou de perto, e não há como saber quantos outros passaram. A validação depende da velocidade de leitura humana, e a prosa do agente ("todos os testes passam") ocupa o lugar de um resultado de ferramenta.

> Misuse contexts: o agente aceitando baseline ou pulando o hook de commit para fazer o step passar (checklist O).

### R-PS-002: A tradução está errada sem estar quebrada

- **Persona:** R-P-002 (Citizen dev)
- **Goals:** G-004, G-005
- **Setting:** o citizen pede uma funcionalidade em linguagem natural e recebe um diff.

O código roda, os testes passam e a funcionalidade existe, mas não é o que ele queria: o agente resolveu outra versão do problema, que cabe no mesmo texto do pedido. Ele não lê o código, então não tem como perceber. Recebe um resumo técnico que confirma o PASS e aprova. A distância entre o que concebeu e o que registrou (lacuna 1 de H-005) só aparece depois, em uso.

> Misuse contexts: aprovação do citizen virando ritual (cenário ético 3.4 do EMT).

---

## 3. Cross-Reference Map

| Artifact ID | Artifact Title | Design Artifact | Relationship |
|-------------|---------------|----------------|-------------|
| R-P-001 | Power dev | product-design-as-intended EMT 1.1; SS-001; JM-TB-001 | Feeds |
| R-P-002 | Citizen dev | product-design-as-intended EMT 1.1; SS-002; JM-TB-002 | Feeds |
| R-P-003 | Pesquisador do harness | product-design-as-intended EMT 1.2 | Feeds |
| R-PS-001 | O agente escreve mais rápido do que eu reviso | product-design-as-intended EMT 1.3; H-008 | Feeds |
| R-PS-002 | A tradução está errada sem estar quebrada | product-design-as-intended EMT 1.3; H-001, H-005, D-004 | Feeds |

---

## 4. Processing Status

| Artifact | ID | Status | Design Iteration | Notes |
|----------|-----|--------|-----------------|-------|
| Persona | R-P-001 | pending | - | derivada da fundamentação, 2026-10-05 |
| Persona | R-P-002 | pending | - | derivada da fundamentação, 2026-10-05 |
| Persona | R-P-003 | pending | - | derivada da fundamentação, 2026-10-05 |
| Problem scenario | R-PS-001 | pending | - | H-008 |
| Problem scenario | R-PS-002 | pending | - | H-001, H-005 |

---

## 5. Discovered User Journeys

<!-- maintained-by: human (researcher/designer) -- prose is human-only; append-only enforced by check_changelog_append_only.py; INCORPORATED markers allowed above JM-E-NNN headings via apply_marker.py -->

> Jornadas observadas em sessões reais (ensaio de primeiro ciclo, piloto). São achados empíricos: o que os usuários *de fato* fazem.

_Nenhuma jornada descoberta ainda. O primeiro candidato é o ensaio de primeiro ciclo da v0.10.0 (plan-000073 step 8)._

---

## CHANGELOG

<!-- Append-only. Format: YYYY-MM-DD | <entry-id> | added|revised|revoked|superseded | plan-NNNNNN | <note> -->

2026-10-05 | R-P-001 | added | - | persona power dev, derivada da fundamentacao (H-001)
2026-10-05 | R-P-002 | added | - | persona citizen dev, derivada da fundamentacao (H-001)
2026-10-05 | R-P-003 | added | - | persona pesquisador do harness
2026-10-05 | R-PS-001 | added | - | agente escreve mais rapido do que a revisao humana (H-008)
2026-10-05 | R-PS-002 | added | - | traducao errada sem estar quebrada (H-001, H-005)
