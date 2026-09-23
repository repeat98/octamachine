# WP-08 — Extract and identify DSP boot payloads locally

- Status: `waiting`
- Owner: unassigned
- Branch: unassigned
- Updated: 2026-09-23
- Depends on: [WP-02](WP-02-target-profiles.md), [WP-03](WP-03-evidence-contract.md), [WP-04](WP-04-machinedrum-baseline.md)
- Gate: G1

## Result

Identify the firmware's own DSP payloads and boot protocol without redistributing them.

## Scope and starting points

Use Gearmulator's `mdromdata.*`, `mddsp.*`, host-port handling, and the reference boot trace. Name payload A and B by their observed source DSP/host-port identity, not an assumed target core role. Keep full payloads, disassembly, and upload-word traces under ignored output paths.

## Deliverables

- A read-only local extraction/manifest tool in `src/image/` or `scripts/`.
- `docs/reports/WP-08-dsp-payloads.md` with payload identities, ranges, word packing, hashes, entry points, and upload ordering.

## Acceptance checklist

- [ ] Extraction reproduces the observed boot uploads for both source DSPs with explicit byte/word order.
- [ ] P/X/Y and external-memory ranges, overlays, and loader stages are distinguished rather than guessed from file offsets.
- [ ] Repeated extraction is deterministic and rejects unsupported/truncated images.
- [ ] Only reviewed metadata and independently authored synthetic fixtures are committed.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: No execution work recorded for this packet.
- Next action: Follow the CPU's two DSP upload sequences and map each word stream back to the local image.
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).
