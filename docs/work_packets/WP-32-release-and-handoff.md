# WP-32 — Prepare a reproducible contributor release

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-28](WP-28-integrated-regression.md), [WP-29](WP-29-image-and-recovery-gate.md), [WP-31](WP-31-hardware-parity.md)
- Gate: G6

## Result

Publish the source/tooling and documented support state needed for another contributor to reproduce the port.

## Scope and starting points

Review source and license provenance from WP-01, current upstream pins/patches, installation/recovery instructions, known issues, and exact supported profiles. Respect upstream distribution restrictions; a local build result is not permission to ship firmware or combined emulator binaries.

## Deliverables

- A source/tooling release checklist, support matrix, migration/recovery notes, and contributor quick start.
- `docs/reports/WP-32-reproduction.md` recording an independent reproduction or the remaining blocker.

## Acceptance checklist

- [ ] A second clean environment or independent contributor reproduces the documented build and applicable acceptance results.
- [ ] All claims name the tested firmware/hardware/profile and remaining fidelity exceptions.
- [ ] Published material excludes private firmware/derived artifacts and follows the recorded source/binary distribution decisions.
- [ ] Status, packet history, upstream patch disposition, and next-work backlog are consistent for a new agent.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Ask the documented workflow to reproduce the exact accepted profile from a clean environment and record where it fails.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
