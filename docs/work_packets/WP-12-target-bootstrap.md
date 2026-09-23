# WP-12 — Reach target reset, vectors, and memory setup

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-05](WP-05-octatrack-baseline.md), [WP-10](WP-10-architecture-decision.md), [WP-11](WP-11-image-transforms.md)
- Gate: G2

## Result

Execute the source firmware's initial path through an approved target bootstrap and reach CP20.

## Scope and starting points

Implement only the chosen load placement, entry handoff, stack/vector setup, and address adaptation in `src/compat/`, `src/image/`, and focused octemu patches. Preserve an unmodified Octatrack baseline profile. Treat CPU-only debug paths as probes until integrated behavior is measured.

## Deliverables

- A reproducible transformed-image load command and bounded target boot probe.
- `docs/reports/WP-12-bootstrap.md` with initial state, memory ownership, and first-divergence evidence.

## Acceptance checklist

- [ ] The source image and transform manifest are identified and the target entry state is explicit.
- [ ] CP10 reset/entry and CP20 memory/vector milestones are observed in the target profile.
- [ ] Source aliases and target cache/memory behavior are validated for the accessed ranges.
- [ ] Unknown accesses or exceptions stop with a useful diagnostic; no fabricated success response hides a boot dependency.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Implement the smallest WP-10 bootstrap and compare its first control-register/memory checkpoint with the reference.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
