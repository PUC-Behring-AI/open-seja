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

### Baseline do Step 1 (worktree ~/worktrees/open-seja-sem-gherkin, base 2b17d27) | 2026-10-20
- pytest: `uv run --no-project --with pytest python -m pytest .claude/skills/scripts/tests/ --continue-on-collection-errors -q` (o python3 do sistema não tem pytest): 12 failed, 626 passed, 2 errors
- falhas e erros da base:
  - ERROR .claude/skills/scripts/tests/test_generate_spo.py
  - ERROR .claude/skills/scripts/tests/test_generate_spo_design_system.py
  - FAILED .claude/skills/scripts/tests/test_html_report.py::TestConvert::test_lang_attribute
  - FAILED .claude/skills/scripts/tests/test_html_report.py::TestConvert::test_no_external_refs
  - FAILED .claude/skills/scripts/tests/test_html_report.py::TestConvert::test_profile_document_toc
  - FAILED .claude/skills/scripts/tests/test_html_report.py::TestConvert::test_profile_onboard_has_checklist_js
  - FAILED .claude/skills/scripts/tests/test_html_report.py::TestConvert::test_profile_report_has_interactive_js
  - FAILED .claude/skills/scripts/tests/test_html_report.py::TestConvert::test_self_contained
  - FAILED .claude/skills/scripts/tests/test_html_report.py::TestConvert::test_style_css_override
  - FAILED .claude/skills/scripts/tests/test_html_report.py::TestConvert::test_title_in_output
  - FAILED .claude/skills/scripts/tests/test_summarize_artifacts.py::test_extracts_header_fields
  - FAILED .claude/skills/scripts/tests/test_summarize_artifacts.py::test_resolve_prefers_canonical_over_progress_companion
  - FAILED .claude/skills/scripts/tests/test_summarize_artifacts.py::test_resolve_prefers_canonical_over_qa_companion
  - FAILED .claude/skills/scripts/tests/test_summarize_artifacts.py::test_resolves_plan_id
- run_all_checks.py (exit 1), FAIL na base: check_docs, check_plan_coverage (REQ-VAL-001, REQ-PERM-001/002), check_api_auth_decorators, check_backend_test_coverage, check_conventions, check_frontend_test_coverage, check_i18n_keys, check_migration_chain, check_po_parity, check_skill_system, check_validation_constants_sync, check_version_changelog_sync, check_vuln_patterns, check_worktree_health

### Step 1 -- reflection-on-action | 2026-10-20 22:36 UTC | Preservar o ladder e abrir a linhagem nova
- happened: Tag archive/gherkin-ladder-v0.11.0 criada em bfac21f; worktree ~/worktrees/open-seja-sem-gherkin com dev-sem-gherkin em 2b17d27; baseline gravado: 626 passaram, 12 falhas e 2 erros, os mesmos que o plano previa.
- deviated: O python3 do sistema não tinha pytest; a suíte rodou com uv run --no-project --with pytest.
- less-sure: run_all_checks.py falha em 14 checks já na base; a comparação dos próximos steps é por nome de check, não por exit code.
- gate: not-installed

### Step 2 -- reflection-on-action | 2026-10-20 22:38 UTC | Portar o núcleo do ULID (plano 19, steps 1 a 9)
- happened: Os 9 commits entraram com cherry-pick -n e os append-only restaurados do HEAD; conflitos em test_step_notes.py (ficou só o bloco do plano 19), check_plugin_registry.json (só check_ledger_ids) e CHANGELOG.md (só o Unreleased, com D-005); pa-000008 fechada, pa-000007 dispensada. pytest: 776 passaram, mesmas 12 falhas e 2 erros da base; check_ledger_ids sem erro.
- deviated: 6320002 também conflitou, mas só no _output/INDEX.md, que a restauração resolve; o -x do cherry-pick não vale com -n, e a linha (cherry picked from commit ...) foi escrita à mão em cada mensagem; os commits usam a identidade dos commits anteriores via variáveis de ambiente, sem tocar no git config.
- less-sure: O upgrade/SKILL.md portado ainda cita D-010 (o plano o deixa para o Step 12); o progress do plano 19 portado cita check_plan_scenarios em notas históricas.
- gate: not-installed

