# Research 000018 | FEATURE-X | 2026-10-06 22:47 | Upgrade multi-dev: esquema de IDs e pontos de colisao
source: reflection-000017 -- IDs computados localmente colidem entre maquinas; sha ou inteiro?
tags: multi-dev, artifact-ids, ledger, architecture, dx, data-integrity, seja-mcp

## User brief

> source: reflection-000017. Upgrade multi-dev do SEJA: o open-seja e usado por times e o uso precisa ser sincrono porque reserve_id.py ("single-writer assumed") computa IDs localmente como inteiro sequencial a partir de _output/INDEX.md, e dois devs em maquinas diferentes podem reservar o mesmo ID. Perguntas: (1) onde a escrita concorrente colide de fato hoje (INDEX.md, briefs.md, pending.jsonl, telemetry.jsonl, conversation-trace.jsonl, decision-digest) e o que o merge do git resolve ou nao; (2) esquema de ID para o core (rastreio semiotico do SDLC): inteiro sequencial vs hash de conteudo vs ID do commit do git (circularidade: o SHA so existe depois do commit que contem o nome do arquivo com o ID; variantes: SHA do commit pai como prefixo, hash do conteudo do artefato, ULID) vs prefixo por dev + sequencial; o que depende da ordem numerica (regex do macro-index, check_plan_coverage, links plan-NNNNNN em arquivos Human (markers), pending); (3) fronteira front-end (harness na ponta, ex. Claude Code) vs core do SEJA, e se o ID legivel pertence ao front ou ao core; (4) relacao com plan-000004 / H-007 (seja como servico): o problema de IDs e anterior ao servico e vale sem ele? Entregar recomendacao e recorte para um /plan "upgrade multi-dev".

Mensagens do designer durante a pesquisa (verbatim):

> que tal usar o id do commit do git ?

> o ID leggível tambem poderia ter um apelido no front end

> tipo: O plano do Criar Projeto

## Agent interpretation

O ID de artefato do SEJA acumula tres funcoes num unico inteiro: **identidade** (endereco nunca reatribuido, para onde apontam cross-refs, marcadores e proveniencia), **alocacao** (quem entrega o proximo numero sem colisao) e **legibilidade** (as pessoas dizem "o plan 7"). A restricao do designer de que o numero legivel e citado *entre maquinas* elimina numeros locais por clone (modelo Mercurial) e renumeracao pos-merge. Logo a pergunta nao e "hash ou inteiro", e sim "onde fica o ponto de serializacao que torna o inteiro global". Com uma branch compartilhada e sem servico, esse ponto so pode ser o `origin/<branch>`. O hash entra como chave secundaria e imutavel do core; o apelido entra como signo do front-end que resolve para o ID.

Restricoes levantadas em entrevista:

| Pergunta | Resposta do designer |
|---|---|
| Topologia | Um repo, todos na mesma branch (pull/push direto, sem PR) |
| O ID legivel importa? | Importa: citam em conversa ("o plan 7") |
| Servico central agora? | Offline so com git; o servico (H-007) vem depois e consome o mesmo esquema |
| Apelido | Sim, no front-end, em linguagem natural ("o plano do Criar Projeto") |

## Files

