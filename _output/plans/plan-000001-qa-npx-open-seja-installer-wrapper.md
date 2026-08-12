# QA Log | Plan 000001 | 2026-08-12 02:18 UTC | npx open-seja installer wrapper

## Brief

Criar o primeiro plano do open-seja: instalavel/atualizavel via `npx open-seja <target>`, com o contexto ja discutido (research-000026 do Doutourado) herdado inline no brief.

## Q&A Log

## Q1
vamos criar um primeiro plano para o open-seja: instalalavel/atualizavel usando npx, ja discutido aqui. vamos salvar este contexto para plano que devera ser executado em open-seja

## A1
Invoquei `open-seja:plan` com um brief auto-contido resumindo o contexto herdado do research-000026 (Doutourado, nao acessivel a partir do open-seja): decisao de nao seguir o molde `npx skills add --skill <nome>` nem modelar como plugin nativo do Claude Code; mecanica atual do `/seja-setup` (fluxo interativo, nao um script deterministico); convencao 2026 de wrapper fino sem duplicar arquivos; pre-requisito ja cumprido (`/seja-setup --here` rodado em 2026-08-12).

Escrevi o plano com 5 steps: (1) scaffold do pacote npm, (2) `lib/core.js` com parsing de args e decisao clone/reuse/abort (logica pura, testavel), (3) `lib/bootstrap.js` com clone/verificacao/handoff para o `claude` (I/O fino), (4) wiring de `bin/cli.js` ponta a ponta, (5) `npm/README.md` + metadados finais do `package.json`. Documentei explicitamente em "Alternatives rejected" a decisao de nao cobrir a feature de "fonte configuravel" (Rec 11 do research-000026) neste mesmo plano -- escopo separado.

Rodei o `plan-reviewer` em profundidade Standard (shortlist sintetizada para o prefixo FEATURE-O, sem linha propria na tabela: SEC, ARCH, TEST, DX, OPS, COMPAT). Convergiu na iteracao 1 apos 3 deep-dives: (a) COMPAT -- `claude` seria invocado sem `shell: true`, quebrando silenciosamente no Windows (shim `.cmd`/`.ps1` nao resolvido); corrigido escopando `shell: process.platform === 'win32'` so' as duas chamadas que invocam `claude`, nunca em `clone()` (mantendo a superficie livre de shell onde ha entrada do usuario); (b) TEST -- o dispatch de `bin/cli.js` so' tinha cobertura para `--help`; corrigido extraindo `run(argv, deps)` injetavel e adicionando testes unitarios para os caminhos abort/clone/claude-indisponivel; (c) DX -- `--version <tag>` era parseado mas nunca consumido (flag fantasma); removido do escopo deste plano, deferido para o plano futuro de fonte configuravel.
