# WP-01 — Reproduce source and dependency provenance

- Status: `done`
- Owner: Codex
- Branch: `work/wp-01-source-provenance`
- Updated: 2026-09-23
- Accepted delivery: [PR #4](https://github.com/repeat98/octamachine/pull/4), merged as `29471d01c61bbd8e83aa925157ae8fc4e25ddfa8` on 2026-09-23
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

- Completed: Recorded local source and recursive dependency revisions, patch hashes, dirty checkout state, host toolchain, octemu prerequisites, and source license notices. Applied the trace patch to a clean pinned Gearmulator MD/MM worktree and built `mdLib`. PR #4 was accepted and merged.
- Remaining: None for WP-01. G0 remains open pending target profiles and MD/OT baseline evidence.
- Next action: Dispatch WP-02 and WP-03.
- Waiting on: None.
- Blockers: No technical blocker. G0 remains open until the target profiles and MD/OT baseline packets add their evidence.
- Evidence: [WP-01 provenance report](../reports/WP-01-provenance.md); dated source/build observation in [research log](../RESEARCH_LOG.md); accepted delivery [PR #4](https://github.com/repeat98/octamachine/pull/4), merged as `29471d01c61bbd8e83aa925157ae8fc4e25ddfa8`.

## Prompt history

### 2026-09-23 / prompt 1 — Establish source provenance and reproduce the trace build

- Request: Start work on the port, using the next unclaimed technical packet.
- Starting state → ending state: Ready → in review; all WP-01 acceptance items have evidence and the branch is submitted as a draft PR.
- Owner / branch: Codex / `work/wp-01-source-provenance`.
- Completed:
  - [x] Reconciled WP-34 PR #3 as merged at `6cdc258` before starting technical work.
  - [x] Compared the reference manifest with available checkout commits, recursive submodules, local modifications, and patch hashes.
  - [x] Applied the trace patch to a clean worktree at Gearmulator MD/MM `8cea0524a75435122c20b669ca114c9ac6509ba2` and built `mdLib`.
  - [x] Recorded octemu host requirements, current prerequisite detection, source notices, and the upstream combined-binary restriction.
  - [x] Committed and pushed the packet to `work/wp-01-source-provenance`; opened draft PR #4.
- Remaining:
  - [ ] Maintainer review/merge; the project G0 gate remains open pending WP-02–05 evidence.
- Changed files: `docs/reports/WP-01-provenance.md`, this packet, `docs/STATUS.md`, `docs/RESEARCH_LOG.md`, `docs/GETTING_STARTED.md`, `docs/BOOT_FEASIBILITY.md`, and WP-34's merge reconciliation.
- Verification:
  - `git apply --check` — passed on the clean pinned Gearmulator MD/MM worktree.
  - `git diff --check` in the temporary source worktree — passed.
  - CMake configure and Ninja `mdLib` build — passed (222 build steps); no firmware was loaded.
  - `make -C vendor/octemu doctor` — passed; all required and optional host tools were found.
  - `make check` — passed; 9 reference repositories validated and Python scripts compiled.
  - `git diff --check` — passed; modified documentation link check — all 45 local links and heading anchors resolved across 7 files.
  - `git push -u origin work/wp-01-source-provenance` — passed; draft PR #4 is open against `main`.
  - GitHub CLI lookup at prompt start could not reach `api.github.com`; the user's successful pull made the `origin/main` ref available locally at the WP-34 merge commit. A subsequent agent `git fetch origin` could not write `.git/FETCH_HEAD` under the sandbox.
- Findings: The earlier trace build used a modified nested DSP tree. The isolated build succeeded using the parent pin and required recursive source contents at their recorded Git-link commits. Octemu's installed host prerequisites are present, but its dependency, QEMU, and application builds were not run.
- Blockers: None for WP-01 acceptance.
- Next action: Maintainer review/merge. WP-02 and WP-03 are the next technical packets after WP-01 review.
- Delivery: Draft [PR #4](https://github.com/repeat98/octamachine/pull/4); source/report commit `ee13514` is pushed.

### 2026-09-23 / prompt 2 — Reconcile merged source-provenance delivery

- Request: Reconcile WP-01 after the user merged PR #4 on GitHub.
- Starting state → ending state: In review → done; all WP-01 acceptance items are complete and PR #4 is merged.
- Owner / branch: Codex / `work/wp-01-source-provenance`.
- Completed:
  - [x] Verified PR #4 merged into `main` as `29471d01c61bbd8e83aa925157ae8fc4e25ddfa8` on 2026-09-23.
  - [x] Recorded the accepted delivery, closed the handoff, and updated project status and the next dispatch queue.
- Remaining: None for WP-01. G0 remains open pending WP-02–05 evidence.
- Changed files: This packet, `docs/reports/WP-01-provenance.md`, and `docs/STATUS.md`.
- Verification:
  - GitHub PR lookup — PR #4 is `MERGED`, base `main`, merge commit `29471d01c61bbd8e83aa925157ae8fc4e25ddfa8`.
  - `git fetch origin` — passed; `origin/main` advanced to the PR #4 merge commit.
  - `make check` and `git diff --check` — recorded after this reconciliation.
- Findings: Source provenance and the clean trace-patched `mdLib` build are accepted; firmware execution and G0 target/baseline evidence remain open in their owning packets.
- Blockers: None for WP-01.
- Next action: Dispatch WP-02 and WP-03.
- Delivery: PR #4 merged as `29471d01c61bbd8e83aa925157ae8fc4e25ddfa8`; reconciliation commit follows.
