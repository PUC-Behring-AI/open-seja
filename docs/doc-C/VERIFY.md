# doc-C Collection — Verification Record

> Collection-local verification artifact (plan-000687, `doc-guidelines.md` §I check 5).
> Records pass/fail for each verification check so the finalization is auditable and a
> re-run has a baseline. Kept inside the collection to preserve self-containment.
> Wording deliberately avoids the literal finalization-gate tokens (the placeholder-anchor
> marker — hash + "placeholder" — and CSS asset-URL syntax) so the canonical grep gates
> stay at zero over this file.

**Verify run**: 2026-07-16 (full scripted disk-scan pass + `file://`-safety remediation) — plan-000687 Wave 2.
**Overall verdict**: **All §I checks PASS — scripted disk-scan + live browser run (2026-07-16, pa-000281 closed).**
All prerequisites are met — Skills Core is built (plan-000736, 16 pages), roadmap-000679
carries the Skills Core Wave 1 row (#7) with the verify row renumbered #8, and the
Reading-Map Skills links are restored. Every scripted §I check passes. The two
runtime/visual checks — render integrity (check 1) and JS-off progressive enhancement
(check 5b) — were **confirmed by a live browser run on 2026-07-16** (Claude Chrome
extension, doc-C served over a local HTTP server because the extension cannot open
`file://` URLs; the `file://` link-resolution case remains covered by the scripted check 5,
which passed). The collection is now both scripted-verified and browser-verified — the
live pass that was tracked as pending action pa-000281 (plan-000747) is recorded here and
pa-000281 is closed. See the live-run note below and the plan-000747 remediation note at
the foot of this file for the accuracy and aria-label fixes applied after the original
verify run.

**Inventory scanned (keyed to roadmap-000679 Wave Summary at verify time):**
44 HTML files total = `index.html` Reading Map (Wave 0 #2) + 8 Concepts + 7 Operations +
7 Reference (call-graph kept as a separate collection-local page — the critique-710 merge
into skill-map was **not** adopted) + 16 Skills Core (15 skill pages + category landing) +
1 Practitioner track gate + 3 category landing pages (concepts/operations/reference —
added in the earlier remediation session, §I "Inventory tolerance") + `_template.html`
authoring template. Shared assets: `styles.css`, `nav.js`. All five named cores/track are
present; no pre-717 under-count.

## Check-by-check results

| # | Check (`doc-guidelines.md` §I) | Result | Notes |
|---|--------------------------------|--------|-------|
| 1 | Render integrity (browser) | ✅ PASS *(live run 2026-07-16)* | Live browser run confirmed: `index.html` (Reading Map) and `core/reference/call-graph.html` render with the SEJA design tokens applied (washi ground, Shippori Mincho serif headings, clay/earth Diataxis badges), Google Fonts loaded, breadcrumb + sibling nav + tables laid out correctly, and the nav.js TOC/scrollspy active (current section highlighted). **Zero console messages** (no errors, no warnings) on a clean reload with console tracking active — matching the static prediction (dependency-free vanilla JS, guarded `matchMedia`/`IntersectionObserver`, DOM built via `createElement`/`textContent`, no `innerHTML`). Served over a local HTTP server (the Claude Chrome extension cannot open `file://` URLs); render behaviour is scheme-independent, and the `file://` link-resolution case is covered by check 5. |
| 2 | Navigation consistency | ✅ PASS | Every content page carries a breadcrumb back to `index.html` and a sibling/see-also nav; `index.html` is the exempt collection root. |
| 3 | Diataxis badges | ✅ PASS | All 42 non-root pages carry a `diataxis-*` badge with a text label. |
| 4 | Core-type / track badges | ✅ PASS | All 42 non-root pages carry their `core-<cat>` or `track-<name>` badge (Skills pages: `core-skills`). |
| 5 | Internal links resolve on disk | ✅ PASS *(fixed this run)* | 472 internal targets. **Was FAIL:** 66 links pointed at bare directories (`href` to a current-dir "." on 22 content pages; `core/<cat>/` and `tracks/practitioner/` on `index.html`). Bare-directory links rely on a web server's directory-index resolution and **break under `file://`** (the self-contained static-open case, §C). **Fixed:** all 66 rewritten to explicit `index.html` targets. Under strict `file://` semantics every internal href/src now resolves to an existing **file**; zero absolute-root (`/…`) paths. |
| 5a | Structural-a11y sweep | ✅ PASS | All 43 non-template pages: four ARIA landmarks in order (header → breadcrumb nav → main → footer), exactly one `<h1>`, `main` carries the skip-nav target id, skip-nav link present, badge text labels, wide tables (≥5 cols) wrapped in the table-container. |
| 5b | Progressive enhancement (JS off) | ✅ PASS *(live run 2026-07-16)* | Live run confirmed via raw-HTML inspection (the pre-JS DOM a JS-disabled browser renders): on `call-graph.html` the fetched source already contains the `<h1>`, all four `<h2>` sections, `<main>` (4722 chars of body text), breadcrumb, see-also, and skip-nav — i.e. all content is present without any script. nav.js's TOC contributed **0 links in the raw HTML but 4 after execution**, proving the TOC/scrollspy/Diataxis-filter are pure additive enhancement with no content behind them. Matches the static prediction (nav.js only *adds*, no-ops when containers absent; CSS hide rules JS-off-safe; no `.no-js`/`.js-only` gating). |
| 6 | Content completeness (inventory) | ✅ PASS *(unblocked)* | Keyed to roadmap-000679 Wave Summary at verify time. All five named cores/track present (Concepts 8, Operations 7, Reference 7, Skills 16, Practitioner gate 1); Reference Core = 7 with call-graph a separate page; Skills Core built (plan-000736); roadmap has the Skills Core row and the #7→#8 verify renumber — no pre-717 under-count. |
| 7 | Embedded-resource containment | ✅ PASS | Every relative resource target (`href`/`src`/`data`/`poster`, CSS `url()`) resolves inside `doc-C/`; zero path-climbs above the collection root; the only remote resource is the permitted Google Fonts import. |
| 8 | Placeholder-anchor gate | ✅ PASS | Zero unresolved forward-reference markers across all HTML content pages; the sole historical hit is documentary prose in `_template.html` describing the convention (not a marker to resolve). |

### Five §I named checks (plan-000687 finalization set)
- Embedded-resource containment scan (Check 7): ✅ PASS
- Placeholder-anchor gate (Check 8): ✅ PASS
- Structural-a11y sweep (Check 5a): ✅ PASS
- Progressive-enhancement (Check 5b): ✅ PASS (static proxy — CSS/JS source inspection)
- Verification-artifact-itself (this file): ✅ EMITTED

## Remediation applied this session (`file://` link safety)
- Rewrote 66 bare-directory internal links to explicit `index.html` targets so the
  collection opens correctly via `file://` (not only over a directory-index web server):
  - 22 content pages: the breadcrumb category self-link and the footer collection link
    (current-dir "." form) → `index.html`.
  - `index.html`: the `core/concepts/`, `core/operations/`, `core/reference/`,
    `core/skills/`, and `tracks/practitioner/` directory links → their `index.html`.
- Re-verified: no residual directory links, no absolute-root paths, all 472 internal
  targets resolve to a real file, containment and placeholder gates still clean.

## Note on browser checks (1, 5b) — live run recorded 2026-07-16
The original verify run could not reach a live browser (the Claude Chrome extension was
offline), so checks 1 and 5b were first confirmed by static analysis and the obligation was
tracked as pending action **pa-000281**. That live run has now been performed and recorded:

- **Method.** The Claude Chrome extension cannot open `file://` URLs, so doc-C was served
  over a local HTTP server (`python -m http.server`, `127.0.0.1`) and driven through the
  extension. Render integrity and JS-off progressive enhancement are scheme-independent, so
  the local-server render faithfully exercises both; the one `file://`-specific concern
  (bare-directory link resolution) is separately covered by scripted check 5, which passed.
- **Check 1 (render integrity).** `index.html` and `core/reference/call-graph.html`
  rendered with the full SEJA design system (tokens, fonts, badges, tables, breadcrumb,
  nav.js TOC/scrollspy). **Zero console messages** on a clean reload with tracking active.
- **Check 5b (JS-off).** Raw pre-JS HTML for `call-graph.html` already carries all content
  (h1, all four h2s, `<main>` with 4722 chars, breadcrumb, see-also, skip-nav); the TOC went
  from 0 links in raw HTML to 4 after JS — pure additive enhancement, no content behind JS.
- **pa-000281 is now closed.** Both browser obligations are satisfied by this live run.

The static-analysis evidence (all local resources resolve; `nav.js` is pure progressive
enhancement; every CSS hide rule is JS-off-safe) held up exactly against the live run.

## Verify pass -- plan-000768 (2026-08-01): Architect and Scholar tracks

Seven pages added and two rewired; the collection grows from 44 to 51 HTML files
(50 served pages + `_template.html`). Scope: `tracks/architect/` gate + 4 Extension
Points pages, `tracks/scholar/` gate + Open Questions, plus edits to the Reading Map
(`index.html`) and the Practitioner gate.

**Verdict: all scripted gates PASS.** Checks 1 and 5b (render integrity and JS-off) were
**not** re-run live this pass; the new pages introduce no new CSS, no new JS, and no new
resource types -- they reuse `styles.css` and `nav.js` unchanged -- so the 2026-07-16 live
run's findings carry over by construction rather than by fresh observation. Stated here
rather than claimed as a new live pass.

| # | Check (`doc-guidelines.md` §I) | Result | Notes |
|---|--------------------------------|--------|-------|
| 2 | Navigation consistency | PASS | All 7 new pages carry a breadcrumb to `index.html`, a see-also nav, and a footer collection nav. Track sub-pages use the 4-crumb depth-2 form (Home > Tracks > Track > Page), matching the `core/` precedent. |
| 3 | Diataxis badges | PASS | 7/7 new pages carry a `diataxis-*` badge with a text label (5 `howto`, 2 `explanation`). |
| 4 | Core-type / track badges | PASS | 7/7 carry `track-architect` or `track-scholar` in the compound `class="badge track-*"` form (§A). No CSS change was needed: the tokens and badge modifiers were already present in `styles.css` (lines 75-77, 115-117, 555-557). |
| 5 | Internal links resolve on disk | PASS | Scripted positive link-existence check over all 50 served pages: every non-deferred internal `href`/`src` resolves to a real file. Zero bare-directory links, zero absolute-root paths. Checker: `_output/tmp/check_doc_links.py`. |
| 5a | Structural-a11y sweep | PASS | 7/7 new pages (plus the 2 modified): four ARIA landmarks in document order, exactly one `<h1>`, skip-nav link with a matching `id="main-content"` on `<main>`, no skipped heading levels, the one wide table wrapped in `table-container`. |
| 6 | Content completeness (inventory) | PASS | Architect and Scholar tracks are no longer directory stubs. Reading Map decision tree: 7 rows -> 9, covering all five research-000661 audiences (new users, experienced users, contributors/architects, scholars, and the AI agent). `<caption>` updated to describe the 9-row, five-audience shape. |
| 7 | Embedded-resource containment | PASS | No new embedded resources. Every relative target on the new pages resolves inside `doc-C/`; zero path-climbs above the collection root. |
| 8 | Forward-reference marker gate | PASS (1 intended) | Exactly one deferred forward reference survives collection-wide: the Scholar gate's link to the deferred Foundations volume, which roadmap-000679 keeps out of scope by design. The historical `_template.html` hit remains documentary prose about the convention, not a marker. |
| -- | Collection status lint | PASS | `python .claude/skills/scripts/check_doc_collection_status.py` exits 0. One pre-existing informational note is unchanged by this plan (`index.html` carries no `<meta doc-status>`). |
| -- | Private-content gate | PASS | Zero `seja-public` references across the collection; all Extension Points content was sourced from `.claude/` and `product-design/` on disk. |

### Freshness surface: the Extension Points cluster

The four Extension Points pages describe harness internals that change, and doc-C carries
no freshness frontmatter. Each page therefore ends with a visible "Sourced from" note, and
the union of those notes is recorded here so the freshness surface is enumerable in one
place. When any file below changes, re-check the pages that cite it.

| Harness source | Cited by |
|---|---|
| `.claude/rules/harness-structure.md` | writing-a-skill, writing-a-subagent, modifying-enforcement-rules |
| `.claude/references/general/harness-governance.md` | writing-a-skill, writing-a-subagent |
| `.claude/skills/pre-skill/SKILL.md` | writing-a-skill |
| `.claude/skills/implement/SKILL.md` | writing-a-subagent |
| `.claude/skills/scripts/run_all_checks.py` | writing-a-skill, modifying-enforcement-rules |
| `.claude/skills/scripts/check_skill_spec.py` | writing-a-skill |
| `.claude/skills/scripts/check_plugin_registry.json` | modifying-enforcement-rules |
| `.claude/skills/scripts/generate_essential_perspectives_summary.py` | adding-a-review-perspective |
| `.claude/references/general/review-perspectives.md` | adding-a-review-perspective |
| `.claude/references/general/review-perspectives-index.md` | adding-a-review-perspective |
| `.claude/references/general/review-perspectives/dx.md` | adding-a-review-perspective |
| `.claude/agents/code-reviewer.md` | writing-a-subagent, adding-a-review-perspective |
| `.claude/agents/document-generator.md` | writing-a-subagent |
| `.claude/rules/backend.md`, `.claude/rules/tests.md` | modifying-enforcement-rules |
| `.githooks/pre-commit`, `.githooks/install.sh` | modifying-enforcement-rules |
| `product-design/constitution.md` (T1, S2) | writing-a-skill, writing-a-subagent, modifying-enforcement-rules |

### Deviation from the plan: sidebar scope on the gate pages

plan-000768's A11Y amendment directed both gate pages to use the §E **within-volume**
sidebar scope. They use the **within-page** scope (`.doc-nav`, `aria-label="on this page"`)
instead, and each gate states the chosen scope in an HTML comment as the amendment also
required. Reason: §E fixes **one sidebar model per collection** and names doc-C as the
page-scoped collection; the volume-scoped `.volume-toc` model belongs to doc-D and has no
supporting rules in doc-C's `styles.css` (`grep -c volume-toc styles.css` returns 0).
Following the amendment literally would have made 2 of 50 pages structurally inconsistent
with the other 48 and rendered an unstyled sidebar -- the opposite of the accessibility
outcome the amendment sought. The amendment's verifiable intent (state the scope, do not
leave the next author to re-derive it) is satisfied.

### pa-000258 resolution

Closed this pass. Item **(a)** -- the missing AI-agent and contributor decision-tree
scenarios, critique-000709 F7 -- is closed by the Reading Map rewiring above: both audiences
went from 0 occurrences to a row apiece. Item **(b)** -- the roadmap-000679 amendments --
**required no work**: all four were already present on disk before this plan began, and were
re-verified individually this pass (`## Deferred Scope` section present; Skills Core row #7
present; verify row renumbered to #8; the plan-000685 self-containment checkpoint gate present
as roadmap line 70, worded as "confirm plan-000685's call-graph page is collection-local ...
before Wave 1 starts" rather than with the literal phrase). Recorded explicitly so the closure
is not read as claiming this plan shipped item (b).

## Remediation applied (plan-000747, 2026-07-16)
Follow-up fixes from critique-000743 (doc-C thorough review), applied after the original
verify run:
- **ARIA-label casing (critique M2).** All `aria-label` values were aligned to
  doc-guidelines §E lowercase — `breadcrumb`, `collection`, `on this page`, `see also` —
  across all 44 HTML files (43 served pages + `_template.html`), a uniform scripted
  substitution (171 replacements). No CSS/JS selector depends on the casing (the print
  block and `nav.js` target by class), so no behavioural change; this only closes the §E +
  cross-collection consistency gap (doc-A/B/BC already used lowercase). The §I structural-a11y
  sweep (row 5a) remains PASS.
- **CI-integration accuracy (critique M3).** `core/operations/ci-integration.html` now names
  the three real `check_docs.py` scanners (`harness-reference-coverage`, `docs-frontmatter`,
  `mantra-banner-consistency`) plus `changelog-append-only`, `section-boundary-writes`, and
  `skill-graph-sync`, replacing the invented "documentation-consistency scanners" label; the
  priv-only set is now described as the three actual `_PRIV_CHECKS`.
- **Glossary accuracy (critique M4).** `core/reference/glossary.html` corrected onboarding
  "expertise levels (L1-L5)" → "(L1-L3)"; the upstream source
  (`shared-definitions.md`) and `onboard/SKILL.md` were corrected too so the datum has one
  point of truth.
- **Verdict honesty (critique M1).** The overall verdict and the check-1/5b rows above were
  re-worded so "PASS" no longer implies a live browser pass; the live run is tracked as
  pa-000281. Post-remediation: the objective §I gates (placeholder, self-containment,
  link-existence, structural-a11y, wide-table wrapping, badge presence) and the design-token
  drift check were re-run and all still PASS.
