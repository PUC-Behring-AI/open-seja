# Plan 000001 | FEATURE-O | 2026-08-12 02:09 | npx open-seja installer wrapper | Review: standard
plan_format_version: 1

## User brief

> Tornar o open-seja instalavel e atualizavel via `npx open-seja <target>`, um wrapper npm fino que automatiza o que `/seja-setup` ja faz hoje (clone + `/seja-setup --here` para instalacao nova; `/seja-setup --upgrade` quando o target ja existe) -- nao adotar o molde per-skill `npx skills add --skill <nome>` (skills.sh), nem modelar como plugin nativo do Claude Code (bundle somente-leitura sempre-sincronizado). O harness inteiro deve ter uma unica opcao de instalacao, nao fragmentada por skill.
>
> Contexto herdado do research-000026 (feito no repositorio Doutourado, nao acessivel a partir daqui -- resumido inline no brief da skill `/plan`):
>
> 1. open-seja e' um fork pessoal de experimentacao/extensao do harness SEJA, semeado a partir de `simonedjb/seja` (upstream), com a intencao explicita de nao divergir muito -- mesma licenca CC BY-NC 4.0, atribuicao preservada.
> 2. Praticas 2026 investigadas: `npx skills add <repo> --skill <nome>` (skills.sh) e' o padrao emergente para skills individuais, mas foi descartado para o SEJA como um todo (nao e' uma skill isolada). "Plugin nativo do Claude Code" (bundle somente-leitura sempre-sincronizado) tambem descartado -- incompativel com o modelo atual de copiar-e-deixar-o-consumidor-customizar.
> 3. Mecanica atual do `/seja-setup`: `resolve_seja_version.py` ja aceita `--remote <url>`; o clone real no upgrade flow (`_internal/seja-setup/upgrade/SKILL.md` step 2) e' hardcoded para `https://github.com/simonedjb/seja` salvo quando um path local e' fornecido manualmente na conversa. `detect_setup_state.py` tem `SEJA_PUBLIC_RE`/`SEJA_PRIV_RE` hardcoded so' para `simonedjb/seja(-priv)`. Generalizar isso ("fonte configuravel") fica fora do escopo deste plano -- ver Alternatives rejected.
> 4. Convencao 2026 de nao duplicar arquivos ao empacotar: o pacote npm deve ser um wrapper fino (clone + invocacao do slash-command), nao uma copia paralela do harness.
> 5. Pre-requisito ja cumprido: `/seja-setup --here` ja rodado neste repo em 2026-08-12 -- `product-design/conventions.md`, `_output/`, `.seja-version` (v0.9.1) ja existem; identidade git local `arodrigues-puc-rio` configurada; remote `upstream` (`simonedjb/seja`) ja adicionado ao lado de `origin`.

## Agent interpretation

**Problem**: instalar ou atualizar o open-seja hoje exige clonar o repositorio manualmente e lembrar/digitar o comando `/seja-setup --here` (ou `--upgrade`) dentro de uma sessao do Claude Code -- mais atrito e menos descobrivel do que o padrao `npx <ferramenta> <alvo>` que usuarios esperam em 2026 (ex.: `npx create-react-app`, `npx skills add`).

**Approach**: publicar um pacote npm fino (`open-seja`, `bin: open-seja`) que faz **apenas** a parte mecanica e deterministica -- clonar o repo (ou reconhecer um checkout existente), verificar que `git` e a CLI `claude` estao disponiveis, e entao **entregar o controle** para uma sessao interativa do `claude` ja posicionada no diretorio certo, com o comando `/seja-setup` como prompt inicial. A logica de deteccao de estado (`fresh-download` vs `finalised` vs `partial-init`, os prompts `AskUserQuestion` do questionario, o scaffolding de arquivos) continua inteiramente dentro do `/seja-setup` existente (Python, ja testado) -- o wrapper JS nao duplica nada disso, so' bootstrap + handoff. Isso segue diretamente a Rec 12 do research-000026 (nao duplicar arquivos/logica ao empacotar).

