# WP-07 — Reconcile memory, MMIO, and clock contracts

- Status: `done`
- Owner: Codex
- Branch: `work/wp-07-memory-and-mmio`
- Updated: 2026-09-24
- Depends on: [WP-04](WP-04-machinedrum-baseline.md), [WP-05](WP-05-octatrack-baseline.md)
- Gate: G1
- Accepted delivery: [PR #13 squash-merged as 5184aa20cada2a949354874f77c58b3e440a84eb](https://github.com/repeat98/octamachine/pull/13)

## Result

Produce one evidence-backed register and address contract for source and target hardware.

## Scope and starting points

Investigate the documented DSP address, SRAM-size, and CPU-clock disagreements. Inventory mapped ranges, aliases, bus widths, flash commands, reset values, interrupt routes, timers, UARTs, and DMA where used. Clock claims need units, divisors, and a primary-source or measured basis.

## Deliverables

- `docs/reports/WP-07-memory-mmio.md` with source/target address and register tables.
- Trace summaries and focused probes for disputed ranges, access widths, and clock relationships.

## Acceptance checklist

- [x] The DSP windows are resolved for the Gearmulator reference model; SRAM and clock differences are bounded with explicit physical-board measurements remaining. See the [memory/MMIO report](../reports/WP-07-memory-mmio.md).
- [x] Every source peripheral touched through the reference idle checkpoints has a proposed target owner and access semantics; unobserved CPU DMA and M-Bus paths are explicitly excluded. See the report's [peripheral activity table](../reports/WP-07-memory-mmio.md#peripheral-activity-through-reference-idle) and [post-ready trace](../reports/WP-07-memory-mmio.md#post-ready-initialization-and-idle-trace).
- [x] Proposed mappings cover coherent aliases, executable/writable regions, initial stack, vectors, and address overlaps. No alias probe is claimed.
- [x] Octemu RAM/MMIO windows are labeled as PC-side instrumentation; physical Octatrack decoding remains unproven. See [target model and instrumentation boundary](../reports/WP-07-memory-mmio.md#octatrack-target-model-and-instrumentation-boundary).

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: All four WP-07 documentation acceptance criteria are complete. PR #13 was explicitly authorized for merge and squash-merged as 5184aa20cada2a949354874f77c58b3e440a84eb. The report stays bounded to Gearmulator observations, pinned model behavior, and NXP documentation; its target alias and peripheral plan was not implemented or probed.
- Remaining: G1 is open. Alias coherence, code/vector/stack execution, MMIO guards, the HI08-to-HDI24 bridge, and physical clock/decode require later implementation or hardware evidence beyond this documentation packet.
- Next action: Continue WP-06's unchecked adaptation assessment using the accepted map. Continue DSP feasibility only after WP-08's accepted delivery; PR #13's merge does not clear G1.
- Waiting on: None for WP-07's packet criteria.
- Blockers: Physical board identity and schematic access are unavailable, so physical HI08 decode, the MBAR+0x1003 signal, and host clock remain unverified.
- Evidence: [WP-07 memory/MMIO report](../reports/WP-07-memory-mmio.md), WP-04 trace summary and private full traces, MCF5206E and MCF54455 primary manuals, and pinned octemu board source. Raw firmware-dependent traces remain private.
- Delivery: [PR #13](https://github.com/repeat98/octamachine/pull/13) squash-merged as 5184aa20cada2a949354874f77c58b3e440a84eb on 2026-09-24. This closes WP-07's documentation packet; it does not establish target implementation or G1 acceptance.

## Prompt history

### 2026-09-24 / prompt 1 — reconcile memory, MMIO, and clock evidence

- Request: Continue the Machinedrum-to-Octatrack port after the maintainer's manual squash merge; resolve or bound WP-07's memory, register, and clock disagreements using accepted reference evidence.
- Starting state → ending state: `waiting` → `in_review`; WP-04 and WP-05 are accepted prerequisites.
- Owner / branch: Codex / `work/wp-07-memory-and-mmio`, based on accepted `main` commit `148494c212d2d11fd21ad58f56c44b324d4c91bb`.
- Completed:
  - [x] Reconciled WP-05 PR #11 as merged at `148494c212d2d11fd21ad58f56c44b324d4c91bb`; G0 now has its required target baseline.
  - [x] Classified the private WP-04 reset-to-ready cold/cached traces by address, direction, width, and count without copying MMIO payloads into the repository.
  - [x] Extended the address-only trace in a disposable Gearmulator copy from firmware-ready through cold/cached idle. The driver exited 0; both intervals matched all 43 summary rows and the published frame/MCU-cycle checkpoints on a repeated process run.
  - [x] Resolved the Gearmulator reference HI08 map to `0x00500000`/`0x00600000`; bounded the MAME comment discrepancy and kept the physical board decode open.
  - [x] Bounded 8 KiB silicon SRAM versus Gearmulator's 64 KiB backing, the 25.447/40 MHz model split, and the unknown `MBAR+0x1003` byte write.
  - [x] Proposed target ownership/semantics for each MMIO group, a coherent source-alias plan, executable/writable placement, stack/vector storage, and overlap handling. Labeled the target model's RAM/MMIO windows as PC-side instrumentation.
  - [x] Committed and pushed the packet branch and opened draft PR #13.
- Remaining:
  - [ ] Confirm required checks on the final head, receive review, and reconcile accepted delivery.
  - [ ] Implement and probe alias coherence, code copy/execute, vector fetch, stack push, unknown-MMIO handling, and HI08-to-HDI24 bridge semantics under later packets.
  - [ ] Measure physical clock and board decode after Machinedrum board identity/schematic access is available.
- Changed files: this packet; `docs/reports/WP-07-memory-mmio.md`; `docs/STATUS.md`; `docs/COMPATIBILITY_MATRIX.md`; `docs/RESEARCH_LOG.md`; `docs/BOOT_FEASIBILITY.md`; WP-05 merge reconciliation.
- Verification:
  - `cmake -S <disposable Gearmulator source> -B <scratch build> ... -Dgearmulator_SYNTH_ELEKTRON=ON` — configured successfully after adding the source checkout's parent CMake helper files to the scratch copy.
  - `cmake --build <scratch build> --target mdPanelReadinessFirmwareTest --parallel 4` — passed; upstream AsmJit and Mach-O alignment warnings remain.
  - Address-only post-ready capture — repeated twice with exit 0; cold idle reached frame/cycle `837900` / `760000005`, cached idle reached `573300` / `520000005`; aggregate access rows and checkpoints matched. The tracer discarded per-access values and retained address/width/direction counts only.
  - `make check` — passed; nine reference repositories validated, Python scripts compiled, and 20 tests passed.
  - PR #13 GitHub checks on `a7fa44efb9c5d6451cd008ab2c4a2bb068b2c313` — scaffold and GitGuardian security checks passed; review and accepted merge remain outstanding.
  - `git diff --check` — passed.
  - Private trace address/direction/width aggregation and static firmware reset review — completed locally; no raw MMIO values or firmware bytes are in the report.
  - Octemu alias/device probes and physical hardware measurements — not run; remain future implementation and hardware gates.
- Findings: See the report. The reference-model DSP windows and source SRAM size are bounded by runtime trace/model inspection plus primary part documentation. Gearmulator's 40 MHz trace window agrees with its 40 MHz setting; the physical clock remains unknown. The single `MBAR+0x1003` write is outside the documented SIM map and is not assigned a fabricated meaning.
- Blockers: No physical board/schematic for the clock and decode measurements; no code-level target probes in this report-only packet.
- Next action: Continue WP-08 from accepted `main` while G1 implementation evidence remains open; keep WP-07 draft pending architecture evidence and review.
- Delivery: [Draft PR #13](https://github.com/repeat98/octamachine/pull/13) opened at `a7fa44efb9c5d6451cd008ab2c4a2bb068b2c313`; scaffold and GitGuardian checks passed. Later status reconciliation is in the enclosing follow-up commit.

### 2026-09-24 / prompt 2 - review WP-07 evidence and reconcile records

- Request: take the next dispatch item by auditing draft PR #13 and reconciling its packet and project status.
- Starting state -> ending state: in_review -> in_review; the packet-level evidence remains complete, while review, implementation, G1, and physical gates remain open.
- Owner / branch: Codex / work/wp-07-memory-and-mmio, continuing from PR head dfa80bb372d4888db483efb7cedc5371fab7acec; origin/main remains 148494c212d2d11fd21ad58f56c44b324d4c91bb.
- Completed:
  - [x] Rechecked all four WP-07 acceptance items against the report; they are bounded to Gearmulator/source documentation and proposed target ownership, with no alias or physical behavior claimed.
  - [x] Confirmed draft PR #13 has successful scaffold and GitGuardian checks at audited head dfa80bb372d4888db483efb7cedc5371fab7acec and at pushed documentation-reconciliation head 9dafa73695bea65a6c996f6163e81efcd4fa84c7; no review decision is present.
  - [x] Moved the completed commit/push/PR item from the prior prompt's Remaining list to Completed, and refreshed the status overview to the current PR head.
- Remaining:
  - [ ] Obtain maintainer review/acceptance; keep PR #13 draft while G1 architecture evidence is incomplete.
  - [ ] Implement and probe alias coherence, code copy/execute, vectors, stack, unknown MMIO, and HI08-to-HDI24 behavior under the later implementation packets.
  - [ ] Measure physical clock, board decode, and SRAM access bounds when hardware identity and access are available.
- Changed files: this packet; docs/STATUS.md.
- Verification:
  - `make check` - passed; reference validation succeeded and all 20 unit tests passed.
  - `git -c core.autocrlf=true diff --check` - passed; Git reported only the configured LF-to-CRLF conversion warnings for the two edited Markdown files.
  - PR #13 checks passed at pushed head `9dafa73695bea65a6c996f6163e81efcd4fa84c7`: both scaffold jobs and GitGuardian.
  - No firmware, raw trace, source, or target behavior was changed or newly measured.
- Findings: the current PR accurately labels its target map as a proposal and its measurements as Gearmulator/PC-model evidence. The packet acceptance list is complete for this documentation scope; G1 and the later implementation/hardware checks are separate and remain incomplete.
- Blockers: no PR review decision has been submitted; hardware identity/access is unavailable; alias and bridge probes belong to later implementation work.
- Next action: keep PR #13 in draft pending review and G1 evidence; continue WP-08 as the next independent packet, then return to WP-06 startup mapping after the WP-07 map is accepted.
- Delivery: this prompt's packet-history correction and PR status update are delivered by the enclosing commit on the existing draft PR #13 branch.

### 2026-09-24 / prompt 3 — recheck WP-07 review state and source claims

- Request: Continue the queued WP-07 review, reconcile current PR and main state, and identify any supportable report correction.
- Starting state → ending state: `in_review` → `in_review`; the four packet evidence criteria remain complete, while PR acceptance, G1, target implementation, and physical measurements remain open.
- Owner / branch: Codex / `work/wp-07-memory-and-mmio`, continuing from PR head `cc481624825cd7e1aa5821f24d4476ef8f8d5610`; `origin/main` remains `148494c212d2d11fd21ad58f56c44b324d4c91bb`.
- Completed:
  - [x] Reconciled live PR #12–14 state: all remain open draft PRs with no review decisions; PR #13 is mergeable and its scaffold and GitGuardian checks passed at the audited head.
  - [x] Rechecked the four WP-07 acceptance items against the report. Source-map and clock claims remain bounded to Gearmulator, source documentation, or PC-side octemu modeling; no target alias execution or physical decode is claimed.
  - [x] Cross-checked the cited NXP source claims: MCF5206E manual §5.1 specifies 8 KiB SRAM and §6.1 lists 8-, 16-, and 32-bit port sizes; MCF54455 manual §4.3.8 specifies a 64-entry full-associative Harvard TLB with 32-entry instruction and data TLBs. These are silicon documentation, not proof of board configuration or target MMU setup.
  - [x] Ran `make check`; all nine reference validations, Python compilation, and 20 unit tests passed. `git diff --check` passed before commit.
  - [x] Updated the packet handoff and project dispatch state to the current PR head and review status.
- Remaining:
  - [ ] Obtain maintainer review/acceptance; keep PR #13 in draft while G1 architecture evidence is incomplete.
  - [ ] Implement and probe alias coherence, code copy/execute, vectors, stack, unknown MMIO, and HI08-to-HDI24 behavior under later packets.
  - [ ] Measure physical clock, board decode, and SRAM access bounds when board identity and access are available.
- Changed files: `docs/work_packets/WP-07-memory-and-mmio.md`; `docs/STATUS.md`.
- Verification:
  - `make check` — passed: nine reference repositories validated, Python scripts compiled, and 20 tests passed.
  - PR #13 scaffold checks and GitGuardian — passed at audited head `cc481624825cd7e1aa5821f24d4476ef8f8d5610`; no review decision is present.
  - No firmware, raw trace, source, target behavior, or hardware was changed or newly measured. Physical and emulator implementation gates remain skipped.
- Findings: No technical correction was supported by this audit. The delivery is complete for WP-07's documentation criteria, not for G1 or the later implementation and hardware work.
- Blockers: PR review/acceptance is pending; physical board identity/access is unavailable. These do not prevent independent WP-08 work.
- Next action: continue WP-08 from accepted `main`; keep WP-07 draft pending review and G1 evidence, then use its reviewed map to bound remaining WP-06 startup-register analysis.
- Delivery: this prompt's record/status reconciliation is committed and pushed on the existing draft PR #13 branch.

### 2026-09-24 / prompt 4 — reconcile maintainer ready-for-review state

- Request: Incorporate the maintainer's PR state change, correct the stale draft instruction, and continue only within the documented G1 gate.
- Starting state → ending state: packet `in_review` → `in_review`; PR #13 changed from draft to ready for review, with no review decision or merge. G1 remains open.
- Owner / branch: Codex / `work/wp-07-memory-and-mmio`; PR head `cff94ec283841ff9bdd4a3ac8218856afb26c155`; `origin/main` remains `148494c212d2d11fd21ad58f56c44b324d4c91bb`.
- Completed:
  - [x] Confirmed PR #13's `ready_for_review` timeline event was performed by `repeat98` at 2026-09-24 11:47 UTC; the PR is open, mergeable, has no reviews, and has no review decision.
  - [x] Confirmed scaffold checks passed at head `cff94ec283841ff9bdd4a3ac8218856afb26c155`.
  - [x] Replaced the PR description's stale “keep in draft” line with the current state: ready for review, but unmerged until G1 architecture evidence is accepted. The first `gh pr edit` attempt returned a Projects classic deprecation error and made no change; the equivalent REST update succeeded.
  - [x] Updated the packet handoff and `docs/STATUS.md` to match the ready-for-review state.
- Remaining:
  - [ ] Obtain maintainer review/acceptance; G1 architecture evidence from WP-06–10 is incomplete, so do not mark WP-07 done or merge it yet.
  - [ ] Implement and probe alias coherence, code copy/execute, vectors, stack, unknown MMIO, and HI08-to-HDI24 behavior under later packets.
  - [ ] Measure physical clock, board decode, and SRAM access bounds when board identity and access are available.
- Changed files: `docs/work_packets/WP-07-memory-and-mmio.md`; `docs/STATUS.md`. Updated external metadata: [PR #13 description](https://github.com/repeat98/octamachine/pull/13).
- Verification:
  - `make check` — passed after these record changes: nine reference repositories validated, Python scripts compiled, and 20 tests passed. `git diff --check` — passed.
  - PR #13 scaffold checks passed at audited head `cff94ec283841ff9bdd4a3ac8218856afb26c155`; no review decision is present.
  - No firmware, raw trace, target behavior, or hardware was changed or newly measured.
- Findings: The maintainer's ready-for-review action supersedes the prior draft state. The stated G1 gate still prevents acceptance as done and merging. The packet's four documentation criteria remain complete.
- Blockers: maintainer review/acceptance and G1 evidence are pending. Independent WP-08 work can proceed.
- Next action: continue WP-08 from accepted `main`; return to WP-06 startup-register analysis after the WP-07 map is accepted.
- Delivery: this reconciliation is committed and pushed on the existing PR #13 branch.

### 2026-09-24 / prompt 5 — reconcile authorized PR #13 merge

- Request: Reconcile the completed WP-07 delivery after the user explicitly authorized merging all open pull requests; keep packet completion separate from G1 acceptance.
- Starting state -> ending state: in_review -> done; all four WP-07 documentation criteria were already evidenced, and PR #13 is now squash-merged.
- Owner / branch: Codex / work/wp-07-memory-and-mmio; merge reconciliation recorded while integrating PR #13 into the current WP-06 branch.
- Completed:
  - [x] Confirmed PR #13 was squash-merged as 5184aa20cada2a949354874f77c58b3e440a84eb on 2026-09-24.
  - [x] Marked the packet done because all four documentation-scope acceptance items and its definition of done are satisfied.
  - [x] Updated project status and the compatibility matrix to cite the accepted report and merged delivery.
  - [x] Kept G1, physical measurements, and later alias/bridge implementation work open.
- Remaining:
  - [ ] Map actual source startup-register effects against the accepted map under WP-06; keep its adaptation item open until evidence supports a mechanism.
  - [ ] Continue WP-08/WP-09 DSP feasibility without treating the WP-07 merge as proof of target execution.
- Changed files: docs/work_packets/WP-07-memory-and-mmio.md; docs/STATUS.md; docs/COMPATIBILITY_MATRIX.md; docs/RESEARCH_LOG.md; docs/work_packets/WP-06-coldfire-compatibility.md.
- Verification: PR #13 merge state and SHA were confirmed through GitHub. The reconciled WP-06 branch passed make check (nine reference validations, Python compilation, and 20 tests) and git diff --check.
- Findings: PR acceptance closes the bounded documentation packet only. No alias probe, physical clock/decode measurement, or target boot was added.
- Blockers: Physical Machinedrum/Octatrack identity and access remain unavailable.
- Next action: Hand off the updated WP-06 branch with PRs #12 and #14 open. The next owner should verify the pushed head and required checks, then decide whether to proceed with the separately authorized merges. Keep G1 unchecked.
- Delivery: This reconciliation is included in the current WP-06 branch update.
