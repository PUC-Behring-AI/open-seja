# Roadmap 000006 | 2026-10-04 | SEJA: ciclo default de desenvolvimento de software (PLAN com grill e specify)

> **Origem**: movido do ledger do Doutourado em 2026-10-05 (proposal-000088; la era `roadmap-000056`). Os IDs roadmap-000006 e plan-000007..000016 sao deste ledger (tabela no roadmap). Referencias a research-NNNNNN, reflection-NNNNNN, communication-NNNNNN, roadmap-000062 e plan-000064..000074 apontam para o ledger do Doutourado (repositorio do pesquisador). Caminhos `open-seja/...` em Files passam a ser relativos a raiz deste repositorio.
>
> | Doutourado | open-seja |
> |---|---|
> | roadmap-000056 | roadmap-000006 |
> | plan-000076 | plan-000007 |
> | plan-000077 | plan-000008 |
> | plan-000078 | plan-000009 |
> | plan-000079 | plan-000010 |
> | plan-000080 | plan-000011 |
> | plan-000081 | plan-000012 |
> | plan-000082 | plan-000013 |
> | plan-000083 | plan-000014 |
> | plan-000084 | plan-000015 |
> | plan-000085 | plan-000016 |

spawned: plan-000007, plan-000008, plan-000009, plan-000010, plan-000011, plan-000012, plan-000013, plan-000014, plan-000015, plan-000016

> Reescrito em 2026-10-04. A versão de 2026-09-30 tratava o `seja-dev` como preset do open-seja. O nome do arquivo
> foi mantido para não quebrar referências (INDEX, roadmap-000062); o escopo mudou (ver "O que mudou").

## User Brief (verbatim)

> implementar versao tunada do seja para desenvolvimento de software: da intenção (prompt inicial) ao grill-me até construir intenção detalhada -> construir gerkin files (uncle bob phylosophy) -> testes -> Implementação (crap + mutation tests) olhar filosofia do uncle bob + pockc. hipotese é que o as coded divirja menos do as intended

Refinamento (2026-10-04):

> [o modo] faz um trabalho de quebra da intenção em LN para sub representações: gherkin, testes e especificação antes da implementação. serve tanto para citizen como power dev. [...] quero que o perfil seja o mesmo para power e citizen. acho até que não precisamos de preset. vamos colocar isso como o modo default do seja, que é pensado para desenvolvimento de software

## Q&A

- Preset (`dev`, `power-dev`) ou modo default? **Modo default do SEJA.** Não há preset e não há perfil: um único
  caminho para citizen e power dev. O `apprentice` (D-004, preset `apprentice`) fica para depois e não é tratado aqui.
- Como a escada entra no ciclo? **Dentro do `/plan`.** O ciclo continua PLAN → IMPLEMENT → REFLECT (H-008):
  PLAN = grill → specify → escrever o plano; IMPLEMENT = teste vermelho por cenário → código → gate; REFLECT =
  divergência por degrau. Sem skills novas antes do `/plan` e sem "ativação": é o comportamento padrão. Tarefas sem
  código (docs, pesquisa) pulam a fase specify por tipo de tarefa, não por modo do projeto.
- Pré-requisito do item 9 do roadmap-000062 (primeiro ciclo real)? **Não.** Este roadmap só depende de H-008
  registrada e do gate (plan-000065) e dos hooks (plan-000068) já entregues.

## Hipótese

**H-009 (proposta, filha de H-008):** se o SEJA decompõe a intenção em linguagem natural em representações
progressivamente mais formais (intenção detalhada com REQ IDs → cenários Gherkin → testes executáveis → código) e só
implementa depois, o *as-coded* diverge menos do *as-intended* do que no ciclo padrão (PLAN → IMPLEMENT → REFLECT de
H-008). A divergência é medida **por degrau da escada**, não só no fim.

Por que serve ao citizen e ao power dev sem perfis: o degrau do meio, o Gherkin, é quase linguagem natural. Quem não
programa valida *o que* será construído nele; quem programa valida também os degraus de baixo (testes, contratos). A
cadeia, os artefatos e os gates são os mesmos; só muda quem olha cada degrau.

Filosofia (research-000050): Uncle Bob (agentes estreitos por papel, Gherkin como critério de aceitação, CRAP por
função, mutação, "PASS is a tool result, not a sentence") e Pocock (o humano como loop externo que impõe opinião ao
código; TDD como loop de feedback, não cerimônia).

## O que mudou em relação ao rascunho de 2026-09-30

