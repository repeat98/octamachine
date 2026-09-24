# Project status

Updated: 2026-09-24. Read this before claiming work. The [port plan](PORT_PLAN.md) defines gates and dependencies; each [packet record](PORT_PLAN.md#work-packet-index) owns its detailed status and checklist.

## Present state

Source reproduction and emulator baselines. The pinned Gearmulator Machinedrum model reaches repeated OS 1.63 firmware-ready, factory-initialized, and no-stimulus idle checkpoints. The unmodified Octatrack OS 1.40C now reaches the PTCH project screen headless and windowed in octemu, with a scripted PLAY/lamp/STOP response. **No Machinedrum boot on octemu or physical Octatrack has been demonstrated.** No ported DSP audio or flashable candidate is available.

### Established evidence

- [x] Reference index, contributor workflow, pinned octemu source, and separate emulator patches are in place.
- [x] Local firmware and research checkouts are ignored; proprietary inputs stay local.
- [x] Read-only image audit identifies the supplied 8 MiB MD UW OS 1.63 dump and its static reset vectors.
- [x] Reproduced the trace-instrumented Gearmulator `mdLib` build from the pinned parent source and relevant recursive dependency commits; see [WP-01 provenance report](reports/WP-01-provenance.md).
- [x] Capture and repeat the Machinedrum reference boot in Gearmulator, including firmware-ready, factory-initialized, and idle checkpoints; see the [WP-04 baseline report](reports/WP-04-md-baseline.md).
- [x] Capture and accept the unmodified Octatrack OS 1.40C headless/UI baseline in octemu; the source archive pin, boot state, panel response, host playback artifact, and merged delivery are documented in the [WP-05 report](reports/WP-05-ot-baseline.md).

Evidence: [WP-01 provenance report](reports/WP-01-provenance.md), [WP-02 profile report](reports/WP-02-target-profile.md), [WP-03 evidence contract](reports/WP-03-evidence.md), [WP-04 baseline report](reports/WP-04-md-baseline.md), [WP-05 baseline report](reports/WP-05-ot-baseline.md), [WP-06 CPU compatibility report](reports/WP-06-coldfire.md), [boot feasibility](BOOT_FEASIBILITY.md), [research log](RESEARCH_LOG.md), [compatibility matrix](COMPATIBILITY_MATRIX.md), accepted main through `148494c`.

## Active work and current handoff

[WP-00 — Planning, status, and agent handoff](work_packets/WP-00-planning-and-status.md) is done: [PR #2](https://github.com/repeat98/octamachine/pull/2) merged as `d8f8a76` on 2026-09-23. Its acceptance and delivery are reconciled in the packet record.

- [x] Expand the roadmap into 34 packets with outputs, prerequisites, and acceptance criteria.
- [x] Define gates, checkpoints, fidelity/evidence rules, and the hardware feasibility decision.
- [x] Add reusable handoff/status templates and require a checklist after every work prompt.
- [x] Pass document validation: 42 Markdown files, 240 local links/anchors, 34 packet IDs, acyclic dependencies, truthful initial states; `make check` and whitespace checks pass.
- [x] Accept/merge WP-00 and reconcile its status.

[WP-34 — Contributor documentation](work_packets/WP-34-contributor-documentation.md) is done: [PR #3](https://github.com/repeat98/octamachine/pull/3) merged as `6cdc258` on 2026-09-23; its acceptance and delivery are reconciled in the packet record.

- [x] Rewrite the README around the goal, current evidence, emulator roles, and contribution entry points.
- [x] Add a single getting-started guide and improve contributor, fixture, and compatibility guidance.
- [x] Document the verified main protection requirements and reconcile WP-00 acceptance.
- [x] Validate 51 Markdown files, 301 local links/anchors, 35 packet records, all 10 upstream links, and 15 shell examples; `make check` passes. Detailed results are in WP-34.
- [x] Reconcile maintainer merge and mark WP-34 done.

[WP-01 — Source provenance](work_packets/WP-01-source-provenance.md) is done on `work/wp-01-source-provenance`: [PR #4](https://github.com/repeat98/octamachine/pull/4) merged as `29471d01c61bbd8e83aa925157ae8fc4e25ddfa8` on 2026-09-23. Its source/build criteria and documentation checks pass; WP-04 and WP-05 now record the independent MD/OT emulator baselines. G0 awaits WP-05 delivery acceptance.

- [x] Record local reference and recursive dependency revisions, source modifications, patch hashes, toolchain, prerequisites, and license notices.
- [x] Apply the bus trace patch to a clean Gearmulator MD/MM worktree and build `mdLib` with pinned dependency contents.
- [x] Reconcile accepted delivery and mark WP-01 done.

WP-01 itself establishes source reproducibility only; the later runtime evidence is recorded separately under WP-04.

[WP-02 — Target profiles](work_packets/WP-02-target-profiles.md) is done: [PR #6](https://github.com/repeat98/octamachine/pull/6) merged as `e964334ef84790a16a5a500399d8c0f8a0c4e97f` on 2026-09-23. The local Machinedrum SPS-1UW OS 1.63 image matches all recorded reference fingerprints; WP-05 verifies the Octatrack OS distribution archive pin and runtime version. The physical hardware identity remains unavailable, so the selected Octatrack MKII emulator profile is provisional. See the [profile report](reports/WP-02-target-profile.md) and [shareable metadata](../tests/fixtures/machinedrum-sps1uw-os1.63.profile.json).

- [x] Identify the Machinedrum OS 1.63 raw image and document its model label, size, and matching public fingerprints.
- [x] Record the provisional Octatrack MKII emulator profile, feature inventory, deferred variants, and missing input consequences.
- [x] Submit the WP-02 branch for review.
- [x] Reconcile the accepted PR #6 merge.

No new firmware execution or hardware checkpoint is established by this profile inventory.

[WP-03 — Evidence contract](work_packets/WP-03-evidence-contract.md) is done: [PR #7](https://github.com/repeat98/octamachine/pull/7) merged at `2d13237cd9644a8f4574b3dc793f7ac03cd78685`. Versioned run manifests, JSONL capture rules, a first-divergence comparator, and synthetic outcome tests are documented in the [WP-03 report](reports/WP-03-evidence.md). Its checks establish tooling behavior with synthetic events only.

- [x] Define the four initial-state modes, ordered stimulus timing, clock metadata, PC semantics, limits, and stop outcomes.
- [x] Require matching comparison plans and report the first field/event divergence.
- [x] Exercise equivalent, divergent, missing, failed, and truncated inputs with synthetic fixtures.
- [x] Run the synthetic checks through `make check`.
- [x] Merge WP-03 after required CI checks pass.

[WP-04 — Machinedrum baseline](work_packets/WP-04-machinedrum-baseline.md) is done: [PR #9](https://github.com/repeat98/octamachine/pull/9) merged as `fb2c29d07f6d0468944fa5d80c960fb7e387e6ec`. The [baseline report](reports/WP-04-md-baseline.md) records two matching full MMIO runs, bounded cold/cached boot checkpoints, failure handling, and passing WP-03 comparisons of the repeated cold and cached manifests. Raw traces remain private and local.

- [x] Reach named firmware-ready, factory-initialized, and no-stimulus idle checkpoints under finite frame and wall-clock limits.
- [x] Compare two repeated blank-flash runs and separately labeled cached starts; event order and checkpoint metadata match.
- [x] Capture reset, SIM, both DSP HI08 boot streams, panel startup, and idle scheduler progress.
- [x] Prove trace cap, missing-image, and stalled-driver outcomes report failure or incomplete evidence.
- [x] Pass required GitHub checks, merge PR, and reconcile the accepted delivery.

[WP-05 — Octatrack baseline](work_packets/WP-05-octatrack-baseline.md) is done: [PR #11](https://github.com/repeat98/octamachine/pull/11) squash-merged as `148494c212d2d11fd21ad58f56c44b324d4c91bb`. The [report](reports/WP-05-ot-baseline.md) and two WP-03 metadata pairs record OS 1.40C reaching `PTCH` headless and windowed, with a scripted PLAY/lamp/STOP response. The official distribution archive matched octemu's pin. The emulator's live monitor showed host-side pitch/underflow artifacts; no audio parity or hardware behavior is claimed.

- [x] Verify the pinned OS archive and build the pinned octemu/QEMU/DSP sources.
- [x] Reach the PTCH screen and complete the panel walk under bounded headless and windowed runs.
- [x] Map CPU, DSP, panel, storage, and audio interfaces to the pinned source.
- [x] Separate guest audio-block timing from host timeout/playback behavior; keep private inputs and captures local.
- [x] Merge PR #11 and reconcile the accepted delivery.

[WP-06 — ColdFire compatibility](work_packets/WP-06-coldfire-compatibility.md) is in review in draft [PR #12](https://github.com/repeat98/octamachine/pull/12) on `work/wp-06-coldfire-compatibility`; its `scaffold` and GitGuardian checks pass. The [report](reports/WP-06-coldfire.md) and firmware-free probes compare selected MCF5206E/CFV4e arithmetic, exception, privilege, level-4 interrupt-mask, VBR, EUSP, and startup MOVEC behavior. The source startup prefix records ten control-register writes. Manual comparison shows the source and target RAMBAR encodings differ; target ACR/CACR facilities exist despite QEMU model gaps. Reset-vector fetch, external edge-sensitive level 7, adaptation selection, wider runtime coverage, and physical behavior remain open.

- [x] Reproduce the first 100,000 executed Machinedrum startup instructions as a sanitized Gearmulator summary; the local firmware and raw traces remain private.
- [x] Compare selected arithmetic, stack, trap/RTE, and privilege behavior on the `m5206` and `cfv4e` QEMU CPU models.
- [ ] Resolve reset-vector fetch and external level-7 comparisons, check adaptation mechanisms against target facilities and privilege, and extend runtime coverage.
- [ ] Establish physical CPU/control-register behavior.

## Gate checklist

- [x] G0: reproducible source/target profiles and MD/OT baseline captures — WP-00–05.
- [ ] G1: accepted hardware-realizable architecture — WP-06–10.
- [ ] G2: target bootstrap, host services, original DSP payloads, panel transport, live audio — WP-11–18.
- [ ] G3: integrated behavior, fidelity, load/fault coverage — WP-19–28.
- [ ] G4: local candidate and board-specific recovery readiness — WP-29.
- [ ] G5: authorized physical startup and parity evidence — WP-30–31.
- [ ] G6: independent reproduction and supported-profile delivery — WP-32.

Link the report and accepted revision when checking a gate. Skipped runs do not satisfy a gate.

## Next dispatch queue

WP-04 and WP-05 are accepted, and WP-35's import and c10 follow-up are merged. WP-06's current report bounds the reset-fetch and external level-7 test-board gaps and maps the startup control-register encodings; runtime handler coverage and adaptation selection remain open. WP-07 can now reconcile the source/target memory and peripheral map from accepted WP-04/WP-05 evidence, followed by WP-08's DSP upload inventory. WP-35 remains Gearmulator-only prior evidence and does not replace those packet checks.

1. [WP-07 — Memory and MMIO](work_packets/WP-07-memory-and-mmio.md): build the source/target register and address contract from the accepted WP-04 trace, WP-05 target profile, and WP-06 startup register names.
2. [WP-06 — ColdFire compatibility](work_packets/WP-06-coldfire-compatibility.md): extend executed runtime coverage and revisit startup adaptation after WP-07 maps the register effects.

Use the [handoff template](templates/AGENT_HANDOFF.md) with one packet's scope and explicit file ownership.

[WP-35 — octamad Machinedrum import](work_packets/WP-35-octamad-md-import.md) is done. Import [PR #8](https://github.com/repeat98/octamachine/pull/8) merged as `a5d53264a68015b5d6d057079e41d535ed9b98e5`; c10 replay follow-up [PR #10](https://github.com/repeat98/octamachine/pull/10) merged as `711ca1114190ebaf4d7c04a834353d3ff6e0ec12` after required checks passed. Its excursion remains Gearmulator-only evidence and adds no roadmap prerequisite.

## Cross-cutting unknowns and blockers

| Item | Current evidence | Owner / next action |
| --- | --- | --- |
| Source reproduction and reference startup | WP-01 records recursive revisions and clean builds; WP-04 records repeated MD startup traces/checkpoints in Gearmulator; WP-05 records unchanged OS 1.40C reaching `PTCH` and a scripted panel response in octemu and is accepted in `148494c` | Continue WP-06; neither emulator establishes physical parity |
| Exact target profile | WP-02 documents octemu's Octatrack MKII/MCF54455 profile; WP-05 verifies the OS 1.40C distribution archive pin and boots the extracted image. Physical board/carrier identity remains unavailable | Keep the hardware profile provisional; physical identification stays open for later hardware gates |
| Octatrack panel response | measured (octemu only) | A bounded windowed run accepted PLAY and STOP; the panel screenshot shows a PLAY indicator and lit sequencer lamp. This is one scripted path, not full control coverage. See [WP-05](reports/WP-05-ot-baseline.md). | [WP-05](work_packets/WP-05-octatrack-baseline.md), [WP-18](work_packets/WP-18-panel-protocol.md), [WP-20](work_packets/WP-20-control-surface.md) |
| Source map disagreements | HI08 addresses, SRAM size, CPU clock differ across references; [WP-35](reports/WP-35-octamad-md-import.md) adds static firmware evidence for the HI08 map | WP-07 resolves with traces/primary sources |
| Target execution strategy | CPU/DSP similarity alone does not establish a port. [WP-35](reports/WP-35-octamad-md-import.md): both MD DSP programs execute from external RAM, which the DSP56721 lacks. Voice-DSP relocation is demonstrated in the reference, and the E12 samples cannot be DSP-resident | WP-06–10 assess and choose a realizable mechanism, starting from the WP-35 ledger candidates |
| Distribution | WP-01 records source notices and octemu's stated combined-QEMU restriction; no octamachine-wide license is declared | WP-32 follows the recorded notices and any maintainer decision |
| Physical validation/recovery | No hardware test or recovery proof exists | WP-29–31 after emulator gates and explicit hardware authorization |

These are open project questions. Mark an individual packet blocked only when a specific condition actually prevents its next action.

## Update after every work prompt

Update this overview and the assigned packet **in the same commit as the work**. Preserve other active owners' entries. The packet is the detailed source of truth; keep this file focused on project-wide changes and the next queue.

- [ ] Reconcile any previously merged PR and dependency changes.
- [ ] Record packet owner, branch, current lifecycle state, and last update.
- [ ] Check only completed criteria backed by evidence.
- [ ] Append prompt history with completed/remaining checklists, commands/results, blockers, and precise next action.
- [ ] Update this overview's active work, gate evidence, and next dispatch queue.
- [ ] Commit/push the scoped work and report delivery status plus the remaining checklist in the final reply.

A blocked work prompt still leaves an entry saying what was attempted and what unblocks it. Pure questions/status replies do not need artificial file edits or empty commits.
