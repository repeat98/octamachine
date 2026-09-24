# WP-07 — Reconcile memory, MMIO, and clock contracts

- Status: `in_review`
- Owner: Codex
- Branch: `work/wp-07-memory-and-mmio`
- Updated: 2026-09-24
- Depends on: [WP-04](WP-04-machinedrum-baseline.md), [WP-05](WP-05-octatrack-baseline.md)
- Gate: G1
- Accepted delivery: pending review; [draft PR #13](https://github.com/repeat98/octamachine/pull/13)

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

- Completed: Reconciled the accepted WP-05 baseline, traced source MMIO by address/direction/width through cold and cached idle, bounded source-map and clock disagreements against pinned models and NXP manuals, and documented a proposed target alias/peripheral plan.
- Remaining: PR acceptance and physical Machinedrum/Octatrack measurements. The mapping plan has not been implemented or probed in octemu.
- Next action: Keep PR #13 in draft while G1 architecture evidence remains incomplete; continue WP-08 from accepted `main`.
- Waiting on: None for this documentation packet; physical board identity is needed for the remaining hardware measurements.
- Blockers: No physical board/schematic is available, so physical HI08 decode, the `MBAR+0x1003` signal, and the host clock cannot be verified.
- Evidence: [WP-07 memory/MMIO report](../reports/WP-07-memory-mmio.md), WP-04 trace summary and private full traces, MCF5206E and MCF54455 primary manuals, and the pinned octemu board source. Raw firmware-dependent traces remain private.
- Delivery: [Draft PR #13](https://github.com/repeat98/octamachine/pull/13) is open on `work/wp-07-memory-and-mmio`; packet acceptance evidence is complete, but G1 remains open and delivery is not merged.

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
  - [x] Confirmed draft PR #13 has successful scaffold and GitGuardian checks at head dfa80bb372d4888db483efb7cedc5371fab7acec and no review decision.
  - [x] Moved the completed commit/push/PR item from the prior prompt's Remaining list to Completed, and refreshed the status overview to the current PR head.
- Remaining:
  - [ ] Obtain maintainer review/acceptance; keep PR #13 draft while G1 architecture evidence is incomplete.
  - [ ] Implement and probe alias coherence, code copy/execute, vectors, stack, unknown MMIO, and HI08-to-HDI24 behavior under the later implementation packets.
  - [ ] Measure physical clock, board decode, and SRAM access bounds when hardware identity and access are available.
- Changed files: this packet; docs/STATUS.md.
- Verification:
  - `make check` - passed; reference validation succeeded and all 20 unit tests passed.
  - `git -c core.autocrlf=true diff --check` - passed; Git reported only the configured LF-to-CRLF conversion warnings for the two edited Markdown files.
  - PR #13's existing scaffold and GitGuardian checks were successful at the audited head `dfa80bb372d4888db483efb7cedc5371fab7acec`; the new documentation-only commit still needs its own CI result.
  - No firmware, raw trace, source, or target behavior was changed or newly measured.
- Findings: the current PR accurately labels its target map as a proposal and its measurements as Gearmulator/PC-model evidence. The packet acceptance list is complete for this documentation scope; G1 and the later implementation/hardware checks are separate and remain incomplete.
- Blockers: no PR review decision has been submitted; hardware identity/access is unavailable; alias and bridge probes belong to later implementation work.
- Next action: keep PR #13 in draft pending review and G1 evidence; continue WP-08 as the next independent packet, then return to WP-06 startup mapping after the WP-07 map is accepted.
- Delivery: this prompt's packet-history correction and PR status update are delivered by the enclosing commit on the existing draft PR #13 branch.
