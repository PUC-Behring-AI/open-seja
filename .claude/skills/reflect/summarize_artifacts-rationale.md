---
designer_description: "Maintainer rationale for summarize_artifacts.py: historical artifact citations and design-choice context extracted from the script body so runtime code stays concise while the audit trail remains self-contained."
---

# summarize_artifacts rationale

Maintainer-only context for `summarize_artifacts.py`. This file is not imported or loaded by the script; it is versioned next to the script so historical design context stays discoverable without keeping private artifact citations in runtime comments.

> Runtime contract: do not import this file from Python code. Keep each citation entry to one self-contained paragraph that explains what the cited artifact changed and why the script is marked by it.

## Citation rationale

- **plan-000295**: The artifact resolver accepts both fully qualified and bare IDs so callers can summarize a known artifact without remembering its directory. The concrete historical example is illustrative only and has been replaced with a placeholder.
- **plan-000066**: For plans, the summary also reads the sibling `plan-<id>-progress.md` (via `step_notes.parse_notes` and the `- communication:` / `- drift:` lines written by `step_notes.py record`) so `/reflect` can present the four evidence sources (step notes, quality gate, communication, drift) as recorded. Agent-written text (less-sure, the drift report header) is only emitted inside quotes and attributed ("agent recorded"), never as the skill's own voice; missing evidence is reported as "not offered" / "not measured" instead of being omitted. Missing gate JSONs and missing drift reports degrade to "(json missing)" / "(report missing)" rather than raising.
