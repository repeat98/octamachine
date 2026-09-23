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
- Next action: Build a per-payload resource table from WP-08 and compare its largest memory and peripheral requirements with the target.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
