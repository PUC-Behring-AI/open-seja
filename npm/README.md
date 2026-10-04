# open-seja

Install or upgrade the [open-seja](https://github.com/PUC-Behring-AI/open-seja)
Claude Code harness with a single command.

```bash
npx open-seja my-project             # new install
npx open-seja my-project --upgrade   # upgrade an existing checkout
```

## Requirements

- **Node.js** >= 18
- **git** on your PATH
- The **`claude` CLI** installed and authenticated (see <https://claude.com/claude-code>)

## What this command does

I clone a fresh copy of the harness into the target directory for you, check
that the `claude` CLI is actually there, and then hand your terminal over to an
interactive Claude Code session already sitting in that directory with
`/seja-setup` as its first prompt.

If the target directory already exists and looks like an open-seja checkout (it
has a `.seja-version` file), I skip the clone and reuse it. If it exists but is
something else, I stop and tell you rather than writing into it.

With `--upgrade`, the handoff prompt becomes `/seja-setup --upgrade`, which
refreshes the harness files while preserving your project-specific
configuration.

## What happens next

Inside the Claude Code session, `/seja-setup` asks you a few questions and scaffolds the project. After that I
suggest a first cycle, small enough to finish in one sitting:
[Your first cycle](https://github.com/PUC-Behring-AI/open-seja/blob/main/docs/quickstart.md#your-first-cycle).
It is a hypothesis, not a promise; the page that says what would confirm it or refute it is
[the hypothesis](https://github.com/PUC-Behring-AI/open-seja/blob/main/docs/hypothesis.md).

These links resolve only once this release reaches `main`; until then `npx` clones `main` and delivers the previous
harness.

## What this command does *not* do

**It does not finish the setup by itself.** The wrapper is deliberately thin:
it only does the mechanical part (clone, prerequisite check, handoff). All the
real work — detecting the setup state, asking you the configuration questions,
scaffolding `product-design/` and `_output/` — happens inside the interactive
`/seja-setup` session, where the harness's own Python logic remains the single
source of truth.

That means **this is not usable unattended in CI**: `/seja-setup` asks you
questions and waits for answers.

## Attribution

open-seja is a derivative of
[SEJA -- Semiotic Engineering Journeys with Agents](https://github.com/simonedjb/seja),
Copyright (c) 2025-2026 Simone Diniz Junqueira Barbosa, licensed under
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). This version has been modified
(installer, quality gate, `/mob`, per-step reflection notes); see the
[CHANGELOG](https://github.com/PUC-Behring-AI/open-seja/blob/main/CHANGELOG.md). Provided as-is,
without warranties (Section 5 of the license); non-commercial use only. The name `open-seja` is used
with the trademark holder's permission.

## License

The open-seja harness is distributed under CC BY-NC 4.0 (non-commercial), the
same license as its upstream, [simonedjb/seja](https://github.com/simonedjb/seja).
See the `LICENSE` file shipped with this package.
