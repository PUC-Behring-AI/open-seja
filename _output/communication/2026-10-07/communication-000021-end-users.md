# Communication 000021 | USR | 2026-10-07 00:45 UTC | End Users

> **Fonte**: `_output/plans/plan-000019-upgrade-multi-dev-identidade-por-ulid.md`, com o porque em `_output/research-logs/research-000018-upgrade-multi-dev-esquema-de-ids.md` (recomendacoes revisadas e perguntas de acompanhamento) e na decisao D-005 de `product-design/product-design-as-intended.md`.

## Para quem eu escrevo

Eu escrevo para voce que usa o open-seja num repositorio compartilhado com outras pessoas, na mesma branch, e que vive com os artefatos que o harness produz: planos, pesquisas, reflexoes, comunicacoes. Este texto e o espelho do PLAN: o plano contado a quem vai conviver com ele, antes de qualquer codigo. Se alguma parte nao sobreviver a ser contada, e isso que eu quero descobrir agora, e nao depois.

## O open-seja em uma pagina

O open-seja e a distribuicao de acesso aberto do SEJA, um harness para o Claude Code. Eu trato desenvolvimento assistido por IA como comunicacao projetada: voce me diz o que quer, nas suas palavras, antes de qualquer codigo; eu registro isso como intencao que uma maquina consegue enderecar; eu so considero um passo feito quando uma ferramenta diz que passou; e ao fim de cada fase eu lhe devolvo um espelho, para que voce veja a distancia entre o que pediu e o que existe.

O problema que eu resolvo: quando um agente escreve mais rapido do que voce consegue revisar, a traducao da sua intencao pode estar errada sem estar quebrada. Eu existo para que voce exerca autoria sem precisar ler cada linha, e para que o que nao foi medido apareca como nao medido.

O que me diferencia: a intencao vem antes do codigo e fica registrada em arquivo; cada artefato tem identidade estavel e historia; a voz de cada arquivo e de quem a emitiu; e eu aplico a mim mesmo o que exijo dos projetos, numerando minhas apostas e dizendo o que as refutaria. Hoje eu estou entre uma versao e a seguinte, e este plano e uma das mudancas que preparam a proxima.

## O que eu entendi de voce

Eu sei que voces sao mais de um na mesma branch, cada um na sua maquina, e que as vezes algum de voces trabalha sem rede. Eu sei que, hoje, quando dois de voces reservam um artefato ao mesmo tempo, os dois podem receber o mesmo numero, e nada avisa: os dois planos coexistem em silencio ate alguem tropecar. Eu sei que o numero curto, "plan 7", e comodo de dizer em voz alta, e que voce ja se acostumou a ele. E eu sei que a ordem dos arquivos na arvore importa para voce: abrir a pasta e ver o que veio antes.

Por isso eu projetei esta mudanca para que nenhum de voces precise combinar nada com ninguem, nem antes nem depois, e para que a ordem na arvore continue de pe. Em troca, eu lhe peco duas coisas: aceitar um ID mais longo e atualizar o harness junto com o seu time.

## O que muda para voce

- **O ID de um artefato novo passa a ter a data e um sufixo curto.** Em vez de `plan-000020`, voce vera algo como `plan-20261007-k3m9qz`. A data e o dia em que o artefato nasceu; o sufixo vem de um identificador gerado na sua propria maquina, sem consultar ninguem.
- **O nome do arquivo segue o mesmo padrao.** `plan-20261007-k3m9qz-<assunto>.md`. Como a data vem primeiro, a pasta continua ordenada no tempo.
- **O cabecalho ganha uma linha `uid:`.** E a identidade completa do artefato, logo abaixo do titulo. Voce nao precisa ler nem digitar essa linha; ela existe para que eu e as ferramentas futuras saibamos, sem ambiguidade, de qual artefato se trata.
- **Nasce uma pasta `_output/ids/`.** Cada artefato novo deixa ali um registro de nascimento pequeno: tipo, titulo, instante em que nasceu, de onde veio, e um token anonimo de quem o criou. Um arquivo por artefato, para que o git funda o trabalho de voces sem conflito.
- **O INDEX.md deixa de guardar estado.** Hoje ele carrega linhas de reserva que podem ficar orfas. Depois, ele e regenerado inteiro a qualquer momento a partir do que existe, e nada se perde ao regenerar.
- **Eu passo a acusar ID duplicado.** Um verificador novo roda antes de cada skill e no preflight. Se dois artefatos tiverem o mesmo ID, ou se um registro de nascimento ficar sem artefato por muito tempo, eu lhe digo qual e qual antes de voce commitar.
- **Eu mudo o que lhe digo ao reservar.** Em vez de "reservado 000020", eu digo "reservado 20261007-k3m9qz" e mostro o uid ao lado.

