# WP-23 — Map durable firmware state to target storage

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-10](WP-10-architecture-decision.md), [WP-19](WP-19-integrated-boot.md)
- Gate: G3

## Result

Preserve Machinedrum state semantics across saves, reloads, and cold restarts.

## Scope and starting points

Separate source ROM, writable flash, battery-backed state, user samples, and transient runtime caches using the observed behavior. Define target CompactFlash/file layout, versioning, atomic update/recovery strategy, capacity, and error handling. The existing source dump and user projects are immutable inputs.

## Deliverables

- A versioned storage adapter and documented state/container layout.
- `docs/reports/WP-23-storage.md` with save/restart/restore procedures and CP80 evidence.

## Acceptance checklist

- [ ] Baseline kits, patterns, songs, globals, and applicable sample references survive a cold restart with equivalent state.
- [ ] Interrupted saves and full/missing/read-only media have defined outcomes that preserve the last valid state where promised.
- [ ] Format/version mismatches are diagnosed without silently rewriting user input.
- [ ] State snapshots, checksums, and restored startup behavior are reproducible; emulator-only persistence assumptions are explicit.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Trace which source memory regions change during one save and define their target ownership and commit boundary.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
