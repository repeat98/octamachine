# octamachine

**Port the actual Elektron Machinedrum firmware to the Octatrack, as close to 1:1 as possible.**

The aim is to run the original Machinedrum OS and DSP programs on Octatrack hardware, preserving its machines, effects, sequencer, UI behavior, MIDI, sampling, and saved state. Hardware differences may require small, documented adaptations. Each change must be backed by evidence and a comparison with the original behavior.

**Current stage: feasibility research.** The local MD UW OS 1.63 image has been identified and trace instrumentation has been compiled. Machinedrum boot on octemu or Octatrack hardware, ported DSP audio, and a flashable build are still unproved. See [project status](docs/STATUS.md) for the current evidence and next work.

[Getting started](docs/GETTING_STARTED.md) · [Port plan](docs/PORT_PLAN.md) · [Contributing](CONTRIBUTING.md) · [Agent handoff](docs/templates/AGENT_HANDOFF.md)

## Start here

You can contribute to documentation, source research, and synthetic tooling without firmware or an Octatrack. The repository checks need **Git, Make, and Python 3.10+**, with no third-party Python packages.

```sh
git clone https://github.com/repeat98/octamachine.git
cd octamachine
make check
```

This validates the reference manifest, compiles the Python scripts, and runs the synthetic capture-comparison checks. Emulator builds and firmware execution have separate prerequisites.

