# WP-24 — Preserve UW sampling and audio-input behavior

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-17](WP-17-audio-and-intercore.md), [WP-20](WP-20-control-surface.md), [WP-23](WP-23-persistent-storage.md)
- Gate: G3

## Result

Run the baseline UW record/playback paths through target inputs, memory, and storage.

## Scope and starting points

Use the original firmware's sampling machines and WP-02 inventory. Measure sample packing, record/playback addressing, input routing, resampling where supported, memory/capacity limits, and state references. Synthetic locally generated audio is preferred for repeatable stimuli.

## Deliverables

- Required input/sample-memory adapters and a UW capture/playback scenario set.
- `docs/reports/WP-24-uw.md` with sample-state, audio, and boundary comparisons.

## Acceptance checklist

- [ ] Supported record/playback flows run through original firmware and reproduce sample content within declared tolerances.
- [ ] Memory boundaries, sample end/loop behavior, routing, and gain are verified for the selected baseline.
- [ ] Samples and their kit/project references persist and restore through WP-23 without aliasing or corruption.
- [ ] Concurrent sampling, playback, and edits remain bounded and any target-specific capacity change is documented.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Run one controlled input waveform through the smallest baseline record/playback flow and compare the resulting sample metadata and output.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
