# WP-05 — Capture Octatrack boot in headless and UI modes

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-01](WP-01-source-provenance.md), [WP-02](WP-02-target-profiles.md), [WP-03](WP-03-evidence-contract.md)
- Gate: G0

## Result

Establish a working target-side reference and document emulator limitations before port changes.

## Scope and starting points

Use octemu's `src/board/ot-board.c`, panel/DSP bridges, `src/script.c`, and its setup instructions. Supply the selected Octatrack OS locally, record the optional SDRAM/pacing patch, and isolate card/NVRAM state. Exercise both a scripted headless run and the real-time panel using the same firmware/state profile.

## Deliverables

- `docs/reports/WP-05-ot-baseline.md` with reproducible build/run commands and observed limitations.
- Reviewed boot/panel/audio metadata and a minimal reusable scripted panel walk.

## Acceptance checklist

- [ ] Unmodified target firmware reaches an observed ready state in a bounded headless run.
- [ ] The UI run accepts a known panel action and shows the corresponding firmware response.
- [ ] CPU, DSP, panel, storage, and audio interfaces relevant to the port are located in source and linked to the run profile.
- [ ] Emulator host pacing and known audio artifacts are documented separately from guest timing; no hardware parity is inferred.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Check the Octatrack input profile and run octemu's normal boot procedure with isolated local state.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
