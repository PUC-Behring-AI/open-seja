# PROJECT CONVENTIONS

> Synthetic fixture shaped like a long-lived research archive: Markdown first,
> independent Python sub-projects, own output folder and own extra variables.

| Variable | Value | Description |
|----------|-------|-------------|
| `PROJECT_NAME` | Archive Fixture | Synthetic archive |
| `PROJECT_MODE` | brownfield | Project mode |
| `OUTPUT_DIR` | `_output` | Root directory for generated artifacts |
| `PLANS_DIR` | `${OUTPUT_DIR}/plans` | Plan output folder |
| `RESEARCH_DIR` | `${OUTPUT_DIR}/research-logs` | Research log folder |
| `CODEBASE_DIR` | `.` | Codebase root |
| `BACKEND_FRAMEWORK` | none | CLI/library project |
| `FRONTEND_FRAMEWORK` | none | No web UI |
| `TESTING_STACK` | pytest + ruff + pyright | Testing summary |
| `SECRETS_EXTRA_SKIP_DIRS` | .venv,vendored | Extra directories skipped by the secret scan |
| `LOCAL_ONLY_VARIABLE` | kept | A variable that only this project defines |
