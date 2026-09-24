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

- Completed: Reconciled WP-05 as accepted; profiled the first 100,000 executed Machinedrum startup instructions with a sanitized Gearmulator counter; added independent `m5206`/`cfv4e` instruction, exception, VBR, EUSP, and MOVEC probes; documented QEMU model gaps and reset/interrupt limits in the [WP-06 report](../reports/WP-06-coldfire.md).
- Remaining: Physical level-7 and reset-vector behavior; executed runtime instruction coverage; map the unshared startup register writes and their operands before selecting an adaptation.
- Next action: Start WP-07's memory/MMIO map reconciliation from the accepted WP-04 trace and MCF54455 register map; retain level 7 and reset-vector fetch as explicit model/hardware limits.
- Waiting on: None; WP-04 and WP-05 prerequisites are accepted.
- Blockers: Physical reset, interrupt, and register behavior cannot be confirmed without the actual target hardware. The target MCF54455 manual documents RAMBAR at a different MOVEC encoding from the MCF5206E and no source MBAR encoding; exact firmware operands/effects remain unrecorded. QEMU also lacks faithful models for these paths.
- Evidence: [WP-06 report](../reports/WP-06-coldfire.md); firmware-free probes and reproduction instructions in [`tests/probes/wp06/`](../../tests/probes/wp06/); sanitized startup-summary patch [0003](../../patches/gearmulator-md-mm/0003-opt-in-coldfire-execution-summary.patch). Prior WP-35 evidence remains static/Gearmulator-only and predates the WP-03 evidence contract.
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

2026-09-23: [WP-35](WP-35-octamad-md-import.md) linked prior evidence in the current handoff. That was not a work prompt on this packet, and it changed no status or checklist item.