### Step 3 -- reflection-on-action | 2026-10-20 22:39 UTC | Portar as skills do ULID (plano 19, steps 10 a 13 e correções)
- happened: f720db0, e415c95, d9a47c4 e 2f44bbb entraram com conflito só no progress do plano 19 (resolvido apensando as linhas novas); d34c8ab entrou com cherry-pick -n e os conflitos de plan/SKILL.md e drift/SKILL.md ficaram com o texto da base mais a troca de ID; 04ecf9f excluído; skills-manifest regenerado. pytest: 805 passaram, mesmas falhas da base; check_skill_spec PASS; a busca de termos do ladder em .claude/ e docs/reference voltou vazia.
- deviated: d34c8ab foi aplicado por último, depois de 2f44bbb, e não na ordem original; criei um segundo worktree da base em scratchpad para comparar checks, a remover no fim.
- less-sure: O manifest regenerado só mudou a data: os argument_hint da base não tinham as flags do ladder, então nada precisou sair.
- gate: not-installed

### Step 4 -- reflection-on-action | 2026-10-20 22:46 UTC | Portar os textos do plano 19 em _output/
- happened: 2f3cffb, 594a65b e b630b6c entraram nessa ordem (cronológica); D-010 virou D-005 no plano 19, o adendo de renumeração saiu, o plano 19 e o QA log ganharam as notas de linhagem; o STATUS da D-005 foi gravado por apply_marker.py depois da confirmação do designer; check_ledger_ids e check_human_markers_only --staged passaram.
- deviated: b630b6c também mudava a research-000018 (spawned: plan-000019 duplicado); esse hunk saiu. O QA log do plano 19 ficou com as 4 citações de D-010 no texto original e uma nota no fim.
- less-sure: O plano 19 portado tem o DONE em linha própria acima do H1; o check_ledger_ids não reclamou, mas não conferi como o generate_macro_index o lê.
- gate: not-installed
- human: "Gravar o marcador"

### Step 5 -- reflection-on-action | 2026-10-20 22:47 UTC | Fazer os scripts portados citarem a D-005
- happened: Os cinco docstrings trocaram D-010 por D-005; o git grep do Verify voltou vazio; pytest com 805 passando e as mesmas falhas da base.
- deviated: nenhum desvio
- less-sure: nada novo
- gate: not-installed

### Step 6 -- reflection-on-action | 2026-10-20 23:00 UTC | Registrar a D-006 e tirar o Gherkin do as-intended
- happened: Rascunho escrito em _output/tmp/design-rascunho-d006-2026-10-20.md e aprovado como está; prosa gravada por script com substituições exatas, D-004 superseded e D-006 proposed por apply_marker.py; check_human_markers_only --staged acusou 86 linhas, todas da reescrita, aceitas pelo designer; commit 5a0dfd9.
- deviated: A busca do Verify acha uma linha fora da D-006, da D-004 e do CHANGELOG: o fim da H-009 cita o nome da tag archive/gherkin-ladder-v0.11.0, que o rascunho aprovado trazia; design-standards.md não é Human (markers) e não aparece no verificador.
- less-sure: A D-004 ficou com o texto original e só o marcador superseded; a constituição (Q4) e a ux-research ainda citam H-009 e D-004, o que continua correto mas não foi relido.
- gate: not-installed
- human: "Gravar como está; Aceito, pode commitar"

### Step 7 -- reflection-on-action | 2026-10-20 23:01 UTC | Escrever a referência do jogo de linguagem como entrevista do /plan
- happened: plan-language-game.md criado com JDL-001 a JDL-011: entrada e saída no plano, lances, as três respostas com destino, fontes das cenas e aviso de confidencialidade, rodada com as seis dimensões, teste da surpresa, teto com três saídas, bom requisito, jogo curto, Retradução e aprovação, voz; exemplo genérico de contas a pagar. A busca do Verify deu 0.
- deviated: As regras foram renumeradas (11 em vez de 8) porque trouxeram bom requisito, teto, aprovação e voz da regra antiga; a regra de volta à entrevista clássica e a de registro do experimento saíram, como o plano pedia. Inspeção de nomes de pessoas: só uma citação bibliográfica (filósofo do jogo de linguagem), permitida por C2; nenhum nome de pessoa da equipe ou de instância.
- less-sure: As justificativas das opções Aceito/Recuso/Corrijo usam a forma curta de uma linha; a convenção a permite, mas não sei se o designer prefere a forma de duas linhas ali.
- gate: not-installed

