# Plan 20261020-k3m9qz | FEATURE-B | 2026-10-20 10:00 | Contas pagas e aviso de vencimento | Review: light
uid: 01M5DGKNMZ0000000000K3M9QZ
plan_format_version: 3

## User brief

> quero marcar contas como pagas e ser avisado antes de vencer

## Agent interpretation

Marcar contas como pagas e avisar três dias antes do vencimento.

## Intenção
- Objetivo: marcar contas como pagas e ver um aviso antes do vencimento. (A1, F1)
- O que você vê no fim: a conta paga na lista de pagas e o aviso na tela inicial. (A1, A2)
- Não faz: não envia comprovante por e-mail. (A3)
- Pronto quando: a conta marcada aparece na lista de pagas e o aviso aparece três dias antes. (A1, A2)

## Requisitos
- REQ-contas-001: Você pode marcar uma conta como paga. Para que: você sabe o que ainda falta pagar. (A1)
- REQ-contas-002: Você vê um aviso três dias antes do vencimento. Para que: você não paga multa. (A2)

## Casos de uso
- **REQ-contas-001**: Segunda de manhã, você abre a lista de contas, marca a de luz como paga e ela aparece na lista de pagas. (A1)
- **REQ-contas-002**: A conta de água vence sexta; na terça você abre a tela inicial e vê o aviso. (A2)

## Retradução

Eu entendi que você quer marcar contas como pagas e ver um aviso três dias antes do vencimento.

O que eu não vou fazer: enviar comprovantes por e-mail.

Aprovação: aprovado em 2026-10-20

## Nas suas palavras
- F1: "quero marcar contas como pagas e ser avisado antes de vencer"
- A1 (cena, aceitou): "Segunda de manhã. Você marca a conta de luz como paga." -> "Aceito"
- A2 (e se, corrigiu): "Na terça você vê o aviso." -> "o aviso tem de chegar três dias antes"
- A3 (contra-cena, recusou): "O sistema envia o comprovante por e-mail." -> "o comprovante eu mando quando quiser"

## Steps

### Step 1: Marcar conta como paga
Implementar a marcação.
- **Files**: app/contas.py (modify)
- **Verify**: testes passam
- **Tests**: when você marca uma conta como paga, ela aparece na lista de pagas (REQ-contas-001)
- **Covers**: REQ-contas-001
- **Traces**: REQ-MC-011
- [ ] Done

### Step 2: Aviso de vencimento
Implementar o aviso.
- **Files**: app/aviso.py (create)
- **Verify**: testes passam
- **Tests**: when faltam três dias, o aviso aparece (REQ-contas-002)
- **Covers**: REQ-contas-002, REQ-contas-009
- [ ] Done

### Step 3: Documentar
Atualizar o README.
- **Files**: README.md (modify)
- **Verify**: README cita a marcação
- **Tests**: N/A (documentação)
- [ ] Done
