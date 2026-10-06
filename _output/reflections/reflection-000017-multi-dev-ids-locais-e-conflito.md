# Reflection 000017 | 2026-10-06 22:30 UTC | Multi-dev: IDs locais e conflito entre maquinas

**Lens**: product

## Artifacts reflected on

- [plan-000004](../plans/plan-000004-seja-como-servico-mvp-seja-config-kb-seja-setup.md) | 2026-09-04 | seja como serviço MVP: seja-config, KB e o papel do seja-setup

## Summary

**Brief que abriu a reflexão** (palavras do designer):

> o open-seja está sendo usado por times de desenvolvimento. mas o uso tem de ser síncrono, em alguma medida, pois os ids são computados localmente e podem ter conflito, caso 2 devs invoquem uma skill ao mesmo tempo em maquinas diferentes. vamos refletir sobre iisso e bolar um plano para um upgrade do seja: multi-dev

**plan-000004**, como registrado:

- **Problema, nas palavras do plano**: "o SEJA não tem hoje fronteira própria. Ele é markdown e Python inertes que o Claude Code anima ao ler `.claude/`; não existe nenhum ponto em que outra harness (OpenCode, Cursor, um agente próprio) possa *chamá-lo*."
- **Abordagem**: documento de exploração (`docs/seja-as-a-service.md`) em 7 steps: modelo de serviço, `seja-config`, KB (corpus, exclusões, regenerabilidade), redefinição do `/seja-setup` como provisionamento, mapa de consumo, registro na intenção (H-007), roadmap-spec. O plano declara que "não constrói nada".
- **Review log**: o deep-dive SEC apontou que a recuperação é uma segunda travessia de fronteira de confiança que a ignore-list de ingestão não modela.
- **Estado**: pendente há 32 dias no ledger (banner do pre-skill em 2026-10-06); nunca implementado.
- **Não medido**: notas por step, nota da fase de plano, evidência de portão, comunicação do plano e deriva. Nenhum dos quatro espelhos foi oferecido ou registrado.

**Contexto de código observado na sessão** (não interpretado): `reserve_id.py` declara em sua docstring "single-writer assumed". Ele lê o maior ID numérico em `_output/INDEX.md`, calcula o próximo inteiro sequencial zero-padded a 6 dígitos e apensa uma linha RESERVED; a escrita usa `os.replace`, atômica apenas dentro de uma máquina.

## Reflection

> seja como serviço. casa com conversa entre designers sobre a arquiitetura front-back do seja. o que é front end na ponta do harners, claude code aqui por ex, e o core da funcioinalidade do seja: o rastreio semiotiico do SDLC. Neste caso estamos pensando na funcioinialidade core do seja: os ids são um inteiro sequencial, melhor seria um sha ?

## Follow-ups

Questões abertas que a reflexão deixou, sem resposta aqui:

- O que, no ID de um artefato, é front-end (apresentação do harness, ex.: Claude Code) e o que é core (rastreio semiótico do SDLC)? O inteiro sequencial legível pertence a qual dos dois lados?
- Se o identificador do core for um hash de conteúdo, o que entra no conteúdo hasheado: brief, data, autor, artefato anterior na cadeia (`source:`/`spawned:`)? Dois devs com o mesmo brief no mesmo instante produzem o mesmo hash?
- O que acontece com os lugares que hoje dependem da ordem numérica: a regex do macro-index (`# Reflection <id> | ...`), `check_plan_coverage`, `pending.jsonl`, o `decision-digest`, os links `plan-NNNNNN` nos arquivos Human (markers)?
- Onde, além de `INDEX.md`, a escrita concorrente de dois devs colide hoje: `briefs.md`, `telemetry.jsonl`, `conversation-trace.jsonl`, `pending.jsonl`? O conflito é resolvido por combinação entre pessoas ou no merge do git?
- O plan-000004 (seja como serviço, H-007) é o lugar onde a questão dos IDs entra, ou a questão é anterior a ele e vale mesmo sem serviço (IDs sem coordenação)?
- Que artefato vem a seguir: `/research` para a fronteira front/core e o esquema de ID, ou `/plan` direto para o upgrade multi-dev?
