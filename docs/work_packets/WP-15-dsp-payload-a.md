# WP-15 — Run original DSP payload A

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-10](WP-10-architecture-decision.md), [WP-14](WP-14-dsp-host-bridge.md)
- Gate: G2

## Result

Execute payload A with the target layout and verify its first observable program behavior.

## Scope and starting points

Payload A is the source DSP identity fixed in WP-08; WP-10 chooses its target core. Adapt only the proven instruction, P/X/Y, peripheral, or relocation differences. Use controlled host/serial input so this packet can proceed independently of payload B integration.

## Deliverables

- Payload A layout/transform metadata and minimal DSP adapters under `src/dsp/`.
- `docs/reports/WP-15-dsp-a.md` with trace/state/output comparisons and cycle/memory use.

## Acceptance checklist

- [ ] Original payload A reaches its measured entry and processing checkpoints with all transformations listed.
- [ ] Critical fixed-point arithmetic, addressing, interrupt, and memory behavior matches the declared comparison contract.
- [ ] Controlled inputs produce the expected state or output blocks with justified tolerances.
- [ ] Memory and cycle headroom are measured; a silent or idle loop alone is not accepted as functional payload execution.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Load payload A at its approved target location and compare its first host-visible program checkpoint.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
