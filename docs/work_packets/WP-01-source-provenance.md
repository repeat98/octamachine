# WP-01 — Reproduce source and dependency provenance

- Status: `ready`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: none
- Gate: G0

## Result

Provide a clean, reproducible source baseline whose results can be compared across contributors.

## Scope and starting points

Start with `references.json`, `scripts/references.py`, `patches/`, and both emulators' build instructions. Record recursive submodule commits and local modifications, including nested DSP sources. Preserve existing research checkouts; use a clean separate build where needed. Inspect license notices, including octemu's stated restriction on distributing its combined binaries.

## Deliverables

- `docs/reports/WP-01-provenance.md` with exact source/dependency/toolchain versions and license/provenance inventory.
- Reproducible setup/build instructions or a focused setup-script correction, with local build outputs ignored.

## Acceptance checklist

- [ ] Root, emulator, recursive dependency, and patch revisions are recorded; dirty source state is disclosed.
- [ ] The trace patch applies to a clean pinned Gearmulator checkout and its relevant library builds.
- [ ] Octemu prerequisites and supported host assumptions are recorded; unavailable prerequisites are explicit.
- [ ] Contribution-source permissions and binary distribution restrictions are inventoried without inventing a license grant.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Compare `references.json` with each checkout and its recursive submodules; identify the first clean build configuration.
- Waiting on: No packet dependency. Confirm required inputs when claiming the packet.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
