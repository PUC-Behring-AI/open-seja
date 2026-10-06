# SECURITY CHECKLISTS -- open-seja

> **Escopo:** harness local para o Claude Code. Não há serviço exposto em rede, frontend, login nem entrada HTTP. As superfícies web clássicas são **N/A**. As superfícies vivas são: segredos (K), dependências (J), o próprio portão e seus hooks (O) e a fronteira de distribuição (P). O modelo de ameaças do harness está em `.claude/references/general/threat-model.md`.

---

## Checklist A -- New Endpoint

**N/A** -- sem endpoints.

## Checklist B -- File Upload

**N/A** -- sem upload; o harness lê arquivos do repositório do próprio usuário.

## Checklist C -- User-Generated Content (XSS)

**N/A (mínimo)** -- o HTML gerado (`--html`, SPO) é aberto localmente pelo próprio usuário; ao gerar HTML, escapar conteúdo vindo de artefatos.

## Checklist D -- Authentication Changes

**N/A** -- sem autenticação.

## Checklist E -- CSRF

**N/A.**

## Checklist F -- Security Headers

**N/A.**

## Checklist G -- CORS

**N/A.**

## Checklist H -- Database

**N/A** -- sem banco.

## Checklist I -- Mass Assignment Prevention

**N/A.**

## Checklist J -- Dependency Security

- [ ] Scripts do harness continuam só com biblioteca padrão
- [ ] Dependências do template de portão declaradas como `--dev` no projeto, nunca no harness
- [ ] Ferramentas externas stubadas nos testes do harness

## Checklist K -- Secret Management

- [ ] Nenhum segredo em fonte, em `_output/` ou em `product-design/` (constituição S3)
- [ ] `.env` no `.gitignore`
- [ ] `check_secrets.py` limpo antes do commit (`/design`, post-skill)
- [ ] Segredo commitado por acidente é rotacionado e o histórico limpo

## Checklist L -- SSRF Prevention

**N/A** -- scripts do harness não fazem chamadas de rede.

## Checklist M -- Logging & Monitoring Security

- [ ] `conversation-trace.jsonl` passa pelo mascaramento antes de gravar (exit 2 pede confirmação)
- [ ] Nenhuma chave em telemetria ou briefs

## Checklist N -- Backup & Restore Security

**N/A** -- recuperação é o git.

## Checklist O -- Portão e hooks

- [ ] O portão roda sem rede e sem chave de API no ambiente filho (S1)
- [ ] `--accept-baseline`, `git commit --no-verify`, `-n` e `core.hooksPath` negados ao agente; escrita em `quality-baseline.json` e nas linhas `GATE_*` recusada (S2)
- [ ] Hooks `Stop` e `PreToolUse` instalados e conferidos com `/hooks` e `/permissions`
- [ ] Marcadores de evasão (`skip`, `xfail`, `no cover`, `no mutate`) só com motivo registrado

## Checklist P -- Fronteira de distribuição

- [ ] `main` só recebe o que `tools/publish-manifest.txt` inclui (C3)
- [ ] Nenhum nome de parceiro, instituição conveniada ou pessoa em `_output/` e `product-design/` (C2)
- [ ] Atribuição e licença CC BY-NC 4.0 preservadas (C1)

## Quick Reference -- Validation Constants

| Constant | Backend | Frontend | Value |
| -------- | ------- | -------- | ----- |
| CRAP funções tocadas / teto | `gate.py` | N/A | 10 / 30 |
| Rodadas do portão por step | `/implement` | N/A | 3 |
