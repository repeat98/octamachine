# WP-02 — Define firmware and target hardware profiles

- Status: `ready`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: none
- Gate: G0

## Result

Fix the exact source firmware and target profile against which 1:1 compatibility will be judged.

## Scope and starting points

Use the image auditor and `docs/BOOT_FEASIBILITY.md`. The local MD UW OS 1.63 dump is an initial input, not support for every Machinedrum variant. Identify Octatrack revision and OS/carrier inputs where relevant; mark an emulator-only profile provisional until physical hardware is identified. Inventory baseline firmware features from its documentation and observed behavior.

## Deliverables

- `docs/reports/WP-02-target-profile.md` and shareable profile metadata under `tests/fixtures/`.
- A feature inventory covering boot, machines, sequencer, panel, MIDI, UW sampling, and persistence for the selected baseline.

## Acceptance checklist

- [ ] Source model/revision, file/container format, size, and fingerprints are reproducibly identified.
- [ ] Target model/revision and carrier requirements are identified, or the profile is explicitly provisional with the physical hardware gate closed.
- [ ] Supported baseline features and deferred variants are enumerated with evidence sources.
- [ ] Missing local firmware/hardware inputs and their effect on later packets are recorded; no private payload is committed.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Run the existing auditor on the local dump and inventory the target hardware and Octatrack firmware information actually available.
- Waiting on: No packet dependency. Confirm required inputs when claiming the packet.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
