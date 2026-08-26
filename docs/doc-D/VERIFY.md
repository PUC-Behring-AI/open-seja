# Verification Report -- doc-D Collection

**Date**: 2026-07-17
**Plan**: 000765, Step 9 (re-verify after nav generator run; supersedes plan-000728 Step 3 sweep)
**Scope**: 39 HTML files (31 included nav pages + 5 consolidated `*-print.html` pages + 3 excluded root pages) + `nav.js`

---

## plan-000765 note -- what changed since the previous sweep

This report re-verifies the collection **after** `build_doc_volume_nav.py` was run for real (plan-000765, Step 5). Three properties of the collection changed and are reflected below:

- **(a) Zero-JavaScript property RETIRED.** The former Check 4 asserted the collection "ships zero JavaScript." That property no longer holds and has been intentionally dropped: the 31 included pages now each carry a generator-injected `<script src="…/nav.js" defer>` tag. Check 4 is **reworded** from "ships zero JavaScript" to a **progressive-enhancement** check (every page renders and is fully navigable with JS disabled; `nav.js` only adds scroll-spy highlighting and the mobile sidebar toggle). Do NOT re-assert "no script tags in the collection."
- **(b) New page count.** The collection now includes **5 consolidated per-volume print pages** (`<volume>/<volume>-print.html`) and one collection-root **`nav.js`**. Included nav pages = 31 (25 chapters + 5 volume indexes + `reading-map.html`).
- **(c) New `volume contents` nav landmark.** Every included nav page (and every consolidated page) now carries an added `<nav aria-label="volume contents">` (the `.volume-toc` sidebar on nav pages; the `.volume-contents` top jump-nav on print pages). The old wording "four ARIA landmarks" is superseded by the **revised nav inventory** stated in Check 3.

---

## Check 1: Embedded-Resource Containment Scan

**Result: PASS**

All relative `href`/`src` attributes on the **31 included nav pages and the 5 consolidated print pages** resolve to files inside the `_output/docs/doc-D/` collection folder. This includes the newly injected `nav.js` script `src` (depth-adjusted: `../nav.js` on the 30 depth-1 pages, `nav.js` on `reading-map.html`), the "Single-page / print view" links from each volume index, and every intra-page `#…` fragment. **Zero triple-parent (`../../../`) traversals** anywhere. Programmatic sweep over the 36 live pages returned **0 containment issues** (0 escaping paths, 0 missing files).

**Exceptions noted (all non-issues, confined to the 3 excluded root pages)**:
- `_template.html`: `../styles.css`, `../nav.js`, `../index.html`, `../reading-map.html`, and `{{PREV_CHAPTER}}`/`{{NEXT_CHAPTER}}` placeholders. `_template.html` is a non-live skeleton written from a hypothetical depth-1 chapter location; its `../` hrefs and mustache placeholders are not navigable. Excluded per plan.
- `authoring-guide.html`: `../execution-layer/lifecycle-pipeline.html`, `constitution-guide.html`, `marker-system.html#marker-types` — all verified to sit inside `<pre>`/`<code>` documentation-example blocks (confirmed programmatically), not navigable links. Its real head links (`styles.css`, `index.html`) resolve.
- Remote `https://` / `mailto:` URLs are permitted and excluded from this check.

## Check 2: Placeholder / Link Resolution Gate

**Result: PASS**

**(a) `#placeholder` count**: 0 occurrences across all 39 files.

**(b) Consolidated-page in-page fragments**: every `href="#<chapter-slug--section>"` (and `#<chapter-slug>` chapter-jump) on the 5 print pages resolves to an existing `id` on that page. **0 dangling fragments.** The per-chapter `<slug>--<id>` namespacing scheme holds.

**(c) Print-view links**: every `*-print.html` link (the "Single-page / print view" links from the 5 volume indexes) resolves to an existing file on disk. **0 broken print-view links.**