**Alternatives rejected**:
- `npx skills add open-seja --skill <nome>` (convencao skills.sh, per-skill) -- rejeitada porque fragmentaria a instalacao em 16 comandos separados e perderia o scaffolding coerente que `/seja-setup --here` ja oferece num unico fluxo (Rec 9 do research-000026).
- Modelar como plugin nativo do Claude Code (bundle somente-leitura, sempre-sincronizado) -- rejeitada porque o modelo do SEJA e' copiar-e-deixar-o-consumidor-customizar (`.claude/rules/`, `product-design/` sao editados apos instalar); um bundle read-only nao suporta isso (Rec 10 do research-000026).
- Reimplementar a deteccao de estado e o scaffolding do `/seja-setup` nativamente em JS, de forma totalmente nao-interativa -- rejeitada: duplicaria a logica de `detect_setup_state.py` em duas linguagens, criando risco de deriva toda vez que a logica de setup do harness evoluir. O design "wrapper fino + handoff" mantem o Python como fonte unica de verdade.
- Cobrir tambem a feature de "fonte configuravel" (generalizar o hardcode de `simonedjb/seja` em `resolve_seja_version.py`/`detect_setup_state.py`) neste mesmo plano -- rejeitada por escopo: e' uma mudanca separada, mais profunda, nos internals do `/seja-setup` (nao no wrapper npm), e nao e' pre-requisito para o wrapper funcionar (o wrapper ja tem seu proprio `REPO_URL` fixo apontando para o open-seja). Fica para um plano futuro se decidirmos perseguir a Rec 11 do research-000026.

## Files

Lidos / analisados:

- `.claude/skills/seja-setup/SKILL.md`, `.claude/skills/_internal/seja-setup/here/SKILL.md`, `.claude/skills/_internal/seja-setup/upgrade/SKILL.md` -- confirma que o fluxo real de setup/upgrade e' inteiramente orientado por um agente lendo SKILL.md (com `AskUserQuestion` interativo), nao um script determinístico -- por isso o wrapper npm so' pode fazer bootstrap + handoff, nunca substituir a sessao interativa
- `.claude/skills/seja-setup/detect_setup_state.py` -- estados `fresh-download`/`finalised`/`partial-init`/`dev-repo-refuse`; o wrapper nao precisa reimplementar nada disso, so' entregar o prompt `/seja-setup` e deixar o dispatch no-arg (ja existente) decidir
- `product-design/conventions.md` (deste repo) -- confirma `BACKEND_FRAMEWORK`/`FRONTEND_FRAMEWORK` = none; o pacote npm e' a primeira peca de codigo "de produto" real deste projeto

## Best practices

- Convencoes de pacote CLI npm: campo `bin` no `package.json`, shebang `#!/usr/bin/env node` no entry point, versionamento semantico.
- Separacao pure-logic vs I/O: `lib/core.js` exporta funcoes puras e testaveis (parsing de args, decisao clone/reuse/abort); `lib/bootstrap.js` isola as chamadas de `child_process` (git, claude) -- fronteira de I/O nao testada por unit test, coberta por verificacao manual/smoke.
- `stdio: 'inherit'` no `spawn` do `claude` para handoff transparente -- o terminal do usuario continua a sessao interativa sem qualquer buffering intermediario do wrapper.
- Principio de wrapper fino (Rec 12 do research-000026): nao duplicar logica ja existente e testada em Python.

## Design decisions

**User-visible impact**: quem quiser instalar ou atualizar o open-seja passa a rodar `npx open-seja <target>` (instalacao nova) ou `npx open-seja <target> --upgrade` (atualizacao) a partir de qualquer terminal com Node.js, `git` e a CLI `claude` instalados, em vez de clonar manualmente e lembrar o comando slash exato. O wrapper cuida so' do bootstrap (clone + verificacao de pre-requisitos) e entrega o controle para a sessao interativa do `claude` ja com `/seja-setup` como primeiro prompt -- o restante do fluxo (questionario, scaffolding) continua identico ao que existe hoje.

**Trade-offs accepted**: ganha-se um ponto de entrada memoravel e descobrivel, alinhado com a convencao 2026 de instaladores `npx`. Perde-se automacao completa nao-interativa -- o wrapper nao consegue terminar o setup sozinho (ex.: em CI), porque o scaffolding do `/seja-setup --here` e' inerentemente interativo (`AskUserQuestion`). Essa e' uma limitacao deliberada, nao um descuido: automatizar mais a sessao interativa exigiria um modo nao-interativo novo dentro do proprio `/seja-setup` (fora de escopo aqui) ou um harness headless dirigindo o Claude Code programaticamente (tambem fora de escopo).