## O que nao muda

- **Todo ID antigo continua valido, para sempre.** Nenhum artefato existente muda de nome, de numero ou de conteudo. `plan-000007` continua sendo `plan-000007`, citavel e rastreavel como hoje.
- **Os comandos sao os mesmos.** `/plan`, `/research`, `/reflect`, `/implement` e as demais skills funcionam como antes; so o ID que elas lhe devolvem muda de forma.
- **Os marcadores nos seus arquivos de voz humana aceitam os dois formatos.** Eu nao lhe peco para reescrever nenhum marcador, changelog ou decisao que ja existe.
- **A ordem na arvore continua cronologica.** O prefixo de data faz esse papel.
- **O seu nome nao entra no ledger.** O registro de nascimento guarda um token derivado do seu e-mail do git, nao o seu nome. Isso segue a regra que ja vale para tudo em `_output/`.
- **As decisoes D-NNN e as pendencias `pa-` ficam como estao.** Mudancas nesses identificadores ficam para um plano separado.

## O que voce precisa fazer

1. **Atualizar o harness junto com todo mundo que compartilha o ledger.** Esta e a unica exigencia real. Um harness anterior nao corrompe nada ao encontrar artefatos novos, mas fica cego a eles: continua emitindo IDs no formato antigo (e a janela de colisao segue aberta para ele), indexa os artefatos novos como "Other" sem ID, nao os acompanha em cobertura nem em pendencias, e **recusa commitar** qualquer arquivo de voz humana que tenha um marcador no formato novo. Se um de voces ficar para tras, e ele quem vai esbarrar nisso, sem aviso claro.
2. **Depois de atualizar, regenerar o INDEX.md.** As linhas de reserva orfas de hoje desaparecem nessa regeneracao. Nao ha nada a migrar: se a pasta `_output/ids/` nao existir ainda, ela nasce na primeira reserva.
3. **Passar a citar artefatos novos pela data e pelo sufixo.** "O plano de sete de outubro, k3m9qz" e o que voce tem por enquanto para falar de um artefato novo em voz alta. Um apelido pronunciavel, derivado do identificador e igual em todas as maquinas, esta previsto para um plano seguinte; eu digo isso para que voce nao espere dele agora.

## O que voce perde e o que ganha

| Voce perde | Voce ganha |
|---|---|
| O numero curto. "Plan 7" cabia numa frase; `20261007-k3m9qz` nao cabe tao bem. | Nenhuma combinacao entre maquinas: cada um reserva na sua, com ou sem rede, e nunca colide. |
| A ordem entre artefatos criados no mesmo dia por pessoas diferentes. Dois artefatos do mesmo dia ordenam entre si pelo sufixo, nao pela hora. | A ordem entre dias continua garantida pela data no nome, mais legivel do que o numero. |
| Um unico formato de ID. O harness passa a conviver com os dois por tempo indefinido. | Nenhuma renumeracao, nunca. O que nasceu com um ID morre com ele, e artefatos antigos ficam intactos. |
| A sensacao de que o INDEX.md "sabe" o que esta reservado. | Um INDEX.md que voce pode regenerar sem medo, e um verificador que acusa duplicata em vez de deixar passar em silencio. |

