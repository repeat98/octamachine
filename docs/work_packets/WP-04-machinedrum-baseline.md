# WP-04 — Capture the Machinedrum reference boot

- Status: `done`
- Owner: Codex
- Branch: `work/wp-04-machinedrum-baseline`
- Updated: 2026-09-23
- Depends on: [WP-01](WP-01-source-provenance.md), [WP-02](WP-02-target-profiles.md), [WP-03](WP-03-evidence-contract.md)
- Gate: G0
- Accepted delivery: PR #9 merged as `fb2c29d07f6d0468944fa5d80c960fb7e387e6ec` after required checks passed

## Result

Reproduce the Machinedrum OS 1.63 startup in the pinned Gearmulator model and establish bounded reference checkpoints for blank-flash and cached startup.

## Scope and starting points

Use `mdLib/mdmc.cpp`, `mdhardware.cpp`, `mddevice.cpp`, `mdsim.cpp`, the ROM loader, and the existing bus trace patch. Add or use a bounded headless driver with explicit local firmware/state paths. Account for factory caches, initial RAM/flash, polling loops, trace caps, and the difference between current and executing PC. Limit the capture to one machine instance per run unless the format identifies instances.

## Deliverables

- A documented headless boot/capture command and minimal integration code or upstream patch.
- `docs/reports/WP-04-md-baseline.md` plus reviewed checkpoint metadata; full traces stay ignored.

## Acceptance checklist

- [x] The pinned local image reaches named reference initialization and idle checkpoints under a finite timeout; see the [baseline report](../reports/WP-04-md-baseline.md).
- [x] Repeated cold boots from the same blank-flash state have matching redacted event ordering; cached starts are separately labeled and compared.
- [x] Reset state, SIM setup, both DSP HI08 streams, panel startup, and advancing no-stimulus scheduler checkpoints are captured; raw MMIO values remain local.
- [x] Trace cap, missing firmware, and stalled-driver cases fail or report incomplete evidence instead of passing silently.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: All four packet acceptance criteria have runtime or negative-case evidence in the [baseline report](../reports/WP-04-md-baseline.md). The repeated cold and cached run manifests compare equivalent through the WP-03 comparator. Results apply to the Gearmulator MD model only.
- Remaining: None for WP-04. Project gate G0 remains open until WP-05 establishes the Octatrack baseline.
- Next action: Begin WP-05 by verifying the pinned Octatrack OS distribution archive and its local provenance before using the extracted OS as a baseline.
- Waiting on: none for WP-04.
- Blockers: None for WP-04 evidence; G0 still awaits the Octatrack baseline.
- Evidence: The report contains safe checkpoint metadata, source/patch fingerprints, trace counts, WP-03 comparison results, and reproduction commands. Raw firmware-dependent traces remain under a private local path.
- Delivery: PR #9 merged as `fb2c29d07f6d0468944fa5d80c960fb7e387e6ec`.

## Prompt history

### 2026-09-23 / prompt 1 — Capture bounded Machinedrum cold and cached startup

- Request: Continue the port while the user is unavailable, reconcile the merged WP-03 dependency, and work toward 07:00 Berlin time; the user authorized merging after required checks pass.
- Starting state → ending state: Waiting → in review; all four WP-04 acceptance criteria have measured evidence, with PR delivery pending.
- Owner / branch: Codex / `work/wp-04-machinedrum-baseline`.
- Completed:
  - [x] Reconciled WP-03 PR #7 as merged at `2d13237cd9644a8f4574b3dc793f7ac03cd78685` and marked its packet done.
  - [x] Added a bounded headless test driver with explicit firmware path, blank-flash/cached initial states, named checkpoints, and finite wall/frame limits.
  - [x] Built the driver from Gearmulator MD/MM `8cea0524a75435122c20b669ca114c9ac6509ba2` and pinned recursive source contents; added an idempotent two-patch preparation workflow.
  - [x] Captured two repeat runs in both summarized and full-private modes. The full run recorded 10,340,278 events per driver run without filtering or truncation; checkpoint metadata and event order matched.
  - [x] Exercised trace-cap, missing-firmware, and stalled-driver failures; all returned incomplete/failed outcomes.
  - [x] Added the reviewed report and updated the research log, compatibility matrix, boot feasibility, getting-started guide, and project status.
- Remaining:
  - [ ] Push/open PR, pass required GitHub checks, merge, and reconcile accepted delivery on the next work prompt.
  - [ ] WP-05 remains required to close G0; it must verify the local Octatrack firmware source archive first.
- Changed files: `.gitattributes`, `patches/gearmulator-md-mm/0002-md-baseline-checkpoints.patch`, `scripts/capture_md_baseline.py`, `scripts/prepare_gearmulator.py`, `tests/test_capture_md_baseline.py`, `docs/reports/WP-04-md-baseline.md`, `docs/work_packets/WP-03-evidence-contract.md`, this packet, `docs/STATUS.md`, `docs/RESEARCH_LOG.md`, `docs/COMPATIBILITY_MATRIX.md`, `docs/BOOT_FEASIBILITY.md`, and `docs/GETTING_STARTED.md`.
- Verification:
  - `make check` — passed; nine reference repositories validated, scripts compiled, and 15 tests passed.
  - `make gearmulator-prepare` — passed on the already-patched pinned checkout; reruns recognize the dependent patch stack as applied.
  - Clean extracted source: patch 0001 plus patch 0002 — `git apply --check` and apply passed; reverse-check on the patched checkout passed.
  - CMake/Ninja — built `mdPanelReadinessFirmwareTest`, `mdIdleSchedulerFirmwareTest`, and `mdUwFirmwareTest` from the pinned clean source export; relevant panel/readiness driver executed.
  - Full-private baseline capture — passed twice with 300-second child limits and a 12,000,000-record cap; 10,340,278 records per run, no cap, matching checkpoints and event ordering.
  - Negative capture cases — trace cap returned exit 4/incomplete, missing image returned exit 2/failed, and a 0.05-second stall returned exit 4/incomplete.
  - Octatrack emulator and physical hardware — not run in WP-04; no Octatrack baseline or hardware evidence is claimed.