- `.claude/skills/scripts/reserve_id.py` -- alocador max+1 sobre a coluna ID de `_output/INDEX.md` (:44, :64-67, :115); apensa linha RESERVED no fim (:120-127); docstring "single-writer assumed" (:8, :16); `os.replace` atomico so por maquina (:81-102).
- `.claude/skills/scripts/generate_macro_index.py` -- INDEX.md e derivado dos headers, exceto as linhas RESERVED, preservadas (:585-626) e descartadas quando o artefato aparece (:649-653). Regex de H1 por tipo (:90-218), todos `(\d+)` com `zfill(6)`.
- `.claude/skills/scripts/pending.py` -- `pa-NNNNNN` max+1 (:127-136); redutor last-write-wins por id funde dois registros distintos com o mesmo id (:151-160); `_append` le e reescreve o arquivo inteiro (:118-124).
- `.claude/skills/scripts/conversation_trace.py` -- `qa-NNNNNN` max+1 (:89-97); `backfill-skill` reescreve o arquivo inteiro (:190-193).
- `.claude/skills/scripts/apply_marker.py` -- `D-NNN` max+1 (:219-234) dentro de arquivo Human (markers).
- `.claude/skills/scripts/human_markers_registry.py` -- gramatica dos marcadores fixa `plan-\d{6}` (:81, :105, :112, :120) em prosa humana.
- `.claude/skills/scripts/update_cross_refs.py` -- edita a linha `spawned:` do artefato de origem no lugar (:134-136).
- `.claude/skills/scripts/mark_brief_done.py` -- assume briefs.md newest-first (:19, :102).
- `.claude/skills/scripts/migrate_to_global_ids.py` -- renumeracao one-shot ja existente; "rewrites history", pula `.jsonl` (:59).
- `.claude/references/general/harness-governance.md:91` -- contrato de escrita diferida: estado compartilhado atualizado pos-merge, serializado na main.
- `.claude/references/general/batch-execution-pattern.md:20-22` -- reservar IDs antecipadamente evita conflito entre subagentes.
- `.claude/references/general/report-conventions.md:9` -- define o ID como sequencial, 6 digitos, global.
- `product-design/constitution.md` -- T3: artefatos de `_output/` sao imutaveis; correcao por apensamento.
- `_output/INDEX.md:10-12, :22` -- fragilidade ja visivel numa so maquina: plan-000007, 000009 e 000015 indexados como "Other" com ID vazio (header com campo METACOMM extra), e as linhas RESERVED correspondentes nunca sao descartadas.
- `_output/plans/plan-000004-seja-como-servico-mvp-seja-config-kb-seja-setup.md` -- H-007; `docs/seja-as-a-service.md` planejado nao existe.
- Sem `.gitattributes` no repo; sem hook pre-commit ativo (`.githooks/` ausente, `core.hooksPath` nao definido); nenhum verificador de ID duplicado ou RESERVED orfao em `check_plugin_registry.json`.

## Q&A log

### Q1

(brief acima, mais as tres mensagens do designer durante a pesquisa)

### A1

**1. Onde a escrita concorrente colide hoje, e o que o git resolve.**

| Arquivo | Padrao de escrita | Verdade ou derivado | Merge de dois appends divergentes |
|---|---|---|---|
| `INDEX.md` | RESERVED no fim; regenerado inteiro no post-skill | derivado, exceto RESERVED (entrada da alocacao) | conflito textual no fim; e o unico lugar onde a colisao de numero poderia ser notada, e nao e |
| `briefs.md` | insercao no topo; edicao de uma linha no lugar | verdade | conflito (mesmo ponto sob o header) |
| `telemetry.jsonl`, `conversation-trace.jsonl`, `pending.jsonl` | append no fim (pending reescreve tudo) | verdade (logs de eventos) | conflito textual; `pa-` e `qa-` colidem por max+1; o redutor do pending **funde** dois registros distintos com o mesmo `pa-` em silencio |
| `briefs-index.md`, `decision-digest.jsonl` | reescrita total | derivados | conflito, mas regeneraveis |
| `.pending-*-stamp` | sobrescrita de uma linha; lido por mtime | estado de throttle | conflito; checkout reseta mtime |
| linha `spawned:` do artefato de origem | edicao no lugar | verdade | mesma linha: um filho se perde |
| `## Decisions` do as-intended | `D-NNN` max+1, apensado no fim da secao | verdade, humano | conflito no rebase (raro, aceitavel como detector) |

O git resolve nada disso por conta propria: nao ha `merge=union`, e dois arquivos `plan-000018-*.md` com slugs diferentes coexistem sem que nada reclame. A colisao hoje e **silenciosa** ("Looks fine to me").

**2. Esquema de ID.** Candidatos avaliados por ARCH, DX, DATA, OPS, TEST, SEC, COMPAT e UX (research-reviewer):

