# WP-29 — Package a local candidate and rehearse recovery

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-11](WP-11-image-transforms.md), [WP-28](WP-28-integrated-regression.md)
- Gate: G4

## Result

Prepare a reproducible local image candidate and a concrete hardware recovery procedure.

## Scope and starting points

Use the WP-10 boot strategy and the selected board profile. Check container layout, loader expectations, placement, reserved regions, checksums, and how stock operation is restored. Follow primary/device-specific recovery instructions; do not infer an unbrick path from successful emulation.

## Deliverables

- A local-only candidate builder/validator and manifest; no derived image is distributed.
- `docs/reports/WP-29-hardware-readiness.md` with recovery steps, prerequisites, candidate identity, and go/no-go checklist.

## Acceptance checklist

- [ ] Identical approved inputs produce the same candidate and pass structural/load checks in the target emulator profile.
- [ ] Stock recovery assets and exact physical access requirements are identified for the selected hardware revision.
- [ ] The recovery procedure is rehearsed to the extent possible without flashing and its unproven steps are explicit.
- [ ] The hardware run scope, stop conditions, backups, and maintainer authorization requirement are recorded before WP-30.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Audit the chosen boot/container path and write a candidate-specific recovery plan before producing a flashable artifact.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