| Antes | Agora |
|---|---|
| Preset `dev` gerado do open-seja (como `apprentice`) | Modo default do próprio SEJA; sem preset, sem perfil |
| Eixo: skills + gate | Eixo: **escada de representações** (intenção → cenário → teste → código) com medida por degrau |
| Skills `/grill`, `/specify`, `/build` separadas | Fases do `/plan` e do `/implement`; ciclo continua PLAN → IMPLEMENT → REFLECT |
| Item 5 `quality-gate-python` | **Removido:** entregue pelo roadmap-000062 (plan-000065, done) |
| Hooks/deny no item 10 | **Removido:** entregue pelo roadmap-000062 (plan-000068, done) |
| Piloto em `pegasus` com controle | Piloto com controle (SEJA v0.10.x padrão), a definir no item 9 |
| Depende de item 9 do 62 | Não depende |

## Source

- `_output/roadmaps/roadmap-000062-open-seja-publico-hipotese-plan-implement-reflect-com-quality-gates.md` (read -- H-008, gate e hooks absorvidos, item 11 STE100)
- `_output/research-logs/research-000050-quality-gate-deterministico-crap-mutation-python-cpp.md` (read -- pipeline de Uncle Bob, limiares, §10 encaixe no open-seja)
- research-000047 do Doutourado (mapear hipotese do parceiro para o seja-as-intended) (read -- registro de hipóteses no open-seja, fronteira C1)
- `product-design/product-design-as-intended.md` (read -- D-004, D-005; sem REQ markers)

Repositório de execução: **open-seja** (worktree/branch por plano). Este arquivo vive no Doutourado (ledger de IDs do
pesquisador). C1: nada de nome de parceiro nos artefatos que forem ao open-seja.

## Decisões que este roadmap pede ao designer

| Wave | Decisão | Opções | Recomendação |
|---|---|---|---|
| 0 | Forma das fases grill/specify | fases internas do `/plan` / skills separadas invocáveis também avulsas | fases internas do `/plan`, cada uma invocável avulsa (`/plan --grill`, `--specify`) se o item 1 achar útil |
| 0 | Quando a fase specify é pulada | por tipo de tarefa (sem código) / nunca | por tipo de tarefa; o `/plan` decide e registra o motivo |
| 0 | Layout por feature | `features/<slug>/{intent.md,*.feature,gate.json}` / arquivos em `_output/` | pasta por feature, rastreável por `@REQ-NNN` |
| 0 | Definição de "divergência" | só cenários verdes / rastreabilidade completa / composta por degrau | composta, reportada por degrau (não um número único) |
| 1 | Runner de Gherkin em Python | pytest-bdd / behave | pytest-bdd (mesmo `uv run pytest`) |
| 3 | Onde roda o teste-primeiro e o Coder/Cleaner/Hardener | `/implement` por step / skill separada | `/implement` por step (`--pipeline`, previsto no 62) |

## Wave Summary

### Wave 0 -- Fundação (sequencial)
| # | ID | Title | Scope | Type | Plan | Status |
|---|-----|-------|-------|------|------|--------|
| 1 | default-cycle-contract | Contrato do ciclo estendido: fases grill e specify dentro do `/plan`, plano com steps ligados a cenários, teste-primeiro no `/implement`, layout por feature, D-NNN e H-009 (filha de H-008) com condição de refutação; retrocompatibilidade com planos antigos | backend | design | plan-000007 | done |
| 2 | drift-metric | Definição operacional de divergência **por degrau** (intenção→cenário, cenário→teste, teste→código) e desenho do controle com o ciclo padrão | backend | technical | plan-000008 | planned |

### Wave 1 -- Fases do PLAN (parallel)
| # | ID | Title | Scope | Type | Plan | Depends on | Status |
|---|-----|-------|-------|------|------|-----------|--------|
| 3 | plan-grill-phase | Fase grill do `/plan`: entrevista até intenção detalhada com REQ IDs, em linguagem que o citizen valida (voz controlada do item 11 do 62) | backend | design | plan-000009 | default-cycle-contract | planned |
| 4 | gherkin-spec-format | Convenção de `.feature` (tag `@REQ-`) + validador (steps sem duplicata/ambiguidade, rastreabilidade) | backend | technical | plan-000010 | default-cycle-contract | planned |

