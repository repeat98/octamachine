# WP-00 — Planning, status, and agent handoff

- Status: `in_review`
- Owner: Codex (current prompt)
- Branch: work/expanded-port-plan
- Updated: 2026-09-23
- Depends on: none
- Gate: G0

## Result

Make the project dispatchable as bounded work packets with durable status after every work prompt.

## Scope and starting points

Own the plan, packet briefs, status overview, handoff templates, agent instructions, and contributor/PR links. This packet records the existing technical baseline; writing the roadmap does not complete the technical packets.

## Deliverables

- Expanded `docs/PORT_PLAN.md` and numbered packet briefs with dependencies and acceptance criteria.
- `docs/STATUS.md`, reusable templates, and mandatory per-prompt reporting in `AGENTS.md`.

## Acceptance checklist

- [x] Packet dependencies, concrete outputs, acceptance checklists, and the hardware feasibility decision are documented in the plan and WP-00–33 briefs.
- [x] Existing completed work is distinguished from planned work and unverified runtime claims in the plan and status overview.
- [x] Every work prompt has a durable status, completed/remaining checklist, evidence, and next-action procedure in AGENTS.md and both templates.
- [x] Contributor entry points and the PR template reference the new workflow.
- [x] Local document links and dependency graph are checked; `make check` passes (commands/results below).

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Check an item only when its evidence exists.

## Current handoff

- Completed: Expanded plan, 34 packet briefs, status overview, handoff templates, and contributor/PR workflow; document and scaffold checks passed.
- Remaining: Maintainer review/merge, then reconcile this packet's accepted delivery. Technical execution remains in WP-01 onward.
- Next action: Review this branch for ingestion; after acceptance, record the merge and dispatch WP-01 source provenance (WP-02 and WP-03 are also ready).
- Waiting on: No packet dependency. Confirm required inputs when claiming the packet.
- Blockers: none recorded.
- Evidence: Existing docs/history through `0e8e42b`; the expanded plan, packet records, templates, and verification results below.
- Delivery: Enclosing commit on `work/expanded-port-plan`; the final prompt reply supplies its hash and push/PR outcome. Reconcile acceptance on the next work prompt.

## Prompt history

### 2026-09-23 / prompt 1 — Expand the plan for agent work packets

- Request: Substantially extend the porting plan for later agent assignments and require status plus completed/remaining checklists after every prompt.
- Starting state → ending state: Unstructured future milestones → planning packet in review; no new firmware checkpoint claimed.
- Owner / branch: Codex / `work/expanded-port-plan`.
- Completed:
  - [x] Reviewed repository instructions, prior image/trace audit, source references, and existing contributor workflow.
  - [x] Defined G0–G6, CP00–CP90, architecture feasibility, fidelity comparisons, source guide, risks, and validation layers.
  - [x] Created WP-00–33 with dependency links, concrete deliverables, acceptance checklists, and next actions.
  - [x] Added project status and reusable packet/agent handoff templates.
  - [x] Required durable per-prompt status/checklists in AGENTS.md, CONTRIBUTING.md, README, and the PR template.
  - [x] Checked document links/anchors, packet structure, initial states, and dependency graph; scaffold checks passed.
- Remaining:
  - [ ] Maintainer review/merge and subsequent status reconciliation.
  - [ ] WP-01–03 source/profile/evidence preparation, followed by actual MD and OT baseline captures.
- Changed files: `docs/PORT_PLAN.md`, `docs/STATUS.md`, `docs/work_packets/`, `docs/templates/`, `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, `.github/PULL_REQUEST_TEMPLATE.md`.
- Verification:
  - `make check` — passed: 9 reference repositories validated and Python scripts compiled.
  - `git diff --check` — passed. The staged check then caught extra blank lines at EOF in new packet files; normalized those endings and reran `git diff --cached --check` before delivery.
  - Inline Python document audit — passed: 42 changed/new Markdown files, 240 local links/anchors, 34 unique packet IDs, all dependencies resolve, graph acyclic, no technical packet falsely marked executed. The audit also checked required packet sections, acceptance lists, index coverage, and trailing whitespace.
  - Emulator/hardware runs — not run for this documentation packet; all corresponding technical gates remain open.
- Findings: Existing image identification and compiled trace instrumentation are starting evidence. No runtime boot, DSP parity, or hardware result was added by this prompt.
- Blockers: None for documentation delivery; technical unknowns are listed in project status.
- Next action: Review/merge WP-00, reconcile its accepted revision, then begin WP-01 using the handoff template.
- Delivery: Enclosing commit on `work/expanded-port-plan`; final reply reports the concrete commit and PR. Review/merge remains pending.
