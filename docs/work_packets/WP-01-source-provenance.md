# WP-01 — Reproduce source and dependency provenance

- Status: `in_progress`
- Owner: Codex
- Branch: `work/wp-01-source-provenance`
- Updated: 2026-09-23
- Depends on: none
- Gate: G0

## Result

Provide a clean, reproducible source baseline whose results can be compared across contributors.

## Scope and starting points

Start with `references.json`, `scripts/references.py`, `patches/`, and both emulators' build instructions. Record recursive submodule commits and local modifications, including nested DSP sources. Preserve existing research checkouts; use a clean separate build where needed. Inspect license notices, including octemu's stated restriction on distributing its combined binaries.

## Deliverables

- `docs/reports/WP-01-provenance.md` with exact source/dependency/toolchain versions and license/provenance inventory.
- Reproducible setup/build instructions or a focused setup-script correction, with local build outputs ignored.

## Acceptance checklist

- [x] Root, emulator, recursive dependency, and patch revisions are recorded; dirty source state is disclosed.
- [x] The trace patch applies to a clean pinned Gearmulator checkout and its relevant library builds.
- [x] Octemu prerequisites and supported host assumptions are recorded; unavailable prerequisites are explicit.
- [x] Contribution-source permissions and binary distribution restrictions are inventoried without inventing a license grant.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: Recorded local source and recursive dependency revisions, patch hashes, dirty checkout state, host toolchain, octemu prerequisites, and source license notices. Applied the trace patch to a clean pinned Gearmulator MD/MM worktree and built `mdLib`.
- Next action: Commit and push the report, then submit WP-01 for review.
- Waiting on: No packet dependency.
- Blockers: None. The current shared branch contains the successful pull of `origin/main` at `6cdc258`; a direct fetch from this sandbox could not write `.git/FETCH_HEAD`.
- Evidence: [WP-01 provenance report](../reports/WP-01-provenance.md); dated source/build observation in [research log](../RESEARCH_LOG.md).

## Prompt history

### 2026-09-23 / prompt 1 — Establish source provenance and reproduce the trace build

- Request: Start work on the port, using the next unclaimed technical packet.
- Starting state → ending state: Ready → in progress; all technical acceptance items have evidence, delivery remains.
- Owner / branch: Codex / `work/wp-01-source-provenance`.
- Completed:
  - [x] Reconciled WP-34 PR #3 as merged at `6cdc258` before starting technical work.
  - [x] Compared the reference manifest with available checkout commits, recursive submodules, local modifications, and patch hashes.
  - [x] Applied the trace patch to a clean worktree at Gearmulator MD/MM `8cea0524a75435122c20b669ca114c9ac6509ba2` and built `mdLib`.
  - [x] Recorded octemu host requirements, current prerequisite detection, source notices, and the upstream combined-binary restriction.
- Remaining:
  - [ ] Commit and push this packet; open a draft PR or provide the compare URL.
- Changed files: `docs/reports/WP-01-provenance.md`, this packet, `docs/STATUS.md`, `docs/RESEARCH_LOG.md`, `docs/GETTING_STARTED.md`, `docs/BOOT_FEASIBILITY.md`, and WP-34's merge reconciliation.
- Verification:
  - `git apply --check` — passed on the clean pinned Gearmulator MD/MM worktree.
  - `git diff --check` in the temporary source worktree — passed.
  - CMake configure and Ninja `mdLib` build — passed (222 build steps); no firmware was loaded.
  - `make -C vendor/octemu doctor` — passed; all required and optional host tools were found.
  - `make check` — passed; 9 reference repositories validated and Python scripts compiled.
  - `git diff --check` — passed; modified documentation link check — all 45 local links and heading anchors resolved across 7 files.
  - GitHub CLI lookup at prompt start could not reach `api.github.com`; the user's successful pull made the `origin/main` ref available locally at the WP-34 merge commit. A subsequent agent `git fetch origin` could not write `.git/FETCH_HEAD` under the sandbox.
- Findings: The earlier trace build used a modified nested DSP tree. The isolated build succeeded using the parent pin and required recursive source contents at their recorded Git-link commits. Octemu's installed host prerequisites are present, but its dependency, QEMU, and application builds were not run.
- Blockers: None for WP-01 acceptance.
- Next action: Review the staged scope, commit/push, and submit WP-01 as a draft PR. WP-02 and WP-03 remain the next technical packets.
- Delivery: Enclosing delivery commit; hash and PR/compare result will be reported after submission.
