# QA Log | Plan 000005 | 2026-09-18 14:34 UTC | Registrar a hipótese SDLC 3.0 em seja-as-intended (seção 2 + Decisions)

## Brief

Registrar a hipótese SDLC 3.0 no `product-design/seja-as-intended.md` como nova seção 2 + seção `## Decisions`, em seis passos ordenados (allowlist com teste; prosa pronta para colar; `D-001` via `DECISION_APPEND`; CHANGELOG; emenda ao plan-000004; verificação C1 e citações). Fonte: log de pesquisa privado do arquivo Doutourado, não citado por ID aqui (restrição C1).

## Q&A Log

## Q1

source: research-NNNNNN (Doutourado, privado -- não citar por ID no open-seja). Registrar a hipótese SDLC 3.0 no product-design/seja-as-intended.md como nova seção 2 + seção ## Decisions. Passos, nesta ordem: (1) adicionar product-design/seja-as-intended.md a HUMAN_MARKERS_FILES em .claude/skills/scripts/human_markers_registry.py, com teste; (2) entregar a prosa da seção 2 (2.1 três fases como grão grosso de P-005; 2.2 faixa EXPLAIN/COMMUNICATE -- EXPLAIN-deriva contínua vs EXPLAIN-retradução por H-003, COMMUNICATE gated por P-005; 2.3 seta REDESIGN = deriva por evento; 2.4 H-005 as-conceived/as-intended/as-coded com duas lacunas e refutação; 2.5 governança = P-004+H-002, sem ID; 2.6 três registros de Schön relidos nas fases, refina 1.2.4; 2.7 H-006 harness que evolui da reflexão do time, WikiSkill arXiv 2608.27454 como contraste), Q-011..Q-013, e ## Decisions vazia entre ## Questões abertas e ## Referências -- prosa é autoria humana, pronta para colar; (3) --dry-run e aplicar D-001 (três fases = grão grosso de P-005; fecha Q-008) via DECISION_APPEND sem --note; (4) CHANGELOG_APPEND: seção 2 added, H-005/H-006 added, Q-011..Q-013 added, Q-008 answered D-001, Q-004 candidate, Q-006 partial, 1.2.4 refined, hipótese do plan-000004 passa a ser H-007; (5) editar Step 6 do plan-000004 (achado "## Decisions não existe" fica obsoleto; numeração H-007); (6) verificar grep -ri "stone|tecgraf" vazio e a citação Hassan et al. TOSEM 2026. Restrição C1: nenhum ID de artefato privado, nenhuma data de apresentação, nenhum nome de parceiro, nenhuma imagem de deck.

*(ID numérico do log de origem redigido para `NNNNNN` neste registro, em `_output/briefs.md` e no conversation trace, por C1.)*

## A1

Levantei o estado real antes de planejar:

- `product-design/seja-as-intended.md` (607 linhas): seção 1 com P-001..P-007 e H-001..H-004; `## Questões abertas` com Q-001..Q-010; `## Referências`; Apêndices A/B; `## CHANGELOG` com três linhas escritas à mão (`§ 1 | added`, `Q-003 | held-open`, `Apêndice B | added`). Sem `## Decisions`. Seções separadas por `---`.
- `human_markers_registry.py`: `HUMAN_MARKERS_FILES` tem cinco entradas e **não inclui** o arquivo; `apply_marker.py` recusa qualquer marcador nele hoje.
- `apply_marker.py::_apply_decision_append`: insere o `D-NNN` após a última linha não vazia antes do próximo `## `. Simulei em Python: um `---` entre `## Decisions` e `## Referências` faria o `D-001` cair **depois** da régua; sem o `---`, cai dentro da seção. O bloco de colagem omite esse `---`.
- `CHANGELOG_APPEND`: regex `DATA | [A-Z]+-[A-Z]+-\d{3,} | (added|revised|revoked|superseded) | (plan-NNNNNN|-) | nota`. Testei: `H-005 | added` rejeitado, `Q-008 | answered` rejeitado, `SEJA-H-005 | added` aceito. Nenhuma das linhas pedidas no passo (4) passa -- nem os IDs deste arquivo nem as ações `answered`/`candidate`/`partial`/`refined`.
- plan-000004, Step 6 (linhas 152-176) e emenda ARCH (linha 296): assume que `## Decisions` não existe, que `CHANGELOG_APPEND` se aplica, e numera "última hipótese H-004, última questão Q-010".
- `check_human_markers_only.py` roda no post-skill 6c sobre o diff staged e, em violação, pergunta abortar/prosseguir -- logo a prosa colada pelo designer precisa ser commitada por fora do post-skill, antes do commit dos marcadores.
- Citações verificadas na web: Hassan, Oliva, Lin, Chen & Jiang, "Towards AI-Native Software Engineering (SE 3.0): A Vision and a Challenge Roadmap", ACM TOSEM, DOI 10.1145/3807901, online em 21 ago. 2026 (preprint arXiv:2410.06107, 2024) -- "TOSEM 2026" confere. Tang, Rashtchian, Ferng, Tomkins, Juan & Vu, "WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution", arXiv:2608.27454, 27 ago. 2026 -- confere.

## Q2

(AskUserQuestion) Como registrar as linhas do CHANGELOG, dado que o regex de `CHANGELOG_APPEND` rejeita os IDs e as ações desse arquivo? Opções: (a) prosa humana, colada junto com a seção 2; (b) alargar o regex no fork; (c) reformular os IDs para o esquema do script (`SEJA-H-005`).

## A2

**Prosa humana (colar junto com a seção 2).** O passo (4) do brief se funde ao passo (2): as nove linhas de CHANGELOG entram no bloco pronto para colar, como as três linhas já existentes; só `D-001` vai pelo script. Zero mudança no harness além da allowlist; fork colado ao upstream (`CONVENTION_2`); um só esquema de ID no documento público. Consequência anotada na linha `Q-006 | partial`: a promessa do cabeçalho do arquivo (agente apensa CHANGELOG via `apply_marker.py`) segue não cumprível para os IDs deste arquivo.

## Q3

(implícito) Gerar o plano.

## A3

Plano 000005 gerado com cinco passos (`REDESIGN-O`, revisão Light: 5 passos, 4 arquivos): (1) allowlist + `test_human_markers_registry.py` com quatro comportamentos observáveis; (2) bloco pronto para colar com cinco pontos de inserção -- seção 2 (2.1-2.7, H-005, H-006), Q-011..Q-013 + fechamento de Q-008 na tabela, `## Decisions` sem `---` antes de `## Referências`, duas referências verificadas, nove linhas de CHANGELOG -- commitado pelo designer por fora do post-skill; (3) `D-001` via `DECISION_APPEND` com `--dry-run` primeiro, sem `--note`, seguido de `check_human_markers_only.py --staged`; (4) emenda **aditiva** ao plan-000004 (fragmentos P4-S6-F1..F4 marcados superseded, texto substituto apensado como Plan Amendment iteração 2; numeração H-007 / Q-014); (5) verificações C1 (grep `stone|tecgraf`, IDs privados) e citações. Revisão Phase 1 com ARCH, DX, SEC, COMPAT, TEST, DATA todas Adopted; sem conflitos. O ID do log de origem que o brief literal carregava foi redigido em `_output/briefs.md` e no conversation trace antes do commit, por C1.
