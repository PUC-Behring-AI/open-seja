# Feature de exemplo (plan-000010)

Exemplo fictício e completo de uma feature no esquema `features/<slug>/` (`.claude/references/template/feature-layout.md`) escrita na convenção `.claude/references/general/gherkin-spec-format.md`:

- `features/task-list/intent.md`: 2 requisitos, "Modelo e termos", "Fora do escopo".
- `features/task-list/manage-tasks.feature`: 4 cenários em português (`# language: pt`), um `Esquema do Cenário` com 2 linhas e um cenário `@skip`.
- `conftest.py.example`, `test_task_list.py.example`: modelo para o pytest-bdd (primeiro adaptador de runner; recomendação, CYC-026). Têm o sufixo `.example` para o pytest do harness não os coletar. Para rodar, copie a pasta para um diretório de trabalho e tire o sufixo.
- `cucumber_states.py.example`: leitura de referência do relatório Cucumber JSON para os estados do DRM-003.

Validar: `python .claude/skills/scripts/check_features.py .claude/references/template/feature-example` (sai 0; o aviso do `@skip` e a informação de "Fora do escopo" são esperados).

Rodar no pytest-bdd (num diretório descartável):

```bash
uvx --with pytest-bdd pytest --strict-markers --cucumberjson=report.json --junitxml=junit.xml
```

Resultado esperado: 2 cenários verdes (o `Esquema do Cenário` conta como um), 1 vermelho por `AssertionError` (REQ-task-list-002) e 1 desligado por `@skip`. Detalhes em `gherkin-spec-format.md`, seção 10.
