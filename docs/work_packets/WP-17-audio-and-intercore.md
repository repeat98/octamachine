# WP-17 — Connect DSPs, serial audio, and target routing

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-15](WP-15-dsp-payload-a.md), [WP-16](WP-16-dsp-payload-b.md)
- Gate: G2

## Result

Run the original payloads together through a concrete target audio path.

## Scope and starting points

Map source DSP-to-DSP traffic, host messages, serial slots, frame clocks, sample packing, and target input/output channels. Resolve sample-rate differences from measured configurations. Any resampling, channel reduction, or timing change is a fidelity deviation that needs an explicit decision.

## Deliverables

- DSP interconnect and audio routing adapters with a documented clock/channel diagram.
- `docs/reports/WP-17-audio-path.md` with CP50 evidence, latency, and underflow/overflow observations.

## Acceptance checklist

- [ ] Both original payloads exchange live data and advance on the declared guest clock relationship.
- [ ] Known channel/impulse stimuli establish sign, word packing, frame alignment, gain, and channel routing.
- [ ] CP50 is reached with bounded queues and no unexplained sample drops, repeats, or drift.
- [ ] The physical target mechanism and measured resource cost are documented for every serial/host bridge.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Connect the smallest measured source DSP-to-DSP stream and observe its framing before enabling the full output path.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result. Prior evidence from the octamad Machinedrum excursion: the producer→mixer ESSI0 stream carries 16 words per sample in 512-word periods (32 samples × 16 voices, voice-major). The voice DSP paces itself on port C frame sync and the mixer on a DMA poll ([WP-35 report](../reports/WP-35-octamad-md-import.md)). It is Gearmulator-only, predates the WP-03 contract, and checks no item here.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).

2026-09-23: [WP-35](WP-35-octamad-md-import.md) linked prior evidence in the current handoff. That was not a work prompt on this packet, and it changed no status or checklist item.
