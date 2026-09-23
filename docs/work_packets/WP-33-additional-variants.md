# WP-33 — Extend to another firmware or hardware variant

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-32](WP-32-release-and-handoff.md)
- Gate: Optional

## Result

Evaluate one additional profile without weakening the accepted baseline.

## Scope and starting points

Select one new source OS/model or target hardware revision with maintainer agreement. Re-run identity, CPU/DSP/resource, behavior, packaging, and recovery gates for the changed boundary. Do not group several unmeasured variants under one compatibility claim.

## Deliverables

- A new explicit profile, scoped transformation changes, and variant-specific evidence.
- An updated support matrix showing baseline results and the new variant independently.

## Acceptance checklist

- [ ] The selected variant and changed boundaries are identified before implementation.
- [ ] Existing baseline regression remains passing while the new profile gets its own evidence and tolerances.
- [ ] Hardware and recovery claims are restricted to the physically tested variant.
- [ ] Any reused evidence has a written justification; unmeasured equivalence is not marked complete.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Choose one requested variant and enumerate which earlier gates must be repeated.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
