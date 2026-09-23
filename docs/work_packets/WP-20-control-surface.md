# WP-20 — Map the full control surface and UI

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-18](WP-18-panel-protocol.md), [WP-19](WP-19-integrated-boot.md)
- Gate: G3

## Result

Make baseline Machinedrum operations accessible through the Octatrack panel and emulator UI.

## Scope and starting points

Use the WP-02 feature inventory to map keys, encoder turns/pushes, modifiers, LEDs, display pages, and context-dependent actions. Define any layer/chord and crossfader behavior deliberately. Keep headless scripts and interactive UI tied to the same firmware event path.

## Deliverables

- A complete control/display mapping document and its adapter implementation.
- Reproducible panel walks covering edit, navigation, transport, and representative configuration flows.

## Acceptance checklist

- [ ] Every baseline source control has a reachable target action or an explicit unresolved fidelity exception.
- [ ] Press/release, held modifiers, encoder acceleration, and simultaneous controls are verified where supported.
- [ ] Headless and interactive runs produce corresponding firmware state/display results from equivalent actions.
- [ ] A contributor can complete the documented core workflow using target controls without injecting private internal state.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Inventory currently unreachable controls and implement one coherent edit/navigation flow with its headless replay.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
