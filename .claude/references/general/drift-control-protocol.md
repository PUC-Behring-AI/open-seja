---
designer_description: "When the pilot needs to compare the extended cycle with the standard cycle on the same feature, I'm the control protocol: two arms, a designer-written oracle kept secret, replicas, time to the first approved feature, a comparison rule and the threats to validity -- so the comparison tests H-009 and does not flatter it."
---

# GENERAL - DRIFT CONTROL PROTOCOL

> Desenho do controle de H-009 (roadmap-000006, plan-000008; `product-design/product-design-as-intended.md` §3 subseção 2.9, D-004, D-007). A pergunta: o ciclo estendido reduz a divergência por degrau em relação ao ciclo padrão? A medida complementar: o tempo até a primeira feature aprovada.
>
> Este arquivo diz **como comparar**. A definição do que se conta (D1, D2, D3a, D3b, estados, fórmula) está em `drift-metric.md`; aqui ela é citada, não redefinida. Quem executa o protocolo é o plan-000016 (piloto). O registro de cada execução usa `.claude/references/template/pilot-run-record.md`.
>
> Idioma: pt-BR, identificadores em en-US. Marcação: `[default; aceito 2026-10-06]` indica uma decisão pendente do plan-000008 aceita no default.

## 1. Objetivo e pergunta

H-009 afirma que decompor a intenção em representações progressivamente formais (intenção detalhada com REQ -> cenários -> testes -> código) faz o *as-coded* divergir menos do *as-intended* do que o ciclo padrão (PLAN -> IMPLEMENT -> REFLECT de H-008). Este protocolo compara os dois ciclos na **mesma feature**, contra a **mesma régua**.

Pergunta: em cada degrau (D1, D2, D3a, D3b) e na métrica comparável O1, a divergência do ciclo estendido é menor que a do ciclo padrão? Medida complementar: quanto tempo cada ciclo leva até a primeira feature aprovada pelo designer?

É um **estudo de caso**: poucas features, números brutos, sem teste estatístico.

## 2. Os dois braços e o que é fixado igual

| | Braço A (padrão) | Braço B (estendido) |
|---|---|---|
| Ciclo | PLAN -> IMPLEMENT -> REFLECT sem grill nem specify; plano v1; `Tests:` por step | grill -> specify -> plano v2 -> teste vermelho por cenário -> código -> gate (CYC-001) |
| Harness | SEJA v0.10.x pinada (sem as fases novas) | harness com o ciclo estendido |

Fixado **igual** nos dois braços e por execução:

- o brief textual (palavra por palavra);
- o commit inicial do repositório;
- a versão de modelo;
- o orçamento: número máximo de iterações e tempo máximo de relógio;
- um worktree limpo por execução;
- as mesmas ferramentas e o mesmo portão, quando o projeto o tem.

## 3. O oráculo

O **oráculo** é a régua independente. O designer o escreve **antes** de qualquer braço rodar.

- **Formato**: lista de REQs em linguagem natural e cenários de aceitação em Gherkin, com a tag `@REQ-<slug>-NNN` em cada cenário, mais os testes executáveis desses cenários (os testes do oráculo).
- **Sigilo**: o oráculo não entra no contexto do agente do braço A e não é copiado para o braço B. O B produz os próprios REQs e cenários pelo grill; o designer responde ao grill **só a partir do oráculo**, sem informação nova.
- **Versionamento**: o oráculo é congelado num commit e o seu hash (SHA-256 da lista de arquivos, em ordem alfabética) é registrado em cada registro de execução. Oráculo alterado depois da primeira execução invalida as execuções anteriores.
- **Por que**: sem régua externa o ciclo estendido mede a si mesmo com os cenários que ele mesmo escreveu (lei de Goodhart).

## 4. Métrica comparável e retrofit

**O1**: fração de cenários do oráculo que falham no código final. `O1 = falham / n`, com `n` = cenários do oráculo. Os testes do oráculo rodam sobre o código final de cada braço.

**D3b contra o oráculo**: o código tocado que os testes do oráculo não exercitam, calculado por `drift-metric.md` (DRM-005) com os testes do oráculo no lugar dos testes de cenário do braço. É o mesmo cálculo nos dois braços.

**Degraus nativos só no B.** O braço A não tem REQ nem cenário próprios. D1 e D2 do A são medidos por **retrofit**: mapear os REQs do oráculo para os critérios do plano v1 e para os testes do A. A auditoria semântica (`drift-metric.md`, DRM-010; decisão pendente 1 = B `[default; aceito 2026-10-06]`) cobre **todos** os REQs do retrofit do A e pelo menos 30% dos REQs do B, cega (o auditor não sabe de que braço vem), com `adequado: sim | parcial | nao` numa coluna separada do D.

Degraus **comparáveis diretamente**: D3a, D3b e O1. D1 e D2 só **pelo retrofit**, e a assimetria é ameaça declarada (seção 9).

## 5. Ordem e réplicas

- **Ordem alternada.** A ordem dos braços alterna entre features. Cada feature recebe uma ordem sorteada, registrada antes da primeira execução.
- **Réplicas por braço**: 3 execuções `[default; aceito 2026-10-06]` (decisão pendente 2 = B). Relatam-se as três; nunca a média sozinha. Se o orçamento do piloto não cobre seis execuções, usa-se 1 por braço e declara-se que a variância do agente não foi medida.
- Cada execução parte do mesmo commit inicial, em worktree limpo, sem memória das anteriores.