### Step 8 -- reflection-on-action | 2026-10-20 23:02 UTC | Definir o plano v3 (intenção, requisitos, casos de uso, testes)
- happened: plan-intent-and-cases.md criado com PIC-001 a PIC-009 (cabeçalho, ordem das cinco seções, formato de cada uma, Covers:, contrato do verificador); plan-step.md ganhou a linha Covers e a regra de decomposição; report-conventions.md ganhou a subseção das seções do plano v3.
- deviated: A linha Aprovação: da Retradução ficou como warning, não error: o verificador roda depois de cada rodada, antes da aprovação, e um error ali travaria o jogo. O primeiro Verify deu 0 porque o template escrevia **Covers**:, sem o literal Covers:; acrescentei o literal num segundo commit.
- less-sure: O check_plan_coverage.py de verdade fica em .claude/skills/design/, não em scripts/ como o plano dizia; o regex dele é sensível a maiúsculas, então o slug minúsculo não colide.
- gate: not-installed

### Step 9 -- reflection-on-action | 2026-10-20 23:04 UTC | Criar check_plan_intent.py
- happened: Testes e fixtures escritos antes (vermelhos na coleta, módulo ausente); o verificador saiu com PIC-002 a PIC-008, varredura sem argumento de PLANS_DIR que pula -progress e -qa-, --json com schema_version, saída 0/1/2; registrado no fim do registry. 22 testes verdes; suíte com 827 passando e as mesmas falhas da base; run_all_checks sem check novo falhando, check_plan_intent PASS; ruff limpo depois de ordenar um import.
- deviated: Os testes passaram de primeira depois do código, sem rodada de correção; acrescentei testes além dos seis do plano (seção ausente, Retradução, quatro linhas da Intenção, Covers em N/A, ID do plano em Traces, Para que, duplicado, origem, slug maiúsculo, erro de uso).
- less-sure: A regra de origem só olha o último parêntese da linha; uma origem escrita no meio da frase não é conferida.
- gate: not-installed

### Step 10 -- reflection-on-action | 2026-10-20 23:05 UTC | Pôr o jogo de linguagem e o plano v3 no /plan
- happened: O worker padrão ganhou o passo 2b (jogo em rodadas, check_plan_intent depois de cada rodada, Retradução com Aprovar/Ajustar/Descartar, jogo curto sem código e em item de roadmap) e a validação de Covers: no passo 5; o wrapper passou a plan_format_version 3 no metadata e no C3, com --light e o resumo de roadmap em v1; o worker de roadmap diz que os itens jogam o jogo curto; quickguide e help descrevem o jogo. check_skill_spec PASS; a fixture v3_completo sai 0.
- deviated: Item de roadmap tem código, então a marca 'nenhum (tarefa sem código)' seria falsa: o verificador passou a aceitar qualquer linha 'nenhum (<motivo>)' e o roadmap usa 'nenhum (jogo curto, item de roadmap)'; PIC-002 e um teste novo acompanharam (24 testes verdes).
- less-sure: O ID passa a ser reservado e o cabeçalho gravado antes do jogo, para salvar as rodadas; se o usuário descartar, fica um plano incompleto no ledger, e o passo 2b não diz o que fazer com ele.
- gate: not-installed

### Step 11 -- reflection-on-action | 2026-10-20 23:06 UTC | Fazer o /implement ler o plano v3 e testar por requisito
- happened: Version check do modo auto com v1, v3 (check_plan_intent primeiro, para se sair != 0), v2 (frase de aviso e manual) e outro valor (para); passo 2 e passo 7 do modo manual: em v3 o teste por requisito vem antes do código, citando o ID, vermelho pelo motivo certo; contrato do subagente no modo auto com o mesmo; metadata 3 com comentário; quickguide atualizado. check_skill_spec PASS; pytest 829 passando, mesmas falhas da base.
- deviated: O metadata plan_format_version do /implement ficou 3 com um comentário YAML dizendo que lê 1 e 3 e roda 2 em manual; não achei script que leia esse campo.
- less-sure: Nenhum teste automatizado exercita o /implement em Markdown; só um ensaio real com um plano v3 mostra se o executor segue a ordem do teste por requisito.
- gate: not-installed