O designer aceitou as duas primeiras perdas de forma explicita: o numero curto e substituivel por um apelido, e a ordem dentro do dia "nao importa tanto". Se para o seu time ela importa, esta e a hora de dizer.

## O que eu me comprometo a manter

- **Eu nao toco no que ja existe.** Artefato e marcador antigos ficam como estao. A historia do seu ledger e evidencia, nao rascunho.
- **Eu aviso antes, nao depois.** Duplicata de ID aparece antes do commit, com os dois caminhos nomeados, e nao numa descoberta acidental semanas depois.
- **Eu nao guardo o seu nome.** O registro de nascimento usa um token anonimo; voce pode trocar esse token por um apelido seu, se quiser.
- **Eu nao preciso de rede para funcionar.** Reservar um ID e um ato local. Voce pode trabalhar dias sem sincronizar e o seu trabalho se funde depois sem conflito.
- **Eu digo o que nao faco neste plano.** Apelidos pronunciaveis, resolucao de apelido para artefato e os identificadores secundarios de pendencias e QA ficam para planos seguintes. Nao espere isso desta entrega.
- **Eu so entrego com a suite verde.** Cada passo do plano tem teste antes do codigo, e o conjunto so entra quando os verificadores do harness nao acusam falha nova.

## Pergunte a si mesmo

A resposta honesta a qualquer uma destas perguntas pode mandar o plano de volta para a mesa. E melhor que volte agora.

1. **Voce cita IDs em voz alta, em reuniao ou no chat, com frequencia?** Se "plan 7" e parte do vocabulario do time todo dia, a perda do numero curto vai doer antes de o apelido chegar. Nesse caso, talvez o apelido precise vir junto, e nao depois.
2. **Voces criam varios artefatos no mesmo dia, em pessoas diferentes, e precisam saber qual veio primeiro?** Se sim, a ordem dentro do dia importa para voce, ao contrario do que o designer assumiu, e o prefixo precisaria incluir a hora.
3. **Voce tem scripts, atalhos ou integracoes suas que leem o nome do arquivo esperando seis digitos?** Qualquer coisa que procure `plan-` seguido de seis numeros vai passar batido pelos artefatos novos. Eu cuido do que esta dentro do harness; o que esta fora dele e seu, e eu nao vejo.
4. **Alguem do time vai ficar numa versao antiga do harness por mais do que alguns dias?** Se a resposta e sim, essa pessoa vai ter commits recusados sem entender por que. Ou todos atualizam juntos, ou o plano precisa de um modo de transicao que hoje ele nao tem.

## Como me dizer que algo nao bateu

- **Antes do codigo existir**: a janela e agora, entre este espelho e o `/implement`. Leve a resposta das perguntas acima para quem vai executar o plano, ou anote no proprio arquivo do plano. Uma resposta "sim" na pergunta 2 ou na 4 muda o plano; na 1 ou na 3, muda a ordem dos planos seguintes.
- **Se voce discorda da decisao de fundo** (identidade sem coordenacao, no lugar de um numero global): o lugar e um `/design`, que reabre a decisao D-005 com a sua razao registrada nas suas palavras. As alternativas que foram rejeitadas, e por que, estao escritas la.
- **Depois de usar**: `/reflect` registra o que voce disser, literalmente, sem prescrever mudanca. Se o ID novo atrapalhar na pratica, e por ali que isso vira entrada para o proximo ciclo.
- **Se encontrar um comportamento errado** (uma duplicata que eu nao acusei, um marcador que eu recusei sem motivo): abra um `/research` com o caso concreto. Um verificador que falha em silencio e exatamente o que este plano existe para evitar.

Eu nao prometo prazo de resposta; prometo que nada do que voce disser nesses canais se perde, e que o plano nao avanca para o codigo enquanto este espelho estiver sendo lido.
