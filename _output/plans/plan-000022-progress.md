# Progress -- Plan 000022

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

## Iteration Log

### Plan -- reflection-on-action | 2026-10-07 15:51 UTC | specify-switch: interruptor da specify por projeto e escolha por plano
- happened: Plano de 11 steps a partir do adendo 2026-10-07 do roadmap-000006; grill curta (harness) com duas respostas do designer; revisao deep com 6 deep-dives e emendas A1-A6 aplicadas nos Steps.
- deviated: O plano reabre mais que D-009 e CYC-004: tambem D-005, CYC-018, CYC-029 e CYC-033. Steps 4, 5, 8, 9 e 11 passaram a ter Tests reais (a premissa de que o PFS-013 exigia N/A estava errada). O CHANGELOG ja tem a secao v0.11.0 cortada sem tag, entao o Step 11 escreve nela, nao em Unreleased. Antes do plano, foi preciso integrar dev com origin/dev (colisao de D-005 e do contador de IDs).
- less-sure: Nome da flag de desligar (--no-specify ou --without-specify) e sequencia de release com o plan-000020 ficam para o Step 2; a leitura por protocolo de H-009 so e mensuravel no piloto com oraculo.
- gate: not-applicable
- communication: declined

### Step 1 -- reflection-on-action | 2026-10-07 16:03 UTC | Rascunho da revisão para o /design
- happened: Rascunho escrito em _output/tmp com a nova D-NNN que substitui a D-009, a revisão da D-005 em duas formas, o ajuste a H-009 (ITT e por protocolo, mensurável só no piloto com oráculo), o alcance no contrato e no protocolo, e as três decisões do designer.
- deviated: Erro no adendo do roadmap escrito hoje (braço B no lugar de A), corrigido por apensamento (T3).
- less-sure: Se a forma 1 da revisão da D-005 (só citar) basta para quem lê só as decisões.
- gate: not-installed

### Step 2 -- reflection-on-action | 2026-10-07 16:25 UTC | Registrar a revisão no /design
- happened: O designer aprovou o rascunho no /design. D-011 registrada (STATUS proposed, plan-000022) com a A.1 como está; D-009 marcada superseded. D-005 pela forma 1: a D-011 cita os dois pontos que mudam, a D-005 fica como está. Flag de desligar: `--without-specify`. Release: interruptor na v0.11.0, PKB (plan-000020) na v0.12.0. O /design não vira segunda porta (fora do escopo). Parte B: o designer autorizou o agente a inserir o texto de B.1 literalmente no §3 2.9 (override explícito de T4 neste turno, anotado num comentário acima do trecho).
- deviated: D-011 com Consequences e Rejected Alternatives em linha única (o verificador só aceita os rótulos DDR em linha única). As três linhas do CHANGELOG (D-011, D-009, H-009) foram apensadas à mão: o regex do CHANGELOG_APPEND só aceita IDs `XXX-YY-NNN` (lacuna já registrada em 2026-09-18). A linha `*Source:*` que o próprio apply_marker escreve também é acusada pelo check_human_markers_only.
- less-sure: Se a D-010 deve receber o STATUS que ficou faltando no merge; não mexi.
- gate: not-applicable

### Step 3 -- reflection-on-action | 2026-10-07 16:26 UTC | Emendas ao contrato, à grill, à specify e ao formato de plano
- happened: Cinco referências receberam só acréscimos marcados emenda 000022, citando a D-011: no contrato, CYC-035 (três classes de pulo), CYC-036 (SPECIFY_DEFAULT, --with-specify, --without-specify, linha Specify default:) e emendas ao CYC-018/Compatibilidade, CYC-029, linha 2 de Decisões pendentes e CYC-033, cada uma com Ruptura que pode provocar, mais linhas Emendado por nas regras antigas e uma linha nova em cada tabela; duas linhas na GRL-012; emenda ao SPC-002; gramática, PFS-002, PFS-013, PFS-016 e chaves --json em plan-from-scenarios.md; ressalva em plan-step.md. numstat com 0 remoções; run_all_checks com o mesmo conjunto de falhas antes e depois.
- deviated: A linha de base real era 19 passed / 14 failed, não 18/15: check_human_markers_only passava. Acrescentei à gramática um erro PFS-002 não listado no plano: opt-out com Specify default: off (simétrico a default off com on, porque --without-specify com off não faz nada). No PFS-013 emendado, defini que default off/opt-out com Tests reais e Scenarios N/A não emite nem o info.
- less-sure: Se o Step 5 deve aceitar a classe tarefa sem código só com acento (sem acento cai no legado, com a mesma classe); e se o erro opt-out com off deve ganhar fixture no Step 5, que não o lista.
- gate: not-installed

