# Project status

Updated: 2026-09-23. Read this before claiming work. The [port plan](PORT_PLAN.md) defines gates and dependencies; each [packet record](PORT_PLAN.md#work-packet-index) owns its detailed status and checklist.

## Present state

Scaffolding, feasibility research, and source reproduction. A clean trace-instrumented Gearmulator `mdLib` build is now reproduced. **No Machinedrum boot on octemu or Octatrack hardware has been demonstrated.** No ported DSP audio or flashable candidate is available.

### Established before the expanded plan

- [x] Reference index, contributor workflow, pinned octemu source, and separate emulator patches are in place.
- [x] Local firmware and research checkouts are ignored; proprietary inputs stay local.
- [x] Read-only image audit identifies the supplied 8 MiB MD UW OS 1.63 dump and its static reset vectors.
- [x] Reproduced the trace-instrumented Gearmulator `mdLib` build from the pinned parent source and relevant recursive dependency commits; see [WP-01 provenance report](reports/WP-01-provenance.md).
- [ ] Capture an actual Machinedrum reference boot and unmodified Octatrack headless/UI baseline.

Evidence: [WP-01 provenance report](reports/WP-01-provenance.md), [WP-02 profile report](reports/WP-02-target-profile.md), [WP-03 evidence contract](reports/WP-03-evidence.md), [boot feasibility](BOOT_FEASIBILITY.md), [research log](RESEARCH_LOG.md), [compatibility matrix](COMPATIBILITY_MATRIX.md), repository history through `e964334`.

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

[WP-01 — Source provenance](work_packets/WP-01-source-provenance.md) is done on `work/wp-01-source-provenance`: [PR #4](https://github.com/repeat98/octamachine/pull/4) merged as `29471d01c61bbd8e83aa925157ae8fc4e25ddfa8` on 2026-09-23. Its source/build criteria and documentation checks pass. G0 remains open pending accepted capture tooling and runtime baselines.

- [x] Record local reference and recursive dependency revisions, source modifications, patch hashes, toolchain, prerequisites, and license notices.
- [x] Apply the bus trace patch to a clean Gearmulator MD/MM worktree and build `mdLib` with pinned dependency contents.
- [x] Reconcile accepted delivery and mark WP-01 done.

This advances source reproducibility only; no firmware runtime checkpoint has been reached.

[WP-02 — Target profiles](work_packets/WP-02-target-profiles.md) is done: [PR #6](https://github.com/repeat98/octamachine/pull/6) merged as `e964334ef84790a16a5a500399d8c0f8a0c4e97f` on 2026-09-23. The local Machinedrum SPS-1UW OS 1.63 image matches all recorded reference fingerprints; the selected Octatrack MKII emulator target is provisional because the local OS source archive and physical hardware identity are unavailable. See the [profile report](reports/WP-02-target-profile.md) and [shareable metadata](../tests/fixtures/machinedrum-sps1uw-os1.63.profile.json).

- [x] Identify the Machinedrum OS 1.63 raw image and document its model label, size, and matching public fingerprints.
- [x] Record the provisional Octatrack MKII emulator profile, feature inventory, deferred variants, and missing input consequences.
- [x] Submit the WP-02 branch for review.
- [x] Reconcile the accepted PR #6 merge.

No new firmware execution or hardware checkpoint is established by this profile inventory.

[WP-03 — Evidence contract](work_packets/WP-03-evidence-contract.md) is in review on `work/wp-03-evidence-contract`. Versioned run manifests, JSONL capture rules, a first-divergence comparator, and synthetic outcome tests are documented in the [WP-03 report](reports/WP-03-evidence.md). Its checks establish tooling behavior with synthetic events only; firmware baselines remain unproved.

- [x] Define the four initial-state modes, ordered stimulus timing, clock metadata, PC semantics, limits, and stop outcomes.
- [x] Require matching comparison plans and report the first field/event divergence.
- [x] Exercise equivalent, divergent, missing, failed, and truncated inputs with synthetic fixtures.
- [x] Run the synthetic checks through `make check`.
- [ ] Merge WP-03 after required CI checks pass.

## Gate checklist

- [ ] G0: reproducible source/target profiles and MD/OT baseline captures — WP-00–05.
- [ ] G1: accepted hardware-realizable architecture — WP-06–10.
- [ ] G2: target bootstrap, host services, original DSP payloads, panel transport, live audio — WP-11–18.
- [ ] G3: integrated behavior, fidelity, load/fault coverage — WP-19–28.
- [ ] G4: local candidate and board-specific recovery readiness — WP-29.
- [ ] G5: authorized physical startup and parity evidence — WP-30–31.
- [ ] G6: independent reproduction and supported-profile delivery — WP-32.

Link the report and accepted revision when checking a gate. Skipped runs do not satisfy a gate.

## Next dispatch queue

WP-01 and WP-02 are accepted; WP-03 is delivered for review. After WP-03 merges, WP-04 and WP-05 can collect runtime baselines if their local inputs are verified. The Octatrack distribution archive is not present in current workspace evidence, so WP-05 must resolve that input first.

1. [WP-04 — Machinedrum baseline](work_packets/WP-04-machinedrum-baseline.md): establish a bounded reference boot with the verified local image and Gearmulator profile after WP-03 acceptance.
2. [WP-05 — Octatrack baseline](work_packets/WP-05-octatrack-baseline.md): verify/reacquire the pinned OS distribution before a stock headless/UI run.

Use the [handoff template](templates/AGENT_HANDOFF.md) with one packet's scope and explicit file ownership.

[WP-35 — octamad Machinedrum import](work_packets/WP-35-octamad-md-import.md) is in review on `work/wp-35-octamad-md-import`. It is maintenance and adds no prerequisite. It brings Gearmulator-only prior evidence and tools for WP-06–10, WP-14–17, WP-25 and WP-26 (the [report](reports/WP-35-octamad-md-import.md), `scripts/md_reference/`), linked from each of those packets. No acceptance item or gate changes on its strength.

## Cross-cutting unknowns and blockers

| Item | Current evidence | Owner / next action |
| --- | --- | --- |
| Source reproduction | WP-01 is accepted; its report records recursive revisions and a clean trace-patched `mdLib` build, with no firmware execution | WP-03 defines evidence; WP-04 records the first MD runtime trace after the contract merges |
| Exact target profile | WP-02 documents octemu's Octatrack MKII/MCF54455 profile and expected OS 1.40C; the extracted local OS section's source archive and physical board/carrier identity are unavailable | WP-05 verifies/reacquires the pinned firmware input; physical profile remains provisional and the hardware gate stays closed |
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
