# WP-13 — Adapt host interrupts, timers, and essential peripherals

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-07](WP-07-memory-and-mmio.md), [WP-12](WP-12-target-bootstrap.md)
- Gate: G2

## Result

Provide the host services needed for forward progress with measured timing and exception behavior.

## Scope and starting points

Map the observed SIM, timer, interrupt, UART, watchdog, and DMA dependencies through mechanisms approved in WP-10. Use independently authored probes before full firmware integration. Do not require the complete firmware scheduler to be running to validate these primitives.

## Deliverables

- Focused host-side adapters under `src/compat/` and target emulator support patches where justified.
- `docs/reports/WP-13-host-peripherals.md` with register semantics, interrupt routing, and timing comparisons.

## Acceptance checklist

- [ ] Required register widths, reset values, acknowledgements, and interrupt priorities match the source contract.
- [ ] Timer/interrupt probes reach CP30 and show bounded service latency in guest clock units.
- [ ] Masked, pending, repeated, and nested events behave as required by the observed source paths.
- [ ] Each adapter is implementable on the physical target; remaining unused/unmapped registers stay explicit.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Implement and probe the earliest timer/interrupt dependency that blocks the WP-12 boot path.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
