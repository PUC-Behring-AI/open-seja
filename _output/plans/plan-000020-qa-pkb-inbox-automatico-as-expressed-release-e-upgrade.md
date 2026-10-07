# QA Log | Plan 000020 | 2026-10-07 00:43 UTC | PKB inbox automatico, as-expressed em H-005, release e upgrade do Doutourado

## Brief

"vamos gerar um plano? para executar tudo de uma vez" -- a partir da nota de inbox do Doutourado de 2026-10-06 (ideia do inbox automatico da PKB, lacuna as-expressed em H-005, pendencia de upgrade do harness).

## Q&A Log

## Q1

ideia para o open seja: tudo o que e digitado aqui no chat e vai para o artefato seja tambem vai para o inbox. permitir o seja instanciar um PKB como o inbox (colocar minhas anotacoes la, para que eu possa percorrer historicamente). linkar com os communicates e criar um live communicate no inbox; a partir disso temos um conteudo a curar e seguir no fluxo do repositorio bootstrap (fork personal_knowledge_base_bootstrap).

## A1

Capturei a ideia como nota no inbox/ do Doutourado com tres leituras: captura dupla derivada do conversation-trace e dos briefs (nao uma quarta fonte de verdade); SEJA instanciando a camada PKB no molde do plan-000072; live communicate como preparacao continua da faixa EXPLAIN/COMMUNICATE, candidata a Q-011. Riscos: duplicacao de registro, segredos fluindo para pasta indexada, ritual (inbox que acumula sem ser processado).

## Q2

isso entra como uma lacuna atual no open-seja e na hipotese. esta faltando o /design no ciclo quando o as-expressed, as-intended e as-coded divergem muito.

## A2

Li como refinamento de H-005: as-expressed e um quarto estado (a fala registrada), que divide a lacuna 1 em 1a (as-conceived -> as-expressed, nao capturavel) e 1b (as-expressed -> as-intended, comparavel por texto). No ciclo falta limiar e gatilho que levem deriva grande ao /design em vez do /plan; hoje toda deriva vira bug de codigo, que e a condicao de refutacao de H-005.

## Q3

ok, parece plausivel. o open-seja produz automaticamente o inbox da pkb. depois vamos ter que atualizar o seja no doutourado, ainda estamos apontando para o seja upstream. temos que fazer o upgrade para o open-seja.

## A3

Direcao fechada (inbox automatico, sem flag nem perfil) e pendencia de upgrade anotadas: Doutourado em v0.9.1 do upstream, open-seja em v0.10.1 (nunca taggeado); ordem publish -> seja-setup --upgrade com dry-run, preservando skills PKB, conventions e sources.txt.

## Q4

vamos gerar um plano? para executar tudo de uma vez

## A4

Plano unico (13 steps, FEATURE-X, revisao deep). Decisoes do plano: forma = template pkb/ + script pkb_inbox.py (init/capture/digest) acionado pela etapa 7f do post-skill, com interruptor "PKB_DIR nao vazio e inbox/README.md existe"; as 5 skills PKB ficam so no template (entram num projeto via init --with-skills ou /seja-setup --pkb); a emenda a H-005 e Q-014 viram rascunho em _output/tmp/ + pendencia para o /design (T4); release v0.11.0 (MINOR; v0.10.x nunca taggeado) em vez do v0.10.1 do brief; upgrade do Doutourado com o script antigo do alvo, WARN de conventions esperado, commit do repositorio pai fica com o designer. A revisao deep (6 deep-dives) gerou 10 emendas, aplicadas nos Steps 2-8, 10-12.

## Q5

(oferta do espelho) Quer que o plano seja contado a uma audiencia? / Depois do commit, o que fazer?

## A5

Designer: seguir sem comunicar; "prepare o prompt para eu implementar com o opus". Comunicacao registrada como declinada no progress file; o plano e commitado e o prompt de implementacao e entregue na conversa.
