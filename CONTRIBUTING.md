# Contributing

Help run the actual Machinedrum firmware and its own DSP programs on the Octatrack with the smallest measured adaptations. Each contribution should advance one reproducible result.

Read [AGENTS.md](AGENTS.md) for repository-wide instructions. [Getting started](docs/GETTING_STARTED.md) is the single setup guide for the scaffold, firmware audit, research sources, and emulators.

## Choose a contribution

You can start with documentation, source research, and synthetic tooling without owning firmware or hardware. Firmware execution and hardware claims need the corresponding local inputs and evidence.

1. Check [project status](docs/STATUS.md) and the [packet index](docs/PORT_PLAN.md#work-packet-index).
2. Read a packet's scope, dependencies, deliverables, acceptance checklist, and current handoff.
3. Record your owner name and branch. Coordinate file ownership if another contributor is active.
4. Work toward one bounded result. Split larger work using the [packet template](docs/templates/WORK_PACKET.md).

WP-01 (source provenance), WP-02 (target profiles), and WP-03 (evidence contract) are the initial technical queue. An agent can use the [handoff template](docs/templates/AGENT_HANDOFF.md).

| Contribution | Useful result |
| --- | --- |
| Source research | One resolved compatibility question with pinned sources, observations, and uncertainty |
| Capture tooling | Repeatable stimulus/checkpoint capture with explicit timeout, truncation, and missing-input behavior |
| Image tooling | Verified, reversible local transformations and synthetic tests for rejection cases |
| CPU/DSP/I/O adapter | One measured boundary implemented with before/after evidence |
| Emulator support | A focused upstream change or reviewable patch plus the evidence for a deliberate pin update |
| Documentation | A corrected command, clearer handoff, reconciled status, or better explanation of existing evidence |

Register new or maintenance work in the packet index. Keep IDs stable and leave technical acceptance criteria open until they are proved.

## Work on a branch

Start from the current target `main`. Keep unrelated local work intact.

With write access, from a clean checkout:

```sh
git fetch origin
git switch -c work/your-packet-name origin/main
```

For a fork, first fork the repository on GitHub and clone your fork instead of the upstream URL in the quick start. In that clone, `origin` points to your fork. Add the target repository as `upstream` once if it is not already configured:

```sh
git remote add upstream https://github.com/repeat98/octamachine.git
git fetch upstream
git switch -c work/your-packet-name upstream/main
```

Continue on the existing branch when updating its PR. Do not reset dirty vendor checkouts or unintentionally stage a submodule pin. `vendor/octemu` is tracked as a submodule; the other `vendor/` repositories are ignored research copies.

## Record every work prompt

Update the packet and [project status](docs/STATUS.md) in the same commit as your work, including research, partial progress, and blocked attempts.

- [ ] Record owner, branch, date, and lifecycle state.
- [ ] Check only acceptance criteria supported by evidence.
- [ ] Append a dated prompt entry with completed `[x]` and remaining `[ ]` items.
- [ ] Record changed files, commands/results, skipped gates, observations versus inferences, and blockers.
- [ ] Leave one precise next action and the inputs needed to perform it.
- [ ] Update the research log/matrix if technical conclusions changed.

Keep previous prompt history. A delivered packet is `in_review`; `done` requires satisfied criteria and accepted/merged delivery. Reconcile a prior merge at the start of the next work prompt. Pure questions and read-only status replies do not need artificial file edits or empty commits.

## Evidence for review

A reviewer should understand the claim without proprietary firmware. Use [reviewed capture metadata](tests/fixtures/README.md) and the plan's [evidence contract](docs/PORT_PLAN.md#evidence-and-comparison-contract).

| Include | Be specific about |
| --- | --- |
| Scope | Packet ID, profile, dependency evidence, criterion/checkpoint advanced |
| Source state | Revisions, recursive dependencies, applied patches, dirty-tree state, build tools |
| Reproduction | Exact command, initial state, ordered stimuli, timeout, expected and observed result |
| Comparison | Reference run, units, clock source, declared tolerance, first divergence |
| Limits | Missing inputs, skipped checks, remaining stubs, unverified hardware assumptions |
| Handoff | Completed/remaining checklist and next action |

Run `make check` for every changed packet. Run relevant emulator or hardware checks when the change requires them. For documentation-only work, check local links, command names against the implementation, and whitespace; do not invent runtime results.

Source comments, static image inspection, emulator traces, and physical measurements are different kinds of evidence. Label them. `make check` validates the reference manifest, Python syntax, and synthetic capture cases; it does not prove firmware compatibility.

## Commit, push, and open a PR

For every prompt that changes files:

1. Inspect the working tree and review the diff.
2. Stage explicit packet paths, including its record and `docs/STATUS.md`.
3. Review the staged diff and run the required checks.
4. Commit the focused result and push the task branch.
5. Open/update one PR against `repeat98/octamachine:main`, using the [PR template](.github/PULL_REQUEST_TEMPLATE.md). Keep incomplete acceptance work in draft.
6. Report the packet/status, completed/remaining checklist, commit, branch, push result, PR, and next action.

For the example branch above:

```sh
git push -u origin work/your-packet-name
gh pr create --repo repeat98/octamachine --base main
```

GitHub's web compare flow also works. If you cannot create a PR, provide the pushed branch and compare link. If a push fails, retain the local commit and report the failure. Do not force-push shared history.

### Protected main and review

The `Protect main` ruleset was verified on 2026-09-23:

- Changes arrive through PRs.
- The `scaffold` check from GitHub Actions must pass.
- The branch must be up to date before merging.
- Review conversations must be resolved.
- Force pushes and branch deletion are blocked; the bypass list is empty.
- Required approvals are currently zero so the sole maintainer can merge their own PRs. This does not authorize an agent to merge.

View the [current rules](https://github.com/repeat98/octamachine/rules) if GitHub's merge requirements differ from this snapshot. A maintainer handles ingestion; agents do not merge automatically.

When `main` advances, merge the latest target branch into your published task branch, resolve conflicts without dropping either contributor's status/history, rerun affected checks, and push. For a direct branch:

```sh
git fetch origin
git merge origin/main
git push
```

For a fork, fetch/merge `upstream/main` instead and push to `origin`. Required checks may need to run again. External-contributor workflows can require maintainer approval before GitHub Actions runs.

## Firmware and upstream changes

Keep ROMs, OS files, extracted DSP payloads, transformed images, raw traces/audio, and private project/sample data local. DSP-upload MMIO traces can contain firmware words. See [artifact guidance](tests/fixtures/README.md) before attaching evidence to an issue or PR.

Record source and license provenance before importing third-party implementation. octemu documents restrictions on distributing its combined binaries. Proposed octemu improvements should normally go to [its upstream repository](https://github.com/markandrus/octemu); retain separate patches here when needed and update pins deliberately.

Hardware tests follow the plan's recovery and explicit authorization gates. The [definition of done](docs/PORT_PLAN.md#definition-of-done) applies to every packet.