| I want to… | Start with |
| --- | --- |
| Understand what works and what is still unknown | [Project status](docs/STATUS.md) and [compatibility matrix](docs/COMPATIBILITY_MATRIX.md) |
| Set up sources, audit my firmware, or run an emulator | [Getting started](docs/GETTING_STARTED.md) |
| Pick a concrete contribution | [Contributor guide](CONTRIBUTING.md) and [work packet index](docs/PORT_PLAN.md#work-packet-index) |
| Hand work to an agent | [Handoff template](docs/templates/AGENT_HANDOFF.md) and [AGENTS.md](AGENTS.md) |
| Review the current technical evidence | [Boot feasibility](docs/BOOT_FEASIBILITY.md) and [research log](docs/RESEARCH_LOG.md) |

## How the port is being developed

1. **Establish reference behavior.** Identify exact firmware/source revisions and capture Machinedrum behavior in Gearmulator MD/MM.
2. **Prove the target setup.** Run unmodified Octatrack firmware in octemu, both headless and with its real-time front panel.
3. **Choose a feasible architecture.** Verify CPU, DSP, memory, and peripheral requirements against mechanisms that can run on the physical Octatrack.
4. **Adapt and compare.** Bring up the original host firmware and DSP payloads, then test controls, sequencing, audio, MIDI, and persistence.
5. **Validate on hardware.** Proceed through image, recovery, and physical parity gates before claiming support.

The [port plan](docs/PORT_PLAN.md) breaks this into numbered work packets with prerequisites, deliverables, acceptance checklists, and handoffs. Every work prompt records completed and remaining work. A successful emulator experiment only establishes the behavior that was measured.

### The two emulator roles

| Emulator | Role here | How it is included |
| --- | --- | --- |
| Gearmulator MD/MM | Machinedrum reference for boot, state, MIDI, and audio comparisons | Pinned research checkout fetched into ignored `vendor/gearmulator-md-mm/` |
| octemu | Octatrack target environment with headless scripts and a real-time SDL panel | Pinned source submodule at `vendor/octemu/` |

octemu is included as source. Build it locally with its dependencies and your own Octatrack OS; the pinned version documents a macOS setup. It currently boots Octatrack firmware. A Machinedrum target profile is future port work. [Emulator setup and run commands](docs/GETTING_STARTED.md#octatrack-emulator).

## Contribute one work packet

The first technical assignments are source provenance (WP-01), firmware/target profiles (WP-02), and capture/comparison contracts (WP-03). Check the [live queue](docs/STATUS.md#next-dispatch-queue) before claiming one.

Use a task branch or fork, advance one observable result, and submit a PR with reproduction steps and evidence. Update the packet's status, completed/remaining checklist, and next action after every work prompt. [CONTRIBUTING.md](CONTRIBUTING.md) covers the full flow, including the protected `main` branch and required CI check.

## Upstream work

These projects supply the research and tooling foundations. Each has its own license and support scope.

| Repository | Role |
| --- | --- |
| [sambanks/octabam](https://github.com/sambanks/octabam) | Octatrack 1.40C image tooling, hardware research, ColdFire/DSP work, and verification harnesses; a possible tooling or carrier base subject to feasibility work |
| [markandrus/octemu](https://github.com/markandrus/octemu) | Octatrack emulation with headless scripts and an SDL front panel; our tracked source submodule |
| [joelanders/gearmulator-md-mm](https://github.com/joelanders/gearmulator-md-mm) | Firmware-running Machinedrum and Monomachine reference emulator |
| [dsp56300/gearmulator](https://github.com/dsp56300/gearmulator) | Upstream emulator architecture and CPU/DSP foundations |
| [mamedev/mame](https://github.com/mamedev/mame/blob/master/src/mame/elektron/elektronmono.cpp) | Elektron hardware skeleton and notes; marked non-working/no-sound |
| [mxldyn/octamax](https://github.com/mxldyn/octamax) | Earlier Octatrack image-format and memory-map research |
| [dsp56300/dsp56300](https://github.com/dsp56300/dsp56300) | DSP emulation used by the surrounding projects |
| [joelanders/mc68k-md-mm](https://github.com/joelanders/mc68k-md-mm) | ColdFire/68k emulator fork used by Gearmulator MD/MM |
| [mischa85/elektron-firmware-tool](https://github.com/mischa85/elektron-firmware-tool) | Elektron firmware container tools used by octemu and related work |
| [QEMU](https://gitlab.com/qemu-project/qemu) | CPU emulation base for octemu's patched build |

[references.json](references.json) records the research repositories and selected pins. `make refs` fetches missing checkouts; it leaves existing directories untouched. Only `vendor/octemu` is a tracked submodule. Other research checkouts remain ignored. Local emulator changes are kept as reviewable patches under `patches/`.

## Repository map

| Path | Purpose |
| --- | --- |
| `docs/GETTING_STARTED.md` | Setup, commands, expected outcomes, troubleshooting |
| `docs/STATUS.md` | Current evidence, active work, next queue |
| `docs/PORT_PLAN.md` | Architecture questions, gates, dependency index |
| `docs/work_packets/` | Packet briefs, checklists, prompt histories |
| `docs/templates/` | Reusable work packet and agent handoff |
| `scripts/` | Reference management, emulator patch setup, read-only image audit, and capture comparison |
| `src/image/`, `src/compat/`, `src/dsp/` | Reserved homes for port implementation |
| `patches/` | Separate octemu and Gearmulator changes |
| `tests/fixtures/` | Reviewed metadata and future synthetic comparison fixtures |
| `base_firmware/`, `private/`, `out/`, `build/` | Ignored local inputs, captures, and build output |

## Firmware, distribution, and hardware

Firmware is supplied locally by contributors. Keep ROMs, OS files, extracted DSP programs, derived images, raw captures, and private samples/projects out of Git. Put Machinedrum inputs in ignored `base_firmware/`; see the [artifact guidance](tests/fixtures/README.md) before sharing evidence.

The pinned octemu README documents restrictions on distributing its combined binaries. Follow each upstream project's license; linking or fetching a project does not grant permission to redistribute its code or firmware. This repository has not yet declared a project-wide code license.

There is no supported installation or flashing procedure for this port yet. Physical tests require the plan's emulator, image, recovery, and authorization gates.

octamachine is independent of Elektron and the upstream projects listed above.
