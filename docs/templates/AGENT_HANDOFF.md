# Agent handoff template

Copy the prompt below, replace placeholders, and hand off **one bounded packet**. Read [project status](../STATUS.md) first. Dependency evidence must be accepted before claiming dependent acceptance criteria. For large packets, define children with the [packet template](WORK_PACKET.md) before assigning implementation.

## Copyable prompt

> Work on **<WP-ID — title>** in this repository.
>
> Read `AGENTS.md`, `CONTRIBUTING.md`, `docs/PORT_PLAN.md`, `docs/STATUS.md`, and `docs/work_packets/<packet-file>.md` first. Inspect the working tree and preserve unrelated changes. Reconcile any previous delivery that has merged.
>
> **Result for this assignment:** <one concrete result, or a bounded subset of the packet with remaining criteria kept open>.
>
> **Dependencies:** <IDs, accepted PR/commit and evidence links; unresolved prerequisites if any>.
>
> **Inputs available:** <local firmware profile/path placeholders, source pins/patches, toolchain, hardware availability>. Discover missing inputs before depending on them; do not invent traces or claim skipped tests passed.
>
> **Scope and ownership:** <allowed files/interfaces and shared-file coordination>. Keep the original MD firmware and DSP programs as the behavior source. Document the smallest measured hardware adaptations. Split new scope into a named child/follow-up packet.
>
> **Verification:** <packet-specific commands, comparison scenario, checkpoints, and negative cases>. Run `make check`; record exact outcomes and unavailable gates. Firmware, extracted payloads, derived images, raw captures, and private data remain ignored.
>
> **After every work prompt:** update the packet's owner/branch/state, acceptance checklist, current handoff, and dated prompt history. Include checked completed items and unchecked remaining items, evidence, commands/results, blockers, and one precise next action. Update `docs/STATUS.md` in the same commit. Update the research log and compatibility matrix when technical conclusions change.
>
> **Delivery:** make a focused commit and push the task branch for each prompt that changes files, then open/update the PR following the repository template. Keep incomplete work in a draft. Do not merge or flash hardware without the separately required maintainer direction. If pushing or PR creation is unavailable, retain the work and report the exact failure plus a compare link where possible.
>
> **Final reply:** packet ID/status, completed [x] and remaining [ ] checklist, verification results, commit/branch/push result, PR or compare link, and next action. Do not call the packet done until its criteria and acceptance requirements are met.

## First useful assignment

Start with [WP-01 — Source provenance](../work_packets/WP-01-source-provenance.md):

- Result: a reproducible source/build manifest with recursive pins, applied patches, dirty-state findings, prerequisites, and distribution constraints.
- Inputs: the current repository and local reference checkouts; no firmware execution is needed to begin the inventory.
- Scope: inspect source state first; do not reset dirty vendor work. Capture local modifications and use a clean separate checkout when needed for reproduction.
- Deliverable: `docs/reports/WP-01-provenance.md` plus any narrowly required reproducibility tooling.
- Stop boundary: completing WP-01 does not claim a firmware boot. WP-04/WP-05 own those captures after all their prerequisites pass.

Use the actual packet's acceptance checklist to decide completion. The template is not permission to invent unavailable firmware, fabricate hardware results, or expand an assignment into the entire port.
