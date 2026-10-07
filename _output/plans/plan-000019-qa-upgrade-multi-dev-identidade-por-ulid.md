# QA Log | Plan 000019 | 2026-10-07 20:05 UTC | Upgrade multi-dev: identidade por ULID, gramatica aditiva e verificador

## Brief

"/implement 19" -- execucao do plan-000019 em auto mode (14 steps), quality gate final e post-skill.

## Q&A Log

## Q1

/implement 19

## A1

Executei o plano em auto mode, um subagente e um commit por step, na ordem 1-9, 14, 10-13; branch de rollback `pre-plan-000019`. Os 14 steps terminaram em SUCCESS, cada um com nota de reflexao no progress file (gate: not-installed). Quality gate: `run_all_checks` 20 PASS / 14 FAIL, igual ao pre-plano; suite 1810 passed / 4 failed (as 4 da linha de base); revisao de codigo com 1 critico (`check_ledger_ids` nao reconhecia tipos com hifen) corrigido em 2f44bbb, junto com A2, A8 e os warnings novos do `check_docs`; 8 advisorios diferidos. Plano marcado DONE.

## Q2

(Oferta de medir deriva) -- Seguir sem medir (Recomendado).

## A2

Registrei `drift: not-measured` no progress file.

## Q3

(Marcador da D-010, as-coded, docs) -- "qual o impacto de implementar os apelidos ? já tem plano ?"; as-coded: Adiar (pendencia); docs: Pular.

## A3

Registrei as pendencias verify-as-coded (pa-000020) e update-documentation (pa-000021). Respondi que R2-4 nao tem plano: a research-000018 o pos como terceiro plano, depois de R2-5. O escopo seria apelido derivado pronunciavel do ULID no registro de nascimento, `alias:` livre opcional no header e `resolve_artifact.py` para /explain, /communicate e a retraducao ao citizen. O impacto e aditivo e menor que o deste plano, porque o apelido nunca entra em caminho nem em regex de marcador. Fica em aberto o apelido de artefatos legados, que nao tem uid.

## Q4

como ficam repositorios seja com artefatos previos, ao fazer upgrade ?

## A4

Nada e renomeado (T3): IDs de 6 digitos continuam validos e todas as regexes aceitam os dois formatos. `_output/ids/` nasce na primeira reserva, entao nao ha migracao. Na primeira regeneracao, o INDEX.md perde as linhas RESERVED, e planos com `# DONE` em linha propria passam a ser indexados como Plan. Artefatos novos saem com `YYYYMMDD-xxxxxx` e `uid:`. O `check_ledger_ids` no pre-skill pode revelar duplicatas antigas reais. Ressalvas: projetos com numeracao por tipo anterior ao `migrate_to_global_ids` teriam pares acusados como duplicados (A10); IDs legados curtos ficam ignorados por tres parsers (A5); versoes mistas do harness no mesmo ledger quebram o commit de marcadores novos, por isso a nota de upgrade pede atualizacao conjunta. O ensaio rodou num clone deste repositorio (ledger legado), nao em outro projeto nem num upgrade por tag.

## Q5

(Marcador da D-010, reapresentado) -- Marcar proposed (Recomendado).

## A5

Apliquei `<!-- STATUS: proposed | plan-000019 | 2026-10-07 -->` na D-010 via `apply_marker.py`.
