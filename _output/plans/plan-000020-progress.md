# Progress -- Plan 000020

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

## Iteration Log

### Plan -- reflection-on-action | 2026-10-07 00:21 UTC | PKB inbox automatico, as-expressed em H-005, release v0.11.0 e upgrade do Doutourado
- happened: Plano unico com 13 steps (12 + split 7a/7b) em tres frentes: camada PKB (template + pkb_inbox.py init/capture/digest + post-skill 7f), rascunho para o /design (H-005 as-expressed, Q-014, limiar) e release + upgrade cross-repo. Revisao deep com 6 deep-dives e 10 emendas aplicadas.
- deviated: O brief pedia a tag v0.10.1; o plano publica v0.11.0 (funcionalidade nova = MINOR; v0.10.x nunca foi taggeado) e deixa o caminho de dois releases como alternativa. As 5 skills PKB ficam so no template (nao entram no .claude/skills do open-seja) depois da revisao ARCH. O interruptor da captura passou de 'existe inbox/' para 'PKB_DIR nao vazio e inbox/README.md existe'. A emenda a H-005 nao e aplicada pelo agente: vira rascunho + pendencia para o /design (T4).
- less-sure: Se o designer aceita a excecao de i18n (SKILL.md PKB em pt-BR no main); se o residuo as-expressed vs brief e um sinal util ou so ruido antes de haver limiar fixado; se o upgrade do Doutourado com o script antigo (v0.9.1) se comporta como previsto no dry-run.
- gate: not-applicable
- communication: declined

### Step 1 -- reflection-on-action | 2026-10-07 21:36 UTC | Template da camada PKB: notas-raiz e templates de nota
- happened: Criei .claude/references/template/pkb/ com inbox/README.md, logs/README.md, logs/log.md, Objetivos.md, index.md e os 6 templates de nota. Verify passou: 6 templates, todos com frontmatter, check_secrets limpo.
- deviated: O submodule do bootstrap estava vazio, entao copiei os templates de Templates/ do Doutourado (mesma origem, citada por URL no README). Troquei um travessao tipografico do Diario.md por --. Os esqueletos de Objetivos e index sao genericos, sem o conteudo do Doutourado, e sem acentos nos textos novos.
- less-sure: Se os templates do Doutourado coincidem byte a byte com o bootstrap atual (nao pude conferir).
- gate: not-installed

### Step 2 -- reflection-on-action | 2026-10-07 21:37 UTC | Template da camada PKB: as 5 skills de manutencao
- happened: Copiei as 5 skills (SKILL.md, quickguide e references) do Doutourado para template/pkb/skills/ e generalizei as mencoes a projetos/, Proposta, pegasus, disciplinas e AEWSOME. Verify passou: grep vazio e name: igual a pasta nas 5.
- deviated: Troquei travessoes e aspas tipograficas por -- e aspas retas (regra do harness). Copiei tambem as pastas references/ de weekly-review e compress, que o passo nao citava.
- less-sure: Se as frases generalizadas ('projetos do seu arquivo') bastam para as skills funcionarem em arquivo sem pasta de projetos; nao rodei as skills.
- gate: not-installed

### Step 3 -- reflection-on-action | 2026-10-07 21:39 UTC | pkb_inbox.py init: instanciar a camada PKB, idempotente
- happened: Criei pkb_inbox.py com init (--target, --with-skills, --dry-run, --json) e 8 testes escritos antes; verde. Adicionei PKB_DIR nas duas conventions.
- deviated: PKB_DIR e lido por regex do conventions.md do alvo, nao por project_config.get_path, porque get_path so resolve contra o REPO_ROOT do harness e --target pode ser outro repo. pytest nao estava instalado; rodei via uv run --no-project --with pytest.
- less-sure: Se a leitura por regex diverge de project_config em casos de borda (valores com ${...}); logs/<ano> usa o ano corrente.
- gate: not-installed

