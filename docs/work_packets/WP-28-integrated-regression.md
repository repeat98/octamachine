# WP-28 — Assemble the repeatable integration gate

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-20](WP-20-control-surface.md), [WP-21](WP-21-sequencer-and-midi.md), [WP-22](WP-22-sysex-and-transfers.md), [WP-24](WP-24-uw-sampling.md), [WP-25](WP-25-machine-and-effects-parity.md), [WP-26](WP-26-realtime-budget.md), [WP-27](WP-27-faults-and-restarts.md)
- Gate: G3

## Result

Run the complete selected-profile acceptance corpus with public and private inputs kept explicit.

## Scope and starting points

Integrate existing packet scenarios rather than rewriting them. Public CI runs source/synthetic checks; local firmware runs consume user-supplied inputs and return skipped or failed states accurately. Exercise both headless automation and real-time UI/audio where required, and pin the source/patch/profile combination.

## Deliverables

- A documented single integration entry point with result manifest and feature coverage summary.
- `docs/reports/WP-28-integration.md` and public CI wiring for checks that need no proprietary inputs.

## Acceptance checklist

- [ ] The full baseline corpus can be reproduced from documented sources and private-input manifests.
- [ ] Required missing firmware/hardware cannot turn the complete integration gate green; public synthetic success is labeled separately.
- [ ] Failures report the first checkpoint/scenario divergence and preserve ignored diagnostic artifacts.
- [ ] Headless, UI, sequencing, audio, UW, storage, load, and recovery results are tied to the same candidate revision.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Compose the packet runners around one candidate manifest and identify missing coverage before adding new implementation.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
