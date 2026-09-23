# WP-09 — Assess DSP instruction and resource fit

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-05](WP-05-octatrack-baseline.md), [WP-08](WP-08-dsp-payload-inventory.md)
- Gate: G1

## Result

Decide whether the original DSP payloads have a plausible execution path on the selected target cores.

## Scope and starting points

Compare observed instructions, fixed-point arithmetic, saturation/rounding, P/X/Y spaces, external-memory timing, interrupts, host ports, serial audio, and cross-core communication. Use octemu's DSP model and primary DSP manuals, and separate emulator support from documented silicon behavior.

## Deliverables

- `docs/reports/WP-09-dsp-fit.md` with per-payload compatibility and memory/cycle budgets.
- Small synthetic probes for critical opcode, memory, interrupt, and serial-interface differences.

## Acceptance checklist

- [ ] Each payload's memory/overlay needs fit a concrete proposed layout or has an explicit allocation blocker.
- [ ] Arithmetic and instruction differences are backed by probes or primary documentation.
- [ ] Host/serial interfaces and shared resources have an evidenced mapping with an initial timing budget, or a quantified blocker for WP-10.
- [ ] Unverified hardware assumptions and any payload patch requirements are listed before integration is approved.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Start from the WP-35 resource table and measure what it leaves open: the mixer's data footprint and relocation, whether the sine is written after boot, and DSP5636x timing of one relocated engine.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result. Prior evidence from the octamad Machinedrum excursion: a resource table for the voice DSP (code 15.6 K, tables 23–28 K, a 32 K sine read as both X and Y, P-I buffers up to 24.6 K, E12 samples 201.8 K words). Both programs execute from external RAM, and the DSP56721 has none. Reference-model work is ~1,650 (voice DSP) and ~1,850 (mixer) cycles per sample, and program fetch from the shared window adds ~80 % ([WP-35 report](../reports/WP-35-octamad-md-import.md)). It is Gearmulator-only, predates the WP-03 contract, and checks no item here.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).

2026-09-23: [WP-35](WP-35-octamad-md-import.md) linked prior evidence in the current handoff. That was not a work prompt on this packet, and it changed no status or checklist item.