**Metacommunication impact**: `npm/README.md` e' copy nova voltada ao usuario, descrevendo o comando `npx open-seja`. Usar frase na voz I/you onde fizer sentido (ex.: "I clone a fresh copy of the harness for you and hand off to an interactive Claude Code session for the rest of setup").

## Steps

### Step 1: Scaffold do pacote npm -- diretorio, package.json inicial e stub do entry point

Criar a estrutura basica do pacote npm dentro do repositorio, sem logica ainda. `package.json` declara o nome `open-seja`, o campo `bin` apontando para `bin/cli.js`, e metadados minimos (versao inicial `0.1.0`, `type: "commonjs"`, `engines.node >=18`). `bin/cli.js` e' so' um stub com shebang que sera preenchido no Step 4.

- **Files**: `npm/package.json` (create), `npm/bin/cli.js` (create)
- **References**: N/A
- **Interface**: `npm/package.json` declara `"bin": {"open-seja": "./bin/cli.js"}`
- **Verify**: `node npm/bin/cli.js` roda sem erro de sintaxe (mesmo que ainda nao faca nada)
- **Tests**: N/A (scaffolding puro, sem logica de negocio)
- [ ] Done

### Step 2: Implementar `lib/core.js` -- parsing de argumentos e decisao clone/reuse/abort (logica pura, testavel)

Duas funcoes puras, sem I/O: `parseArgs(argv)` interpreta os argumentos de linha de comando (`target` posicional obrigatorio, `--upgrade` opcional, `--help`); `resolveTarget(target, targetExists, hasSejaVersion)` decide a acao (`'clone' | 'reuse' | 'abort'`) sem tocar o filesystem diretamente -- recebe os sinais ja resolvidos como parametros para ficar testavel sem mocks pesados. Escrever `npm/test/core.test.js` cobrindo os casos abaixo. **(Amendment C, iteration 1)** `--version <tag>` foi removido do parser: um `--version` aceito e nunca lido por nenhum consumidor downstream (nem `bootstrap.clone`, nem `bin/cli.js`) seria uma flag fantasma -- o usuario a passaria acreditando que fixa uma tag/branch e o wrapper silenciosamente a ignoraria (breakdown DX "Looks fine to me" / Ib). Fixar uma tag/branch especifica fica para um plano futuro junto com a "fonte configuravel" (Rec 11 do research-000026, ja fora de escopo -- ver Alternatives rejected), quando houver tempo de adicionar tratamento de erro para tag invalida e cobertura de teste correspondente.

- **Files**: `npm/lib/core.js` (create), `npm/test/core.test.js` (create)
- **References**: N/A
- **Interface**: exporta `parseArgs(argv: string[]) -> {target: string, upgrade: boolean, help: boolean}` (lanca erro descritivo se `target` ausente e `help` for `false`); `resolveTarget(target: string, targetExists: boolean, hasSejaVersion: boolean) -> {action: 'clone'|'reuse'|'abort', reason?: string}`
- **Verify**: `node --test npm/test/core.test.js` passa
- **Tests**: `parseArgs(['my-project'])` devolve `{target: 'my-project', upgrade: false, help: false}`; `parseArgs(['my-project', '--upgrade'])` devolve `upgrade: true`; `parseArgs(['--help'])` devolve `{help: true}` sem exigir `target`; `parseArgs([])` lanca erro cuja mensagem menciona o argumento `target` obrigatorio; `resolveTarget('x', false, false)` devolve `action: 'clone'`; `resolveTarget('x', true, true)` devolve `action: 'reuse'`; `resolveTarget('x', true, false)` devolve `action: 'abort'` com `reason` mencionando que o caminho existe e nao parece um checkout do open-seja
- [ ] Done

### Step 3: Implementar `lib/bootstrap.js` -- clone, verificacao de pre-requisitos e handoff para o `claude`

