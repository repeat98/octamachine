# WP-11 — Build a reversible local image transformation pipeline

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-10](WP-10-architecture-decision.md)
- Gate: G2

## Result

Apply only the transformations approved by the architecture decision and make each change auditable.

## Scope and starting points

Use `src/image/` and the existing auditor. Design source identity checks, range digests, relocations, linker placements, ordered patch manifests, overlap detection, and deterministic output. Store original/replacement firmware bytes locally; share metadata and transformation code only where provenance permits.

## Deliverables

- A local-only transformation entry point with dry-run/report mode and synthetic fixtures.
- `docs/reports/WP-11-image-transforms.md` documenting the manifest, invariants, and rollback procedure.

## Acceptance checklist

- [ ] Unsupported source identities and unexpected bytes/range digests fail before output is written.
- [ ] Reports identify every changed range and reason; overlapping or out-of-bounds writes fail.
- [ ] Equivalent inputs produce identical outputs and the approved inverse/restore path reproduces the source digest.
- [ ] Source dumps remain immutable, output stays ignored, and no flash command is coupled to image generation.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Define the smallest manifest entry needed by WP-10 and implement its invariants on a synthetic image.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
