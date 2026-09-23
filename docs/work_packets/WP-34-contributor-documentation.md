# WP-34 — Improve README, setup, and contributor documentation

- Status: `in_review`
- Owner: Codex
- Branch: work/readme-and-contributor-guide
- Updated: 2026-09-23
- Depends on: [WP-00](WP-00-planning-and-status.md), accepted in PR #2 / `d8f8a76`
- Gate: Maintenance
- Accepted delivery: pending

## Result

Give new contributors a clear starting point, accurate setup commands, and a practical route from one work packet to a reviewable PR.

## Scope and starting points

Own README, CONTRIBUTING, the getting-started guide, fixture/evidence guidance, compatibility-matrix navigation, and associated status/index records. Reconcile WP-00's accepted delivery. Inspect the existing Makefile, Python CLIs, pinned octemu setup/CLI/scripts, and the verified main ruleset.

This is a documentation packet. Emulator implementation, source pin changes, firmware captures, and hardware work remain with the technical packets.

## Deliverables

- A concise README with the actual-firmware goal, honest status, quick start, documentation map, and all upstream references.
- One detailed setup guide covering scaffold, local inputs, reference checkouts, Machinedrum tracing, and octemu headless/UI use.
- Contributor branch/fork/PR guidance aligned with protected main, plus reviewed artifact/evidence guidance.
- Reconciled project status and packet history.

## Acceptance checklist

- [x] README explains the goal, current evidence, emulator roles, and first contribution without requiring firmware for scaffold work.
- [x] Setup commands and prerequisites match the checked-in implementation; expected results and their limits are explicit.
- [x] Contributor instructions cover status/checklists, scoped delivery, protected main, and reviewable private-input evidence.
- [x] All upstream repository references remain available; local documentation links and packet dependencies resolve.
- [x] WP-00 acceptance is reconciled; this prompt's status/history is recorded; scaffold and whitespace checks pass.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies.

## Current handoff

- Completed: Improved and validated README, setup, contributor, and evidence guidance; reconciled WP-00 acceptance.
- Remaining: Maintainer review/merge, then reconcile this packet's accepted delivery. Clean emulator build/runtime baselines remain separate technical work.
- Next action: Review the documentation branch for ingestion; after acceptance, record its merge and start WP-01 source provenance.
- Waiting on: None; WP-00 is accepted.
- Blockers: None.
- Evidence: Local Makefile/scripts and octemu source at the recorded pin; PR #2 merge `d8f8a76`; GitHub effective rules for main verified in this task.
- Delivery: Enclosing commit on `work/readme-and-contributor-guide`; final reply supplies commit and PR outcome.

## Prompt history

### 2026-09-23 / prompt 1 — Improve README and related docs

- Request: Improve the README and other useful documentation.
- Starting state → ending state: Ready → in review; documentation criteria satisfied, maintainer acceptance pending.
- Owner / branch: Codex / `work/readme-and-contributor-guide`.
- Completed:
  - [x] Checked existing docs, root Makefile/Python CLIs, octemu build/run commands, and prior PR acceptance.
  - [x] Reconciled WP-00 as done following PR #2's merge; retained its original history.
  - [x] Reworked the README and drafted a single setup guide, contributor workflow, and artifact guidance.
  - [x] Linked compatibility boundaries to packet owners and clarified the baseline-to-architecture sequence in boot feasibility.
  - [x] Validated all repository Markdown links, packet dependencies, upstream references, and shell-block syntax; scaffold checks passed.
- Remaining:
  - [ ] Maintainer review/merge and next-prompt reconciliation.
  - [ ] WP-01 clean source reproduction, followed by profiles/capture contracts and runtime baselines in their owning packets.
- Changed files: README, CONTRIBUTING, getting-started/feasibility/matrix/status/plan docs, WP-00/WP-34 records, and fixture guidance.
- Verification:
  - `make check` — passed: 9 reference repositories and Python compilation.
  - Inline Python documentation audit — passed: 51 Markdown files, 301 local links/anchors, 35 indexed packets with acyclic dependencies, all 10 upstream links, 15 shell blocks parsed with `sh -n`.
  - `python3 scripts/references.py list`, `python3 scripts/audit_md_image.py --help`, and `make -n refs refs-status octemu-prepare gearmulator-prepare audit-md IMAGE=base_firmware/machinedrum.bin` — passed; documented root command names/options verified without fetching sources or reading firmware.
  - `git diff --check` — passed; staged whitespace/scope review repeated before delivery.
  - Checked octemu README, Makefile, doctor/fetch scripts, CLI, and `boot-nocard.jsonl` against the documented build order, host prerequisites, and asserted checkpoint. No clean emulator build or firmware/hardware run performed for this documentation packet.
- Findings: The previous README applied the Gearmulator trace patch before fetching its checkout and labeled a timeout-only launch as a test path. Corrected the ordering and documented the actual scripted no-card checkpoint. The image auditor reports mismatches without a failing exit, so its output fields need inspection.
- Blockers: None.
- Next action: Review/merge WP-34, reconcile its delivery, then dispatch WP-01 for technical source reproduction.
- Delivery: Enclosing commit on `work/readme-and-contributor-guide`.