Modulo fino que so' encapsula chamadas de `child_process`/`fs`, sem logica de decisao (essa fica no Step 2). Tres funcoes: `clone(repoUrl, target)` roda `git clone <repoUrl> <target>` via `child_process.execFileSync` (sem `shell: true` -- `git.exe` e' um binario real no PATH do Git for Windows, e `target` e' entrada do usuario, entao mante-lo livre de shell evita qualquer superficie de injecao); `checkClaudeAvailable()` roda `claude --version` e devolve `boolean` (nao lanca erro se ausente, so' reporta); `launchClaude(cwd, initialPrompt)` roda `child_process.spawn('claude', [initialPrompt], {cwd, stdio: 'inherit'})` para entregar o terminal a' sessao interativa. **(Amendment A, iteration 1)** `checkClaudeAvailable()` e `launchClaude()` -- as duas chamadas que invocam o binario `claude` -- devem passar `{shell: process.platform === 'win32'}` (alem das opcoes ja descritas). No Windows, um CLI instalado via `npm install -g` vira um shim `claude.cmd`/`claude.ps1`, e `child_process.spawn`/`execFileSync` sem `shell: true` resolvem o executavel via `CreateProcess`, que nao aplica `PATHEXT` como o `cmd.exe` -- o resultado e' `ENOENT` mesmo com o `claude` corretamente instalado e no PATH. `shell: true` fica restrito a essas duas chamadas (argumento fixo, nunca `target` do usuario) para nao reabrir a superficie de injecao de shell que a chamada `clone()` deliberadamente evita.

- **Files**: `npm/lib/bootstrap.js` (create)
- **References**: N/A
- **Depends on**: Step 2
- **Interface**: exporta `clone(repoUrl: string, target: string) -> void`, `checkClaudeAvailable() -> boolean`, `launchClaude(cwd: string, initialPrompt: string) -> void`
- **Verify**: `node -e "require('./npm/lib/bootstrap.js')"` carrega sem erro; execucao manual de `checkClaudeAvailable()` num terminal com `claude` instalado devolve `true`; **(Amendment A, iteration 1)** execucao manual de `checkClaudeAvailable()` e `launchClaude()` num Windows real (ou CI runner `windows-latest`) com `claude` instalado via `npm install -g` confirma que o CLI e' encontrado (sem `ENOENT`)
- **Tests**: N/A (wrapper fino de I/O sobre `child_process`/`git`/`claude` -- sem logica de negocio assertavel sem mockar toda a fronteira de processo; coberto por verificacao manual no Step 4)
- [ ] Done

### Step 4: Ligar `bin/cli.js` de ponta a ponta -- args, decisao, bootstrap e handoff

Preencher o stub do Step 1: ler `process.argv`, chamar `parseArgs`; se `help`, imprimir uso e sair com codigo 0 sem tocar `git`/`claude`; senao checar `targetExists`/`hasSejaVersion` no filesystem (`fs.existsSync`) e chamar `resolveTarget`; em `abort`, imprimir a `reason` em stderr e sair com codigo != 0; em `clone`, chamar `bootstrap.clone(...)`; checar `checkClaudeAvailable()` e, se `false`, imprimir instrucoes de instalacao da CLI `claude` e sair com codigo != 0; por fim chamar `bootstrap.launchClaude(target, upgrade ? '/seja-setup --upgrade' : '/seja-setup')`. Adicionar teste de integracao leve que roda a CLI como subprocesso so' para o caminho `--help` (o unico caminho seguro de testar automaticamente sem git/claude reais). **(Amendment B, iteration 1)** Extrair essa logica de dispatch para uma funcao exportada `run(argv, deps)` em `bin/cli.js` (`deps` com defaults `{ parseArgs, resolveTarget, bootstrap, fs, exit: process.exit }`, injetavel nos testes) em vez de deixa-la presa ao corpo do script top-level -- assim os caminhos `abort`/`clone`/`checkClaudeAvailable() === false` ficam testaveis com um `bootstrap` mockado, sem git/claude reais, e o unico caminho hoje coberto (`--help`) deixa de ser o unico verificado automaticamente antes do release.

