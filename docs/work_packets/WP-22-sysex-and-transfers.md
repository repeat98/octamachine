# WP-22 — Preserve SysEx, configuration, and bulk transfers

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-21](WP-21-sequencer-and-midi.md)
- Gate: G3

## Result

Transfer baseline firmware state and data through its original supported MIDI protocols.

## Scope and starting points

Inventory actual supported commands before implementation, including kit/pattern/song/configuration transfers and UW sample transfer or faster MIDI modes where present. Bound lengths, timeouts, and buffers. Store user data privately and publish synthetic protocol fixtures or summaries.

## Deliverables

- MIDI/SysEx bridge corrections and a protocol scenario matrix.
- `docs/reports/WP-22-transfers.md` with round-trip, cancellation, and malformed-input results.

## Acceptance checklist

- [ ] Supported state transfers round-trip with equivalent decoded firmware state.
- [ ] Incomplete, oversized, malformed, cancelled, and repeated messages cannot corrupt unrelated state.
- [ ] Bulk transfer respects sequencer/audio timing or exposes a measured baseline-equivalent interruption.
- [ ] Each optional protocol is marked implemented, unsupported by the chosen baseline, or explicitly deferred with a fidelity impact.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Enumerate the baseline transfer commands and capture a minimal configuration round trip.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
