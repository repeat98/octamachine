# WP-06 — Audit ColdFire execution compatibility

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-04](WP-04-machinedrum-baseline.md), [WP-05](WP-05-octatrack-baseline.md)
- Gate: G1

## Result

Identify which observed Machinedrum CPU operations can execute on the target and which require adaptation.

## Scope and starting points

Compare executed startup and representative runtime instructions, control registers, exception frames, privilege transitions, alignment, byte order, atomics, cache behavior, and self-modifying code if observed. Use the pinned mc68k/QEMU implementations and primary processor manuals. Do not treat an all-bytes disassembly as proof of executed instruction coverage.

## Deliverables

- `docs/reports/WP-06-coldfire.md` mapping observed CPU requirements to target capabilities.
- Minimal independently authored instruction/exception probes and a list of unobserved paths.

## Acceptance checklist

- [ ] Each observed incompatibility has an instruction/control-state example and a reproducible probe or reference trace.
- [ ] Reset, vector setup, exception return, interrupt masking, and stack semantics are compared.
- [ ] Any proposed trap, relocation, or patch mechanism is checked against actual target facilities and privilege constraints.
- [ ] The report distinguishes direct execution, bounded adaptation, unresolved behavior, and an identified blocker.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Use the reference startup trace to inventory the first control-register and exception operations and probe those on the target CPU model.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result. Prior evidence from the octamad Machinedrum excursion: the MD MAIN OS startup (link address `0x200000`, SP `0x300000`, the 2,466-byte SRAM copy, entry `0x213a0c`), and a static census of the 44 engine handlers: pure ISA_A functions with no MAC/EMAC, hardware access or calls (section "ColdFire side") ([WP-35 report](../reports/WP-35-octamad-md-import.md)). It is Gearmulator-only, predates the WP-03 contract, and checks no item here.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).

2026-09-23: [WP-35](WP-35-octamad-md-import.md) linked prior evidence in the current handoff. That was not a work prompt on this packet, and it changed no status or checklist item.
