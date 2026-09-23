# WP-27 — Exercise faults, restarts, and state recovery

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-23](WP-23-persistent-storage.md), [WP-26](WP-26-realtime-budget.md)
- Gate: G3

## Result

Make failure and recovery behavior observable before building a hardware candidate.

## Scope and starting points

Inject isolated firmware/device faults, stalled host/DSP links, missing media, interrupted persistence, bad state versions, and repeated reset sequences. Use synthetic fixtures and disposable local state. Compare reference behavior where meaningful and document intentional fail-safe differences.

## Deliverables

- A bounded fault/restart scenario suite with retained diagnostic metadata.
- `docs/reports/WP-27-recovery.md` with failure classification and last-valid-state recovery evidence.

## Acceptance checklist

- [ ] Each injected failure produces a finite observable outcome or a bounded timeout with context.
- [ ] Failed writes/restarts preserve the promised durable state and never modify the source image.
- [ ] Host/DSP/panel resets cannot leave hidden stale state that passes the next boot spuriously.
- [ ] Each recovery limitation has an owner, reproduction, and explicit effect on the hardware-readiness gate.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Interrupt one disposable save/restart sequence and verify recovery against the last known valid state.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
