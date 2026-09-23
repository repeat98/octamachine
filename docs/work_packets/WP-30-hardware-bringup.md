# WP-30 — Perform controlled hardware bring-up

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-29](WP-29-image-and-recovery-gate.md)
- Gate: G5

## Result

Observe the selected candidate on the exact Octatrack hardware under an approved staged procedure.

## Scope and starting points

Requires the maintainer's explicit authorization for this hardware run and the actual target/recovery setup. Advance from entry and memory diagnostics through interrupts, DSP boot, panel readiness, and a controlled audio stimulus. Use limited stages with stop conditions rather than assuming the complete image works because octemu passed.

## Deliverables

- `docs/reports/WP-30-hardware-bringup.md` with board/candidate identity and staged checkpoint results.
- Locally retained diagnostic captures and reviewed shareable evidence, including restoration outcome.

## Acceptance checklist

- [ ] The physical board, candidate digest, recovery setup, and authorized run scope are recorded.
- [ ] Each attempted checkpoint has observed hardware evidence and an explicit pass/fail/stop result.
- [ ] The run stops at predefined anomalies; successful emulator behavior is not substituted for missing physical measurements.
- [ ] Stock restore/recovery is demonstrated within the approved procedure or the packet remains blocked.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Confirm the exact authorized hardware procedure and recovery prerequisites with the maintainer before any device write.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
