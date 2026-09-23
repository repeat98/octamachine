# WP-19 — Reach complete firmware idle and transport startup

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-13](WP-13-host-peripherals.md), [WP-14](WP-14-dsp-host-bridge.md), [WP-17](WP-17-audio-and-intercore.md), [WP-18](WP-18-panel-protocol.md)
- Gate: G3

## Result

Boot the CPU and both DSP payloads together to a usable firmware state in octemu.

## Scope and starting points

Integrate the measured primitives using explicit throwaway initial state. Follow the original firmware through scheduler startup and idle responsiveness; eliminate temporary bootstrap stand-ins that substitute for firmware behavior. Storage durability and complete control mapping remain separate packets.

## Deliverables

- One bounded integrated boot command/script for the selected profile.
- `docs/reports/WP-19-integrated-boot.md` with CP60/CP70 traces and remaining compatibility gaps.

## Acceptance checklist

- [ ] A reproducible cold boot reaches firmware-ready panel state and sustained scheduler/interrupt activity.
- [ ] The original firmware reacts to a defined transport/stimulus sequence and reaches CP70.
- [ ] Every remaining stub, patch, unsupported register, and provisional hardware assumption is inventoried.
- [ ] Repeated fresh-state boots terminate or report failures predictably; timeouts cannot count as successful boot.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Run the combined target profile and resolve its earliest divergence from the reference checkpoint sequence.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