- **Files**: `npm/bin/cli.js` (modify)
- **References**: N/A
- **Depends on**: Step 2, Step 3
- **Interface**: N/A (entry point, sem consumidores dentro do pacote)
- **Verify**: `node npm/bin/cli.js --help` imprime o uso e sai com codigo 0; `node npm/bin/cli.js` (sem argumentos) sai com codigo != 0 e mensagem de erro clara
- **Tests**: quando invocado com `--help`, a CLI imprime o texto de uso em stdout e sai com codigo 0 sem invocar `git` ou `claude` (teste de integracao via `child_process.execFileSync` na propria suite, unico caminho de entrada testado end-to-end). **(Amendment B, iteration 1)** Adicionar testes unitarios de `run(argv, deps)` com `bootstrap`/`fs` mockados: (a) `resolveTarget` devolvendo `abort` -> `deps.exit` chamado com codigo != 0 e a `reason` escrita em stderr, `bootstrap.clone`/`bootstrap.launchClaude` nunca chamados; (b) `resolveTarget` devolvendo `clone` -> `bootstrap.clone(repoUrl, target)` chamado com os argumentos esperados, seguido de `bootstrap.launchClaude(target, '/seja-setup')` (ou `'/seja-setup --upgrade'` quando `upgrade: true`); (c) `bootstrap.checkClaudeAvailable()` mockado para devolver `false` -> `deps.exit` chamado com codigo != 0, `bootstrap.launchClaude` nunca chamado
- [ ] Done

### Step 5: Documentacao do pacote (`npm/README.md`) e metadados finais do `package.json`

Escrever `npm/README.md` com: o comando `npx open-seja <target>` e `npx open-seja <target> --upgrade`; pre-requisitos (`git`, CLI `claude` instalada e autenticada); o que o comando faz (clona/reconhece o checkout, entrega para uma sessao interativa do `claude` com `/seja-setup` como primeiro prompt) e o que ele explicitamente **nao** faz (nao completa o setup sozinho -- o restante e' interativo). Finalizar `package.json`: `license` (mesma licenca do repositorio, CC BY-NC-4.0 -- registrar como nota, nao como campo SPDX padrao do npm, ja que CC BY-NC nao e' uma licenca de software OSI-padrao), `repository` apontando para `github.com/PUC-Behring-Institute-for-AI/open-seja`, `keywords`, `files` (whitelist `bin/`, `lib/`, `README.md`).

- **Files**: `npm/README.md` (create), `npm/package.json` (modify)
- **References**: N/A
- **Depends on**: Step 4
- **Interface**: N/A
- **Verify**: `npm/README.md` existe e documenta os dois comandos (instalar/atualizar); `npm pack --dry-run` dentro de `npm/` lista exatamente `bin/`, `lib/`, `README.md`, `package.json` (sem `test/` no pacote publicado)
- **Tests**: N/A (documentacao + metadados)
- **Docs**: `npm/README.md` e' documentacao nova voltada ao usuario final do wrapper -- nao toca o `README.md` da raiz do repositorio (mantido identico ao upstream por decisao explicita registrada no Step 6 do `/seja-setup --here`, 2026-08-12)
- [ ] Done

## Outcomes

- Pacote npm local completo em `npm/` (`open-seja`, bin `open-seja`), pronto para publicacao manual (`npm publish` dentro de `npm/`) -- publicar exige uma conta/token npm, entao fica como acao humana pos-plano, fora do escopo executavel aqui.
- `npx open-seja <target>` clona (ou reconhece) o checkout e entrega a sessao interativa do `claude` com `/seja-setup` pronto para rodar; `npx open-seja <target> --upgrade` faz o mesmo para `/seja-setup --upgrade`.
- Nenhuma logica de deteccao de estado ou scaffolding foi duplicada -- o wrapper e' estritamente bootstrap + handoff, mantendo Python como fonte unica de verdade (Rec 12 do research-000026).
- A feature de "fonte configuravel" (Rec 11 do research-000026) continua em aberto, fora do escopo deste plano.

## Smoke

false

## Review Log

**Review depth:** Standard
**Deep-dive budget:** 3/6 used

### Step Metadata Validation (pre-Phase-1)

