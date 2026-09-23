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
- Next action: Reconcile the observed DSP1/DSP2 HI08 upload streams with the load records `md_extract.py` parses (section 2: 18,823 words; section 1: 250,123 words, headers included).
- Waiting on: The dependency packets listed above; preparation is allowed, acceptance requires their evidence.
- Blockers: none recorded.
- Evidence: No packet acceptance evidence yet. Existing research is a starting point, not proof of this packet's result. Prior evidence from the octamad Machinedrum excursion: the update container, its five sections, the DSP load-image format and per-space load maps. Section 1 is the voice DSP (Gearmulator DSP2, producer, HI08 `0x600000`) and section 2 the mixer (DSP1, `0x500000`). `scripts/md_reference/md_extract.py` is a candidate for this packet's extraction tool ([WP-35 report](../reports/WP-35-octamad-md-import.md)). It is Gearmulator-only, predates the WP-03 contract, and checks no item here.

## Prompt history

No work prompt has executed this packet. Append a dated entry after every work prompt using the [packet template](../templates/WORK_PACKET.md#prompt-history).

2026-09-23: [WP-35](WP-35-octamad-md-import.md) linked prior evidence in the current handoff. That was not a work prompt on this packet, and it changed no status or checklist item.
