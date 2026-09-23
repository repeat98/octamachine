# WP-18 — Bridge panel startup and event transport

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-07](WP-07-memory-and-mmio.md), [WP-12](WP-12-target-bootstrap.md), [WP-13](WP-13-host-peripherals.md)
- Gate: G2

## Result

Let the actual firmware complete its panel handshake and exchange display/control events.

## Scope and starting points

Use `mdpanel.*`, `mdfrontpanel.*`, octemu's panel UART/wire code, and octabam panel notes. First establish a protocol bridge for startup, display writes, LEDs, button edges, and encoder deltas. Full physical control assignment and UI usability belong to WP-20.

## Deliverables

- A panel protocol adapter and deterministic synthetic panel-event fixtures.
- `docs/reports/WP-18-panel-protocol.md` with handshake and display/control timing evidence.

## Acceptance checklist

- [ ] Firmware startup receives the measured panel responses through a physical-target-capable mechanism.
- [ ] Known button/encoder events arrive with correct press/release, ordering, and timing semantics.
- [ ] LCD/LED messages are decoded or forwarded with a documented target rendering path.
- [ ] Missing, delayed, or malformed panel traffic has bounded behavior and a diagnostic.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Capture the reference panel startup exchange and reproduce only that handshake in the target profile.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
