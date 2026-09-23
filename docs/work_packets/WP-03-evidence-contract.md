# WP-03 — Define captures, checkpoints, and comparisons

- Status: `ready`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: none
- Gate: G0

## Result

Give all later measurements one reproducible evidence format and an explicit pass/fail rule.

## Scope and starting points

Start from `tests/fixtures/README.md` and the proposed checkpoints in the plan. Define run identity, source hashes, initial state, stimulus timing, clock domains, output metadata, and a first-divergence report. Raw MMIO and DSP boot traces can contain firmware words, so keep payload-bearing captures local and publish reviewed summaries.

## Deliverables

- A versioned capture/manifest contract in `docs/reports/WP-03-evidence.md` and small synthetic text fixtures.
- A validator/comparison entry point for the contract, including clear missing-input, failure, and truncation results.

## Acceptance checklist

- [ ] A run distinguishes cold boot, warm restart, cached initialization, and restored state.
- [ ] Event order, timestamps/units, PC semantics, clock origins, and capped/incomplete traces are unambiguous.
- [ ] Comparisons declare exact fields and justified tolerances before judging results; mismatches identify the first divergence.
- [ ] Synthetic equivalent, divergent, missing, and truncated inputs produce distinct outcomes without requiring firmware.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Draft one minimal manifest and checkpoint record using synthetic data, then establish comparison semantics.
- Waiting on: No packet dependency. Confirm required inputs when claiming the packet.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