### Step 4 -- reflection-on-action | 2026-10-07 21:41 UTC | conversation_trace.py list e pkb_inbox.py capture: a nota de inbox derivada
- happened: Adicionei conversation_trace.list_entries e o subcomando list, e em pkb_inbox.py pkb_layer_present e capture (mascaramento via SECRET_PATTERNS importado, comparacao normalizada com o User brief, append sem sobrescrever). 18 testes verdes, ruff limpo.
- deviated: O exemplo ANTHROPIC_API_KEY=sk-... do plano nao casa nenhum SECRET_PATTERNS (exigem valor entre aspas), entao o teste usa api_key = "...". Quando ha falas no trace e --brief, o brief entra como linha extra '> brief' e fica fora da comparacao. Corrigi tambem o DTZ011 antigo de init (date.today -> UTC).
- less-sure: Se o led_to_skill gravado pelo backfill vai coincidir com o --skill passado ao capture (comparo exato apos tirar a barra inicial); se o padrao de segredo do projeto deveria pegar chaves sem aspas.
- gate: not-installed

### Step 5 -- reflection-on-action | 2026-10-07 21:43 UTC | pkb_inbox.py digest: o indice vivo (inbox/_live.md)
- happened: Adicionei digest (funcao e subcomando) que regenera _live.md com cabecalho gerado, tabela cronologica e coluna 'comunicado em'; recusa _live.md alheio com exit 1. 5 testes novos, 20 verdes, ruff limpo no script; duas execucoes dao bytes identicos.
- deviated: A ligacao com comunicacoes olha as 12 primeiras linhas de communication-*.md procurando o caminho do artefato (o cabecalho real usa 'Fonte' em blockquote, nao --source). Sem notas, a frase e 'nenhuma captura ainda'.
- less-sure: Se comunicacoes que citam o artefato so por ID (sem caminho completo) devem contar; se 12 linhas de cabecalho bastam.
- gate: not-installed

### Step 6 -- reflection-on-action | 2026-10-07 21:47 UTC | post-skill: etapa 7f pkb-capture, escopo do commit e gatilho de /design na 2c
- happened: verify_commit_scope.py ganhou a fonte (d) PKB_DIR/ quando a camada existe e _normalize preserva a barra final; 4 testes novos verdes (24 com pkb_inbox). post-skill ganhou 7f (silenciosa sem camada), linha na tabela --deferred, token de checkpoint e gate 2c ampliado com a linha de gatilho; DESIGN_TRIGGER_DRIFT_ITEMS vazio nas duas conventions.
- deviated: O Verify de integracao (capture+digest com inbox staged no open-seja) depende do Step 8 e nao foi rodado; coberto por testes com tmp_path. Os testes usam skill-type desconhecido para isolar o REPO_ROOT mockado. run_all_checks: sem falha nova (check_skill_system passou de FAIL para PASS).
- less-sure: Se a linha DESIGN_TRIGGER_DRIFT_ITEMS com valor vazio e lida bem por project_config e check_conventions; se o pkb_inbox importado no verify_commit_scope pesa em todo commit (e stdlib, mas e mais um import).
- gate: not-installed

### Step 7 -- reflection-on-action | 2026-10-07 21:52 UTC | Step 7a: /seja-setup --pkb e sinal has_pkb_layer
- happened: detect_setup_state ganhou signals.has_pkb_layer via import de pkb_inbox.pkb_layer_present (sem reimplementar); 2 testes novos e o de shape ajustado, 19 verdes. SKILL.md ganhou --pkb e o ancora Offer-PkbLayer (7d do install, 7c do here, 10c do demo) com AskUserQuestion; quickguide atualizado.
- deviated: step_notes.py so aceita --step inteiro: usei 7 e marquei 7a no titulo. O import de pkb_inbox e guardado por try/except ImportError (False se faltar). Ruff mostra erros antigos nos dois arquivos, nao tocados.
- less-sure: Se a camada ficar sem commit apos o 7d e aceitavel; se o sinal usa o conventions do alvo em --cwd (usa cwd como repo_root); o fluxo AskUserQuestion foi descrito, nao executado.
- gate: not-installed