### Wave 2 -- Specify e plano rastreável (parallel)
| # | ID | Title | Scope | Type | Plan | Depends on | Status |
|---|-----|-------|-------|------|------|-----------|--------|
| 5 | plan-specify-phase | Fase specify do `/plan`: intenção detalhada vira `.feature` validado; ponto de aprovação humana (o citizen valida aqui) | backend | technical | plan-000011 | plan-grill-phase, gherkin-spec-format | planned |
| 6 | plan-from-scenarios | Formato do plano: cada step lista os cenários que cobre; `/plan` recusa step sem cenário | backend | technical | plan-000012 | plan-specify-phase | planned |

### Wave 3 -- IMPLEMENT e REFLECT (parallel)
| # | ID | Title | Scope | Type | Plan | Depends on | Status |
|---|-----|-------|-------|------|------|-----------|--------|
| 7 | implement-test-first-build | `/implement` por step: cenário vira teste vermelho pelo motivo certo, Coder, Cleaner (CRAP), Hardener (mutação), contexto curto por papel, loop até PASS; consome o gate do 62 | backend | technical | plan-000013 | plan-from-scenarios | planned |
| 8 | reflect-drift-report | `/reflect` e `/explain drift` leem a matriz intenção-cenário-teste-código-gate e reportam divergência por degrau | backend | technical | plan-000014 | drift-metric, plan-from-scenarios | planned |

### Wave 4 -- Integração e prova (sequencial)
| # | ID | Title | Scope | Type | Plan | Depends on | Status |
|---|-----|-------|-------|------|------|-----------|--------|
| 9 | default-cycle-wiring | `/help` e quickguides pt-BR, upgrade por tag sem quebrar projetos existentes, `run_all_checks` | backend | design | plan-000015 | implement-test-first-build, reflect-drift-report | planned |
| 10 | default-cycle-pilot | O TaskFlow (demo do open-seja, com a stack trocada para Python) no ciclo novo e o mesmo no ciclo padrão; medir divergência por degrau e tempo até a primeira feature aprovada; `/reflect` | backend | technical | plan-000016 | default-cycle-wiring | planned |

> A coluna `Plan` começa como `plan-TBD` em todas as linhas. O ID real só entra depois que `/plan` for invocado para o item. Não reservar IDs antecipadamente.

## Relação com o roadmap-000062

- **Absorvido pelo 62 (done):** `quality-gate-python` (plan-000065) e hooks/deny (plan-000068). O 56 consome o gate.
- **Não depende do item 9 do 62** (primeiro ciclo real). Os dois podem andar em paralelo; a evidência do 9 só
  ajusta os limiares do `/build` (item 7), que já tem o gate disponível.
- **Backlog do 62 que toca este:** D9 (smoke só Flask) e o ruído do `run_all_checks` num projeto novo afetam o piloto
  (item 10) se a feature for em Python.

## Fora do escopo

- `apprentice` / preset `apprentice` (D-004 do Doutourado) e `literature-reviewer` (D-005): presets próprios, tratados depois.
- Gate para C++ e para JS/TS (programa de formacao parceiro): repositórios-piloto próprios (research-000050 §5, §7).
- Coexistência com o serviço `seja-mcp` (roadmap-000055): o modo consome o harness como ele estiver.

## Riscos

- **Fricção para o citizen.** Mais passos antes do código (`/grill`, `/specify`) podem parecer lentidão. Mitigação:
  o piloto mede o tempo até a primeira feature aprovada, além da divergência.
- **Mudança no core.** Sem preset, o modo afeta todos os projetos de software que usam o SEJA; o upgrade por tag e os planos já existentes
  precisam continuar válidos (item 1).
- **Gherkin mal escrito vira ruído.** O validador do item 4 e o ponto de aprovação do item 5 são a defesa.

## Checkpoint Schedule
- None (Waves 0-4 geradas: plan-000007..plan-000016 (todos os 10 itens); definir ao gerar planos de duas ou mais waves)

## Execution Instructions

Nenhum plano gerado. Para cada wave, gerar os planos quando chegar a hora:

### Wave 0 (sequencial)
1. `/plan --framing metacomm default-cycle-contract: fases grill e specify dentro do /plan, plano com steps ligados a cenarios, teste-primeiro no /implement, D-NNN e H-009 com condicao de refutacao`
2. `/plan drift-metric: divergencia por degrau e controle com o ciclo padrao`

### Wave 1 (parallel -- 2 planos)
Dependem da Wave 0: `/plan --framing metacomm` para `plan-grill-phase`; `/plan` para `gherkin-spec-format`.

### Wave 2 (parallel -- 2 planos)
Dependem da Wave 1: `/plan` para `plan-specify-phase`; depois `plan-from-scenarios`.

