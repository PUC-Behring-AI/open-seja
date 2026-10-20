# Progress -- Plan 20261020-688kjs

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

## Iteration Log

### Plan -- reflection-on-action | 2026-10-20 20:45 UTC | Remover o Gherkin do open-seja
- happened: Grill em duas rodadas, plano v2 de 15 steps escrito, revisão Deep devolveu 11 emendas.
- deviated: O brief pedia plano único; a revisão mostra cerca de 24 steps, acima do teto de 12 a 15.
- less-sure: Se plano único ou roadmap; destino de build_checks.py; call-graph sem gerador; docs/doc-A..D da Simone.
- gate: not-applicable

### Plan -- reflection-on-action | 2026-10-20 21:15 UTC | Remover o Gherkin do open-seja (portagem)
- happened: Rumo mudou de remoção arquivo a arquivo para voltar à base pre-plan-000007 e portar ULID e PKB; duas revisões Deep (a segunda achou 4 bloqueantes, aplicados).
- deviated: O brief pedia remover; o plano agora cria uma linhagem nova em branch, não edita dev; sem plano v3 nem grill.
- less-sure: Numeração D-010/D-012/D-013; conflitos reais nos ~25 arquivos de código só aparecem na execução; plano e ids ainda sem commit.
- gate: not-applicable

### Plan -- emenda | 2026-10-20 | Respostas do designer antes do /implement
- happened: Designer confirmou a base 2b17d27 + multi-dev + jogo de linguagem. Step 11 emendado: teste por requisito antes do código também no modo manual ("o teste por requisito vem antes no modo manual").
- deviated: Portão com CRAP e mutação explícito no v3, cleaner e hardener ficam para outra rodada ("vamos deixar CRAP, clean e hardener para outra rodada"); registrados nas pendências do plano.
- less-sure: Os clientes v0.11.0 perdem cleaner e hardener no upgrade (Step 12) até a próxima rodada os trazer de volta.
- gate: not-applicable
