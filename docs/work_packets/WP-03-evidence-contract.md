# WP-03 — Define captures, checkpoints, and comparisons

- Status: `done`
- Owner: Codex
- Branch: `work/wp-03-evidence-contract`
- Updated: 2026-09-23
- Depends on: none
- Gate: G0
- Accepted delivery: [PR #7](https://github.com/repeat98/octamachine/pull/7), merged at `2d13237cd9644a8f4574b3dc793f7ac03cd78685`

## Result

Give all later measurements one reproducible evidence format and an explicit pass/fail rule.

## Scope and starting points

Start from `tests/fixtures/README.md` and the proposed checkpoints in the plan. Define run identity, source hashes, initial state, stimulus timing, clock domains, output metadata, and a first-divergence report. Raw MMIO and DSP boot traces can contain firmware words, so keep payload-bearing captures local and publish reviewed summaries.

## Deliverables

- A versioned capture/manifest contract in `docs/reports/WP-03-evidence.md` and small synthetic text fixtures.
- A validator/comparison entry point for the contract, including clear missing-input, failure, and truncation results.

## Acceptance checklist

- [x] A run distinguishes cold boot, warm restart, cached initialization, and restored state.
- [x] Event order, timestamps/units, PC semantics, clock origins, and capped/incomplete traces are unambiguous.
- [x] Comparisons declare exact fields and justified tolerances before judging results; mismatches identify the first divergence.
- [x] Synthetic equivalent, divergent, missing, failed, and truncated inputs produce distinct outcomes without requiring firmware.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: Defined manifest version 1, JSONL event metadata, completeness and failure outcomes, comparison rules, and the first-divergence report. Added a stdlib validator/comparator plus synthetic fixtures and tests.
- Remaining: None for WP-03.
- Next action: Continue with WP-05; WP-04 now records the separate Gearmulator MD baseline, and its PR delivery is pending.
- Waiting on: Nothing for WP-03.
- Blockers: None for this tooling packet. G0 remains open until the Octatrack baseline is established and both required baselines are accepted.
- Evidence: [WP-03 evidence report](../reports/WP-03-evidence.md), [comparator](../../scripts/compare_captures.py), and [synthetic tests/fixtures](../../tests/fixtures/wp-03/).
- Delivery: PR #7 merged at `2d13237cd9644a8f4574b3dc793f7ac03cd78685`.

## Prompt history

### 2026-09-23 / prompt 1 — Define the versioned capture and comparison contract

- Request: Continue the Machinedrum-to-Octatrack port through eligible packets, reconcile WP-02, and keep working toward 07:00 Berlin time.
- Starting state → ending state: Ready → in review; all four WP-03 acceptance criteria have synthetic tooling or documented contract evidence.
- Owner / branch: Codex / `work/wp-03-evidence-contract`.
- Completed:
  - [x] Reconciled WP-02 PR #6 as merged at `e964334ef84790a16a5a500399d8c0f8a0c4e97f`; WP-02 is now `done`.
  - [x] Specified run identity, source/firmware fingerprints, build metadata, all four initial-state modes, ordered stimulus timing, named clocks, PC semantics, checkpoint triggers, trace limits, stop reasons, and comparison plans.
  - [x] Added `scripts/compare_captures.py` with stable JSON outcomes for equivalent, divergent, missing, invalid, incomplete, and failed capture inputs.
  - [x] Added synthetic manifests/events and ten tests covering tolerance, first divergence, all initial-state modes, missing trace/manifest, invalid duplicate keys, firmware identity enforcement, capture failure, trace cap, and a partial final record.
  - [x] Wired those checks into `make check` and updated setup/contributor/fixture documentation.
- Remaining:
  - [ ] Required GitHub CI checks and PR merge.
  - [ ] Actual MD/OT runtime baselines remain open under WP-04/WP-05; G0 is not cleared by synthetic tooling.
- Changed files: `scripts/compare_captures.py`, `tests/test_compare_captures.py`, `tests/fixtures/wp-03/`, `docs/reports/WP-03-evidence.md`, this packet, `docs/work_packets/WP-02-target-profiles.md`, `docs/STATUS.md`, `docs/RESEARCH_LOG.md`, `docs/COMPATIBILITY_MATRIX.md`, `Makefile`, `README.md`, `CONTRIBUTING.md`, `docs/GETTING_STARTED.md`, and `tests/fixtures/README.md`.
- Verification:
  - `make check` — passed; 9 reference repositories validated, scripts compiled, and 10 synthetic tests passed.
  - `git diff --check` — passed.
  - Local Markdown link/anchor check — passed; 114 local links/anchors across the 10 modified Markdown files.
  - Emulator and hardware runs — skipped; the packet defines and validates the evidence tooling using synthetic events only.
- Findings: Complete, failed, missing, malformed, and incomplete captures are distinct outcomes. A partial final JSONL record cannot pass. Event order follows contiguous capture-writer sequence numbers; timestamps remain tied to declared clock IDs, units, and origins. Numeric tolerance is explicit in the synthetic test plan only and is not a project firmware tolerance.
- Blockers: None for WP-03 acceptance. Required CI and merge conditions remain; G0 still needs real source/target baseline captures.
- Next action: Push/open the WP-03 PR, wait for required checks, merge when GitHub reports a clean eligible state, then start WP-04 and WP-05.
- Delivery: Enclosing commit on `work/wp-03-evidence-contract`; PR pending.

### 2026-09-23 / prompt 2 — Reconcile the accepted WP-03 merge

- Request: At the start of WP-04, reconcile the user's report that WP-03 was merged on GitHub.
- Starting state → ending state: In review → done; WP-03 acceptance had already passed, and PR #7 is merged.
- Owner / branch: Codex / `work/wp-03-evidence-contract` (merge reconciled on `work/wp-04-machinedrum-baseline`).
- Completed:
  - [x] Confirmed local `origin/main` contains merge commit `2d13237cd9644a8f4574b3dc793f7ac03cd78685` titled “Define WP-03 capture comparison contract (#7)”.
  - [x] Updated accepted delivery, handoff, and lifecycle status to done.
- Remaining:
  - [ ] None for WP-03; actual MD and OT baselines remain in WP-04 and WP-05.
- Changed files: This packet and `docs/STATUS.md`.
- Verification:
  - `git log -4 --oneline --decorate` — confirmed PR #7 merge commit is `HEAD` and `origin/main`.
  - `make check` — passed as part of WP-04 work.
- Findings: The merge accepts the synthetic capture/comparison tooling only; it does not supply firmware runtime evidence or close G0.
- Blockers: None for WP-03.
- Next action: Complete bounded Gearmulator runtime capture under WP-04.
- Delivery: WP-03 acceptance was merged in PR #7; this reconciliation is included in the enclosing WP-04 branch commit.
