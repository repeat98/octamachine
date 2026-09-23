# WP-07 — Reconcile memory, MMIO, and clock contracts

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-04](WP-04-machinedrum-baseline.md), [WP-05](WP-05-octatrack-baseline.md)
- Gate: G1

## Result

Produce one evidence-backed register and address contract for source and target hardware.

## Scope and starting points

Investigate the documented DSP address, SRAM-size, and CPU-clock disagreements. Inventory mapped ranges, aliases, bus widths, flash commands, reset values, interrupt routes, timers, UARTs, and DMA where used. Clock claims need units, divisors, and a primary-source or measured basis.

## Deliverables

- `docs/reports/WP-07-memory-mmio.md` with source/target address and register tables.
- Trace summaries and focused probes for disputed ranges, access widths, and clock relationships.

## Acceptance checklist

- [ ] The known DSP-window, SRAM-size, and clock discrepancies are resolved or bounded with explicit remaining measurements.
- [ ] Every peripheral touched up to the reference idle checkpoint has a proposed target-side owner and access semantics.
- [ ] Mapping plans address alias coherence, executable/writable placement, stack/vector storage, and overlapping regions.
- [ ] A PC-side fake register or RAM window is labeled as reference instrumentation unless a physical target mechanism is demonstrated.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Classify the first reference MMIO transactions against both source maps and the Octatrack board model.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result. Prior evidence from the octamad Machinedrum excursion: the firmware's SRAM interrupt handlers access `0x600004`, which supports Gearmulator's `0x500000/0x600000` HI08 map; the SRAM structures located so far end near `0x01001af4`, which is consistent with 8 KiB but is not an access census; the reference model clocks each MD DSP at 101.6064 MHz (sections "DSP identities", "ColdFire side") ([WP-35 report](../reports/WP-35-octamad-md-import.md)). It is Gearmulator-only, predates the WP-03 contract, and checks no item here.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).

2026-09-23: [WP-35](WP-35-octamad-md-import.md) linked prior evidence in the current handoff. That was not a work prompt on this packet, and it changed no status or checklist item.
