# WP-02 — Define firmware and target hardware profiles

- Status: `in_review`
- Owner: Codex
- Branch: `work/wp-02-target-profiles`
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

- [x] Source model/revision, file/container format, size, and fingerprints are reproducibly identified.
- [x] Target model/revision and carrier requirements are identified, or the profile is explicitly provisional with the physical hardware gate closed.
- [x] Supported baseline features and deferred variants are enumerated with evidence sources.
- [x] Missing local firmware/hardware inputs and their effect on later packets are recorded; no private payload is committed.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: Identified the ignored local Machinedrum image as SPS-1UW OS 1.63 by its 8 MiB size and matching MAME CRC-32/SHA-1 and Gearmulator FNV-64 fingerprints. Selected Gearmulator's MKII board-ID profile as the reference configuration and the pinned Octatrack MKII/MCF54455 octemu board as a provisional emulator target. Added the documented feature inventory and public profile metadata.
- Remaining: None for WP-02 acceptance. The local Octatrack OS section has no retained source archive, and no physical MD or OT board revision is identified; both limits are explicit in the profile and remain prerequisites for later runtime/physical claims.
- Next action: Review/merge this profile packet, then dispatch WP-03. WP-04/05 must verify their inputs before recording runtime baselines.
- Waiting on: Maintainer review.
- Blockers: None for the explicitly provisional emulator profile. The physical hardware gate remains closed.
- Evidence: [WP-02 target profile report](../reports/WP-02-target-profile.md), [shareable profile metadata](../../tests/fixtures/machinedrum-sps1uw-os1.63.profile.json), and the pinned emulator sources linked in the report.

## Prompt history

### 2026-09-23 / prompt 1 — Identify the source and provisional target profiles

- Request: Continue the port from the next available queue item after WP-01 was merged.
- Starting state → ending state: Ready → in review; the selected firmware/reference profile and provisional emulator target are documented, with all WP-02 checklist items supported by evidence.
- Owner / branch: Codex / `work/wp-02-target-profiles`.
- Completed:
  - [x] Reconciled WP-01's status-reconciliation PR #5 as merged into `main` at `ad6dac20daef6bb7180732989c521716b62bc5d6`; WP-01 remains done based on accepted PR #4.
  - [x] Ran the image auditor on `base_firmware/elektron_sps1-1uw_os1.63.bin` and confirmed its public OS 1.63 fingerprints and expected size.
  - [x] Identified the Gearmulator MKII board-ID configuration and octemu's Octatrack MKII/MCF54455 target declaration at their recorded commits.
  - [x] Inventoried the documented OS 1.63 baseline features and deferred MKI, +Drive, non-UW, and other-revision variants.
  - [x] Recorded the missing Octatrack distribution archive and unidentified physical hardware; no firmware payload was added.
- Remaining:
  - [ ] Maintainer review/merge of the WP-02 records.
  - [ ] Physical target identification and runtime baselines remain in later packets; they are not claimed by this profile inventory.
- Changed files: `docs/reports/WP-02-target-profile.md`, this packet, `docs/STATUS.md`, `docs/RESEARCH_LOG.md`, `docs/COMPATIBILITY_MATRIX.md`, and `tests/fixtures/machinedrum-sps1uw-os1.63.profile.json`.
- Verification:
  - `python3 scripts/audit_md_image.py --json base_firmware/elektron_sps1-1uw_os1.63.bin` — passed; 8 MiB size, MAME CRC-32/SHA-1, and Gearmulator FNV-64 all match OS 1.63. The local SHA-256 was not added to the report or repository.
  - Local input inventory — the extracted Octatrack main-OS section exists at 1,112,560 bytes; its source distribution ZIP is absent, so its identity is unverified.
  - `shasum -a 256 vendor/octemu/downloads/OCTATRACK_OS1.40C_dist.zip` — unavailable because the expected archive is absent.
  - `make check` — passed; 9 reference repositories validated and Python scripts compiled.
  - Local Markdown-link/anchor check — passed, 55 links across the five modified Markdown files.
  - `python3 -m json.tool tests/fixtures/machinedrum-sps1uw-os1.63.profile.json` and `git diff --check` — passed.
  - Octemu boot and hardware tests — skipped; this packet identifies profiles only. The distribution source and physical board/carrier identity are unavailable in the workspace evidence.
- Findings: The firmware image identifies the SPS-1UW OS 1.63 profile but does not identify a physical MKI/MKII or +Drive unit. The reference emulator selects an MKII board-ID strap. The target emulator source is explicitly an Octatrack MKII board, while the physical target remains provisional.
- Blockers: None for WP-02 acceptance. The physical hardware gate remains closed.
- Next action: Review/merge WP-02; then dispatch WP-03. WP-04 and WP-05 must confirm the source and target firmware inputs before their respective runtime baselines.
- Delivery: Enclosing commit on `work/wp-02-target-profiles`; branch compare: https://github.com/repeat98/octamachine/compare/main...work/wp-02-target-profiles