| Candidato | Veredito | Razao decisiva |
|---|---|---|
| A. Sequencial + prefixo por dev (`plan-ar-000007`) | rejeitar | "plan 7 de quem?"; quebra ~30 regexes e a gramatica dos marcadores em prosa humana; codifica o alocador no endereco |
| B. Hash no core + numero local por clone + apelido (Mercurial) | rejeitar como ID visivel; manter a ideia como chave secundaria | numero local falha a restricao "cito entre maquinas" (a armadilha conhecida do hg); hash de **conteudo** e instavel porque planos mudam depois de nascer (status, review log, progress) |
| C. Hash no core + numero global atribuido no merge (renumeracao) | rejeitar como caminho padrao | viola T3 (reescreve historia compartilhada); "plan 18" no standup vira "plan 19" depois do push; `migrate_to_global_ids.py` mostra que renumerar aqui e lossy |
| D. Reserva git-nativa por ref/tag em `refs/seja/ids/` | primitiva certa, armazenamento errado | atomica no servidor, mas invisivel ao macro-index e sujeita a restricao de namespace de refs em alguns hosts |
| E. Manter tudo + `merge=union` + verificador + `seja reconcile` | adotar a parte de merge-friendliness e o verificador | nao remove a corrida; `reconcile` e C de novo |
| **D' (sintese). Reserva por push na branch compartilhada, um arquivo por ID em `_output/ids/`, INDEX.md 100% derivado** | **adotar** | ver abaixo |

**SHA do commit do git (ideia do designer):** nao viavel como ID, por tres razoes. (a) Circularidade: o SHA so existe depois do commit que ja precisa conter o ID no nome do arquivo e no header. (b) O SHA do commit **pai** identifica o ponto da branch, nao o artefato: dois artefatos nascidos sobre o mesmo pai colidem; e o candidato A disfarcado. (c) Hash de conteudo e instavel pelo motivo acima. O que **e** viavel: sha256 de um **registro de nascimento imutavel** (tipo, titulo, autor, timestamp UTC, artefato de origem), funcionalmente um ULID com proveniencia, gravado como linha de header `uid:` e nunca no nome do arquivo. Dois devs com o mesmo brief no mesmo segundo produzem uids diferentes porque o autor difere.

**Como D' funciona.** A entrada da alocacao sai de dentro do INDEX.md (um arquivo derivado e regenerado) e vira um diretorio de marcadores, um arquivo por reserva: `_output/ids/000018.json` com `{type, title, author, ts_utc, uid}`. `reserve_id.py --sync` faz `git fetch`, calcula o max sobre `_output/ids/` no local **e** em `origin/<branch>`, escreve o marcador, commita e faz push; se o push for rejeitado, `pull --rebase` e tenta de novo com o novo max (tentativas limitadas). Como cada ID e um caminho proprio, dois devs reservando o mesmo numero produzem um conflito add/add **no mesmo caminho**, que e exatamente o detector de colisao, e nunca um conflito textual em INDEX.md. O macro-index passa a ler o estado RESERVED do diretorio, e INDEX.md fica inteiramente derivado, seguro para regenerar depois de cada pull. Offline: reserva local com `provisional: true`; o post-skill recusa fazer push de artefato provisorio ate o `--sync` passar, e a unica renumeracao possivel e de artefato nunca compartilhado, o que nao viola T3. E o contrato de escrita diferida de `harness-governance.md:91` com o `origin` no papel do orquestrador.

**O que depende da ordem numerica**: so os quatro geradores max+1 (artefatos, `pa-`, `qa-`, `D-NNN`) e alguns globs ordenados (`check_plan_coverage:226`, `generate_decision_digest:145`, `step_notes:112`). Todo o resto (regexes do macro-index, marcadores, cross-refs, check_docs) depende so do **formato** `\d{6}`. Manter o inteiro visivel e acrescentar `uid:` e `alias:` como linhas de header e mudanca aditiva, MINOR; mudar o formato visivel e MAJOR, com migracao de prosa em arquivos Human (markers).

**3. Fronteira front-end / core.** O **core** e dono da identidade (nunca reatribuida; carregada em nome de arquivo, header, cross-refs e marcadores) e do registro imutavel de qual numero legivel foi atribuido (`_output/ids/`). O **front-end** e dono da apresentacao e do apelido. Hoje o inteiro de 6 digitos e identidade e rotulo ao mesmo tempo; fica assim para enderecos, e o apelido entra como signo do front-end: linha `alias:` opcional em texto livre (pt-BR permitido), resolvida por um `resolve_artifact.py "<apelido | id | 'plan 7'>"` usado por `/explain`, `/communicate` e pela retraducao ao citizen. Apelido nao e unico por natureza (dois devs podem chamar planos diferentes de "Criar Projeto"): unicidade vira **aviso** no verificador, nunca nome de arquivo; sanitizar antes de qualquer uso em caminho.

