# Project status

Updated: 2026-09-23. Read this before claiming work. The [port plan](PORT_PLAN.md) defines gates and dependencies; each [packet record](PORT_PLAN.md#work-packet-index) owns its detailed status and checklist.

## Present state

Scaffolding and feasibility research. **No Machinedrum boot on octemu or Octatrack hardware has been demonstrated.** No ported DSP audio or flashable candidate is available. Planning progress does not count as runtime progress.

### Established before the expanded plan

- [x] Reference index, contributor workflow, pinned octemu source, and separate emulator patches are in place.
- [x] Local firmware and research checkouts are ignored; proprietary inputs stay local.
- [x] Read-only image audit identifies the supplied 8 MiB MD UW OS 1.63 dump and its static reset vectors.
- [x] Optional MD bus tracing instrumentation compiled as mdLib in the existing local setup.
- [ ] Reproduce that build from clean recursive source state; the earlier setup included nested DSP changes.
- [ ] Capture an actual Machinedrum reference boot and unmodified Octatrack headless/UI baseline.

Evidence: [boot feasibility](BOOT_FEASIBILITY.md), [research log](RESEARCH_LOG.md), [compatibility matrix](COMPATIBILITY_MATRIX.md), repository history through `0e8e42b`.

## Active work and current handoff

[WP-00 — Planning, status, and agent handoff](work_packets/WP-00-planning-and-status.md) is done: [PR #2](https://github.com/repeat98/octamachine/pull/2) merged as `d8f8a76` on 2026-09-23. Its acceptance and delivery are reconciled in the packet record.

- [x] Expand the roadmap into 34 packets with outputs, prerequisites, and acceptance criteria.
- [x] Define gates, checkpoints, fidelity/evidence rules, and the hardware feasibility decision.
- [x] Add reusable handoff/status templates and require a checklist after every work prompt.
- [x] Pass document validation: 42 Markdown files, 240 local links/anchors, 34 packet IDs, acyclic dependencies, truthful initial states; `make check` and whitespace checks pass.
- [x] Accept/merge WP-00 and reconcile its status.

[WP-34 — Contributor documentation](work_packets/WP-34-contributor-documentation.md) is `in_review` on `work/readme-and-contributor-guide`.

- [x] Rewrite the README around the goal, current evidence, emulator roles, and contribution entry points.
- [x] Add a single getting-started guide and improve contributor, fixture, and compatibility guidance.
- [x] Document the verified main protection requirements and reconcile WP-00 acceptance.
- [x] Validate 51 Markdown files, 301 local links/anchors, 35 packet records, all 10 upstream links, and 15 shell examples; `make check` passes. Detailed results are in WP-34.
- [ ] Maintainer review/merge, then reconcile WP-34 acceptance.

No technical execution packet has been completed by writing this plan.

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

These packets have no technical packet prerequisite. Their first actions establish the inputs needed for later work.

1. [WP-01 — Source provenance](work_packets/WP-01-source-provenance.md): inspect exact recursive revisions, local changes, build prerequisites, and licenses; reproduce a clean source build.
2. [WP-02 — Target profiles](work_packets/WP-02-target-profiles.md): establish baseline MD and OT firmware/hardware identities, local input availability, and supported-feature inventory.
3. [WP-03 — Evidence contract](work_packets/WP-03-evidence-contract.md): define capture fields, checkpoint triggers, reset/stimulus conventions, and comparison rules.

After those are accepted, dispatch [WP-04](work_packets/WP-04-machinedrum-baseline.md) and [WP-05](work_packets/WP-05-octatrack-baseline.md). Use the [handoff template](templates/AGENT_HANDOFF.md) with one packet's scope and explicit file ownership.

## Cross-cutting unknowns and blockers

| Item | Current evidence | Owner / next action |
| --- | --- | --- |
| Source reproduction | Existing trace build is not a clean recursive reproduction | WP-01 records patches, nested revisions and clean build |
| Exact target profile | Hardware revision and local OT input availability are not established by the current audit | WP-02 inventories inputs; use a clearly provisional emulator profile if needed |
| Source map disagreements | HI08 addresses, SRAM size, CPU clock differ across references | WP-07 resolves with traces/primary sources |
| Target execution strategy | CPU/DSP similarity alone does not establish a port | WP-06–10 assess and choose a realizable mechanism |
| Distribution | octemu documents restrictions on distributing its combined binaries | WP-01 records license/provenance constraints; WP-32 follows them |
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
