# WP-04 — Capture the Machinedrum reference boot

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-01](WP-01-source-provenance.md), [WP-02](WP-02-target-profiles.md), [WP-03](WP-03-evidence-contract.md)
- Gate: G0

## Result

Reproduce a real firmware cold boot in Gearmulator and establish the reference checkpoints.

## Scope and starting points

Use `mdLib/mdmc.cpp`, `mdhardware.cpp`, `mddevice.cpp`, `mdsim.cpp`, the ROM loader, and the existing bus trace patch. Add or use a bounded headless driver with explicit local firmware/state paths. Account for factory caches, initial RAM/flash, polling loops, trace caps, and the difference between current and executing PC. Limit the capture to one machine instance per run unless the format identifies instances.

## Deliverables

- A documented headless boot/capture command and minimal integration code or upstream patch.
- `docs/reports/WP-04-md-baseline.md` plus reviewed checkpoint metadata; full traces stay ignored.

## Acceptance checklist

- [ ] The pinned local image reaches named reference initialization and idle checkpoints under a finite timeout.
- [ ] Repeated cold boots from the same explicit state have explainable event ordering; warm/cached starts are labeled separately.
- [ ] Reset, SIM setup, both DSP boot streams, panel startup, and scheduler evidence are captured; missing evidence is individually listed and keeps this criterion open.
- [ ] A cap, missing firmware, or stalled boot fails or reports incomplete evidence instead of silently passing.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Inspect Gearmulator's existing headless entry points and factory-state initialization, then run one bounded cold boot.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
