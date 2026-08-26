# doc-B Collection -- Verification Record

> Collection-local verification artifact (plan-000733, `doc-guidelines.md` Section I check 5).
> Records pass/fail for each verification check so the finalization is auditable and a
> re-run has a baseline. Kept inside the collection to preserve self-containment.

**Verify run**: 2026-07-16 -- plan-000733 Step 2.
**Overall status**: LIVE -- doc-B is a complete, distinct documentation edition (Alternative B:
System-Isomorphic). It is NOT superseded by doc-D (formerly doc-BC); the collections are
co-existing alternatives -- see `_output/docs/README.md`. Verification formalizes checks
previously run during plan-000677 execution. (The prior "SUPERSEDED -- see doc-BC" status,
added by plan-000733 from a plan-level supersession, was corrected by plan-000755.)

Inventory scanned: 33 HTML files (2 root-level: `index.html`, `migration-from-docs.html`;
5 volume index pages; 26 chapter pages across 5 volumes) + `styles.css`.

## Check-by-check results

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Placeholder-anchor gate | PASS | `grep -rc '#placeholder'` returns 0 across all 34 files. Plan-000677 Step 1 previously verified this. |
| 2 | Embedded-resource containment | PASS | All relative resource targets (CSS) resolve inside `doc-B/`. Every chapter page references `../styles.css` (resolves to `doc-B/styles.css`); root pages reference `styles.css` directly. No `src` attributes reference external resources. No cross-collection links (the former `../doc-BC/reading-map.html` supersession link was removed by plan-000755). No path-climbs above the docs root. |
| 3 | Internal link resolution | PASS | Every intra-collection `href` resolves to a file on disk. Cross-volume links (e.g., `../vol3/ch1-lifecycle-pipeline.html` from vol2 chapters) all resolve. Fragment-only links (anchors within pages) were not verified for target-id existence but structural patterns are consistent. No cross-collection links remain. |
| 4 | Structural-a11y sweep | PASS | Spot-checked 4 pages (`index.html`, `vol1/ch1-what-is-seja.html`, `vol3/ch2-skills-in-depth.html`, `vol5/index.html`). All have: single `<h1>`, `<header>` + `<nav>` + `<main>` + `<footer>` landmarks, `class="skip-nav"` link, `id="main-content"` target on the main landmark. Breadcrumb `<nav aria-label="breadcrumb">` present on all 33 HTML pages. |
| 5 | Navigation consistency | PASS | Breadcrumb links present on all pages. Volume chapter pages link to `../index.html` (collection root) and their own `index.html` (volume index). Cross-volume chapter links use `../volN/` paths and all resolve. Volume index pages link back to collection root. Footer navigation links consistent across all pages. |
