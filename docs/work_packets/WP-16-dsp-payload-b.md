# WP-16 — Run original DSP payload B

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-10](WP-10-architecture-decision.md), [WP-14](WP-14-dsp-host-bridge.md)
- Gate: G2

## Result

Execute payload B with the target layout and verify its first observable program behavior.

## Scope and starting points

Payload B is the other source DSP identity fixed in WP-08. Share the boot/trace contract with WP-15, and isolate file ownership so both packets can run independently. Synthetic peer inputs are allowed as identified probes and must not be presented as complete two-DSP operation.

## Deliverables

- Payload B layout/transform metadata and minimal DSP adapters under `src/dsp/`.
- `docs/reports/WP-16-dsp-b.md` with trace/state/output comparisons and cycle/memory use.

## Acceptance checklist

- [ ] Original payload B reaches its measured entry and processing checkpoints with all transformations listed.
- [ ] Critical fixed-point arithmetic, addressing, interrupt, and memory behavior matches the declared comparison contract.
- [ ] Controlled inputs produce the expected state or output blocks with justified tolerances.
- [ ] Memory/cycle use and dependencies on payload A are explicit; synthetic peer behavior is labeled.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Load payload B at its approved target location and compare its first host-visible program checkpoint.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
