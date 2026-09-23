# WP-14 — Adapt DSP upload and host-port handshakes

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-08](WP-08-dsp-payload-inventory.md), [WP-09](WP-09-dsp-feasibility.md), [WP-12](WP-12-target-bootstrap.md), [WP-13](WP-13-host-peripherals.md)
- Gate: G2

## Result

Transfer both original DSP payloads through the target interfaces and reproduce their boot handshakes.

## Scope and starting points

Use source HI08 transactions and target DSP port/interrupt mechanisms. Define word packing, backpressure, receive/transmit flags, reset sequencing, timeout behavior, and core identity. Validate communication primitives independently before requiring complete audio processing.

## Deliverables

- A source-to-target DSP host bridge and boot-sequence driver.
- `docs/reports/WP-14-dsp-boot.md` and shareable CP40 metadata for both payloads.

## Acceptance checklist

- [ ] Both payload uploads match WP-08 identities after approved transforms and preserve word order.
- [ ] Host and DSP ready/interrupt transitions match the reference sequence or have a documented required adaptation.
- [ ] Backpressure, reset/retry, and a stalled DSP return finite, diagnosable outcomes.
- [ ] CP40 confirms upload/acknowledgement only; execution and audio remain separate acceptance gates.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Replay the first DSP reset/upload transaction through a minimal target bridge with explicit acknowledgement checks.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