- Files/References/Interface/Verify/Tests present on all 5 steps; no step touches more than 2 files (well under the 5-file cap).
- Dependency ordering: Step 3 declares `Depends on: Step 2`; Step 4 declares `Depends on: Step 2, Step 3`; Step 5 declares `Depends on: Step 4`. Consistent with the linear build-up (scaffold -> pure logic -> I/O -> wiring -> docs).
- Minor gap (not amended -- cosmetic, no regression/incident risk): Step 2 has no explicit `Depends on: Step 1` field even though `npm/lib/core.js` lives under the `npm/` tree scaffolded in Step 1. Execution order is already unambiguous from step numbering and the npm/-relative paths, so this is noted but not treated as a Phase 2 trigger.
- Step 3's `Depends on: Step 2` is nominal (no actual import of `core.js` from `bootstrap.js`) but harmless -- it reflects reading order in the plan, not a real coupling.

### Phase 1 — Perspective Scan (2026-08-12)

Plan prefix `FEATURE-O` has no row in the Perspective Shortcuts table; per caller instruction, used the synthesized shortlist for FEATURE-O (FEATURE-X minus UX/A11Y/I18N, plus OPS/COMPAT borrowed from CHORE-O/DOCUMENT-O for the npm-publish/cross-platform surface): **SEC, ARCH, TEST, DX, OPS, COMPAT**.

| Perspective | Status | Concern |
|-------------|--------|---------|
| SEC | Adopted | `execFileSync`/`spawn` are called with array-form args (no shell interpolation); the only network source (`repoUrl`) is a fixed constant, not user input; no secrets touched by the wrapper. |
| ARCH | Adopted | `cli.js` (thin) -> `core.js` (pure, testable) -> `bootstrap.js` (I/O-only) mirrors `product-design/standards.md § Backend > 4` layered pattern (CLI/MCP thin over framework-agnostic core over the I/O boundary); matches the plan's own "wrapper fino" design decision. |
| TEST | Deferred | Step 4's `bin/cli.js` wiring (parse -> resolve -> dispatch to abort/clone/launch) is only exercised end-to-end for the `--help` path; the `abort`, `clone`, and `checkClaudeAvailable() === false` branches have zero automated coverage before a real user hits them via `npx` — triggers Phase 2 (regression risk on the CLI entry point). |
| DX | Deferred | `parseArgs` parses `--version <tag>` but no downstream consumer (`bootstrap.clone`, `bin/cli.js`) ever reads it — a silent no-op flag (Communicability breakdown Ib, "Looks fine to me") — triggers Phase 2 (standards violation: DX Essential P0 "silent misconfiguration"). |
| OPS | Deferred (light) | No CI workflow exists anywhere in this repo yet (`find` confirms no `.github/workflows/`), so this plan shipping `npm/test/*.test.js` without a CI runner is a pre-existing project condition, not a regression introduced by this plan; not resolved separately -- see the TEST/DX Phase 2 entries below, which strengthen the *local* test surface this plan controls. No Phase 2 OPS deep-dive triggered on its own. |
| COMPAT | Deferred | `bootstrap.js` invokes the `claude` binary via `child_process.spawn`/implied `execFileSync` without `shell: true`; on Windows, an `npm install -g`-installed CLI is typically a `.cmd`/`.ps1` shim, and Node's `spawn`/`execFileSync` without `shell: true` resolve executables via `CreateProcess`, which does not apply `PATHEXT` the way `cmd.exe` does — this is a well-documented Node/Windows gotcha (ENOENT even when `claude` is correctly installed and on PATH) — triggers Phase 2 (concrete production-incident risk: silent breakage for every Windows user of `npx open-seja`, undermining the whole point of the wrapper). |

### Phase 2 — Deep-dive: COMPAT (iteration 1, deep-dive 1/6)

