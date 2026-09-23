# WP-25 — Compare machine families and effects

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-17](WP-17-audio-and-intercore.md), [WP-19](WP-19-integrated-boot.md), [WP-21](WP-21-sequencer-and-midi.md)
- Gate: G3

## Result

Establish an auditable sound/behavior comparison for every baseline machine and effect family.

## Scope and starting points

Create a feature-based corpus from WP-02, then split family coverage into child packets if necessary. Cover representative parameter values, extremes, retriggers, modulation, locks, effects routing, and silence/tail behavior. Compare known non-UW synthesis paths here; WP-24 supplies UW coverage for the combined gate.

## Deliverables

- Text scenario metadata and a coverage table keyed to baseline machine/effect families.
- `docs/reports/WP-25-sound-parity.md` with exact comparisons or justified audio tolerances and mismatch analysis.

## Acceptance checklist

- [ ] Every baseline non-UW machine/effect family is covered; individually listed unresolved gaps keep this criterion and G3 open unless the maintainer approves a scope decision.
- [ ] A deterministic stimulus and reference identity can reproduce each comparison.
- [ ] Differences are localized to arithmetic, scheduling, routing, or another evidenced boundary rather than hidden by a loose threshold.
- [ ] Silence, clipping, unstable output, tails, and parameter/state continuity are included in the acceptance corpus.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Select one representative machine family, declare its comparison contract, and establish the first repeatable audio/state result.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