## 6. Tempo

Eventos:

| Evento | Definição | Fonte |
|---|---|---|
| `t0` | primeira mensagem com o brief | `_output/conversation-trace.jsonl` (`timestamp` da primeira entrada `emitter: user` da execução; `session_id` pode ser `"null"`, então delimitar pelo registro de execução); alternativa: linha `STARTED` do `plan` em `_output/briefs.md` |
| `t_verde` | primeiro `gate full` PASS | `features/<slug>/gate.json` (`ts` com `full.exit_code` 0); sem portão instalado: campo manual |
| `t_aprovada` | aceitação explícita do designer `[default; aceito 2026-10-06]` (decisão pendente 3 = A) | **campo manual** do registro de execução (linha no `/reflect` ou no progress file); o harness não tem fonte automática |

Medidas de tempo, nas duas formas:

- **Relógio de parede** = `t_aprovada - t0`.
- **Tempo atendido pelo designer** = soma dos intervalos entre eventos do designer **menores que 10 minutos**. Intervalo de 10 minutos ou mais conta como ausência e não entra. Quando não há como ordenar os eventos do designer (sem `conversation-trace.jsonl` da execução), o tempo atendido é `t_aprovada - t0` e o registro diz isso.

Reportar ao lado: `t_verde` (o gate verde não diz que a intenção foi atendida) e O1. "Feature aprovada" por `t_verde` sozinho ou por O1 = 0 sozinho não vale: o primeiro ignora a intenção; o segundo pode nunca ser atingido pelo ciclo padrão.

## 7. Regra de comparação e tabela de resultados

**Regra** (leitura operacional da condição de refutação de H-009). "Divergência igual ou maior no estendido em um degrau" significa `D_B >= D_A` naquele degrau, com **empate** quando a diferença for menor que 1 item do denominador (empate não conta como redução). Os degraus comparáveis são D3a, D3b e O1 diretamente; D1 e D2 pelo retrofit. Cada comparação usa as três réplicas de cada braço, lado a lado, e relata os pares.

**Condição de refutação** (por degrau, sem somar): se em dois ou mais dos degraus comparáveis `D_B >= D_A` (sem empate redutor), o ciclo estendido não reduziu a divergência nessa feature.

**Os três medidores de ganho do citizen** (`drift-metric.md`, DRM-010), medidos no braço B e relatados ao lado: ajustes e recusas no specify; escapes de intenção antes vs depois do código; mutantes virados em REQ. Se os três forem zero, a aprovação virou ritual (condição de refutação de H-009).

Tabela de resultados a preencher (uma por feature; réplicas r1, r2, r3):

| Medida | A r1 | A r2 | A r3 | B r1 | B r2 | B r3 | Leitura |
|---|---|---|---|---|---|---|---|
| D1 (retrofit no A) | | | | | | | |
| D2 (retrofit no A) | | | | | | | |
| D3a | | | | | | | |
| D3b (contra o oráculo) | | | | | | | |
| O1 | | | | | | | |
| Tempo: relógio de parede | | | | | | | |
| Tempo: atendido pelo designer | | | | | | | |
| `t_verde` | | | | | | | |
| Auditoria semântica (sim/parcial/nao) | | | | | | | |
| Medidores do citizen (só B) | | | | | | | |

Cada célula traz numerador/denominador e `não medido` com a razão (`drift-metric.md`, DRM-009).

## 8. Covariáveis a registrar

- número de iterações até PASS (por step e total);
- número de perguntas do grill (só B);
- linhas de código tocadas;
- número de REQs (feature com menos de 8 REQs leva a ressalva `amostra pequena`);
- versão de modelo e do harness;
- tempo do portão (`--fast`, `--full`).

## 9. Ameaças à validade

| Ameaça | Mitigação |
|---|---|
| Efeito de aprendizado do designer (o segundo braço se beneficia do primeiro) | ordem alternada e registrada; designer responde só a partir do oráculo |
| Assimetria do retrofit (D1 e D2 do A são reconstruídos, os do B são nativos) | D3a, D3b e O1 são a base da comparação; D1 e D2 lidos com a ressalva; auditoria semântica de todo o retrofit |
| Escopo de uma feature | nenhuma generalização; segunda feature (brownfield) no plan-000016 |
| Viés de oráculo escrito pelo mesmo designer que responde ao grill | sigilo; congelamento por hash; o designer não acrescenta informação ao responder |
| Variância do agente | três réplicas por braço; relatar as três |
| Goodhart: cenários fracos que passam e não provam a intenção | O1 contra o oráculo; auditoria semântica; leitura "escada fechou sem capturar a intenção" |
| Aprovação do citizen virando ritual | os três medidores do citizen; teste da surpresa (CYC-014) |

## 10. Critérios de parada e o que não concluir

- **Parar** uma execução ao estourar o orçamento de iterações ou de tempo; registrar como execução incompleta, com os degraus que couberem e o resto `não medido`.
- **Parar** o piloto se o oráculo mudar depois da primeira execução (recomeçar com novo hash).
- **Não concluir** além da feature: sem generalizar de uma feature para o ciclo em geral.
- **Não usar** p-valor nem "significativo". Reportar números brutos e réplicas.
- **Não somar** degraus nem reduzir o vetor a um número (CYC-016).
- **Não** reabrir nenhuma regra de `drift-metric.md` durante o piloto; mudança é por emenda registrada (CYC-014).
