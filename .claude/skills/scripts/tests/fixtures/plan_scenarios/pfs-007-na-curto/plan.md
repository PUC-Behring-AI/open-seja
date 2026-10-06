# Plan 000900 | FEATURE-O | FIXTURE | 2026-10-06 12:00 UTC | plano de fixture | Review: light
plan_format_version: 2
Feature: contas-da-semana
Specify: approved (rev 1)

## User brief

> Fixture ficticia.

## Steps

### Step 1: Criar a tabela de contas
Descricao autocontida do passo.
- **Files**: src/x1.py (modify)
- **Verify**: testes passam
- **Tests**: N/A (migração)
- **Scenarios**: N/A (tabela usada pelo cenário de ver contas da semana)
- [ ] Done

### Step 2: Listar as contas da semana
Descricao autocontida do passo.
- **Files**: src/x2.py (modify)
- **Verify**: testes passam
- **Tests**: when a conta vence em 3 dias, returns a conta na lista
- **Scenarios**: `contas-da-semana/contas-da-semana.feature::Ver as contas que vencem nos próximos 7 dias`
- [ ] Done

### Step 3: Marcar e desfazer o pagamento
Descricao autocontida do passo.
- **Files**: src/x3.py (modify)
- **Verify**: testes passam
- **Tests**: when a conta e marcada como paga, returns a lista sem a conta
- **Scenarios**: `contas-da-semana/contas-da-semana.feature::Marcar uma conta como paga`, `contas-da-semana/contas-da-semana.feature::Desfazer uma conta marcada como paga por engano`
- [ ] Done

### Step 4: Manter a lista rápida
Descricao autocontida do passo.
- **Files**: src/x4.py (modify)
- **Verify**: testes passam
- **Tests**: when ha 500 contas, returns a lista em ate 2 segundos
- **Scenarios**: `contas-da-semana/contas-da-semana.feature::A lista abre logo com muitas contas`
- [ ] Done

### Step 5: Refatorar o módulo de datas
Descricao autocontida do passo.
- **Files**: src/x5.py (modify)
- **Verify**: testes passam
- **Tests**: N/A (refactor com cobertura prévia)
- **Scenarios**: N/A (refactor)
- [ ] Done

