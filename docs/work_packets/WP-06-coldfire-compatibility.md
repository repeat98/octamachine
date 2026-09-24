# WP-06 — Audit ColdFire execution compatibility

- Status: `in_review`
- Owner: Codex
- Branch: `work/wp-06-coldfire-compatibility`
- Updated: 2026-09-24
- Depends on: [WP-04](WP-04-machinedrum-baseline.md), [WP-05](WP-05-octatrack-baseline.md)
- Gate: G1

## Result

Identify which observed Machinedrum CPU operations can execute on the target and which require adaptation.

## Scope and starting points

Compare executed startup and representative runtime instructions, control registers, exception frames, privilege transitions, alignment, byte order, atomics, cache behavior, and self-modifying code if observed. Use the pinned mc68k/QEMU implementations and primary processor manuals. Do not treat an all-bytes disassembly as proof of executed instruction coverage.

## Deliverables

- `docs/reports/WP-06-coldfire.md` mapping observed CPU requirements to target capabilities.
- Minimal independently authored instruction/exception probes and a list of unobserved paths.

## Acceptance checklist

- [x] Each observed incompatibility has an instruction/control-state example and a reproducible probe or reference trace.
- [x] Reset, vector setup, exception return, interrupt masking, and stack semantics are compared; the level-7 external-input and reset-fetch limits are explicit.
- [ ] Any proposed trap, relocation, or patch mechanism is checked against actual target facilities and privilege constraints.
- [x] The report distinguishes direct execution, bounded adaptation, unresolved behavior, and an identified blocker.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: Reconciled WP-05 as accepted; profiled a sanitized 1,000,000-instruction startup prefix plus nine assignment/eight-hit scenarios and nine trigger/encoder scenarios spanning all eight core engine families; added independent `m5206`/`cfv4e` instruction, exception, VBR, EUSP, MOVEC, alignment, and byte-order probes; documented QEMU model gaps and reset/interrupt limits in the [WP-06 report](../reports/WP-06-coldfire.md).
- Remaining: Broader runtime coverage across the 44 distinct descriptor handlers; atomic/cache/self-modifying-code and device-memory behavior; map the startup register operands and effects before selecting an adaptation; physical level-7 and reset-vector behavior.
- Next action: After WP-07's memory/MMIO map is accepted, use its target map to revisit the source startup register effects and check adaptation candidates against target facilities and privilege; retain level 7 and reset-vector fetch as explicit model/hardware limits. Extend per-engine coverage where a bounded run adds evidence.
- Waiting on: WP-07's map is available in draft PR #13 and awaits review/acceptance; WP-04 and WP-05 prerequisites are accepted.
- Blockers: Physical reset, interrupt, and register behavior cannot be confirmed without the actual target hardware. The target MCF54455 manual documents RAMBAR at a different MOVEC encoding from the MCF5206E and no source MBAR encoding; exact firmware operands/effects remain unrecorded. QEMU also lacks faithful models for these paths.
- Evidence: [WP-06 report](../reports/WP-06-coldfire.md); firmware-free probes and reproduction instructions in [`tests/probes/wp06/`](../../tests/probes/wp06/); sanitized startup-summary patch [0003](../../patches/gearmulator-md-mm/0003-opt-in-coldfire-execution-summary.patch). The new runtime profiles are Gearmulator-only and keep raw traces local.
- Delivery: draft [PR #12](https://github.com/repeat98/octamachine/pull/12) on `work/wp-06-coldfire-compatibility`; it remains draft while checklist items are incomplete.

## Prompt history

### 2026-09-24 / prompt 1 — audit executed ColdFire compatibility

- Request: continue the Machinedrum-to-Octatrack port after the maintainer's manual squash merge of WP-05 PR #11; keep the overnight work moving and avoid claiming unmeasured compatibility.
- Starting state → ending state: `waiting` → `in_review` (draft delivery; one acceptance item remains open).
- Owner / branch: Codex / `work/wp-06-coldfire-compatibility`, based on accepted `main` commit `148494c212d2d11fd21ad58f56c44b324d4c91bb`.
- Completed:
  - [x] Reconciled WP-05 PR #11 as accepted and marked WP-05/G0 complete.
  - [x] Added a source-startup instruction summary that emits only categories, control-register names, and counts; it emits no PCs, opcodes, payloads, or raw MMIO values.
  - [x] Ran the Gearmulator panel-readiness driver with the local OS 1.63 image; the counter captured the first 100,000 executed instructions and the driver exited 0 after cold/cached readiness checks.
  - [x] Added firmware-free arithmetic/stack/exception, target EUSP, and startup MOVEC probes plus the WP-06 report.
  - [x] Compared SR.I level-4 masking on the `m5206` and `cfv4e` QEMU models with a firmware-free timer interrupt.
- Remaining:
  - [ ] Establish reset-vector fetch on a board path that actually performs reset; the current QEMU source path is unresolved.
  - [ ] Test the external edge-sensitive level-7 case; the AN5206 board does not expose that input.
  - [ ] Check any eventual trap/patch/register-shim mechanism against hardware facilities and privilege constraints.
  - [ ] Expand executed runtime/engine instruction and memory-access coverage; resolve physical behavior on hardware.
- Changed files: this packet; WP-05 packet; `docs/STATUS.md`; `docs/RESEARCH_LOG.md`; `docs/COMPATIBILITY_MATRIX.md`; `docs/reports/WP-06-coldfire.md`; `tests/probes/wp06/`; `patches/gearmulator-md-mm/0003-opt-in-coldfire-execution-summary.patch`; `scripts/prepare_gearmulator.py`.
- Verification:
  - `python3 tests/probes/wp06/run.py --cc /opt/homebrew/bin/m68k-elf-gcc --qemu /private/tmp/octamachine-md-import/vendor/octemu/vendor/qemu/build/qemu-system-m68k` — passed; `m5206` and `cfv4e` outputs matched for arithmetic/exception and level-4 interrupt masking; EUSP bit-position and unimplemented-register cases reproduced.
  - `patch --dry-run -p1 -d /private/tmp/octamachine-wp04-clean < patches/gearmulator-md-mm/0003-opt-in-coldfire-execution-summary.patch` — passed against the WP-04 clean Gearmulator source tree.
  - `cmake --build build-wp06 --target mdPanelReadinessFirmwareTest --parallel 4` in a disposable pinned Gearmulator copy — passed; compiler/linker emitted upstream optimization/alignment warnings.
  - The same driver's local-firmware run with `GEARMULATOR_MD_EXEC_SUMMARY_LIMIT=100000` — exit 0; aggregate summary: ten MOVEC writes (VBR ×2, CACR ×2, ACR0 ×2, ACR1 ×2, RAMBAR ×1, MBAR ×1), two status-register writes, and no counted RTE/TRAP/RESET/STOP/USP-stack opcodes in the prefix. Raw firmware and trace outputs remain private.
  - An initial EUSP run used QEMU's `0x10` bit as if it were the manual's bit. Checking the MCF54455 manual corrected the device mask to `0x20`; the runner now reports both and the final comparison passes.
  - An attempted QEMU `system_reset` vector-fetch check did not reach the vector entry. Inspection found QEMU reset sets PC to zero with a TODO to fetch it; `-kernel` directly starts at the ELF entry. Reset equivalence remains unresolved.
  - `make check` — passed: nine reference validations, Python script compilation, and 20 tests; no physical hardware test is available.
- Findings: see the [WP-06 report](../reports/WP-06-coldfire.md). The matching QEMU arithmetic/exception cases are narrow. The VBR alignment and EUSP bit differences, ACR no-op, and RAMBAR/MBAR abort identify target-model gaps. These do not establish physical MCF54455 incompatibility.
- Blockers: no physical target; QEMU `an5206 -kernel` bypasses reset-vector fetch; current QEMU does not faithfully model the observed control-register paths.
- Next action: check whether the actual Octatrack board model or a supported test interface can inject the external edge-sensitive level-7 request; continue after documenting that boundary.
- Delivery: enclosing commit; draft PR remains open until the listed CPU/privilege checks and remaining evidence are addressed.

### 2026-09-24 / prompt 2 — reconcile target control-register and interrupt facilities

- Request: continue after the maintainer's manual squash merge and keep the port moving overnight.
- Starting state → ending state: `in_review` → `in_review` (WP-05 merge already reconciled; WP-06 remains a draft pending broader evidence and acceptance).
- Owner / branch: Codex / `work/wp-06-coldfire-compatibility`, based on accepted main `148494c212d2d11fd21ad58f56c44b324d4c91bb`.
- Completed:
  - [x] Fetched `origin main`; it remains at `148494c212d2d11fd21ad58f56c44b324d4c91bb`, already an ancestor of this branch.
  - [x] Checked pinned QEMU source: `an5206 -kernel` starts at the ELF entry; the Octatrack board wires its modeled device interrupts through two MCF INTCs; neither board exposes a separate external level-7 stimulus; the CPU interrupt path has no edge latch and compares only SR.I against the pending level.
  - [x] Compared both NXP device manuals: source MCF5206E RAMBAR is Rc `0xC04` and MBAR is `0xC0F`; MCF54455 documents RAMBAR at `0xC05`, ACR0–3 and CACR, 1 MiB VBR alignment, and non-maskable edge-sensitive level 7.
  - [x] Bounded the adaptation candidates against target register encodings and supervisor-only privilege; no startup operand values or patch site are published, and no mechanism is selected.
- Remaining:
  - [ ] Map the source RAMBAR/MBAR operands and effects against the target memory/peripheral map before selecting any rewrite or shim.
  - [ ] Extend executed runtime handler coverage beyond the first 100,000 startup instructions.
  - [ ] Obtain a board path for reset-vector and level-7 edge tests, or keep those hardware/model gaps open.
- Changed files: `docs/reports/WP-06-coldfire.md`; this packet; `docs/RESEARCH_LOG.md`; `docs/COMPATIBILITY_MATRIX.md`; `docs/STATUS.md`.
- Verification: `git fetch origin main` succeeded and main remains at the branch base. `make check` passed (nine reference validations, Python compilation, 20 tests); the WP-06 QEMU probe passed on `m5206`/`cfv4e`, including arithmetic/exceptions and level-4 masking; `git diff --check` passed. Pinned-source and official-manual inspection supports the documented reset/level-7 limits and register-map comparison. PR #12's two `scaffold` runs and GitGuardian check passed.
- Findings: the QEMU behavior is not a substitute for the manuals. The MCF54455 supports several registers which the generic `cfv4e` helper leaves unimplemented, but its RAMBAR encoding differs from the source; the source MBAR write has no matching target core-register entry.
- Blockers: no physical Octatrack/Machinedrum and no separate external level-7 test input in either pinned board model.
- Next action: begin WP-07 from accepted `main`, using the reconciled WP-04 trace and the WP-06 startup register inventory; return to WP-06 for runtime coverage after mapping the control-register effects.
- Delivery: enclosing commit updates [PR #12](https://github.com/repeat98/octamachine/pull/12); the PR remains a draft with `scaffold` and GitGuardian checks passing.

### 2026-09-24 / prompt 3 — extend executed ColdFire runtime evidence

- Request: continue the overnight Machinedrum-to-Octatrack port after the maintainer's manual WP-05 squash merge; extend WP-06 runtime evidence and keep firmware-derived traces private.
- Starting state → ending state: `in_review` → `in_review` (runtime evidence expanded; adaptation and physical-hardware criteria remain open).
- Owner / branch: Codex / `work/wp-06-coldfire-compatibility`, based on accepted main `148494c212d2d11fd21ad58f56c44b324d4c91bb`.
- Completed:
  - [x] Reconciled WP-07 as draft PR #13 in review and WP-08 as a pushed evidence branch awaiting PR creation; neither is marked accepted.
  - [x] Built `mdPanelReadinessFirmwareTest` in a separate Gearmulator copy at `8cea0524a75435122c20b669ca114c9ac6509ba2` with the pinned recursive dependencies and WP-04/WP-06 instrumentation.
  - [x] Extended its opt-in summary limit to 1,000,000 executed instructions; the cold/cached driver exited 0 and the summary still reports only control names/categories and aggregate counts.
  - [x] Built the JIT `md_profile` tool with WP-35 host-trace/execution-hook patches in the same isolated source copy.
  - [x] Profiled machine `0x10` assignment plus eight triggers: 562,290,551 instructions, 24 MOVEC-to, 139,161 RTE, 12 TRAP, 1,030,050 move-to-SR, and 77,568 move-from-SR operations.
  - [x] Ran `trace=0x10` (assignment, trigger, encoder A +10, second trigger): 559,651,805 instructions and 3,440 descriptor-handler-range entries across two handler/return buckets. No firmware-derived addresses or raw values were added to the repository.
  - [x] Kept acceptance item 3 unchecked: the exact source register operands/effects still need WP-07's accepted target memory map before a rewrite/shim can be selected.
- Remaining:
  - [ ] Extend runtime coverage beyond the two `0x10` scenarios, including additional engines and relevant memory/alignment/atomic/cache paths.
  - [ ] Map source startup register operands/effects against a reviewed target map and check any proposed mechanism against the physical target's privilege/facility rules.
  - [ ] Resolve reset-vector fetch and external edge-sensitive level 7 through a suitable board path or preserve these as hardware/model limits; establish physical CPU behavior.
- Changed files: this packet; `docs/reports/WP-06-coldfire.md`; `docs/STATUS.md`; `docs/COMPATIBILITY_MATRIX.md`; `docs/RESEARCH_LOG.md`; `tests/probes/wp06/README.md`.
- Verification:
  - `cmake --build <isolated Gearmulator build> --target mdPanelReadinessFirmwareTest --parallel 4` — passed; compiler emitted upstream optimization/alignment warnings.
  - `GEARMULATOR_MD_EXEC_SUMMARY_LIMIT=1000000` with the local OS 1.63 panel-readiness driver — exit 0 after cold/cached checkpoints; the sanitized counter reached 1,000,000 instructions.
  - `cmake --build <isolated profile build> --target md_profile --parallel 4` — passed.
  - `md_profile <local OS 1.63 image> <private output> 0x10` with a 1,000,000,000-instruction counter ceiling — exit 0 at 562,290,551 instructions.
  - `md_profile <local OS 1.63 image> <private output> trace=0x10` with the same ceiling — exit 0 at 559,651,805 instructions; safe aggregation of the private `.calls.txt` reported 3,440 calls across two buckets.
  - `make check` — passed: nine reference validations, Python script compilation, and 20 tests.
  - `git diff --check` — passed.
  - No physical hardware, full all-engine coverage, raw trace publication, or target instruction execution was performed.
- Findings: the one-million startup summary adds no new watched control-register writes beyond the first 100,000 instructions. The two `0x10` runtime scenarios execute many `RTE`, `TRAP`, and SR operations and enter the instrumented source handler range; this is Gearmulator execution evidence only and is not instruction-by-instruction comparison against the target CPU.
- Blockers: WP-07's memory/MMIO packet remains in draft PR #13; WP-08 is pushed but the PR flow was previously blocked by GitHub connector 403, invalid CLI token, and signed-out browser. Physical target and external level-7 stimulus remain unavailable.
- Next action: use WP-07's reviewed map before mapping the startup operands/effects or choosing any control-register adaptation; extend bounded profiles across additional engines once this dependency is accepted. WP-08 still needs a draft PR from its compare link before WP-09 can rely on accepted evidence.
- Delivery: enclosing commit updates draft [PR #12](https://github.com/repeat98/octamachine/pull/12); keep it draft with the adaptation and physical gates open.

### 2026-09-24 / prompt 4 — extend profiles across engine families

- Request: continue WP-06 runtime coverage across representative Machinedrum engine families while preserving private firmware-derived traces.
- Starting state → ending state: `in_review` → `in_review`; the runtime evidence broadens, while the adaptation and physical-hardware criteria remain open.
- Owner / branch: Codex / `work/wp-06-coldfire-compatibility`, based on the pushed WP-06 branch head from prompt 3.
- Completed:
  - [x] Ran separate assignment/eight-hit profiles for TRX-SD (`0x11`), EFM-BD (`0x20`), and E12-BD (`0x30`); all exited 0 below the 1,000,000,000-instruction summary ceiling at 562,231,801; 562,249,453; and 562,158,592 instructions respectively.
  - [x] Ran trace scenarios for GND-SN (`0x01`), TRX-BD (`0x10`), TRX-SD (`0x11`), EFM-BD (`0x20`), E12-BD (`0x30`), and P-I-BD (`0x40`). Each exited 0 below the ceiling and the safe call-file aggregation reported 3,440–3,600 entries across two handler/return buckets per scenario.
  - [x] Kept detailed host/link/memory traces, firmware-derived addresses, and raw call rows under `/private/tmp`; only aggregate counters are included in the report.
  - [x] Confirmed the profiles cover five core engine families but do not identify all 44 descriptor handlers or compare the source instruction stream against the target CPU.
  - [x] Added `alignment_endian.S` to the firmware-free probe runner; both `m5206` and `cfv4e` match on aligned/odd byte, word, and long accesses and odd-address long-store readback.
  - [x] Tried to update the PR #12 description to reflect the new branch evidence; GitHub API returned 403 `Resource not accessible by integration`, so the PR body remains older than the branch/report.
- Remaining:
  - [ ] Extend coverage beyond the five sampled core engine families and test atomic instructions, cache behavior, and self-modifying code where supported by bounded probes.
  - [ ] Establish physical and device-memory alignment/byte-order behavior.
  - [ ] Map startup register operands/effects against WP-07's reviewed target map before selecting a patch or supervisor shim.
  - [ ] Resolve reset-vector fetch, external edge-sensitive level 7, and physical CPU behavior with a suitable board/hardware path.
- Changed files: `docs/reports/WP-06-coldfire.md`; this packet; `docs/STATUS.md`; `docs/COMPATIBILITY_MATRIX.md`; `docs/RESEARCH_LOG.md`; `tests/probes/wp06/alignment_endian.S`; `tests/probes/wp06/run.py`; `tests/probes/wp06/README.md`.
- Verification:
  - `md_profile <local OS 1.63 image> <private output> 0x11`, `0x20`, and `0x30`, each with `GEARMULATOR_MD_EXEC_SUMMARY_LIMIT=1000000000` — all exited 0 below the cap.
  - `md_profile <local OS 1.63 image> <private output> trace=0x01`, `trace=0x10`, `trace=0x11`, `trace=0x20`, `trace=0x30`, and `trace=0x40`, each with the same summary ceiling — all exited 0 below the cap; safe `awk` aggregation printed only unique-PC count, bucket count, and aggregate handler calls.
  - `python3 tests/probes/wp06/run.py --cc /opt/homebrew/bin/m68k-elf-gcc --qemu /private/tmp/octamachine-md-import/vendor/octemu/vendor/qemu/build/qemu-system-m68k` — passed. Both QEMU CPUs returned byte `0x12`, words `0x1234`/`0x3456`, longs `0x12345678`/`0x34567800`, and odd-store readback `0xa1b2c3d4`.
  - `make check` — passed: nine reference validations, Python compilation, 20 tests.
  - `git diff --check` — passed.
  - PR #12 remained open/draft at the pushed head `128730dd758cae6f430849bf96daaf0e7743afc5`. Its GitHub API description update attempt was denied with 403; no branch or PR content was rewritten.
- Findings: one-engine source summaries exercise a long common host runtime for all tested IDs; `trace=` scenarios also enter the instrumented handler range. Each output contained two handler/return buckets, so these aggregate counts do not prove broad descriptor-handler coverage. The two QEMU models agree on the tested odd-address data accesses and big-endian values; this is not physical evidence. All firmware profiles remain Gearmulator-only.
- Blockers: GitHub integration cannot edit PR metadata (403); the published branch and report are current but the PR body remains stale. The WP-07 map awaits review in draft PR #13; physical hardware/reset/level-7 evidence is unavailable.
- Next action: run bounded firmware-free probes for atomic/cache behavior where supported, then return to startup register adaptation after WP-07's map is accepted. Keep the PR body limitation explicit until GitHub write access is available.
- Delivery: enclosing commit updates draft [PR #12](https://github.com/repeat98/octamachine/pull/12); the PR description could not be synchronized due to the documented 403.

### 2026-09-24 / prompt 5 — complete core-family profile coverage

- Request: continue the overnight Machinedrum-to-Octatrack port after the maintainer's manual WP-05 squash merge; complete representative runtime profiles across the core engine families and keep derived traces private.
- Starting state → ending state: `in_review` → `in_review`; profiles now span all eight core families, while the startup adaptation and physical-hardware criteria remain open.
- Owner / branch: Codex / `work/wp-06-coldfire-compatibility`, based on pushed branch head `63f80e49da64eef6ca74ce93d6359bf58f6519ad`.
- Completed:
  - [x] Ran assignment/eight-hit profiles for GND-SN (`0x01`), P-I-BD (`0x40`), INP-GA (`0x50`), MID 01 (`0x60`), and CTR-AL (`0x70`); all exited 0 below the 1,000,000,000-instruction ceiling at 562,282,775; 562,301,574; 562,183,361; 562,194,086; and 562,162,921 instructions respectively.
  - [x] Ran trigger/encoder traces for INP-GA (`0x50`), MID 01 (`0x60`), and CTR-AL (`0x70`); all exited 0 below the ceiling at 559,644,338; 560,135,090; and 559,619,278 instructions. Safe aggregation reported 3,355; 3,680; and 3,408 handler-range entries, respectively; `0x50` formed one handler/return bucket and the other two formed two.
  - [x] Consolidated nine assignment/eight-hit profiles and nine traces across all eight core engine families in the report; the counters remain Gearmulator-only and do not claim all 44 descriptor handlers or target CPU execution.
  - [x] Kept firmware, raw host/link/memory traces, DSP traces, stdout, and address-bearing call rows under `/private/tmp`.
- Remaining:
  - [ ] Map the source startup-register operands/effects against WP-07's accepted memory/MMIO map before selecting any adaptation.
  - [ ] Expand executed coverage across the 44 descriptor handlers and establish atomic/cache/self-modifying-code behavior where observed.
  - [ ] Resolve device-memory alignment, reset-vector fetch, edge-sensitive level 7, and physical CPU behavior with suitable hardware or preserve them as explicit limits.
- Changed files: `docs/reports/WP-06-coldfire.md`; this packet; `docs/STATUS.md`; `docs/COMPATIBILITY_MATRIX.md`; `docs/RESEARCH_LOG.md`.
- Verification: `md_profile <local OS 1.63 image> <private output> <engine ID>` for `0x01`, `0x40`, `0x50`, `0x60`, and `0x70`, and `md_profile <local OS 1.63 image> <private output> trace=<engine ID>` for `0x50`, `0x60`, and `0x70`, each with `GEARMULATOR_MD_EXEC_SUMMARY_LIMIT=1000000000` — all exited 0 below the ceiling. Safe `awk` aggregation emitted only counts; no trace rows were published. `make check` passed (nine reference validations, Python compilation, and 20 tests); `git diff --check` passed; the local Markdown-link scan passed for all five changed documents. No target CPU or physical hardware run was available.
- Findings: the new scenarios extend the earlier TRX/EFM/E12/P-I/GND sample to INP, MID, and CTR; handler-range entries total 3,355–3,680 in these traces. These address-free totals do not identify a specific descriptor handler. The MID trace records 16 TRAPs while the other newly traced scenarios record six; source-model cause is not investigated.
- Blockers: WP-07's proposed memory/MMIO map remains in draft PR #13 pending review. The PR #12 description remains stale after the GitHub integration returned 403; the branch report is current. No physical hardware is available.
- Next action: continue bounded WP-06 runtime coverage, and resume startup-register operand/effect mapping only after WP-07's map is accepted.
- Delivery: enclosing commit updates draft [PR #12](https://github.com/repeat98/octamachine/pull/12); retain draft status while the adaptation and hardware gaps remain.

2026-09-23: [WP-35](WP-35-octamad-md-import.md) linked prior evidence in the current handoff. That was not a work prompt on this packet, and it changed no status or checklist item.