**4. Relacao com plan-000004 / H-007.** O problema de IDs e anterior ao servico e vale sem ele. O que um `seja-mcp` futuro reusa sem mudar: o contrato de reserva (`reserve(type, title, author) -> id`, idempotente sobre o registro de nascimento), o store `_output/ids/` um-arquivo-por-ID (o servico vira o serializador no lugar do push, mesmos arquivos), as linhas `uid:` e `alias:` e o resolvedor, o verificador de duplicados como chamada de validacao, e a gramatica de header e nome de arquivo intacta. Nada em D' assume a ausencia do servico; o servico so substitui o `git push` como ponto de atomicidade.

**Caminhada, dois devs na mesma branch:** A faz `/plan` -> pre-skill roda `reserve_id.py --sync` -> fetch, max=18 no origin -> escreve `_output/ids/000019.json`, commit, push OK -> "reservado 000019 em origin". B, 10 s depois, no mesmo ponto: fetch, max=19 -> escreve `000020.json` -> push OK. Se B tivesse feito fetch antes do push de A: escreve `000019.json`, push rejeitado, `pull --rebase` -> add/add em `_output/ids/000019.json` -> o script detecta, descarta o proprio marcador, recalcula max=19, escreve `000020.json`, push OK. Nenhum dos dois toca INDEX.md.

## Recommendations summary

1. **[HIGH] Adotar D'**: reserva por push na branch compartilhada, um marcador por ID em `_output/ids/`, INDEX.md 100% derivado, `provisional: true` offline, post-skill recusa push de provisorio. Custo: um commit pequeno por reserva e uma ida a rede no inicio de `/plan`, `/research` etc.
2. **[HIGH] `check_ledger_ids.py`** antes de tudo: IDs de 6 digitos duplicados em `_output/**`, RESERVED orfaos ha mais de N dias, `pa-`/`D-NNN` duplicados, apelidos repetidos (aviso). Registrar em `check_plugin_registry.json`, rodar no pre-skill e no `run_all_checks.py`, com caso positivo e negativo. E o unico item que torna a colisao de hoje visivel, e custa quase nada. Manter um reparo **manual** (sucessor com escopo de `migrate_to_global_ids.py`, renumera um artefato e reescreve suas referencias) para o duplicado raro pos-push; nunca automatico.
3. **[MEDIUM] Arquivos compartilhados merge-friendly**: `.gitattributes` com `merge=union` para `_output/*.jsonl` e `briefs.md`; `spawned:` append-only (uma linha por filho) em `update_cross_refs.py`; redutor do pending passa a **falhar** quando um segundo registro de criacao chega com id existente (`pending.py:158-160`); `pa-<utc-compacto>-<4 hex do autor>` e `qa-<sessao-curta>-NNNNNN` para os ids secundarios.
4. **[MEDIUM] `uid:`** (ULID ou sha256 do registro de nascimento) como linha de header aditiva em todo artefato novo, escrita pela mesma reserva. Nenhuma regex a usa hoje; e a identidade de core que o servico e o resolvedor de apelidos vao chavear. Sem retrofit.
5. **[LOW] Apelido como signo de front-end**: `alias:` opcional, `resolve_artifact.py`, unicidade como aviso, sanitizacao antes de uso em caminho.
6. **[LOW] Registrar como D-NNN** a rejeicao de A, B, C e do SHA de commit, para a questao nao reabrir quando o plan-000004 / H-007 retomar.

Recorte sugerido para o `/plan "upgrade multi-dev"`: recs 2 e 3 (prevencao visivel e merge-friendliness, sem mudar formato) num primeiro plano; recs 1 e 4 (D' e `uid:`) num segundo; rec 5 num terceiro, ligado a retraducao do citizen (D-004 do open-seja).

Fontes externas consultadas: [git-bug data model](https://git.secluded.site/git-bug/blob/v0.8.1/doc/design/data-model.md?source=1) (entidades como CRDTs por operacao, IDs por hash, merge por uniao); [Mercurial: revision numbers vs changeset IDs](https://www.mercurial-scm.org/pipermail/mercurial/2006-May/008006.html) (numero local nao e portavel entre clones).
