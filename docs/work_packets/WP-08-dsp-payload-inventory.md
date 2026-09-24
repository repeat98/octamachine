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
- Next action: Obtain maintainer review for draft PR #14 and reconcile accepted delivery. Continue WP-06 as the next independent G1 packet; keep WP-09 gated on WP-08 acceptance.
- Waiting on: Maintainer review/acceptance and the G1 hardware-realizable architecture decision across WP-06–10.
- Blockers: Target DSP56721 execution, target memory fit, and physical HI08 evidence remain unmeasured. Private firmware and traces stay local and are excluded from the PR.
- Evidence: [WP-04 baseline](../reports/WP-04-md-baseline.md) provides the private repeated HI08 traces; the [WP-08 report](../reports/WP-08-dsp-payloads.md) records this packet's independent extraction and exact upload reconciliation while keeping all firmware values local.
- Delivery: Draft PR #14 remains open on work/wp-08-dsp-payload-inventory; last audited head e9cb222aa089a533e88725400b2e849284ad8d86 passed both scaffold checks and GitGuardian. Maintainer review and G1 acceptance remain open.

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

### 2026-09-24 / prompt 2 — open WP-08 draft PR

- Request: review the existing WP-08 branch against its packet criteria, validate available evidence, and open a draft PR while keeping private firmware data local.
- Starting state → ending state: in_review → in_review; the verified evidence branch is now delivered for review, with G1 architecture acceptance still open.
- Owner / branch: Codex / work/wp-08-dsp-payload-inventory, continuing from pushed branch head 4db20850876153b74c43441037f771a3c1fe31e2 based on accepted main 148494c212d2d11fd21ad58f56c44b324d4c91bb.
- Completed:
  - [x] Reviewed the full origin/main-to-WP-08 branch diff: eight intended text/source files; no firmware, ROM, extracted DSP payload, raw trace, or generated capture output is included.
  - [x] Ran make check: nine reference repositories validated, Python compilation passed, and all 20 tests passed.
  - [x] Ran git diff --check against origin/main; it passed.
  - [x] Opened draft PR #14. Its initial scaffold and GitGuardian checks passed; no review decision is present.
- Remaining:
  - [ ] Receive maintainer review and acceptance; keep PR #14 in draft while G1 architecture evidence remains incomplete.
  - [ ] Continue WP-09 only after WP-08 accepted evidence is available.
- Changed files: docs/STATUS.md and this packet; no code or evidence files changed in this prompt.
- Verification: the report records three deterministic extraction runs and eight exact upload-stream matches across two independent full-trace processes. The private update and traces are not present in this checkout, so those data-dependent commands were not rerun here. PR #14's initial checks passed.
- Findings: GitHub CLI write access worked and the branch is now delivered as a draft PR. Target DSP execution, memory fit, audio parity, and physical HI08 wiring remain outside the evidence.
- Blockers: maintainer review and G1 architecture acceptance; private firmware-derived values and traces remain unavailable in this checkout and are not part of the PR.
- Next action: obtain review for PR #14 while continuing independent G1 evidence work; keep WP-09 gated on WP-08 acceptance.
- Delivery: draft PR #14 is open at https://github.com/repeat98/octamachine/pull/14. The enclosing documentation commit and push are reported after delivery.

### 2026-09-24 / prompt 3 — audit WP-08 draft delivery

- Request: continue from the dispatch queue by auditing draft PR #14 against its packet evidence, acceptance checklist, and private-data constraints.
- Starting state → ending state: in_review → in_review; the packet's source-emulator evidence is unchanged and remains pending review/G1 acceptance.
- Owner / branch: Codex / work/wp-08-dsp-payload-inventory, continuing from PR head e9cb222aa089a533e88725400b2e849284ad8d86 based on accepted main 148494c212d2d11fd21ad58f56c44b324d4c91bb.
- Completed:
  - [x] Confirmed the three evidence criteria against the report, extractor history, and parser validation; confirmed the privacy criterion by auditing all eight changed files.
  - [x] Audited the eight-file PR diff and verifier output contract; only reviewed documentation and source code are included, with no firmware, extracted DSP payload, raw trace, or generated capture output.
  - [x] Confirmed PR #14 is open and draft, both scaffold checks and GitGuardian pass at head e9cb222aa089a533e88725400b2e849284ad8d86, and no review decision is present.
  - [x] Refreshed the current WP-08 handoff and project status to the checked PR head and queued WP-06 as the next independent G1 packet.
- Remaining:
  - [ ] Obtain maintainer review and reconcile accepted delivery; keep PR #14 draft while G1 architecture evidence is incomplete.
  - [ ] Continue WP-09 only after WP-08's accepted evidence is available.
- Changed files: docs/work_packets/WP-08-dsp-payload-inventory.md; docs/STATUS.md.
- Verification:
  - make check passed: nine reference repositories validated, Python compilation passed, and all 20 tests passed.
  - git diff --check origin/main...HEAD and git diff --check passed. GitHub's two scaffold checks and GitGuardian passed at audited head e9cb222aa089a533e88725400b2e849284ad8d86.
  - Data-dependent extraction and upload comparisons were skipped in this audit; private values and traces were neither opened nor changed.
- Findings: the report confines upload equality to the pinned Gearmulator model and labels the unresolved pre-record word, trailing words, and target/hardware behavior clearly. The verifier emits metadata only and documents its capture-completeness limit.
- Blockers: no maintainer review decision or G1 architecture acceptance.
- Next action: continue WP-06 as the next independent G1 packet; keep WP-09 gated on WP-08 acceptance and leave PR #14 in draft pending review/G1.
- Delivery: this audit and handoff update are delivered by the enclosing commit on the existing WP-08 branch.
