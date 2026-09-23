# Working in octamachine

These instructions apply to the whole repository, for human contributors and coding agents. Read [README.md](README.md), [CONTRIBUTING.md](CONTRIBUTING.md), [docs/PORT_PLAN.md](docs/PORT_PLAN.md), [docs/STATUS.md](docs/STATUS.md), and the assigned packet in `docs/work_packets/` before changing the port. The goal is to run the actual Machinedrum firmware and its DSP programs on the Octatrack with the smallest measured adaptations.

## One work packet at a time

- Keep each prompt or work packet focused on one compatibility boundary, boot checkpoint, tool, or documentation correction. Preserve unrelated local changes.
- Claim one numbered packet from the [plan index](docs/PORT_PLAN.md#work-packet-index), recording your owner name and branch. Check prerequisite evidence before implementing dependent work. For new scope or maintenance outside an existing packet, use the [packet template](docs/templates/WORK_PACKET.md); split broad work into children rather than silently dropping criteria. The [handoff template](docs/templates/AGENT_HANDOFF.md) provides a reusable assignment prompt.
- Start contribution work from the target repository's current `main` on a descriptive branch such as `work/md-boot-trace`. That remote is usually `origin`, or `upstream` when `origin` is your fork. Continue on the existing branch when updating its PR or a managed worktree. Push directly to `main` only when the maintainer explicitly requests it.
- Record evidence in [docs/RESEARCH_LOG.md](docs/RESEARCH_LOG.md) and update [docs/COMPATIBILITY_MATRIX.md](docs/COMPATIBILITY_MATRIX.md) when a measured conclusion changes. Distinguish observations from inferences; include source repository commits and the firmware revision used locally.
- Keep changes to upstream projects reviewable. `vendor/octemu` is a pinned submodule; the other `vendor/` checkouts are ignored research copies. Propose octemu changes upstream or keep a separate patch here, then update the pin deliberately. Never stage a dirty submodule pointer by accident.

## Keep status and checklists after every work prompt

The packet file is authoritative for its lifecycle state and acceptance checklist. `docs/STATUS.md` summarizes project gates, active work, blockers, and the next dispatch queue. Keep both current in the same commit as the work, including prompts that only produce research, partial progress, or a blocker.

1. At prompt start, inspect the working tree, read the current handoff, and reconcile previously merged PRs. Do not overwrite another owner's entries or discard earlier prompt history.
2. Check an acceptance item only when linked evidence proves it. Keep incomplete items unchecked. Distinguish source documentation, measured behavior, and inference; a scaffold check or compiled emulator does not prove a firmware boot.
3. Update owner, branch, date, and [lifecycle state](docs/PORT_PLAN.md#status-lifecycle-and-prompt-bookkeeping). Append a dated prompt history entry with the request, completed `[x]` items, remaining `[ ]` items, changed files, commands/results (including skips), findings, blockers, and precise next action.
4. Refresh the packet's current handoff and `docs/STATUS.md`. Record prerequisite waits separately from a specific technical/input blocker. Use `in_review` for delivered work pending acceptance; `done` requires the packet criteria and accepted/merged delivery. Hardware feasibility gates need evidence independently of PR status.
5. End each work-prompt reply with a concise completed/remaining checklist, packet ID/status, verification outcome, commit/branch/push result, and PR or compare link. State what the next owner should do.

Use the enclosing commit as the delivery reference in the prompt entry and report its actual hash after committing. Reconcile that hash/PR on the next work prompt; do not create extra commits just to embed a commit's own hash. Pure questions and read-only status requests need an accurate checklist in the reply without artificial file edits or empty commits.

## Finish each prompt with a commit and push

For every prompt that changes repository files, make a focused commit and push it to the task branch before reporting completion. Several commits are fine when they represent separate logical steps. Do not create empty commits for read-only research or questions. Follow a user's explicit request to leave a change uncommitted.

1. Inspect `git status --short --branch` before editing and again before staging. Stage only the files for this packet with explicit paths; never use `git add -A` in a workspace with unrelated changes.
   Include the packet record and `docs/STATUS.md` for every work prompt; preserve other owners' updates in shared documents.
2. Review `git diff --cached --name-status` and `git diff --cached`; check that no firmware, generated output, unrelated file, or unintended submodule change is staged.
3. Run `make check` and the relevant emulator or hardware verification for the change. Record the command, result, and any gate you could not run because firmware or hardware was unavailable. Do not claim an emulated or hardware checkpoint without its trace.
4. Commit with a short imperative subject describing the result. Push the current task branch to a writable remote. Report the commit hash, branch, push result, and any remaining limitation in the final response.

If work is incomplete, commit and push it only on a task branch, describe the unfinished state, and keep its PR in draft. If a push fails, retain the local commit and report the failure accurately. Never force-push a shared branch or rewrite another contributor's published commits.

## Submit a PR for ingestion

- Use one PR for one coherent work packet or a small series of prompts advancing the same checkpoint. Target this repository's `main` from your branch or fork. Use [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md); open a draft PR while evidence or gates remain incomplete.
- After pushing, use GitHub's compare flow or `gh pr create` to open the PR against `repeat98/octamachine:main`. Mark a draft PR ready for review when its stated gates pass.
- Before opening the PR, inspect `git diff --name-status <target-remote>/main...HEAD` and the full diff, including submodule changes. Replace `<target-remote>` with `origin` or `upstream` as appropriate. Confirm the branch contains only intended commits and that `git status --short` has no uncommitted packet changes.
- State the packet ID and status, acceptance checklist, milestone or issue, behavior changed, source commits, firmware revision or fingerprint, commands and results, measured versus inferred conclusions, remaining unknowns, and next action. Link the updated packet/status records. Provide text metadata or reproduction steps so reviewers do not need your local firmware. Review raw MMIO traces before sharing: DSP-upload values can contain firmware payload words.
- Confirm the PR contains no firmware, ROM, derived image, sample, private project data, credentials, or unlicensed third-party code. `base_firmware/`, `private/`, captures, and build output stay local even if Git's ignore rules are changed.
- Wait for CI and review. A green scaffold check alone does not prove firmware compatibility. Do not merge a PR or flash hardware as part of routine ingestion; those decisions require maintainer direction and the gates in the port plan.

If the PR tool is unavailable, push the branch and provide the branch name and compare URL so a contributor can open the PR without losing the work.
