# Plan 000900 | FEATURE-O | FIXTURE | 2026-10-06 12:00 UTC | plano de fixture | Review: light
plan_format_version: 2
Feature: contas-da-semana
Specify: approved (rev 1)

## User brief

> Fixture ficticia.

## Steps

### Step 1: Listar e marcar
Descricao autocontida do passo.
- **Files**: src/x1.py (modify)
- **Verify**: testes passam
- **Tests**: when a conta vence em 3 dias, returns a conta na lista
- **Scenarios**: `contas-da-semana/contas-da-semana.feature::Ver as contas que vencem nos próximos 7 dias`, `contas-da-semana/contas-da-semana.feature::Marcar uma conta como paga`
- [ ] Done

### Step 2: Desfazer e medir
Descricao autocontida do passo.
- **Files**: src/x2.py (modify)
- **Verify**: testes passam
- **Tests**: when desfaz, returns a conta de volta; when ha 500 contas, returns a lista em ate 2 segundos
- **Scenarios**: `contas-da-semana/contas-da-semana.feature::Desfazer uma conta marcada como paga por engano`, `contas-da-semana/contas-da-semana.feature::A lista abre logo com muitas contas`
- [ ] Done

