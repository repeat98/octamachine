# octamachine

Research scaffold for porting the **actual Elektron Machinedrum firmware** to Octatrack hardware as faithfully as possible. The goal is for the Machinedrum OS and its own DSP programs to run on the Octatrack, with small, documented adaptations only where the hardware requires them. This includes the sequencer, machines, UI behavior, MIDI, audio, and persistence—not a new implementation of individual drum voices.

**Status:** scaffolding and feasibility research only. There is no Machinedrum boot on octemu or Octatrack hardware yet, and no flashable image. The different ColdFire, DSP, memory, and peripheral arrangements are substantial compatibility questions. The [port plan](docs/PORT_PLAN.md) and [compatibility matrix](docs/COMPATIBILITY_MATRIX.md) define the evidence needed to answer them.

The first feasibility tool is a read-only audit of a locally supplied Machinedrum image. It checks the known 1.63 size/fingerprints and prints reset vectors without writing or retaining the image. See [boot feasibility](docs/BOOT_FEASIBILITY.md).

## Upstream work

| Repository | What we use it for |
| --- | --- |
| [sambanks/octabam](https://github.com/sambanks/octabam) | Octatrack OS 1.40C image composition, hardware research, DSP/ColdFire tooling, and verification gates. A possible carrier or tooling base; its module system alone is not assumed to run the Machinedrum OS. |
| [markandrus/octemu](https://github.com/markandrus/octemu) | **Pinned submodule** at `vendor/octemu`: real-time Octatrack emulation with an SDL front panel or headless script runs. It uses patched QEMU, DSP56300, and locally supplied Octatrack firmware. |
| [joelanders/gearmulator-md-mm](https://github.com/joelanders/gearmulator-md-mm) | Machinedrum and Monomachine firmware-running reference emulator. Baseline for boot traces, panel/MIDI behavior, DSP state, and audio from firmware you own. |
| [dsp56300/gearmulator](https://github.com/dsp56300/gearmulator) | Upstream emulator architecture and DSP/CPU emulation foundations. |
| [mamedev/mame](https://github.com/mamedev/mame/blob/master/src/mame/elektron/elektronmono.cpp) | Machinedrum/Monomachine skeleton driver and hardware notes; it is marked non-working/no-sound, so it is documentation, not an audio oracle. |
| [mxldyn/octamax](https://github.com/mxldyn/octamax) | Earlier Octatrack OS format and memory-map reverse engineering on which octabam was built. |
| [dsp56300/dsp56300](https://github.com/dsp56300/dsp56300) | DSP56300 emulator used by the surrounding projects. |
| [joelanders/mc68k-md-mm](https://github.com/joelanders/mc68k-md-mm) | ColdFire/68k emulator fork used by Gearmulator MD/MM. |
| [mischa85/elektron-firmware-tool](https://github.com/mischa85/elektron-firmware-tool) | Firmware container tooling used by octemu and the related Octatrack work. |
| [QEMU](https://gitlab.com/qemu-project/qemu) | CPU emulation base used in octemu's patched local QEMU build. |

These are independent projects with their own licenses. Links are references, not vendored dependencies or permission to redistribute code or firmware. See [the port plan](docs/PORT_PLAN.md) for how they fit together.

## Layout

```text
docs/PORT_PLAN.md       architecture, milestones, and evidence gates
docs/RESEARCH_LOG.md    dated findings and unresolved questions
references.json         source repositories and local checkout names
scripts/references.py   list, inspect, and fetch source checkouts
vendor/octemu/          pinned Git submodule, fetched on recursive clone
vendor/*                other Git-ignored research checkouts
patches/octemu/         local octemu compatibility patch
src/image/              future local image inspection and transforms
src/compat/             future CPU, peripheral, I/O, and storage shims
src/dsp/                future DSP payload compatibility work
tests/fixtures/         metadata for user-generated boot and audio captures
```

## Start here

Requires Python 3.10+ and Git. This repository has no third-party Python dependencies.

```sh
git clone --recurse-submodules <this-repository-url>
cd octamachine
make check
make octemu-prepare             # apply the local octemu compatibility patch
make gearmulator-prepare        # apply optional local MD bus tracing
python3 scripts/references.py list
python3 scripts/references.py fetch       # clones reference repos into vendor/
python3 scripts/references.py status      # records the exact checkout commits
python3 scripts/audit_md_image.py /path/to/your-machinedrum-flash.bin
```

Place local Machinedrum dumps under `base_firmware/`; that directory is Git-ignored. The image audit prints fingerprints and reset vectors but never modifies the dump. For the trace setup and its scope, see [boot feasibility](docs/BOOT_FEASIBILITY.md).

MAME is fetched sparsely: only its Machinedrum/Monomachine driver is checked out. The research checkouts are ignored by Git; octemu is the one tracked submodule. Record exact commits used for a result in `docs/RESEARCH_LOG.md`. See [CONTRIBUTING.md](CONTRIBUTING.md) for PR scope and evidence expectations.

To build and run the Octatrack emulator, follow [octemu's setup](vendor/octemu/README.md) from `vendor/octemu/`. Once its dependencies and your own OS are installed:

```sh
cd vendor/octemu
./octemu --headless --cf-card none --nvram none --timeout 5  # scripted/CI path
./octemu                                                    # real-time SDL panel
```

The emulator is supplied as **source** through the submodule. `make octemu-prepare` applies [our small local patch](patches/octemu/0001-sdram-alias-and-interactive-pace.patch): it maps the Octatrack's uncached SDRAM window as an alias, which is needed for octabam's DRAM loader, and adds an optional `--half-speed` mode for a busy development host. The patch is kept separate so it can be reviewed and proposed upstream. Its own `make doctor`, `make setup`, `make os`, `make qemu`, and `make` steps produce the runnable binary. `--script PATH` drives reproducible panel walks in headless mode. octemu's own README notes an audio playback warble, so timing and audio comparisons still need independent confirmation.

The first development step is a **boot feasibility study**: inspect a user-supplied Machinedrum image, compare its ColdFire and DSP requirements to the Octatrack hardware, and trace its early boot in Gearmulator MD/MM. Then make octemu reach the same named checkpoints with an explicit compatibility layer. Keep every firmware transformation byte-checked and reversible. Do not make a flashable image until emulated boot, DSP, I/O, and recovery gates pass. The [port plan](docs/PORT_PLAN.md) gives the full sequence.

## Firmware and hardware

Use only firmware obtained for hardware you own. Do not commit ROMs, Octatrack OS files, dumps, derived images, samples, or project backups. octabam's build derives an image from the user's local Octatrack OS; this repository will follow that model. A custom image can make an Octatrack unusable. Back up projects and follow octabam's [flashing and recovery guide](https://github.com/sambanks/octabam/blob/main/docs/remixer/FLASHING.md) before any hardware test.

This project is independent of Elektron and of the projects linked above. No license is asserted yet for future ported code; provenance and licensing must be settled before importing or publishing any third-party implementation.
