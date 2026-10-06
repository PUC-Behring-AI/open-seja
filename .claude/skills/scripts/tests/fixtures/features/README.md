# Fixtures de check_features.py

Cada pasta e uma raiz de projeto fictícia (`features/<slug>/intent.md`, `*.feature`; `steps/` quando o caso usa `--steps`). `esperado.json` traz `args` (argumentos extras; `{root}` vira a pasta do caso), `exit_code`, a lista exata `findings` (`[regra, severidade, arquivo, linha]`) e, nos casos válidos, `matrix` (cenários por REQ e `scenarios_approved`). Regras: `.claude/references/general/gherkin-spec-format.md`. Nenhum dado real.

- `ok-minimo`: 1 REQ, 1 cenário, nada a achar.
- `ok-completo`: 4 REQs (um retirado), `Background`, `Scenario Outline` com 3 linhas, tags em pt e em en, várias tags num cenário, `Rule` com jornada, `@nao-faz`, `scenarios: approved`.
- `neg-steps-ok`: mesmo texto de step em dois cenários e `And` herdando o tipo: nada a achar (negativo de GHK-006 e GHK-007).
- `neg-valores-diferentes`: steps que só diferem por número não são quase-duplicata (negativo de GHK-008).
- `neg-nome-em-arquivos`: mesmo nome de cenário em arquivos diferentes (negativo de GHK-010).
- `ghk-001-sem-feature`, `ghk-001-pt-sem-declaracao`, `ghk-001-idioma`: arquivo sem `Feature:`; palavra-chave pt sem `# language: pt`; idioma não suportado.
- `ghk-002-sem-tag`: cenário sem tag `@REQ-` (conta 1, alimenta "cenário sem tag" do plan-000008).
- `ghk-003-tags`: tag no nível `Feature`, tag malformada e tag de outro slug.
- `ghk-004-orfa`: tag que cita REQ ausente de `intent.md` (conta 1, alimenta "tag sem REQ").
- `ghk-005-approved`, `ghk-005-grilling`: REQ sem cenário como erro (aprovado) e como info (em grill).
- `ghk-006-duplicado`: step repetido no mesmo cenário.
- `ghk-007-tipos`: mesmo texto como Given e como Then.
- `ghk-008-quase`: steps que só diferem por caixa e pontuação.
- `ghk-009-estrutura`: primeiro step `And`, `<x>` sem coluna, coluna de `Examples` sem uso.
- `ghk-010-nome`: nome de cenário repetido no arquivo.
- `ghk-011-exemplos`: `Scenario Outline` sem `Examples` e `Examples` sem linhas.
- `ghk-012-comportamentos`: `When` depois de `Then`, cenário com 11 steps, `Background` com 4 steps.
- `ghk-013-detalhe`: URL, seletor, SQL, caminho e chamada de função no step.
- `ghk-014-skip`: tag `@skip`.
- `ghk-015-ok`, `ghk-015-duplicada`, `ghk-015-sem-definicoes`, `ghk-015-nao-verificado`: `--steps` com definições completas, duplicadas, ausentes e com padrão `re`.
- `ghk-016-sem-req`, `ghk-016-reservado`, `pasta-sem-intent`: `intent.md` sem REQ válido, slug reservado, pasta com `.feature` e sem `intent.md` (info).
- `ghk-017-termo`, `ghk-017-sem-modelo`: substantivo fora de "Modelo e termos"; intent sem a seção (info).
- `ghk-018-rule`: `Rule` sem jornada e `Rule` com jornada fora de `serve:`.
- `ghk-019-nivel`, `ghk-019-sem-cenario`: `@nao-faz` no nível `Feature`; "Fora do escopo" sem cenário `@nao-faz` (info).
- `sem-features`: diretório sem `features/` (retrocompatibilidade: exit 0).
- `features-de-terceiros`: `features/` estilo behave (`steps/`, `environment.py`, `.feature` sem tag e sem `intent.md`): não é validado.