### Step 7 -- reflection-on-action | 2026-10-07 21:55 UTC | Step 7b: upgrade: preservacao defensiva da camada PKB e tabela de classificacao
- happened: is_preserved protege inbox/, logs/, Templates/, Objetivos.md e index.md raiz; run_upgrade imprime 'camada PKB detectada' (import guardado de pkb_inbox) apos a copia; upgrade/SKILL.md: linha Rules alinhada ao codigo, linha PKB layer, oferta de init no passo 8. 28 testes verdes (6 novos casos + 2 de saida).
- deviated: step_notes.py exige --step inteiro: usei 7 com 7b no titulo. A dica fica antes das migracoes (logo apos a copia e remocao de skills aposentadas). Nao tratei docs/index.md como preservado (so index.md na raiz).
- less-sure: Se o import de pkb_inbox via sys.path funciona quando o script roda de outro cwd (roda: o diretorio do script entra no path); ruff tem erros antigos nos dois arquivos, nao novos.
- gate: not-installed

### Step 8 -- reflection-on-action | 2026-10-07 21:58 UTC | Dogfooding: camada PKB no proprio open-seja
- happened: Rodei init sem --with-skills (camada criada, 0 skills PKB em .claude/skills), capture e digest: 1 nota em inbox/ com 3 falas do usuario e _live.md com 1 captura. Manifesto nao inclui inbox/, logs/, Templates/, Objetivos.md nem index.md (allowlist); build_dist_branch --dry-run nao lista nenhum. Falas conferidas: sem segredos nem nomes de pessoa.
- deviated: capture pulou com nothing-to-capture porque as falas do usuario qa-000015/17/19 estavam com led_to_skill nulo (so a resposta qa-000020 tinha o campo); rodei conversation_trace backfill-skill --skill-id plan nas 3 (alterou conversation-trace.jsonl, que nao foi staged). A nota se chama 2026-10-07-plan-plan-000020-*.md (data de hoje, prefixo plan duplicado), nao 2026-10-06-. grep puc/tecgraf/behring acha 1 linha em inbox/README.md (URL publica do repo bootstrap, do template do Step 1), nao nas notas. verify_commit_scope acusa Objetivos/Templates/index/logs como unexpected (so inbox/ e coberto pela fonte d).
- less-sure: Se a ausencia de backfill das falas do usuario ocorrera no uso real (o post-skill deveria marcar led_to_skill antes de 7f); se o escopo do commit deve incluir a raiz da camada no init; se a URL org no README conta como violacao de C2.
- gate: not-installed

### Step 6 -- reflection-on-action | 2026-10-07 22:09 UTC | Step 6 addendum: capture sees the exchange chain
- happened: Adicionei conversation_trace.exchange_user_entries: para cada entrada claude marcada com led_to_skill == skill, caminha preceding_evt_id por entradas user ate uma entrada claude (ou outra skill); capture passou a usar essa funcao. 7 testes novos, 30 verdes; e2e em tmp (init, trace com so a resposta marcada, capture, digest) gerou a nota com a fala do usuario.
- deviated: Nao mudei o subcomando list nem o pre-skill; a funcao nova e so de biblioteca (sem flag CLI). O texto da etapa 7f nao dependia do comportamento antigo e ficou intacto. run_all_checks: 13 FAIL/1 erro antes e depois, sem falha nova; ruff com os mesmos 10 achados antigos.
- less-sure: Se a cadeia preceding_evt_id e sempre gravada no uso real (append usa 'null' por padrao quando o agente esquece a flag); sem ela a captura volta a nada; --since-evt so existe na funcao nova, nao no capture.
- gate: not-installed
