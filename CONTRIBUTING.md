# Contributing

Pull requests are welcome for measured compatibility research, image inspection tools, boot traces, CPU/DSP/peripheral shims, emulator integration, and documentation. The shared goal is to run the Machinedrum firmware itself on the Octatrack with minimal documented changes. A narrow PR with one reproducible claim is easier to review than a broad unmeasured port.

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

- **Research:** answer one row in the [compatibility matrix](docs/COMPATIBILITY_MATRIX.md). Add a dated entry in [the research log](docs/RESEARCH_LOG.md) with repository commits, firmware revision, commands, observations, and uncertainty.
- **Oracle fixture:** contribute text metadata for a privately captured Machinedrum boot or behavior trace. State model, OS, Gearmulator commit, checkpoint/actions, timing, and hashes. Keep ROMs and audio files out of Git.
- **Image and boot tooling:** inspect and transform user-owned firmware locally. Assert source bytes, log changed offsets, and show the first boot checkpoint reached in octemu.
- **Compatibility shim:** implement one measured CPU, DSP, panel, MIDI, audio, or storage translation. Show the before/after trace and state why the original firmware cannot run unchanged at that boundary.
- **Emulator support:** changes to octemu itself should normally go upstream to [markandrus/octemu](https://github.com/markandrus/octemu). This repository may add integration scripts and a pin update after the upstream change is available.

## Pull request expectations

1. Link the relevant issue or name the port-plan milestone. Keep unrelated changes in separate PRs.
2. Explain the behavior, the source commits, and what was measured versus inferred.
3. Run `make check`. Run the relevant Gearmulator, octemu, octabam, or hardware gate for code that uses them and include commands plus results. If a gate needs firmware or hardware you lack, state that plainly.
4. Do not include Elektron firmware, ROMs, derived flash images, copyrighted third-party code without a compatible grant, or private project/sample data.
5. Update the README or port plan when the contribution changes setup, architecture, or supported behavior.

Reviewers should be able to inspect the change without possessing proprietary firmware. We can accept text fixtures, harness code, and reproducible instructions while keeping the actual binaries local.
