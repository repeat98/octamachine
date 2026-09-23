# WP-26 — Measure real-time load and resource limits

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-20](WP-20-control-surface.md), [WP-21](WP-21-sequencer-and-midi.md), [WP-22](WP-22-sysex-and-transfers.md), [WP-23](WP-23-persistent-storage.md), [WP-24](WP-24-uw-sampling.md), [WP-25](WP-25-machine-and-effects-parity.md)
- Gate: G3

## Result

Demonstrate a bounded performance envelope for the complete target profile.

## Scope and starting points

Stress combinations of supported voices, effects, modulation, sample I/O, panel actions, MIDI bursts, and saves. Report guest CPU/DSP cycles, memory high-water marks, queue lengths, deadline misses, and host wall-clock costs separately. Emulator speed alone cannot prove target silicon headroom.

## Deliverables

- A documented load matrix and measured CPU/DSP/memory/I/O budget.
- `docs/reports/WP-26-realtime.md` with reproducible worst-observed cases and uncertainty bounds.

## Acceptance checklist

- [ ] Representative peak combinations have sustained runs under stated durations and inputs.
- [ ] Queue growth, deadlines, latency, jitter, memory use, and failures are measured rather than judged by audibility alone.
- [ ] Optimizations preserve the fidelity corpus and show before/after evidence.
- [ ] Guest requirements are compared with target resource limits; physical performance claims remain gated on WP-31.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Instrument resource counters and run one representative high-load scenario to identify the first limiting resource.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
