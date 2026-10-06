# Fixtures -- fase specify (plan-000011)

> **Simuladas.** Todos os casos são fictícios, escritos pelo executor do plano. Nenhuma pessoa real aprovou nada; "usuario" é um papel. Nenhum dado real, nenhum nome de pessoa ou organização.

Regras: `.claude/references/general/specify-phase.md`. Verificador: `.claude/skills/scripts/check_specify.py`. Teste: `test_check_specify.py` (lê `esperado.json`).

Cada pasta é uma raiz de projeto. `esperado.json`: `args` (argumentos do verificador), `exit_code`, `status` (estado SPC-013), `reasons`/`reqs` (razões de `stale`), `findings` exatos `[regra, severidade, arquivo, linha]` (SPC-008 embrulha erros e avisos de `check_features.py`), e, nos casos de `--approve`, `intent_final`/`lock_final` (bytes esperados, calculados à parte do verificador) ou `unchanged: true`.

| Caso | O que prova |
|---|---|
| `ok-completo` | 3 REQs (2 comportamento, 1 restrição com Outline), erro com cenário próprio, pt |
| `ok-minimo` | 1 REQ, 1 cenário |
| `ok-en` | en-US: feature sem # language, retradução com What I will not do |
| `spc-001-grilling` | intent.md em grilling: recusa (dispara SPC-001) |
| `spc-001-sem-intent` | pasta só com .feature, --feature: recusa (dispara SPC-001) |
| `spc-001-intent-com-erro` | intent.md aprovado mas com erro P2 em check_intent (dispara SPC-001) |
| `spc-003-sem-cenario` | REQ 002 ativo sem cenário (dispara SPC-003; o GHK-005 do validador fica com ela) |
| `spc-003-retirado-sem-cenario` | REQ 003 retirado sem cenário (não dispara) |
| `spc-003-retirado-com-cenario` | REQ 003 retirado ainda com cenário (dispara SPC-003) |
| `spc-004-sem-numero` | restrição sem número no Então nem em Exemplos (dispara SPC-004) |
| `spc-004-numero-no-entao` | restrição com 'em até 2 segundos' no Então (não dispara) |
| `spc-007-26-palavras` | step com 26 palavras (dispara SPC-007) |
| `spc-007-25-palavras` | step com 25 palavras (não dispara) |
| `spc-008-ghk013` | aviso GHK-013 (URL no step) vira SPC-008 aviso e bloqueia |
| `spc-008-skip` | tag @skip (GHK-014) vira SPC-008 aviso e bloqueia |
| `spc-010-aprovar` | --approve com tudo verde grava lock e 5 campos; repetir dá os mesmos bytes |
| `spc-010-contrato-ninguem` | --contract-by ninguem: aprova a mensagem e registra contrato não lido |
| `spc-010-falha-nao-grava` | --approve com intent em grilling: sai 1 e não escreve nada |
| `spc-012-renomeado-sem-mudanca` | cenário aprovado renomeado sem linha em Mudanças (dispara SPC-012) |
| `spc-012-renomeado-com-mudanca` | cenário renomeado com linha em Mudanças (não dispara; estado stale) |
| `spc-013-aprovado` | lock bate com REQs, rev, hashes e retradução: approved |
| `spc-013-rev-subiu` | rev do REQ 002 subiu depois da aprovação: stale (req-rev, REQ 002) |
| `spc-013-hash-mudou` | .feature editado depois da aprovação: stale (feature) |
| `spc-013-retraducao-mudou` | retradução editada depois da aprovação: stale (retraducao) |
| `spc-013-intencao-reaberta` | intent.md voltou a grilling com scenarios: approved: stale |
| `spc-013-sem-lock` | scenarios: approved sem lock: stale (aprovação sem prova) |
| `spc-013-missing` | pasta com intent.md e sem .feature: missing |
| `spc-017-sem-retraducao` | sem a seção Retradução (dispara SPC-017) |
| `spc-017-req-sem-exemplo` | item do REQ 002 sem exemplo narrado (dispara SPC-017) |
| `spc-017-req-fora` | REQ 003 ativo fora da retradução (dispara SPC-017) |
| `spc-017-nao-faz-faltando` | Fora do escopo tem 2 itens e a retradução diz 1 (dispara SPC-017) |
| `spc-017-sem-primeira-pessoa` | item sem primeira pessoa (dispara SPC-017 aviso) |
| `spc-018-numero-tecnico` | PASS e percentual na retradução (dispara SPC-018) |
| `spc-018-frase-longa` | frase de 26 palavras na retradução (dispara SPC-018) |
| `spc-011-rev-sem-mudanca` | retradução rev 2 sem linha em Mudanças (dispara SPC-011) |
| `spc-011-rev-com-mudanca` | retradução rev 2 com linha em Mudanças (não dispara) |
| `spc-011-teto` | retradução rev 5: passou do teto de 3 ajustes (informação, não falha) |
| `sem-features` | raiz sem features/: sai 0, nada a verificar |
| `features-de-terceiros` | features/ estilo behave, sem intent.md: sai 0 sem achado |
| `pasta-sem-intent` | features/<slug>/ só com .feature, varredura: sai 0 sem achado |
| `check-features-ausente` | validador do plan-000010 ausente: sai 2 e não escreve nada |
| `varredura-aprovado-ok` | varredura sem argumentos: feature aprovada e lock bate, sai 0 |
| `varredura-aprovado-stale` | varredura sem argumentos: scenarios: approved com lock que não bate, sai 1 |
| `varredura-draft` | varredura sem argumentos: feature em draft não reprova |

Execuções de referência (Steps 6 e 7 do plano, simuladas): pastas `ref-a-ajuste/`, `ref-b-sem-codigo/` e `ref-c-stale/`, cada uma com o próprio `README.md`.
