# Plan 000000 | FEATURE-O | FIXTURE | 2026-01-01 00:00 | fixture v2 valida
plan_format_version: 2
Feature: sample-greeting

## User brief

> Fixture ficticia: uma funcao que cumprimenta o usuario pelo nome.

## Steps

### Step 1: Implementar a saudacao
Criar `greet(name)` que devolve "Ola, <name>!" e, sem nome, devolve "Ola!".
- **Files**: src/greet.py (create), tests/test_greet.py (create)
- **References**: product-design/standards.md
- **Interface**: `greet(name: str | None) -> str`
- **Verify**: testes passam
- **Tests**: when name is "Ana", returns "Ola, Ana!"; when name is None, returns "Ola!"
- **Scenarios**: @REQ-sample-greeting-001, @REQ-sample-greeting-002
- **Traces**: REQ-ENT-001
- [ ] Done

### Step 2: Documentar o uso
Acrescentar ao README um exemplo de chamada de `greet`.
- **Files**: README.md (modify)
- **Depends on**: Step 1
- **Verify**: o README mostra o exemplo
- **Tests**: N/A (documento)
- **Scenarios**: N/A (sem comportamento observavel: so documentacao)
- [ ] Done
