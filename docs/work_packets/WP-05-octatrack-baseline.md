# WP-05 — Capture Octatrack boot in headless and UI modes

- Status: `in_review`
- Owner: Codex
- Branch: `work/wp-05-octatrack-baseline`
- Updated: 2026-09-24
- Depends on: [WP-01](WP-01-source-provenance.md), [WP-02](WP-02-target-profiles.md), [WP-03](WP-03-evidence-contract.md)
- Gate: G0
- Accepted delivery: pending review

## Result

Establish a working target-side reference and document emulator limitations before port changes.

## Scope and starting points

Use octemu's `src/board/ot-board.c`, panel/DSP bridges, `src/script.c`, and its setup instructions. Supply the selected Octatrack OS locally, record the optional SDRAM/pacing patch, and isolate card/NVRAM state. Exercise both a scripted headless run and the real-time panel using the same firmware/state profile.

## Deliverables

- `docs/reports/WP-05-ot-baseline.md` with reproducible build/run commands and observed limitations.
- Reviewed boot/panel/audio metadata and a minimal reusable scripted panel walk.

## Acceptance checklist

- [x] Unmodified target firmware reaches the `PTCH` project screen in a bounded headless run and remains there through the scripted guest-time dwell; see the [headless run metadata](../reports/WP-05-ot-headless-v1.manifest.json).
- [x] A windowed UI run accepts PLAY and STOP and observes a lit panel lamp; before/after panel screenshots were inspected locally; see the [UI run metadata](../reports/WP-05-ot-ui-v1.manifest.json).
- [x] CPU, DSP, panel, storage, and audio interfaces are located in octemu/QEMU source and linked to the target run profile in the [report](../reports/WP-05-ot-baseline.md#source-map-for-the-run-profile).
- [x] Host pacing, guest audio-block timing, and the live monitor artifact are distinguished in the report; no hardware parity is inferred.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: Verified octemu's pinned OS 1.40C archive; built the pinned emulator; booted the unchanged image to `PTCH` headless and windowed; verified PLAY/lamp/STOP response in each; recorded versioned metadata and source mapping.
- Remaining: PR review, required checks, and merge reconciliation.
- Next action: Merge PR #11 after the required checks pass, then reconcile the accepted delivery.
- Waiting on: PR merge reconciliation.
- Blockers: none.
- Evidence: [WP-05 report](../reports/WP-05-ot-baseline.md), headless [manifest](../reports/WP-05-ot-headless-v1.manifest.json) and [events](../reports/WP-05-ot-headless-v1.events.jsonl), windowed [manifest](../reports/WP-05-ot-ui-v1.manifest.json) and [events](../reports/WP-05-ot-ui-v1.events.jsonl); reusable walks in `tests/walks/`.
- Delivery: [PR #11](https://github.com/repeat98/octamachine/pull/11) open on `work/wp-05-octatrack-baseline`; required checks have passed for `cc88ceeeeff31f91bb4797f0a335ac9465271d57`.

## Prompt history

### 2026-09-23 / prompt 1 — establish the Octatrack baseline

- Request: continue the Octatrack port overnight and complete the next eligible baseline packet.
- Starting state → ending state: `waiting` → `in_review`; WP-01 through WP-04 and WP-35 were reconciled as accepted prerequisites.
- Owner / branch: Codex / `work/wp-05-octatrack-baseline`.
- Completed:
  - [x] Reacquired the official OS 1.40C distribution archive and verified its pinned SHA-256 before extracting the 1,112,560-byte main image.
  - [x] Built the pinned octemu board, DSP model, frontend, and panel assets; generated a local FX2 project fixture.
  - [x] Ran unmodified OS 1.40C in bounded headless and windowed modes from independent copies of the same card/NVRAM fixture. Both observed `PTCH`, dismissed the loading overlay, verified the PLAY lamp condition, accepted STOP, and exited successfully.
  - [x] Added reusable scripted walks, redacted WP-03 v1 manifests/events, the source map, and the guest/host timing and audio limitations.
- Remaining:
  - [ ] Merge PR #11 and reconcile the accepted delivery.
- Changed files: this packet; `docs/reports/WP-05-ot-baseline.md`; four WP-03 metadata files; two `tests/walks/wp05-*.jsonl` files; `docs/STATUS.md`, `docs/RESEARCH_LOG.md`, and `docs/COMPATIBILITY_MATRIX.md`; WP-35 merge reconciliation.
- Verification:
  - `make -C vendor/octemu doctor`, `setup`, `os`, `JOBS=8 make -C vendor/octemu qemu`, `make -C vendor/octemu`, and `make -C vendor/octemu fixtures` — passed; archive digest matched octemu's pin.
  - Headless run at 2026-09-23 21:44:08 UTC — exit 0; `PTCH`, loading text absent, lamp condition lit, STOP accepted; final mark at block 64,888.
  - Windowed run at 2026-09-23 21:44:49 UTC — exit 0; same screen/input result; before/after PPM captures saved locally; final mark at block 64,274.
  - An earlier no-card run reached `C0MPACT` under 90 seconds; it is supplementary and not counted as the `PTCH` checkpoint.
  - The optional GIF attempt failed after the installed ffmpeg could not load its local x265 dylib; built-in panel screenshots succeeded without ffmpeg.
  - `make check` — passed; nine reference repositories validated, scripts compiled, and all 20 tests passed.
  - PR #11 workflow run `35927460970` — required `scaffold` job passed for `cc88ceeeeff31f91bb4797f0a335ac9465271d57`.
  - `git diff --cached --check` and WP-03 manifest/event validation — passed for both v1 runs; 8 headless and 9 windowed records are complete.
  - The first sandboxed emulator attempt could not open its local panel socket; rerunning the bounded walks with required local IPC access succeeded. The initial fixture retry used stale partial ignored output from that attempt; deleting only those local outputs and rerunning `make fixtures` succeeded.
  - The first `make setup` attempt encountered the root checkout's pre-existing symlink to a dirty shared firmware-tool checkout and stopped before modifying it; setup was rerun with an isolated tool checkout and passed.
- Findings: See the [WP-05 report](../reports/WP-05-ot-baseline.md). The successful UI run reported monitor ratio `0.8420–1.0000`, 298 cents, and 90,181 starved frames. That is a host live-monitor artifact, not guest timing or audio-parity evidence. The optional GIF attempt failed on a missing local x265 dylib; the built-in PPM screenshots were captured and inspected. No physical Octatrack or Machinedrum firmware was run.
- Blockers: none.
- Next action: merge PR #11, then reconcile the accepted delivery.
- Delivery: [PR #11](https://github.com/repeat98/octamachine/pull/11) open; head commit `cc88ceeeeff31f91bb4797f0a335ac9465271d57`.