### Step 12 -- reflection-on-action | 2026-10-20 23:08 UTC | Fazer o upgrade limpar o que o v0.11.0 instalou e avisar
- happened: retired-files.json com 31 entradas (30 da árvore .claude do v0.11.0 e tests/scenario_report.py com o hash do .example que o instala), hashes tirados de git show v0.11.0; upgrade_harness.py ganhou load_retired_files, remove_retired_files (removido / mantido (editado), poda de pastas vazias) e ladder_warnings (features/ e PKB_DIR preenchido), chamados depois das skills aposentadas; upgrade/SKILL.md cita D-005 e descreve a limpeza. 10 testes novos vermelhos por AttributeError, depois verdes (27 no arquivo); suíte com 839 passando e as mesmas falhas da base; ruff sem achado novo (os 14 restantes já existiam).
- deviated: O teste de cobertura da lista e o do hash real usam git com as tags v0.10.1/v0.11.0 e pulam quando as tags não existem (cópia sem histórico); a lista tem 31 arquivos, não só os nomeados no plano, porque o feature-example tem 6 arquivos.
- less-sure: O tests/scenario_report.py de um cliente só sai se for cópia idêntica do .example; não conferi se a instalação do v0.11.0 o copiava sem mudança.
- gate: not-installed

### Step 13 -- reflection-on-action | 2026-10-20 23:09 UTC | Criar tests/compat com um cliente v0.11.0 e um v0.10.1
- happened: Duas fixtures mínimas (v0.11.0 com quatro arquivos do ladder idênticos ao v0.11.0, tests/scenario_report.py, check_intent.py editado, pkb_inbox.py, features/contas e PKB_DIR preenchido; v0.10.1 com um agente antigo), run_upgrade_compat.py que copia a fixture para um diretório temporário, roda upgrade_harness.py deste repositório e lê removido / mantido (editado) / Updated / WARN da saída, e 6 testes verdes; ruff limpo.
- deviated: Rodei o runner à mão sobre as duas fixtures antes de escrever os testes, para ver a saída real; os testes vieram depois, não antes. O upgrade também imprime três WARN de geradores de referência ausentes; o teste filtra só os dois avisos do ladder.
- less-sure: As fixtures têm só uma amostra dos 31 arquivos aposentados; a lista inteira é coberta pelo teste do Step 12 que compara com o git diff das tags.
- gate: not-installed

### Step 14 -- reflection-on-action | 2026-10-21 02:45 UTC | Fechamento: inventário, revisão, busca de resíduos e CHANGELOG
- happened: harness-structure.md e harness-reference.md atualizados à mão (o gerador fica em priv/, ausente), manifest regenerado, baseline de tamanho dos SKILL.md sem mudança, CHANGELOG [Unreleased] com alvo v0.12.0 (Removed, Added, Changed). A revisão de código (standard) achou 3 críticos e 8 advisórios; os 3 críticos foram corrigidos com testes: C1, a lista de aposentados passou a vir da release instalada e o upgrade/SKILL.md roda o script da release; C2, check_plan_intent ganhou --phase game e o jogo curto passou a ter Retradução curta; C3, o plugin sai do tests/conftest.py junto com o carimbo. Também entraram A1, A3, A4 e A5. Final: pytest 852 passando com as mesmas falhas da base, tests/compat 8, run_all_checks sem check novo falhando, ruff limpo nos arquivos novos.
- deviated: O /critique review rodou mesmo com --skip-checks, porque o Step 14 o pede; a revisão parou uma vez no limite de uso e foi retomada. Ficaram sem correção: A2 (qualquer linha 'nenhum (' desliga as regras de requisito), A6 (plano sem versão vai para manual no /implement e é 'nada a verificar' no verificador), A7 e A8. Resíduos aceitos na busca: a frase de aviso do v2 em implement/SKILL.md (prescrita pelo Step 11) e tests/compat/test_upgrade_compat.py (testa a remoção, como o test_upgrade_harness.py já excluído). Os achados novos de ruff em .claude/skills/ vêm dos arquivos do ULID portados (UP017, FURB162).
- less-sure: O caso C1 depende de quem roda o upgrade seguir o passo 5 novo da skill; um cliente que rodar o script antigo dele próprio não recebe a limpeza nem os avisos. tests/compat/conftest.py ignora a pasta fixtures, que tem um conftest de cliente com o plugin.
- gate: not-installed

### Step 15 -- reflection-on-action | 2026-10-21 10:42 UTC | Levar para a linhagem nova o plano que a criou
- happened: Plano, progress, QA log e registro de nascimento copiados para o worktree depois do fechamento (DONE, resumo, reflexão e drift not-measured), e commitados em dev-sem-gherkin.
- deviated: A cópia foi feita depois de marcar o DONE e escrever o resumo, para a branch nova receber a versão final.
- less-sure: Os commits seguintes do post-skill em dev (briefs, INDEX) não vão para a branch nova; só o plano e os seus companheiros.
- gate: not-installed
- drift: not-measured
