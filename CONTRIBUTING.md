# Contributing

Pull requests are welcome for measured compatibility research, image inspection tools, boot traces, CPU/DSP/peripheral shims, emulator integration, and documentation. The shared goal is to run the Machinedrum firmware itself on the Octatrack with minimal documented changes. A narrow PR with one reproducible claim is easier to review than a broad unmeasured port.

Follow [AGENTS.md](AGENTS.md) for the shared work packet, commit, push, and PR submission workflow.

## Set up

```sh
git clone --recurse-submodules <this-repository-url>
cd octamachine
make refs                         # optional research checkouts in vendor/
make check                        # scaffold checks
make octemu-prepare               # apply local compatibility patch
cd vendor/octemu
make doctor                       # reports local build prerequisites
make setup && make os && make qemu && make
./octemu --headless --cf-card none --nvram none --timeout 5
./octemu                       # interactive SDL front panel
```

`make os` in octemu obtains and unpacks **your own** Octatrack OS. The emulator needs that local image and its patched QEMU/DSP dependencies; `git clone --recurse-submodules` gives you its source, not a ready-to-run binary. The local patch is reviewable in `patches/octemu/` and `make octemu-prepare` is safe to rerun. Read [octemu's build instructions](vendor/octemu/README.md) and license before building. Run octemu from its own directory because its QEMU binary, panel assets, and output paths are relative to that directory. `--headless` runs the same emulated firmware without the window, and `--script` can drive repeatable panel walks.

## Pick a contribution

Start with [project status](docs/STATUS.md) and the [packet index](docs/PORT_PLAN.md#work-packet-index). Each packet includes dependencies, concrete deliverables, acceptance criteria, and its current handoff. Claim one packet on a task branch; check prerequisite evidence and agree ownership before working on shared files. WP-01, WP-02, and WP-03 are the initial technical queue. Existing source audits are starting evidence, not completed boot captures.

For work outside the index or a bounded child of a large packet, copy the [work packet template](docs/templates/WORK_PACKET.md), register it in the plan, and link it from its parent where applicable. To assign an agent, use the [handoff template](docs/templates/AGENT_HANDOFF.md).

- **Research:** answer one row in the [compatibility matrix](docs/COMPATIBILITY_MATRIX.md). Add a dated entry in [the research log](docs/RESEARCH_LOG.md) with repository commits, firmware revision, commands, observations, and uncertainty.
- **Oracle fixture:** contribute text metadata for a privately captured Machinedrum boot or behavior trace. State model, OS, Gearmulator commit, checkpoint/actions, timing, and hashes. Keep ROMs and audio files out of Git.
- **Image and boot tooling:** inspect and transform user-owned firmware locally. Assert source bytes, log changed offsets, and show the first boot checkpoint reached in octemu.
- **Compatibility shim:** implement one measured CPU, DSP, panel, MIDI, audio, or storage translation. Show the before/after trace and state why the original firmware cannot run unchanged at that boundary.
- **Emulator support:** changes to octemu itself should normally go upstream to [markandrus/octemu](https://github.com/markandrus/octemu). This repository may add integration scripts and a pin update after the upstream change is available.

## Record every work prompt

Update the assigned packet and `docs/STATUS.md` with the work in each commit. Keep the acceptance checklist honest and append a dated prompt history entry: checked completed items, unchecked remaining items, evidence, commands/results, blockers, and a precise next action. Research and blocked attempts also need a durable record. Preserve earlier entries and other contributors' updates.

Follow the plan's [status lifecycle](docs/PORT_PLAN.md#status-lifecycle-and-prompt-bookkeeping). A delivered packet is `in_review` until accepted/merged and all criteria pass. Reconcile prior merges when starting the next prompt. A source-only check does not establish a runtime gate. Pure questions/status replies do not need artificial edits or empty commits.

## Pull request expectations

1. Link the packet record, project status, and relevant issue or milestone. State packet status, completed/remaining acceptance items, and next action. Keep unrelated changes in separate PRs.
2. Explain the behavior, the source commits, and what was measured versus inferred.
3. Run `make check`. Run the relevant Gearmulator, octemu, octabam, or hardware gate for code that uses them and include commands plus results. If a gate needs firmware or hardware you lack, state that plainly.
4. Do not include Elektron firmware, ROMs, derived flash images, copyrighted third-party code without a compatible grant, or private project/sample data.
5. Update the README or port plan when the contribution changes setup, architecture, or supported behavior.
6. Commit and push each prompt's scoped changes. Open/update a PR against `repeat98/octamachine:main`, using the [PR template](.github/PULL_REQUEST_TEMPLATE.md); keep incomplete work in draft. Report the commit, branch, push result, and PR/compare link. Maintainers decide ingestion; do not merge automatically.

Reviewers should be able to inspect the change without possessing proprietary firmware. We can accept reviewed text metadata, synthetic fixtures, harness code, and reproducible instructions while keeping the actual binaries local. Raw DSP-upload MMIO traces can include firmware words and must remain private. The [definition of done](docs/PORT_PLAN.md#definition-of-done) applies alongside each packet's checklist.
