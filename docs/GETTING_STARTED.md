# Getting started

Start with the path needed for your contribution. Documentation and public scaffold work need no firmware. Emulator work needs additional build tools and local firmware inputs.

[Project overview](../README.md) · [Current status](STATUS.md) · [Contribution workflow](../CONTRIBUTING.md)

## 1. Check the repository

Requirements: Git, Make, and Python 3.10+. The root Python scripts use the standard library.

```sh
git clone https://github.com/repeat98/octamachine.git
cd octamachine
make check
```

Expected result: reference validation reports 9 repositories, then Python compilation succeeds. This checks the scaffold; it does not build an emulator or execute firmware. The `scaffold` job in [GitHub Actions](../.github/workflows/checks.yml) runs the same command.

A normal clone records the octemu submodule pin without downloading its source. For emulator work, `make octemu-prepare` below initializes it. A recursive clone is also supported.

All commands below start in the repository root unless the block changes directory.

## 2. Choose work and record status

Read [STATUS.md](STATUS.md), [AGENTS.md](../AGENTS.md), and the assigned [work packet](PORT_PLAN.md#work-packet-index). Claim one packet on a task branch and record your owner/branch before changing it. WP-01, WP-02, and WP-03 are the initial technical queue.

Use [CONTRIBUTING.md](../CONTRIBUTING.md) for branch/fork setup and PR delivery. After each work prompt, update the packet and status with completed/remaining checklists, evidence, and one precise next action.

## 3. Fetch research sources when needed

```sh
python3 scripts/references.py list
make refs
make refs-status
```

`make refs` fetches missing repositories in [references.json](../references.json). MAME uses a sparse checkout of the Elektron driver. Existing directories are left untouched: this command does not update, clean, or reset them. It does not download firmware.

`make refs-status` prints checkout revisions and flags dirty trees, URL differences, and pin mismatches. Inspect the output: a successful exit alone does not mean every checkout matches its pin. Record recursive dependency revisions separately for reproducible builds.

The tracked `vendor/octemu` submodule is prepared through its own command below. The other `vendor/` checkouts are ignored research copies; changes there must become a reviewed upstream change or a separate patch before they can be part of a contribution.

## 4. Audit a local Machinedrum image

Place your own dump under `base_firmware/`. Replace the example filename below with your actual file.

```sh
make audit-md IMAGE=base_firmware/machinedrum.bin
```

The auditor reads the file, prints size/fingerprints and reset-vector candidates, and leaves it unchanged. Its known profile is the 8 MiB Machinedrum UW OS 1.63 image described in [boot feasibility](BOOT_FEASIBILITY.md).

For a local JSON report:

```sh
mkdir -p out/audit
python3 scripts/audit_md_image.py base_firmware/machinedrum.bin --json > out/audit/md-image.json
```

Read the match fields in the report. The current auditor returns success for any readable file, including a fingerprint mismatch; success is not a support or bootability verdict. A mismatch may indicate a different revision or container. Keep the source immutable and investigate in WP-02.

`base_firmware/` and `out/` are ignored. Share only reviewed metadata, using the [artifact guidance](../tests/fixtures/README.md).

## Machinedrum reference emulator

Fetch the research checkouts first, then initialize the fork's dependencies and apply the optional bus trace patch:

```sh
make refs
git -C vendor/gearmulator-md-mm submodule update --init --recursive
make gearmulator-prepare
```

Follow the build instructions in the pinned Gearmulator checkout for your host. The preparation command applies instrumentation; it does not build or launch the emulator. Inspect any existing local changes before changing dependency revisions.

The trace patch observes SIM, DSP HI08, and unmapped/peripheral accesses. [Boot feasibility](BOOT_FEASIBILITY.md#first-local-tool) describes ROM discovery, trace variables, capture limits, and the next measurement. DSP-upload trace values can contain firmware words, so store raw logs under an ignored path such as `out/md-traces/`.

WP-01 owns clean build reproduction; WP-04 owns bounded reference boot captures. The existing mdLib compilation result does not prove a working standalone or captured firmware boot.

## Octatrack emulator

The pinned octemu source documents a **macOS** build and requires additional dependencies, including Python 3.11+ in its doctor check. The root scaffold's Python 3.10 requirement does not cover this toolchain. Check the pinned [upstream build instructions](https://github.com/markandrus/octemu/blob/87000189418c8ca2026dc047bda220b66802809d/README.md) before installing dependencies.

### Prepare and build

From the octamachine root:

```sh
make octemu-prepare
cd vendor/octemu
make doctor
make setup
make os
make qemu
make
```

What these steps do:

| Command | Result |
| --- | --- |
| `make octemu-prepare` (root) | Initializes the pinned submodule and applies the separate SDRAM-alias/optional-pacing patch; already-applied patches are recognized |
| `make doctor` | Reports missing host tools; resolve required dependencies before continuing |
| `make setup` | Fetches/builds octemu's dependency toolchain |
| `make os` | Obtains/unpacks the selected OT OS locally into `out/os/main.bin`; checks its pinned distribution hash |
| `make qemu` | Builds octemu's patched QEMU |
| `make` | Builds the emulators, panel assets, and default blank card image |

The root patch is [kept separately](../patches/octemu/0001-sdram-alias-and-interactive-pace.patch) for review. A prepared submodule may appear dirty; inspect its diff before staging anything. Keep the recorded pin unchanged unless your packet deliberately updates it.

At this pin, `make os` expects the OT 1.40C distribution. If the upstream download URL fails, the fetch script prints the expected local archive path and manual acquisition instructions. A different firmware hash needs a separately investigated profile; do not override it just to make setup proceed.

### Run headless

Run from `vendor/octemu/` after the build:

```sh
./octemu --headless --cf-card none --nvram none \
  --script tests/walks/boot-nocard.jsonl --timeout 90
```

This is the command used by octemu's `make test-emu` target. The script waits for `COMPACT` on the emulated display, demonstrating a specific no-card startup checkpoint. An unfinished script at the wall-clock timeout returns failure. It does not establish the full firmware-ready checkpoint, audio parity, or a Machinedrum boot.

A launch with only `--timeout` has no scripted assertion; merely exiting after a few seconds is not a boot test.

### Run the real-time UI

From `vendor/octemu/`:

```sh
./octemu
```

This opens the SDL panel with the blank card created by the build and persistent state in `out/state/`. For the same no-card/no-NVRAM setup as the headless example:

```sh
./octemu --cf-card none --nvram none
```

Use disposable copies of card/NVRAM state for experiments. Saves can change those files. Record panel actions and resulting firmware behavior when collecting evidence.

octemu documents playback warble. Host playback artifacts and the patch's optional `--half-speed` diagnostic mode must be distinguished from guest clock/timing measurements. A slowed run cannot satisfy a real-time gate.

These commands run **Octatrack firmware**. A Machinedrum image cannot be substituted into this profile without the port work defined in WP-06 onward.

## Troubleshooting

| Symptom | Next action |
| --- | --- |
| `make check` cannot find Python | Check `python3 --version`; use `make check PYTHON=/path/to/python3` if needed |
| octemu directory is empty after clone | Run `make octemu-prepare` from the root |
| Gearmulator preparation says the checkout is missing | Run `make refs` before `make gearmulator-prepare` |
| Preparation reports a wrong pin or patch conflict | Inspect `make refs-status` and the affected checkout's diff; preserve local work and resolve the mismatch in the packet |
| Nested source/header missing during a build | Follow that emulator's dependency setup and record recursive submodule state |
| octemu cannot find QEMU, panel assets, or OS | Finish setup and run it from `vendor/octemu/` |
| `make os` reports a download/hash error | Follow its local-archive instructions; confirm the expected revision and intact archive |
| Headless process starts but the script does not finish | Inspect the first missing display/checkpoint and retained log; report the run as failed or incomplete |
| Required `scaffold` check is missing on a fork PR | Check GitHub Actions on the PR; a maintainer may need to approve the workflow run |
| Merge is blocked after CI passed | Check whether the branch is behind `main` or review conversations remain unresolved |

For a useful problem report include the packet ID, host/tool versions, exact command, source/patch revisions, initial state, and first error. Keep proprietary inputs and raw captures local. [Contribution evidence checklist](../CONTRIBUTING.md#evidence-for-review).
