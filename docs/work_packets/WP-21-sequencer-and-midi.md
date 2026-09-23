# WP-21 — Preserve sequencer and real-time MIDI behavior

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-19](WP-19-integrated-boot.md)
- Gate: G3

## Result

Compare musical scheduling and external synchronization using the actual firmware.

## Scope and starting points

Exercise the baseline feature inventory: patterns, kits, locks, LFO/state changes, song/transport behavior, tempo/swing, and MIDI machines where supported. Compare internal scheduling and external MIDI clock/start/stop/continue on explicit timelines, including resets and parameter changes.

## Deliverables

- A deterministic sequencing/MIDI scenario catalog and any required interface adaptation.
- `docs/reports/WP-21-sequencer-midi.md` with event timing and state comparisons.

## Acceptance checklist

- [ ] Representative state transitions produce the expected firmware events and parameter state.
- [ ] Internal tempo and external clock paths have measured latency/jitter/drift against the declared tolerances.
- [ ] Input/output ordering, running status where relevant, burst traffic, and stopped/continued transport are covered.
- [ ] No host reimplementation of sequencer logic is used to disguise an original-firmware divergence.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Replay one simple timed pattern under internal clock and compare event/state timing with the reference.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