### Step 4 -- reflection-on-action | 2026-10-07 16:31 UTC | SPECIFY_DEFAULT nas convenções e um leitor
- happened: Escrevi primeiro 13 testes de specify_default em test_project_config.py e os vi vermelhos pelo motivo certo (AttributeError: o módulo não tinha specify_default). Implementei specify_default(root=None) em project_config.py com regex próprio da linha SPECIFY_DEFAULT (valor com ou sem crases), leitura direta de <root>/product-design/conventions.md e da pasta legada, sem cache e sem cair no template; ausente, vazio ou {{...}} = on; outro valor levanta ValueError em pt-BR com o valor lido. Acrescentei a linha na tabela Review Configuration do template ({{SPECIFY_DEFAULT}}) e do conventions.md do open-seja (on). test_project_config.py 20 passed; suíte completa com o mesmo conjunto de 13 falhas pré-existentes; run_all_checks 19/14 com o mesmo conjunto.
- deviated: check_conventions.py ganhou um WARNING de variável definida e nunca referenciada (SPECIFY_DEFAULT), sem erro novo (continua 17 undefined). É inevitável enquanto o Step 3 proíbe ${SPECIFY_DEFAULT} nas referências, como já acontece com GATE_* e MINIMUM_REVIEW_DEPTH. Acrescentei casos além dos listados: template não é lido quando falta o conventions.md, pasta legada project-design/, valor entre crases vazias, e root ausente lendo REPO_ROOT. O valor é normalizado para minúsculas (OFF vira off).
- less-sure: Se aceitar OFF/On em maiúsculas é desejável ou se deveria ser ValueError; e se a linha deveria morar numa seção própria do ciclo em vez de Review Configuration.
- gate: not-installed

### Step 5 -- reflection-on-action | 2026-10-07 16:37 UTC | check_plan_scenarios.py lê a classe do pulo
- happened: Escrevi primeiro 14 fixtures e 33 testes novos e os vi vermelhos pelo motivo certo (44 falhas: AttributeError skip_class, KeyError skip_class no --json, PFS-016 ausente, info do PFS-013 em default off). Implementei skip_class(value) -> (classe | None, motivo) como parser único, a leitura de Specify default: (ausente = on), os erros PFS-002 da gramática e da incoerência do cabeçalho (default off com on ou sem a linha; opt-out com off), o PFS-013 emendado (default off e opt-out com Tests reais e Scenarios N/A (motivo) não emitem nada; chave ou teste sem N/A é erro com a dica da specify desligada), a PFS-016 info (opt-out com on, approved com off) sem ler conventions.md, e as chaves skip_class, skip_reason e specify_default no --json. test_every_checkable_rule_has_a_firing_and_a_clean_case voltou a verde. test_check_plan_scenarios + test_build_checks: 296 passed; suíte completa 1548 passed, 12 failed (as 8 de test_html_report e 4 de test_summarize_artifacts de antes); run_all_checks 19/14 com o mesmo conjunto; plano 000022 e scan saem 0; nenhum esperado.json existente mudou.
- deviated: Fixtures além das cinco listadas: pfs-002-opt-out-com-default-off (erro decidido no Step 3), pfs-002-opt-out-motivo-curto, pfs-002-default-off-sem-linha, pfs-002-specify-default-invalido, pfs-002-specify-default-duplicado, pfs-013-legado-parenteses-na-com-motivo, pfs-013-default-off-sem-na, pfs-016-opt-out-sem-linha e pfs-016-approved-com-default-off. A pfs-016-default-off-com-testes é o caso limpo (nenhum achado), não um disparo. specify_default sai null num v2 cuja linha é ilegível (valor fora de on/off, ou duplicatas que discordam); a referência só fala de on/off em v2. skip_class e skip_reason saem null quando o valor pulado é malformado (o cabeçalho não é confiável, e os steps não são lidos, como no erro de formato de hoje). skip_class também aceita o valor inteiro skipped -- .... Os achados de incoerência e a PFS-016 apontam a linha Specify:.
- less-sure: A classe é sensível a maiúsculas (Opt-out: ... cai no legado); default off: com dois-pontos e nada depois é erro, não default off sem motivo; e se null em specify_default para linha ilegível é melhor que on para o cycle_adherence.py do Step 8.
- gate: not-installed
