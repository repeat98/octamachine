# WP-10 — Choose a hardware-realizable port architecture

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-06](WP-06-coldfire-compatibility.md), [WP-07](WP-07-memory-and-mmio.md), [WP-09](WP-09-dsp-feasibility.md)
- Gate: G1

## Result

Select a justified path for running the actual firmware on Octatrack and record a go/no-go decision.

## Scope and starting points

Evaluate an independent boot path and an Octatrack OS carrier using octabam's tooling. For every compatibility mechanism state where it executes, how memory/register accesses reach it, privilege requirements, interrupt latency, resource ownership, and recovery implications. The PC may emulate the source board for comparison; adding source-only devices to octemu does not establish a target port.

## Deliverables

- `docs/decisions/WP-10-port-architecture.md` with alternatives, chosen boundaries, rejected assumptions, and unresolved gates.
- A concrete CPU/DSP/memory/peripheral ownership diagram and a minimal next-checkpoint experiment.
- An adaptation ledger in the decision record: original behavior, measured constraint, proposed change, affected interface/range, and required regression evidence for every exception.

## Acceptance checklist

- [ ] CPU code, both original DSP payloads, interrupts, I/O, and storage each have a target-realizable ownership path or an evidenced blocker supporting a no-go decision.
- [ ] Direct execution, relocation, instruction patches, peripheral adaptation, and any emulation cost are separately budgeted; unresolved bounds explicitly constrain the decision.
- [ ] Carrier reservations, target memory ownership, and an independent boot/recovery path are compared using evidence.
- [ ] The decision is go, conditional-go, or no-go with explicit reasons; a scope reduction requires maintainer agreement. Only go, or conditional-go after its prerequisites pass, clears G1 for dependent implementation.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Summarize the first hard constraints from WP-06/07/09 and test the most doubtful compatibility mechanism before committing to an architecture.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