**Concern:** `launchClaude()`/`checkClaudeAvailable()` spawn the `claude` binary without `shell: true`; on Windows this fails to resolve `.cmd`/`.ps1` npm-global shims.
**Step ref:** Step 3 (`npm/lib/bootstrap.js`)
**Files read:** Plan Step 3 text (`npm/lib/bootstrap.js` not yet created — pre-implementation review); `product-design/standards.md` (confirmed no Node/npm-specific section exists yet — this is the project's first JS artifact, so no prior project convention to check against; general Node.js platform behavior applies instead).
**Finding:** The plan's own design intent is "handoff transparente" to an interactive `claude` session as the wrapper's entire value proposition (per Design decisions § User-visible impact). If `launchClaude` throws `ENOENT` on Windows because the shim isn't resolved, the wrapper fails silently on first run for a meaningful fraction of the target audience (Windows + `npx`), directly contradicting the plan's stated goal of a "descobrivel/memoravel ponto de entrada." `execFileSync('git', ...)` is unaffected because `git.exe` (Git for Windows) is a real PE executable on PATH, not a shell shim, and keeping it shell-free is also the right SEC call since `target` is user-controlled input.
**Recommendation:** Add `shell: process.platform === 'win32'` to the two `claude`-invoking calls only (`checkClaudeAvailable()`, `launchClaude()`), never to `clone()`. Add a manual Windows verification step to Step 3's Verify field.
**Resolution:** Plan amended — see Plan Amendment (iteration 1) / Step 3 updated in place.

### Phase 2 — Deep-dive: TEST (iteration 1, deep-dive 2/6)

**Concern:** `bin/cli.js`'s dispatch logic (abort / clone / claude-unavailable / launch) is untested beyond the `--help` path.
**Step ref:** Step 4 (`npm/bin/cli.js`)
**Files read:** Plan Step 2 and Step 4 text; `product-design/standards.md § Testing` (project convention: pure logic gets unit tests, I/O boundaries get "manual/smoke" verification — but Step 4's dispatch is control flow over already-pure decisions, not raw I/O, so the same exemption doesn't cleanly apply).
**Finding:** `core.js` (Step 2) already isolates and fully unit-tests the *decision* (`resolveTarget`). What's left untested is whether `cli.js` correctly *acts* on that decision — i.e., whether `abort` really exits non-zero with the reason on stderr, whether `clone` really calls `bootstrap.clone` with the right arguments before `launchClaude`, and whether a `false` `checkClaudeAvailable()` really short-circuits before `launchClaude`. This is exactly the kind of glue-code bug (wrong exit code, swapped argument order, missing early return) that ships silently without any test asserting it, and it sits on the one entry point every `npx open-seja` invocation goes through.
**Recommendation:** Extract the dispatch logic into an exported `run(argv, deps)` function with injectable `{parseArgs, resolveTarget, bootstrap, fs, exit}` defaults, so a mocked `bootstrap` can assert calls/exit codes without touching real `git`/`claude`. Add three new unit tests (abort, clone-dispatch, claude-unavailable) alongside the existing `--help` integration test.
**Resolution:** Plan amended — see Plan Amendment (iteration 1) / Step 4 updated in place.

### Phase 2 — Deep-dive: DX (iteration 1, deep-dive 3/6)

**Concern:** `--version <tag>` is parsed by `parseArgs` but never consumed by any downstream code path described in the plan.
**Step ref:** Step 2 (`npm/lib/core.js`), cross-checked against Step 3/Step 4 (no consumer found in either).
**Files read:** Plan Step 2, Step 3, Step 4 text in full (searched for any `version` usage after `parseArgs` — none found); brief's Alternatives rejected § 4 (source-URL generalization explicitly deferred, but tag/branch pinning is a distinct, narrower concern not addressed there either).
**Finding:** A user who runs `npx open-seja my-project --version v0.9.0` expecting a pinned checkout would get a silent full-`main` clone with no warning — textbook Ib ("Looks fine to me") breakdown per the DX Essential checklist, and also unnecessary public API surface (a flag with no behavior is worse than no flag, since removing a *documented, working* flag later is a breaking change but removing a *silently-ignored* one is not). Wiring it to `git clone --branch <tag>` was considered as an alternative but rejected for this iteration: it would require new error handling for invalid tags and new test coverage, expanding Step 3/Step 4 scope beyond what a Standard-depth review should push into an otherwise-converged plan; it's better deferred to the future plan the brief already earmarks for source/version configurability (Rec 11, research-000026).
**Recommendation:** Remove `--version` from `parseArgs`'s parsed surface and its interface signature for this plan; defer to the future source-configurability plan.
**Resolution:** Plan amended — see Plan Amendment (iteration 1) / Step 2 updated in place.

### Conflict Check (iteration 1)

COMPAT's recommendation (`shell: true` for the two `claude`-invoking calls) and SEC's Essential concern (avoid widening shell-injection attack surface) touch the same code but do not conflict: the recommendation is deliberately scoped to only the two calls whose arguments are fixed literals (`/seja-setup`, `/seja-setup --upgrade`, or no args at all), and explicitly excludes `clone()`, the one call that carries user-controlled input (`target`). SEC's "wins by default" rule is honored by construction — the higher-risk call stays shell-free — so no SEC exception or user sign-off is needed. No other inter-perspective conflicts detected (TEST and DX amendments touch disjoint code paths and are mutually reinforcing: the new `run(argv, deps)` seam from the TEST amendment makes it trivial to also assert in a future test that a removed `--version` flag doesn't resurface).