- Findings: At 44.1 kHz, both DSPs were observed booted by the first 128-frame sample block; exact completion order within that block remains unknown. Cold firmware readiness arrived at frame 102,400, factory initialization completed by frame 793,800, and cached readiness was already available at reset. Both no-stimulus idle checkpoints retained readiness while host, MCU, and DSP clocks advanced. See the report for the event schema, counts, timings, and limits.
- Blockers: None for WP-04. G0 remains open until WP-05 establishes the target-side emulator baseline.
- Next action: Push the branch and open the WP-04 PR; merge after required checks pass, then begin WP-05 by verifying the pinned Octatrack OS distribution archive and its local provenance.
- Delivery: Enclosing commit on `work/wp-04-machinedrum-baseline`; PR pending.

### 2026-09-23 / prompt 2 — Validate WP-04 captures against the WP-03 contract

- Request: Continue the overnight port after the user confirmed a successful pull and GitHub merge; keep progressing through eligible packets toward approximately 07:00 Berlin time.
- Starting state → ending state: In review → in review; WP-04 runtime evidence is complete and PR delivery remains pending.
- Owner / branch: Codex / `work/wp-04-machinedrum-baseline`.
- Completed:
  - [x] Added build metadata input to the bounded capture tool and emitted a WP-03 version-1 manifest and redacted JSONL projection for each repeated cold and cached phase.
  - [x] Compared both repeated pairs with `scripts/compare_captures.py`; cold and cached comparisons each matched all 5,630 declared records with no first divergence.
  - [x] Documented the metadata format, capture commands, comparator invocations, and the distinction between redacted projections and private raw traces.
  - [x] Repeated the full-private capture with the required build metadata argument; both child runs completed with 10,340,278 MMIO records and matching event order.
- Remaining:
  - [ ] Commit/push, open the WP-04 PR, pass required GitHub checks, merge, and reconcile accepted delivery.
  - [ ] WP-05 remains required to close G0; it must verify the local Octatrack firmware source archive first.
- Changed files: `scripts/capture_md_baseline.py`, `tests/test_capture_md_baseline.py`, `tests/fixtures/README.md`, `docs/reports/WP-04-md-baseline.md`, `docs/GETTING_STARTED.md`, `docs/BOOT_FEASIBILITY.md`, `docs/RESEARCH_LOG.md`, `docs/STATUS.md`, and this packet.
- Verification:
  - `scripts/compare_captures.py` cold pair — `equivalent`, 5,630 records compared, no first divergence.
  - `scripts/compare_captures.py` cached pair — `equivalent`, 5,630 records compared, no first divergence.
  - `make check` — passed; nine reference repositories validated, scripts compiled, and 16 tests passed.
  - Full-private capture with build metadata — passed twice with a 300-second child timeout and 12,000,000-record cap; 10,340,278 records per child, no cap, matching checkpoints and event ordering.
- Findings: The runtime evidence now has a WP-03-compatible redacted event projection. It compares ordering and metadata without publishing MMIO values or callback PC samples. Octatrack and hardware behavior remain untested.
- Blockers: None for WP-04 evidence; GitHub checks/merge and WP-05's source archive provenance remain.
- Next action: Commit and push the branch, open the WP-04 PR, then wait for checks before merging.
- Delivery: Enclosing commit on `work/wp-04-machinedrum-baseline`; PR pending.

### 2026-09-23 / prompt 3 — reconcile the merged WP-04 delivery

- Request: continue the overnight port and reconcile the manually merged WP-04 PR after its checks passed.
- Starting state → ending state: `in_review` → `done`; all four runtime acceptance criteria remain supported by the report and traces.
- Owner / branch: Codex / `work/wp-04-machinedrum-baseline` (delivery reconciliation recorded in the WP-35 follow-up branch).
- Completed:
  - [x] Confirmed PR #9 merged at `fb2c29d07f6d0468944fa5d80c960fb7e387e6ec` after all required GitHub checks passed.
  - [x] Reconciled the accepted delivery and marked WP-04 done.
  - [x] Kept G0 open because WP-05's Octatrack baseline is still missing.
- Remaining:
  - [ ] WP-05 must verify or reacquire the pinned Octatrack OS source distribution archive before a stock headless/UI run.
- Changed files: this packet and `docs/STATUS.md`.
- Verification: PR merge metadata and required check status confirmed; WP-04 report evidence remains unchanged. `make check` is run with the enclosing WP-35 follow-up.
- Findings: PR acceptance confirms delivery only; the documented Gearmulator-only limits and no-hardware claim remain unchanged.
- Blockers: none for WP-04; WP-05 owns the remaining G0 evidence.
- Next action: proceed to WP-05 input provenance and baseline capture after this WP-35 follow-up is delivered.
- Delivery: enclosing commit on `work/wp-35-c10-replay-evidence`.