**(d) Included-page in-page fragments**: every `#…` fragment on the 31 included nav pages (including the sidebar's nested `#section` scroll-spy anchors) resolves to an existing `id`. **0 dangling fragments.**

## Check 3: Structural-Accessibility Sweep (revised landmark inventory)

**Result: PASS** -- all 36 live pages (31 included nav pages + 5 consolidated `*-print.html` pages) satisfy the revised landmark inventory with every `<nav aria-label>` unique per page. The previously-recorded duplicate `<nav aria-label="collection">` on the print pages has been **fixed**: the `.volume-nav` "Back to \<Volume\> index" block is now `aria-label="volume navigation"`.

**Revised expected `<nav>` inventory** (replaces the old "four ARIA landmarks" wording -- the `volume contents` nav is the addition):

| Page class | Expected `<nav aria-label>` set (each UNIQUE per page) |
|---|---|
| Chapter pages | `breadcrumb`, `volume contents`, `chapter navigation`, `collection` |
| Volume index pages | `breadcrumb`, `volume contents`, `volume navigation`, `collection` |
| `reading-map.html` (depth-0) | `breadcrumb`, `volume contents`, `collection` |
| Consolidated `*-print.html` | `breadcrumb`, `volume contents`, `volume navigation`, `collection` |

**Included nav pages (31/31 PASS):** exactly one `<h1>` each; skip-nav `<a href="#main-content" class="skip-nav">` is the first focusable element on every page; no skipped heading levels; and the nav set above holds with **every `aria-label` unique per page** and none missing. Observed distribution: 25 chapter pages `(breadcrumb, volume contents, chapter navigation, collection)`, 5 index pages `(breadcrumb, volume contents, volume navigation, collection)`, 1 reading-map `(breadcrumb, volume contents, collection)`.

**Consolidated print pages (5/5 PASS):** each has exactly one `<h1>`, no skipped heading levels, no duplicate `id`s, and skip-nav first-focusable -- and each carries **four uniquely-labelled** `<nav>` landmarks: observed nav tuple per print page `(breadcrumb, volume contents, volume navigation, collection)`. The prior duplicate-`collection` defect is resolved.

- **Fix applied**: `build_doc_volume_nav.py` `build_consolidated_page` now emits the `.volume-nav` "Back to index" block as `<nav aria-label="volume navigation" class="volume-nav">`, distinct from the `<footer>` `<nav aria-label="collection">`. The generator was re-run against real doc-D (idempotent: a second run wrote 0 of 5), regenerating only the 5 `*-print.html` pages.

## Check 4: Progressive Enhancement -- JavaScript is Enhancement, Not a Dependency

**Result: PASS**

**JavaScript is progressive enhancement.** Every page renders and is fully navigable with JavaScript disabled; `nav.js` only adds scroll-spy highlighting and the mobile sidebar toggle. Verified no-JS baseline:

- **Sidebar is plain anchors.** The `.volume-toc` sidebar on each of the 31 included pages is a set of ordinary `<a href>` links (no `onclick`/`data-*` behavior hooks); it navigates fully with JS off. The current/active cue is delivered without JS via `aria-current="page"` + `:target` CSS plus a non-color WCAG 1.4.1 marker.
- **No dead controls with JS off.** The mobile `.volume-toc-toggle` button is created only by `nav.js` at runtime -- **0** of the 31 static pages contain a `volume-toc-toggle` button in their served HTML, so no inert control appears when JS is disabled.
- **Sidebar defaults to expanded.** **0** of the 31 static pages carry `.volume-toc.is-collapsed`; the sidebar is fully visible in the no-JS baseline (`is-collapsed` is applied only by the JS toggle).
- **Consolidated print pages ship zero JS.** All **5** `*-print.html` pages contain **NO `<script>` tag at all** (they are the single-page/print view; scroll-spy and the mobile toggle are irrelevant there).
- **Note (intentional, not a regression):** the 31 included nav pages now legitimately carry the generator-injected `<script src="…/nav.js" defer>` tag. This report does **not** assert "no script tags in the collection"; that former zero-JS property is retired (see plan-000765 note (a)). All 31 included pages carry exactly one `nav.js` script; verified present on 31/31.

## Check 5: Verification Artifact

**Result: PASS**

This file (`VERIFY.md`) is the updated verification artifact for plan-000765 Step 9.

---

## Collection scripts (re-run, still green)

| Script | Exit code | Result |
|---|---|---|
| `python .claude/skills/scripts/check_doc_collection_status.py --root .` | 0 | PASS -- every collection's status consistent with the registry; no stray supersession |
| `python .claude/skills/scripts/check_design_system_token_drift.py` | 0 | PASS -- all canonical tokens aligned across consumers (incl. doc-D inline block) |

---

## Summary

| Check | Description | Result |
|---|---|---|
| 1 | Embedded-resource containment (incl. `nav.js` src, print pages, print-view links) | PASS |
| 2 | Placeholder / link / in-page-fragment resolution | PASS |
| 3 | Structural accessibility (revised nav inventory incl. `volume contents`) | PASS |
| 4 | Progressive enhancement (JS is enhancement; no-JS baseline navigable) | PASS |
| 5 | Verification artifact updated | PASS |

**Overall: PASS.** All 5 checks PASS. The Check-3 duplicate-`<nav aria-label="collection">` defect on the 5 consolidated `*-print.html` pages was fixed by relabelling the `.volume-nav` "Back to index" block to `aria-label="volume navigation"` in `build_doc_volume_nav.py` `build_consolidated_page` and re-running the generator (idempotent; only the 5 `*-print.html` pages regenerated). Every `<nav>` on all 36 live pages now has a unique per-page `aria-label`. Both collection scripts re-run green (exit 0).
