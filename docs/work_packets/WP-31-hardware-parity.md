# WP-31 — Compare hardware sound, timing, state, and endurance

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-30](WP-30-hardware-bringup.md)
- Gate: G5

## Result

Validate actual hardware behavior against the same baseline corpus used in emulation.

## Scope and starting points

Use controlled MIDI/panel stimuli, capture paths with known gain/clock properties, and disposable project data. Repeat feature, storage, restart, and peak-load cases from WP-28. Separate analog/capture-chain effects from digital mismatches and keep raw user captures local.

## Deliverables

- `docs/reports/WP-31-hardware-parity.md` and hardware feature/performance coverage tables.
- Measured tolerances, run durations, failure cases, and any remaining scope-limited fidelity exceptions.

## Acceptance checklist

- [ ] Core sound/behavior scenarios meet their predeclared hardware comparison criteria.
- [ ] Clocking, jitter, latency, sustained load, and resource limits are measured on the selected physical revision.
- [ ] State survives cold restart and approved interrupted-I/O/recovery cases on disposable data.
- [ ] Every baseline feature is passed, explicitly limited, or still blocking; results do not imply support for untested revisions.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Calibrate the hardware capture path and replay one previously passing emulation scenario before starting the broader corpus.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
