# WP-08 — Extract and identify DSP boot payloads locally

- Status: `in_review`
- Owner: Codex
- Branch: `work/wp-08-dsp-payload-inventory`
- Updated: 2026-09-24
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

- [x] Extraction reproduces the observed boot uploads for both source DSPs with explicit byte/word order.
- [x] P/X/Y and external-memory ranges, overlays, and loader stages are distinguished rather than guessed from file offsets.
- [x] Repeated extraction is deterministic and rejects unsupported/truncated images.
- [x] Only reviewed metadata and independently authored synthetic fixtures are committed.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: Extracted and deterministically reproduced all five pinned OS 1.63 section hashes; reconciled section 1/2 record streams against both source DSP upload ports in cold and cached instances across two independent full traces; documented the load maps and parser limits in [the report](../reports/WP-08-dsp-payloads.md).
- Next action: Open a draft PR from the [published branch compare](https://github.com/repeat98/octamachine/compare/main...work/wp-08-dsp-payload-inventory?expand=1); keep it in review until maintainer review and G1 architecture evidence are complete.
- Waiting on: GitHub PR-write access for the connected tools; G1 hardware-realizable architecture remains open in WP-06–10.
- Blockers: The branch is pushed, but the available GitHub connector returned 403 for PR creation, the saved `gh` login token is invalid, and the in-app browser is signed out. The compare link is ready for a signed-in contributor.
- Evidence: [WP-04 baseline](../reports/WP-04-md-baseline.md) provides the private repeated HI08 traces; the [WP-08 report](../reports/WP-08-dsp-payloads.md) records this packet's independent extraction and exact upload reconciliation while keeping all firmware values local.

## Prompt history

### 2026-09-24 / prompt 1 — reconcile uploads with extracted DSP images

- Request: Continue the port after the maintainer's manual WP-05 squash merge; advance the next G1 packet by reconciling firmware DSP load records with measured host-port uploads.
- Starting state → ending state: `waiting` → `in_review`; WP-02, WP-03, and WP-04 are accepted prerequisites.
- Owner / branch: Codex / `work/wp-08-dsp-payload-inventory`, based on accepted `main` commit `148494c212d2d11fd21ad58f56c44b324d4c91bb`.
- Completed:
  - [x] Reconciled WP-05 PR #11 as merged at `148494c212d2d11fd21ad58f56c44b324d4c91bb` and updated G0 status.
  - [x] Inspected WP-04's private-trace policy, WP-35 extraction findings, and the checked-in extractor README; confirmed private firmware and Gearmulator/tool checkouts are available locally.
  - [x] Created a clean WP-08 worktree from accepted `main` without copying ignored firmware or build outputs.
  - [x] Reproduced the pinned update extraction three times with identical stdout, five extracted section hashes, and manifest.
  - [x] Matched both ordered DSP load-record streams exactly against DSP2/`0x00600000` and DSP1/`0x00500000` uploads in cold and cached instances from two independent WP-04 traces; confirmed H:M:L order and upload sequence without emitting payload values.
  - [x] Reviewed the P/X/Y load ranges and separated section framing, DSP boot prefix, one unclassified pre-record word, and later trailing host words.
  - [x] Added a local verifier that rejects explicit truncation markers, malformed bus rows, missing DSP pairs, unexpected byte order, and mismatched/ambiguous upload streams. Its capture-record completeness limitation is documented.
  - [x] Updated the compatibility matrix, research log, and WP-05 accepted-merge record; `make check` and `git diff --check` pass.
- Remaining:
  - [ ] Open the draft PR from the compare link, receive review, and reconcile the accepted delivery; G1 architecture feasibility remains outside this packet's evidence.
- Changed files: `docs/COMPATIBILITY_MATRIX.md`, `docs/RESEARCH_LOG.md`, `docs/STATUS.md`, `docs/work_packets/WP-05-octatrack-baseline.md`, `docs/work_packets/WP-08-dsp-payload-inventory.md`, `docs/reports/WP-08-dsp-payloads.md`, `scripts/md_reference/README.md`, `scripts/md_reference/md_verify_uploads.py`.
- Verification: `python3 scripts/md_reference/md_extract.py` was run three times on the pinned local update; summaries, all five output sections, and the manifest were identical. `python3 scripts/md_reference/md_verify_uploads.py <private-trace-a> <private-trace-b>` verified eight cold/cached upload streams across two independent full traces. `make check` passed (9 reference repositories, Python compilation, 20 tests); `git diff --check` passed. No trace-derived data was written or staged.
- Findings: Both source DSP record streams exactly match the extracted section records at their measured HI08 windows and byte order. The verifier cannot determine whether arbitrary end-of-file capture data was silently lost; completeness must come from the referenced capture records.
- Blockers: GitHub PR creation unavailable through the connected integration/browser session (403; CLI token invalid; browser signed out). Branch is published and the compare link is supplied above.
- Next action: Open a draft PR from the compare link when signed in; meanwhile continue ready packet WP-06. WP-09 preparation can use this report, but its acceptance waits for WP-08 accepted evidence.
- Delivery: commit `eb7d0412e1004410921ab40d61f010f93f6bed77` pushed to `work/wp-08-dsp-payload-inventory`; no PR created.

2026-09-23: [WP-35](WP-35-octamad-md-import.md) linked prior evidence in the current handoff. That was not a work prompt on this packet, and it changed no status or checklist item.
