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

- Completed: Built and ran the pinned patched QEMU against firmware-free probes for CAS, RAM code writes, and cache-control/CACR model paths. The 68020 control executes CAS.L; m5206/cfv4e take vector 4 and report the unchanged CAS target. Both ColdFire models execute replacement RAM code after a write. They execute supervisor CPUSHL.L and CACR writes, then take vector 4 on CACR read. User-mode probes take vector 8 for CPUSHL, CACR writes, and ACR0 writes and vector 4 for CACR reads; each records the expected stacked PC, frame SP, and unchanged sentinel. These remain pinned-QEMU results, not physical cache or register measurements.
- Remaining: Map startup register operands/effects after WP-07 memory/MMIO map acceptance; determine whether source firmware uses CAS or code modification; characterize cache-control effects and physical/device-memory behavior; pursue address-safe attribution across the 44 descriptor handlers; preserve reset, level-7, and physical CPU limits.
- Next action: After WP-07 map acceptance, map source startup register effects and compare candidate adaptation mechanisms with target facilities and privilege rules. Continue only bounded cache-control or firmware-use work that adds address-safe evidence. PR #12 remains the delivery target; keep it in draft pending review and packet acceptance.
- Waiting on: WP-07's map is available in draft PR #13 and awaits review/acceptance; WP-04 and WP-05 prerequisites are accepted.
- Blockers: No physical target is available for silicon, device-memory, reset-vector, or edge-sensitive level-7 measurements. Gearmulator source/image inputs remain unavailable here. Earlier GitHub merge attempts returned 403; the WP-06 push succeeded, but PRs #12 and #13 remain open drafts pending review and acceptance.
- Evidence: [WP-06 report](../reports/WP-06-coldfire.md); probes under [tests/probes/wp06](../../tests/probes/wp06/); startup-summary patch [0003](../../patches/gearmulator-md-mm/0003-opt-in-coldfire-execution-summary.patch). Gearmulator profile traces remain local.
- Delivery: Cache-control evidence commit 1b34de1eeaa9753999ea2f818799a337faecf7d5 was pushed to work/wp-06-coldfire-compatibility and remains included in PR #12. The current head's reported scaffold and GitGuardian checks pass; the PR remains a draft pending review and acceptance.

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

### 2026-09-24 / prompt 6 — profile all core synthesis IDs

- Request: finish the active WP-06 profile sweep, preserve firmware-derived traces locally, and continue the port after reconciling accepted deliveries.
- Starting state → ending state: `in_review` → `in_review`; assignment/eight-hit profiles now cover every core synthesis ID, while startup adaptation, descriptor attribution, and physical-hardware criteria remain open.
- Owner / branch: Codex / `work/wp-06-coldfire-compatibility`, based on pushed branch head `a9f15d7701feb14b5f4ab9375928784c3f7a8b67`.
- Completed:
  - [x] Ran assignment/eight-hit profiles for all 50 core synthesis IDs (`0x01–0x03`, `0x10–0x1d`, `0x20–0x27`, `0x30–0x3f`, and `0x40–0x48`). The runs exited 0 below the 1,000,000,000-instruction ceiling; totals ranged from 562,087,831 to 562,321,559, RTE counts from 139,028 to 139,497, and every run recorded 12 TRAPs.
  - [x] Confirmed the complete core set by asserting the expected 50 IDs against the local engine catalog. A first `0x12` attempt used a non-instrumented binary and emitted no execution summary; it was discarded and rerun with the instrumented binary, which exited 0 at 562,177,565 instructions.
  - [x] Consolidated the 50 rows in the [WP-06 report](../reports/WP-06-coldfire.md), alongside the three existing INP/MID/CTR assignment runs and nine trigger/encoder traces. The counters remain Gearmulator-only and do not attribute calls to all 44 descriptor handlers or compare execution with the target CPU.
  - [x] Kept the OS image, raw output, and detailed trace products under `/private/tmp`; no firmware or capture data entered the repository.