### Wave 3 (parallel -- 2 planos)
Dependem da Wave 2: `/plan` para `implement-test-first-build` e `reflect-drift-report`.

### Wave 4 (sequencial)
`/plan --framing metacomm` para `default-cycle-wiring`; depois `/plan` para `default-cycle-pilot`.

---

## Adendo 2026-10-05 -- emendas da research-000087 (lacuna da intenção)

> Texto acima preservado. Este adendo incorpora os achados da [research-000087](../research-logs/research-000087-lacuna-metacomunicacao-gherkin-roadmap-000006.md) (fonte: reflection-000086, pergunta da orientadora) e a decisão **D-006** do `product-design-as-intended.md`. Nenhum plano foi executado ainda; as emendas são **absorvidas por cada plano no seu Step 1** (conferência do terreno), sem reabrir decisões fechadas. Repositório de execução continua o open-seja (C1).

### O que a pesquisa mudou na leitura da escada

1. **A escada é completa para comportamento e deixa perda declarada** de racional (por quê), modelo conceitual (abstrações, vocabulário), preferências de forma e crenças sobre o usuário. O Gherkin representa comportamento observável de um ator diante de um gatilho; não representa o resto. D1 mede presença de tag sobre o que já virou REQ: não vê omissão (o que não virou REQ) nem distorção (REQ reinterpretado).
2. **Features são contratos endereçáveis, não signos (D-006).** REQ IDs e chaves de cenário são os endereços; os signos são a retradução em primeira pessoa, os exemplos narrados, os mutantes recontados e as ausências declaradas. O citizen aprova a mensagem; o `.feature` é derivado e aprovado como contrato pelo power dev. Mesma escada, sem perfil: muda o objeto de aprovação por receptor.
3. **Teste da surpresa.** Toda emenda e todo signo devolvido ao citizen deve poder provocar uma ruptura decodificável pelo receptor a quem se endereça; item que só confirma (PASS, percentuais) não entra no registro do citizen. Guarda contra o andaime virar ritual.
4. **Perímetro.** A unidade de medida é a feature; fora do perímetro é `legado: não medido`. Greenfield e brownfield são a mesma regra com perímetros diferentes.
5. **Fronteira agnóstica de stack.** Gate contract (JSON, exit codes, `GATE_*_CMD`, já entregues pelo 62) e runner contract (Cucumber JSON + chave de cenário). Acima é SEJA; abaixo é adaptador. Stack sem adaptador degrada para `não medido`.

### Emendas por plano (absorver no Step 1 de cada um)

| Plano | Item | Emendas (rec. da research-000087) |
|---|---|---|
| plan-000007 | 1 default-cycle-contract | Regra do perímetro (16); fronteira agnóstica nomeada: gate contract e runner contract (20); tabela degrau x receptor (25); teste da surpresa como critério de aceitação de emendas (26); registrar D-006 do Doutourado como fonte |
| plan-000008 | 2 drift-metric | D0 resíduo do brief como leitura fora do D, código `NM-SEM-INDICE-BRIEF` (1); subseção "O que o D não vê" e frase na refutação de H-009 (4); três medidores de ganho do citizen na refutação: ajustes no specify, escapes antes vs depois, mutantes virados em REQ (18); códigos `NM-SEM-ADAPTADOR-*` (22) |
| plan-000009 | 3 plan-grill-phase | Frases do brief indexadas e citadas por "Nas suas palavras" / "Fora do escopo" / "Premissas" (1); coluna "Para que" e seção "Modelo e termos" no `intent.md` (2); campo `serve:` ligando a `REQ-MC`/`JM-TB`/`D-NNN` (3); sub-pergunta "o que essa pessoa sabe fazer" na dimensão quem (9); nota C1 sobre `brief` verbatim em `features/` |
| plan-000010 | 4 gherkin-spec-format | Aviso: substantivo entre aspas ou com inicial maiúscula no step deve constar em "Modelo e termos" (2); `Rule:` como jornada ordenada citando `JM-TB-NNN` (7); tag `@nao-faz` opt-in (6c) |
| plan-000011 | 5 plan-specify-phase | **SPC-009 emendado (D-006, rec. 24):** o citizen aprova a retradução em primeira pessoa e os exemplos narrados; o `.feature` é derivado e aprovado como contrato pelo power dev; seção "Retradução" com `rev` no `intent.md` (5); "Fora do escopo" permanece sem cenário (SPC-006) mas aparece na mensagem |
| plan-000012 | 6 plan-from-scenarios | Sem emenda; o `Scenarios:` continua a ser o endereço |
| plan-000013 | 7 implement-test-first-build | Ler Cucumber JSON: "vermelho pelo motivo certo" = `failed`, `undefined` não conta (21); demonstração por cenário na superfície do citizen em M1 (13); Hardener reconta cada mutante sobrevivente em linguagem natural e devolve como pergunta (14); mutação e CRAP só no perímetro, baseline com catraca (16, 17); `scenario-tester` como terceiro amigo antes da aprovação, informativo (8) |
| plan-000014 | 8 reflect-drift-report | D0 e "intenção sem feature" (leitura reversa via `serve:`) (1, 10); "não-faz sem evidência" (6); "código sem cenário" como excesso (11); retradução pós-código lado a lado com a do specify e o brief, julgamento do citizen em `audit.json` (5); rótulo de prova em cada item e supressão de números técnicos no registro do citizen (15); as-coded regenerado da matriz (12); leitura reversa só do que nasceu depois da marca de adoção (17) |
| plan-000015 | 9 default-cycle-wiring | Quickguide pt-BR explica o que o citizen aprova (mensagem) e o que o power dev aprova (contrato) |
| plan-000016 | 10 default-cycle-pilot | **Braço brownfield** com uma feature no `pegasus` (números de legado da research-000050 como baseline) além do TaskFlow (19); medir os três medidores de ganho do citizen (18) e quem aprovou o quê, com quantas idas e voltas |