### Plan Amendment (iteration 1)

- **A — Step 3 (COMPAT):** `checkClaudeAvailable()` and `launchClaude()` now pass `{shell: process.platform === 'win32'}` in addition to their existing options, to resolve `claude.cmd`/`claude.ps1` npm-global shims on Windows; `clone()` stays shell-free (SEC). Step 3's Verify field extended with a Windows-specific manual/CI-runner check.
- **B — Step 4 (TEST):** Dispatch logic (`parseArgs` -> `resolveTarget` -> abort/clone/checkClaudeAvailable/launch) extracted into an exported, dependency-injectable `run(argv, deps)` function. Step 4's Tests field extended with three new unit tests (abort exit code + stderr; clone dispatch calls `bootstrap.clone`/`bootstrap.launchClaude` with expected args; `checkClaudeAvailable() === false` short-circuits before `launchClaude`).
- **C — Step 2 (DX):** `--version <tag>` removed from `parseArgs`'s parsed surface and interface signature (was parsed but never consumed downstream — a silent no-op flag). Deferred to the future source/version-configurability plan already earmarked in the brief's Alternatives rejected § 4.

### Updated To Do (reflecting amended steps)

- [ ] Step 1: Scaffold do pacote npm -- diretorio, package.json inicial e stub do entry point (unchanged)
- [ ] Step 2: Implementar `lib/core.js` -- parsing de argumentos (`target`, `--upgrade`, `--help` -- **`--version` removido, Amendment C**) e decisao clone/reuse/abort (logica pura, testavel)
- [ ] Step 3: Implementar `lib/bootstrap.js` -- clone, verificacao de pre-requisitos e handoff para o `claude`, **com `shell: process.platform === 'win32'` nas duas chamadas que invocam `claude` (Amendment A)**
- [ ] Step 4: Ligar `bin/cli.js` de ponta a ponta via uma funcao exportada e testavel **`run(argv, deps)` (Amendment B)**, com testes unitarios para os caminhos abort/clone/claude-indisponivel alem do `--help` existente
- [ ] Step 5: Documentacao do pacote (`npm/README.md`) e metadados finais do `package.json` (unchanged)

### Re-evaluation & Convergence

All three Phase 2 findings (COMPAT, TEST, DX) resulted in plan changes, now folded into Steps 2-4 in place. Re-evaluating the perspectives whose steps were modified:
- **COMPAT** -> Adopted (Windows shim resolution now explicit, scoped to avoid reopening the SEC-relevant `clone()` call).
- **TEST** -> Adopted (dispatch logic now has an injectable seam and three new unit tests covering the previously-untested branches).
- **DX** -> Adopted (dead flag removed; no remaining silent no-op surface).
- **SEC, ARCH** -> unaffected by the amendments (re-scanned, no new concerns introduced by the `shell: true`/`run(argv, deps)` changes).
- **OPS** -> unchanged (Deferred, light, pre-existing repo-wide condition, not this plan's regression to fix).

All Phase 2 findings resolved with plan changes; no perspective remains Deferred with an unresolved production-incident/regression/standards-violation concern. Converged at iteration 1 (well under the 3-iteration and 6-deep-dive budgets).

### Execution Metrics

| Metric | Value |
|--------|-------|
| Deep-dives used | 3/6 |
| Iterations completed | 1/3 |
| Perspectives shortlisted | 6 (SEC, ARCH, TEST, DX, OPS, COMPAT) |
| Perspectives Adopted | 5 (SEC, ARCH, COMPAT, TEST, DX — the latter three Adopted after iteration 1 amendments) |
| Perspectives Deferred (with rationale) | 1 (OPS — light, pre-existing repo-wide absence of CI, not a regression introduced by this plan) |
| Convergence reason | All Phase 2 findings resolved via plan amendment in iteration 1; no plan-changing concerns remain |
