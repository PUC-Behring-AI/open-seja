# Release process (dev branch only)

open-seja keeps two branches with different trees:

- **`dev`** -- where all work happens. It tracks the harness plus the project's own `product-design/`, `_output/`
  and `tools/`.
- **`main`** -- the distribution branch, what people clone. Its tree is the public surface defined by
  `tools/publish-manifest.txt`, minus `product-design/`. Each release is one commit whose tree is the pruned tree of
  `dev` and whose only parent is the previous `main`. `dev`'s history is not reachable from `main`.

`main` is never merged into `dev` and never receives direct commits. `tools/` (this file included) exists only on
`dev`.

## Cutting a release

From a checkout of `dev` with a clean working tree:

1. Move `## [Unreleased]` in `CHANGELOG.md` to `## [X.Y.Z] - YYYY-MM-DD` (UTC) with an empty `## [Unreleased]` above
   it, set `.seja-version` to `vX.Y.Z`, and commit on `dev`.
2. Preview, write and check the distribution commit:

   ```bash
   python tools/build_dist_branch.py --dry-run
   python tools/build_dist_branch.py
   python tools/build_dist_branch.py --check
   ```

   The commit message defaults to `Release vX.Y.Z (distribution tree of dev <sha>)`, taken from the newest
   versioned heading of the CHANGELOG.
3. Check what a user receives: `git clone --branch main <this repo> /tmp/dist-check`, then in it run
   `python .claude/skills/seja-setup/detect_setup_state.py` (expect `state: fresh-download`).
4. Tag the release on `main`: `git tag -a vX.Y.Z main -m "open-seja vX.Y.Z"`. `/seja-setup --here` pins
   `.seja-version` from `git describe --tags --exact-match HEAD`, and `/seja-setup --upgrade` clones tags, so the tag
   must sit on `main`.
5. Confirm the repository visibility on GitHub, then push (ask before pushing):

   ```bash
   git push origin dev main vX.Y.Z
   ```

The surface is changed in one place only: `tools/publish-manifest.txt`. `build_dist_branch.py` adds the
`product-design/` exclusion on top of it.