### Decisões que este adendo pede ao designer (acrescentadas à tabela acima)

| Wave | Decisão | Opções | Recomendação |
|---|---|---|---|
| 0 | Objeto de aprovação do citizen | `.feature` por requisito (texto atual de SPC-009) / mensagem (retradução + exemplos narrados), `.feature` derivado e aprovado pelo power dev | mensagem (**D-006**, já decidida no Doutourado; o open-seja a registra como D-NNN própria no Step 6 do 000007) |
| 0 | Degrau zero | sem M0 (como está) / D0 como leitura fora do D, nunca portão | D0 como leitura; não reabre "sem M0" |
| 0 | Formato do relatório do runner | nativo do pytest-bdd / Cucumber JSON (ou Messages) | Cucumber JSON; pytest-bdd como primeiro adaptador. Conferir suporte de `--cucumberjson` na versão atual antes de o 000013 depender dele |
| 3 | Reconto de mutantes ao citizen | só para o power dev / recontado em linguagem natural como pergunta ao citizen | recontado; sobrevivente que vira REQ é o medidor mais barato de ganho |
| 4 | Braço brownfield no piloto | só TaskFlow / TaskFlow + uma feature no `pegasus` | os dois; sem brownfield o piloto não vê ruído nem custo de atenção real |

### Hipótese (ajuste a H-009, para a prosa do designer no Step 6 do 000007)

H-009 passa a declarar o próprio alcance: a escada é completa para comportamento operacionalizado, com perda declarada de racional, modelo, preferência e crença sobre o usuário; essas categorias são objeto do degrau zero (D0), da auditoria semântica e da retradução julgada pelo citizen, não do vetor D. Condição de refutação ganha os três medidores de ganho do citizen: se, no piloto, ajustes e recusas no specify, escapes de intenção antes do código e mutantes virados em REQ forem todos zero, a aprovação virou ritual, H-009 cai e H-001 volta a pedir adequação por posição na escala.

### Riscos acrescentados

- **Conformidade no lugar de reflexão.** "Aprovado" e "PASS" como falas do preposto que encerram a conversa. Mitigação: teste da surpresa (26) e rótulo de prova (15).
- **Ruído em brownfield.** Mutação e CRAP fora do perímetro, deriva legada no denominador. Mitigação: perímetro (16), baseline com catraca e leitura reversa só do que nasceu depois (17).
- **Acoplamento a Python.** Mitigação: gate contract e runner contract (20-22); segundo adaptador só com repositório-piloto.
- **Custo de atenção do citizen** sobe com retradução, demonstração e mutantes recontados. Mitigação: a retradução substitui parte do resumo atual; demonstração e mutantes entram por padrão só para sobreviventes e cenários marcados; medido no piloto.

### Fora do escopo deste adendo

Adaptadores C++ e JS/TS (research-000050 §5, §7; repositórios-piloto próprios); MoLIC como representação de jornada (fica como referência; `Rule:` é o substituto mínimo); auditoria semântica por LLM (rejeitada; decisão fechada do 000008).