- Remaining:
  - [ ] Map startup-register operands/effects against WP-07's accepted memory/MMIO map before selecting any adaptation.
  - [ ] Attribute runtime calls across the 44 descriptor handlers; investigate atomic/cache/self-modifying-code and device-memory behavior where bounded probes can provide evidence.
  - [ ] Resolve device-memory behavior, reset-vector fetch, edge-sensitive level 7, and physical CPU behavior with suitable hardware or preserve them as explicit limits.
- Changed files: `docs/reports/WP-06-coldfire.md`; this packet; `docs/STATUS.md`; `docs/COMPATIBILITY_MATRIX.md`; `docs/RESEARCH_LOG.md`.
- Verification: all 43 newly scheduled engine runs exited 0 below the ceiling; the previously incorrect non-instrumented `0x12` attempt was discarded and its instrumented rerun succeeded. Safe local aggregation asserted the exact 50-ID set and reported only aggregate counts. `make check` passed (nine reference validations, Python compilation, 20 tests); `git diff --check` and the local Markdown-link scan passed. GitHub Actions Checks run 57 passed for pushed head `d57c4578205c256f045f197bfc1480a259d4f16b`; no separate combined-status contexts were reported. No target CPU or physical hardware run was available.
- Findings: every core synthesis assignment profile recorded 12 TRAPs and approximately 562.1–562.3 million executed source instructions. The range is consistent across IDs but does not establish instruction-by-instruction CFV4e compatibility or per-descriptor handler coverage. The earlier nine traces still provide aggregate handler-range activity across all eight source engine families.
- Blockers: WP-07's map remains in draft PR #13 pending review. The PR #12 description remains stale because GitHub integration metadata writes returned 403; the draft stays open because the adaptation criterion is incomplete. No physical hardware is available.
- Next action: continue with WP-07 review/acceptance and its memory/MMIO map; then map startup register effects and consider safe per-handler attribution. Keep WP-06 in review until the adaptation and physical gates are addressed.
- Delivery: enclosing commit updates draft [PR #12](https://github.com/repeat98/octamachine/pull/12); retain draft status while acceptance gaps remain.

2026-09-23: [WP-35](WP-35-octamad-md-import.md) linked prior evidence in the current handoff. That was not a work prompt on this packet, and it changed no status or checklist item.

### 2026-09-24 / prompt 7 — reconcile merge requests and continue WP-06

- Request: merge the open pull requests, then continue the Machinedrum-to-Octatrack port in this repository.
- Starting state -> ending state: in_review -> in_review; the requested merges did not change remote state and WP-06 remains a draft with open acceptance work.
- Owner / branch: Codex / work/wp-06-coldfire-compatibility, continued from remote head 3dcb1586f918e86b8b168aeb0deeab8c6ed53a48; main and the working tree were clean before switching branches.
- Completed:
  - [x] Fetched current main and the active WP-06/WP-07/WP-08 branches; origin/main remains 148494c212d2d11fd21ad58f56c44b324d4c91bb.
  - [x] Reconciled PR #12 at head 3dcb1586f918e86b8b168aeb0deeab8c6ed53a48 and PR #13 at head dfa80bb372d4888db483efb7cedc5371fab7acec; both are open, draft, mergeable, have no review submissions or unresolved review threads, and their GitHub Actions Checks runs passed (runs 59 and 47 respectively).
  - [x] Attempted squash merges with expected head SHAs for both PRs. Each GitHub API call returned 403 Resource not accessible by integration; neither PR merged and neither remote branch changed.
  - [x] Attempted to push the WP-06 update to origin; GitHub returned 403 Permission to repeat98/octamachine.git denied to Aquitronic, so the commit remains local and the remote branch head is unchanged.
  - [x] Continued on the existing WP-06 PR branch. Confirmed the pinned octemu submodule is uninitialized, vendor/gearmulator-md-mm and the documented OS 1.63 input path are absent, and m68k-elf-gcc / qemu-system-m68k are not on the local WSL PATH.
- Remaining:
  - [ ] GitHub write/merge access is still needed; keep PRs #12 and #13 in draft while G1 and WP-06 acceptance remain open.
  - [ ] Resume WP-06 startup-register mapping after WP-07's map is accepted and the local source/toolchain inputs are available.
  - [ ] Continue bounded atomic/cache/device-memory probes and preserve reset-vector, level-7, and physical CPU limits explicitly.
- Changed files: this packet and docs/STATUS.md.
- Verification:
  - WSL make check passed: nine reference repositories validated, Python scripts compiled, and all 20 tests passed.
  - Windows Git diff --check passed for the two intended files. WSL Git treated the Windows-mounted checkout's CRLF endings as whitespace across the tree; its result was not used for the final whitespace check.
  - GitHub Actions Checks runs 59 and 47 passed for the reviewed heads of PRs #12 and #13; no review submissions or review threads are present.
  - No new emulator probe was run because the pinned source checkout, local firmware input, cross-compiler, and QEMU binary are unavailable in this workspace.
- Findings: PR #12 and #13 have passing scaffold checks but remain drafts; successful workflow runs and GitHub's mergeable field do not resolve their open packet criteria or G1. The GitHub integration's 403 is an access limitation, not a merge result.
- Blockers: GitHub merge/write operations are unavailable to this integration. No local WP-06 runtime inputs or CPU-model binaries are present.
- Next action: restore GitHub write access and review/accept WP-07 when its broader G1 hold is cleared; then continue WP-06 with the accepted map and a provisioned probe toolchain.
- Delivery: the local commit records this reconciliation for draft PR #12; push to origin was denied with 403, and no PR was merged.

### 2026-09-24 / prompt 8 — inspect pinned QEMU atomic/cache paths

- Request: continue WP-06, initialize and inspect the pinned CPU-model source, add bounded compatibility evidence, and keep packet/status records current.
- Starting state -> ending state: in_review -> in_review; the source audit adds model-coverage findings, while all runtime, adaptation, and hardware acceptance gaps remain open.
- Owner / branch: Codex / work/wp-06-coldfire-compatibility, starting at local commit 284dbe31c527cc8d4e2cad401f5072e83e1785f4; origin/main remains 148494c212d2d11fd21ad58f56c44b324d4c91bb.
- Completed:
  - [x] Initialized vendor/octemu at pinned commit 87000189418c8ca2026dc047bda220b66802809d; confirmed the parent repository submodule pointer is unchanged.
  - [x] Fetched QEMU base e8d693e12af9cbb89d724baadfcc08559669e279 into /tmp/octamachine-qemu-audit and applied all 13 octemu patches successfully.
  - [x] Inspected the pinned m5206/cfv4e CPU feature initializers, cf_movec_to, cache-instruction translator bodies, TCG code-page invalidation, and octemu patch 0008. Added the source-level findings to the report and research log without claiming firmware use or physical behavior.
  - [x] Found m68k-elf-gcc at /home/jannikassfalg/.local/bin/m68k-elf-gcc; the earlier prompt's statement that the compiler and submodule were absent is superseded.
- Remaining:
  - [ ] Run synthetic atomic/cache/self-modifying-code probes against a built copy of the exact pinned model.
  - [ ] Map startup register operands/effects after WP-07's map is accepted; attribute execution across all 44 descriptor handlers only if instrumentation can remain address-safe.
  - [ ] Resolve reset-vector, level-7, device-memory, and physical CPU behavior through suitable board/hardware evidence or retain them as explicit limits.
- Changed files: docs/reports/WP-06-coldfire.md; this packet; docs/RESEARCH_LOG.md; docs/STATUS.md.
- Verification:
  - Exact QEMU base fetched and all 13 octemu patches applied in the temporary source checkout; no build output or source changes were added to the repository.
  - m68k-elf-gcc is present. qemu-system-m68k, Meson, Ninja, pkg-config, and the built DSP56300 archive are absent, so the new CPU probes could not be executed. No firmware-derived input was available.
  - WSL make check passed: nine reference validations, Python compileall, and all 20 tests. Native Windows Git diff --check passed; WSL Git line-ending warnings on the Windows-mounted checkout were not used.
- Findings: the source feature tables do not enable CAS/CAS2 for either tested QEMU model; ACR writes remain TODO, cache-operation bodies have no implementation there, and the TCG patch preserves invalidation for stores overlapping translated code. These are QEMU source observations only. They neither show that the firmware executes those paths nor establish physical MCF54455 behavior.
- Blockers: the pinned QEMU build prerequisites and local Gearmulator/firmware inputs are unavailable; physical reset, level-7, and CPU behavior still require hardware/model evidence. GitHub write/merge access previously returned 403.
- Next action: after WP-07 acceptance, map source startup effects against its memory/MMIO map; provision the pinned QEMU build dependencies and run bounded firmware-free CPU probes. Keep PR #12 in draft while acceptance gaps remain.
- Delivery: the enclosing local commit updates the WP-06 report and draft PR #12 branch; pushing it to origin returned 403 Permission to repeat98/octamachine.git denied to Aquitronic. The remote PR head remains unchanged.


### 2026-09-24 / prompt 9 - run pinned-QEMU CAS and code-coherence probes

- Request: continue the active WP-06 goal and make additional bounded compatibility progress.
- Starting state -> ending state: in_review -> in_review; the pinned QEMU source is now built locally and the new synthetic model checks pass, while adaptation and physical acceptance criteria remain open.
- Owner / branch: Codex / work/wp-06-coldfire-compatibility, continuing from local commit 97f04f8f7e7826f24114c18d1d9a3121fb77aa7a; origin/main remains 148494c212d2d11fd21ad58f56c44b324d4c91bb.
- Completed:
  - [x] Built the exact QEMU base e8d693e12af9cbb89d724baadfcc08559669e279 with all 13 octemu patches and the pinned DSP dependency archives. The parent octemu submodule pointer remains unchanged.
  - [x] Ran the expanded firmware-free runner. The 68020 CAS control changed memory to 0x87654321; m5206 and cfv4e took vector 4 and reported unchanged target memory 0x12345678.
  - [x] Ran the RAM code-write probe on m5206 and cfv4e; both returned 1 before the write and 2 afterward.
  - [x] Reran the existing arithmetic/exception, alignment, interrupt, EUSP, and MOVEC probes; all passed. Added both new sources to the integrated runner and documented the QEMU-only limits.
  - [x] Updated the WP-06 report, compatibility matrix, research log, this packet, and project status.
- Remaining:
  - [ ] Map startup register operands/effects after WP-07 map acceptance; confirm candidate adaptation against target facilities and privilege constraints.
  - [ ] Characterize cache-control effects, physical/device-memory alignment, and whether firmware uses CAS or modifies code.
  - [ ] Attribute execution across the 44 descriptor handlers only if address-safe instrumentation supports it; preserve reset, level-7, and physical CPU limits.
- Changed files: tests/probes/wp06/run.py; tests/probes/wp06/cas_model.S; tests/probes/wp06/self_modifying_code.S; tests/probes/wp06/README.md; docs/reports/WP-06-coldfire.md; docs/COMPATIBILITY_MATRIX.md; docs/RESEARCH_LOG.md; this packet; docs/STATUS.md.
- Verification:
  - make -C vendor/octemu setup - passed and built the pinned DSP archives.
  - QEMU configure used QEMU_EXTRA_CONFIGURE=--disable-werror; compilation reached step 1,472 of 1,473, then the stock final link failed because the pinned board patch adds -lc++ and the temporary GLib/Pixman dependency links lacked host runtime/private libraries. A local generated build.ninja adjustment omitted -lc++, added the DSP VTune archive and required static GLib dependencies, and resolved Pixman; direct Ninja linking passed. The generated changes are outside tracked source.
  - QEMU machine help listed an5206 and octatrack; ldd reported no unresolved runtime libraries.
  - python3 tests/probes/wp06/run.py --cc /home/jannikassfalg/.local/bin/m68k-elf-gcc --qemu /home/jannikassfalg/octamachine/vendor/octemu/vendor/qemu/build/qemu-system-m68k - passed, including CAS control/ColdFire vector results and updated RAM instruction results.
  - make check - passed: nine reference repositories validated, Python scripts compiled, and all 20 tests passed. git diff --check - passed. No firmware or physical hardware was used.
- Findings: these results characterize the pinned QEMU CPU profiles and TCG translation invalidation only. CAS rejection is not evidence of silicon incompatibility; successful RAM code modification is not a physical instruction-cache measurement. Cache-control effects and firmware instruction use remain unresolved.
- Blockers: no physical hardware; WP-07 map acceptance remains prerequisite for startup register adaptation; GitHub write/merge access returned 403 in the prior prompt and both PRs remain drafts.
- Next action: after WP-07 review/acceptance, map the source startup register effects; keep bounded emulator evidence separate from the future hardware gate.
- Delivery: Draft PR #12 remains the delivery target. The enclosing commit hash and push result are reported in the final response.


### 2026-09-24 / prompt 10 - measure pinned-QEMU cache-control paths

- Request: continue WP-06 with bounded cache-control and CACR evidence while WP-07 map acceptance remains pending.
- Starting state -> ending state: in_review -> in_review; the pinned model's supervisor CPUSHL and CACR control paths are now measured, while physical cache effects and startup adaptation remain open.
- Owner / branch: Codex / work/wp-06-coldfire-compatibility, continuing from local commit 68e82c2a09d145415893bc37dac735cc61b89885; cache-control evidence commit 1b34de1eeaa9753999ea2f818799a337faecf7d5 was pushed to origin during this prompt and remains included in PR #12; its latest reported checks pass.
- Completed:
  - [x] Inspected pinned QEMU source: CPUSHL translator bodies are no-ops; ColdFire CACR writes store the value and switch stack as needed; generic CACR reads are enabled only for 68020/030/040/060 feature profiles.
  - [x] Added cache_control.S and integrated it into the runner. Both m5206 and cfv4e execute supervisor CPUSHL.L and a CACR write, then take vector 4 on CACR read; the probe confirms the CACR read did not complete and the synthetic memory sentinel remained 0x13579bdf.
  - [x] Updated the WP-06 report, probe README, compatibility matrix, research log, packet, and project status; retained the cache-effects checklist as incomplete.
- Remaining:
  - [ ] Establish physical cache-control effects and whether firmware uses these paths.
  - [ ] Map startup register operands/effects after WP-07 map acceptance and check adaptation against target facilities and privilege constraints.
  - [ ] Attribute execution across the 44 descriptor handlers only if address-safe instrumentation supports it; preserve reset, level-7, device-memory, and physical CPU limits.
- Changed files: tests/probes/wp06/cache_control.S; tests/probes/wp06/run.py; tests/probes/wp06/README.md; docs/reports/WP-06-coldfire.md; docs/COMPATIBILITY_MATRIX.md; docs/RESEARCH_LOG.md; this packet; docs/STATUS.md.
- Verification:
  - The integrated runner passed with m68k-elf-gcc and the pinned QEMU binary. The cache-control result block matched on m5206/cfv4e: CPUSHL returned, CACR write returned, CACR read took vector 4, read completion remained zero, and memory remained 0x13579bdf.
  - make check passed: nine reference repositories validated, Python scripts compiled, and all 20 tests passed.
  - git diff --check passed. The QEMU source/build tree and submodule pin were unchanged; no firmware or physical hardware was used.
- Findings: pinned QEMU models decode and execute supervisor CPUSHL but the translator body performs no cache operation. They accept a CACR write and take vector 4 when reading CACR. These observations characterize the emulator implementation; no physical cache state or firmware use was measured.
- Blockers: physical cache/register behavior remains unavailable; WP-07 map acceptance is still required for startup adaptation; earlier GitHub merge attempts returned 403 and PR #12 remains a draft pending review and acceptance.
- Next action: after WP-07 map acceptance, map the source startup register effects; keep cache-instruction decode/readback results separate from physical cache conclusions.
- Delivery: cache-control evidence commit 1b34de1eeaa9753999ea2f818799a337faecf7d5 was pushed to origin and remains included in PR #12. The current head's reported scaffold and GitGuardian checks pass; no review acceptance or merge has occurred, so the PR remains a draft.

### 2026-09-24 / prompt 11 — measure user-mode cache-control exceptions

- Request: continue WP-06 with bounded pinned-QEMU user-mode privilege evidence for CPUSHL and CACR MOVEC paths; do not claim physical behavior.
- Starting state -> ending state: in_review -> in_review; user-mode exception dispatch is now measured in the pinned models, while target adaptation and physical acceptance remain open.
- Owner / branch: Codex / work/wp-06-coldfire-compatibility, continuing from pushed commit 7b23ad71d40d57ea712053029d662e6974edd1b9; origin/main remains 148494c212d2d11fd21ad58f56c44b324d4c91bb.
- Completed:
  - [x] Added user_privilege_cache.S and integrated three independent user-mode cases into the WP-06 runner for CPUSHL, CACR write, and CACR read on m5206 and cfv4e.
  - [x] Verified vector 8 for user-mode CPUSHL and CACR write and vector 4 for CACR read on both models. Each of the six cases records one exception, a stacked PC matching the instruction address, frame SP 0x7ef8 from pre-exception SP 0x7f00, and unchanged sentinel 0x13579bdf.
  - [x] Updated the probe guide, WP-06 report, compatibility matrix, research log, packet handoff/history, and status. Reconciled WP-08's draft PR #14 in the project overview.
- Remaining:
  - [ ] Map startup register operands/effects against WP-07's accepted memory/MMIO map and check any adaptation against target facilities and privilege rules.
  - [ ] Establish physical cache-control effects and whether firmware uses these paths; preserve device-memory, reset-vector, level-7, and physical CPU limits.
  - [ ] Attribute execution across all 44 descriptor handlers only if address-safe evidence supports it.
- Changed files: tests/probes/wp06/run.py; tests/probes/wp06/user_privilege_cache.S; tests/probes/wp06/README.md; docs/reports/WP-06-coldfire.md; docs/COMPATIBILITY_MATRIX.md; docs/RESEARCH_LOG.md; this packet; docs/STATUS.md.
- Verification:
  - python3 tests/probes/wp06/run.py --cc /home/jannikassfalg/.local/bin/m68k-elf-gcc --qemu /home/jannikassfalg/octamachine/vendor/octemu/vendor/qemu/build/qemu-system-m68k — passed. The complete integrated suite passed; the new six cases reported vector/frame/SP/PC/sentinel values described above.
  - make check — passed: nine reference validations, Python compileall, and all 20 tests.
  - git -c core.autocrlf=true diff --check — passed. The QEMU source/build tree and submodule pin are unchanged; no firmware or physical hardware was used.
- Findings: user-mode CPUSHL and MOVEC D0-to-CACR raise vector 8 in both pinned profiles. MOVEC CACR-to-D1 raises vector 4, consistent with the current QEMU ColdFire feature gate for CACR reads. These are emulator results and do not establish physical exception priority, cache effects, or firmware use.
- Blockers: WP-07 map acceptance still gates startup-register adaptation. No physical target is available for silicon, device-memory, reset-vector, or edge-sensitive level-7 measurements.
- Next action: after WP-07 map acceptance, map source startup register effects and compare adaptation candidates with target facilities and privilege rules; keep PR #12 draft until review and packet acceptance.
- Delivery: enclosing commit advances the WP-06 branch and updates draft PR #12; report the resulting commit and push status after commit.


### 2026-09-24 / prompt 12 — measure user-mode ACR0 privilege behavior

- Request: continue WP-06 with a firmware-free user-mode ACR0 MOVEC probe on the pinned ColdFire QEMU models.
- Starting state -> ending state: in_review -> in_review; the ACR0 user-mode exception path is now measured, while target adaptation and physical acceptance remain open.
- Owner / branch: Codex / work/wp-06-coldfire-compatibility, continuing from pushed commit b4c269eeeb7ee0fe8a219f9d36dbaaf002cf9e80; origin/main remains 148494c212d2d11fd21ad58f56c44b324d4c91bb.
- Completed:
  - [x] Added an independently authored MOVEC D0-to-ACR0 user-mode case to user_privilege_cache.S and integrated it into run.py for m5206 and cfv4e.
  - [x] Ran the expanded integrated QEMU probe. Both profiles take vector 8 for ACR0 writes; each case records one exception, the expected instruction PC 0x0001006c, frame SP 0x7ef8 from 0x7f00, and unchanged sentinel 0x13579bdf.
  - [x] Updated the probe guide, WP-06 report, compatibility matrix, research log, packet handoff/history, and status with model-only scope and limits.
- Remaining:
  - [ ] Map startup register operands/effects against WP-07's accepted memory/MMIO map and check adaptation against target facilities and privilege rules.
  - [ ] Establish physical cache-control and ACR effects, firmware use, and physical CPU behavior; preserve device-memory, reset-vector, and external level-7 limits.
  - [ ] Attribute execution across all 44 descriptor handlers only if address-safe evidence supports it.
- Changed files: tests/probes/wp06/run.py; tests/probes/wp06/user_privilege_cache.S; tests/probes/wp06/README.md; docs/reports/WP-06-coldfire.md; docs/COMPATIBILITY_MATRIX.md; docs/RESEARCH_LOG.md; this packet; docs/STATUS.md.
- Verification:
  - python3 tests/probes/wp06/run.py --cc /home/jannikassfalg/.local/bin/m68k-elf-gcc --qemu /home/jannikassfalg/octamachine/vendor/octemu/vendor/qemu/build/qemu-system-m68k — passed on the pinned AN5206 QEMU machine with m5206/cfv4e profiles. The new ACR0 results match the expected vector 8, one exception, stacked PC, frame SP, and sentinel.
  - make check — passed: nine reference repositories validated, Python compilation passed, and all 20 tests passed.
  - git diff --check — passed on the reviewed working-tree diff; no whitespace errors. The octemu/QEMU submodule pin is unchanged; no firmware or physical hardware was used.
- Findings: user-mode MOVEC D0-to-ACR0 raises vector 8 on both pinned QEMU profiles. This is consistent with the MCF54455 manual's supervisor-only ACR access classification ([reference manual](https://www.nxp.com/docs/en/reference-manual/MCF54455RM.pdf)), but does not measure supervisor ACR write effects, physical cache/address behavior, or Machinedrum firmware use.
- Blockers: WP-07 map acceptance still gates startup-register adaptation. No physical target is available for silicon, device-memory, reset-vector, or edge-sensitive level-7 measurements.
- Next action: commit and push this prompt's packet update to PR #12, keep it draft pending review/packet acceptance, then after WP-07 map acceptance map source startup register effects.
- Delivery: this prompt's evidence and packet/status records are included in the enclosing commit; report its hash after committing.
