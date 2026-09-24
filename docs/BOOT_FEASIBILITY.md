# Boot feasibility: first source audit

This is the initial evidence report, not a current boot-support claim. Use [getting started](GETTING_STARTED.md) for setup and [project status](STATUS.md) for the current queue. The [compatibility matrix](COMPATIBILITY_MATRIX.md) links each unresolved boundary to its owning packet.

## What the local references establish

At the checked out revisions—Gearmulator MD/MM `8cea0524a75435122c20b669ca114c9ac6509ba2`, MAME `d7ffd71ed97831b7f995337d6c5bd1bbb03898af`, and octemu `87000189418c8ca2026dc047bda220b66802809d`—the references provide a useful starting image profile for Machinedrum UW OS 1.63:

- MAME's `elektronmono.cpp` identifies an 8 MiB flash image named `elektron_sps1-1uw_os1.63.bin`, with CRC-32 `3d552c99` and SHA-1 `a872a2f3527063673d6ea6d3080c4c62ef0cadc1`. Its driver maps the MCF5206E and memory but is explicitly marked non-working and no-sound.
- Gearmulator MD/MM's `mdromloader.cpp` accepts only an 8 MiB image whose fingerprint matches its supported OS. `mdtypes.h` identifies the Machinedrum 1.63 FNV-64 fingerprint as `33b7c1a9e29f43fd`.
- Gearmulator's `mdmc.h` and `mdmemorymap.h` document a modeled MCF5206E address space: bootstrap flash at `0x00000000`, patch RAM at `0x00100000`, main RAM at `0x00200000`, SIM at `0x00300000`, DSP HI08 at `0x00500000` and `0x00600000`, internal SRAM at `0x01000000`, and full flash at `0x10000000`. It aliases patch RAM at `0x00700000` and main RAM at `0x20000000`/`0x40000000`.
- Octemu currently creates an Octatrack MCF54455 board with a CFV4e CPU, initializes Octatrack-specific peripherals and two DSP cores, loads raw OS sections at `0x40000400`, and sets the Octatrack stack. It does not currently provide a Machinedrum reset path, MCF5206E SIM, two Machinedrum HI08 devices, or Machinedrum memory map.
- QEMU in octemu also contains the generic `an5206` MCF5206E evaluation board. That is a possible CPU-level trace harness, but it is not the Machinedrum board and does not model the Machinedrum DSPs, flash banking, panel, or audio hardware.

WP-07 now resolves the operational Gearmulator HI08 map with repeated firmware traces: DSP1/mixer at `0x00500000` and DSP2/voice producer at `0x00600000`; no trace access used `0x00400000`. The MCF5206E manual specifies 8 KiB internal SRAM, so Gearmulator's 64 KiB allocation is emulator backing. MAME's 25.447 MHz and Gearmulator's 40 MHz remain model choices; the NXP 40/50 MHz grades do not identify the physical board clock. See the [WP-07 report](reports/WP-07-memory-mmio.md) for trace coverage and remaining physical measurements.

The MAME and Gearmulator maps are software/emulator descriptions, not a replacement for checking the exact hardware revision. Gearmulator is the useful firmware-running baseline. The target-side Octatrack port still needs an explicit compatibility layer and trace evidence.

## Local image audit — 2026-09-23

The user-supplied image in the ignored `base_firmware/` directory matches the supported Machinedrum UW OS 1.63 image in both emulator references:

- Size: 8 MiB.
- MAME SHA-1: `a872a2f3527063673d6ea6d3080c4c62ef0cadc1`; CRC-32: `3d552c99`.
- Gearmulator FNV-64: `33b7c1a9e29f43fd`.
- Reset PC: `0x0000000c`, inside the bootstrap flash window.
- Initial SP: `0x00000000`, outside the modeled RAM ranges.

Static inspection of the first bootstrap instructions shows the firmware setting supervisor state and configuring ColdFire control registers, including VBR, CACR, RAMBAR0, and MBAR1, before the normal stack is established. This establishes the reset-vector interpretation, but it is not a runtime boot trace. The image itself and its SHA-256 are not recorded in Git or this document.

## First local tool

[`scripts/audit_md_image.py`](../scripts/audit_md_image.py) reads a user-supplied image and reports its size, SHA-256, MAME CRC/SHA-1 matches, Gearmulator fingerprint match, and the first ColdFire stack/reset vectors against the documented map. It does not modify the file. Run it only on a firmware dump you are entitled to use:

```sh
python3 scripts/audit_md_image.py /path/to/your-machinedrum-flash.bin
```

An exact OS 1.63 match gives us a reproducible input for tracing. A fingerprint mismatch may mean a different OS revision or a different dump format; it is not evidence that the device is unsupported.

The optional Gearmulator instrumentation records MCF5206E accesses to SIM, both DSP HI08 windows, and unmapped/peripheral addresses. Prepare the ignored Gearmulator checkout with `make gearmulator-prepare`. For the bounded headless baseline, build `mdPanelReadinessFirmwareTest` and run `scripts/capture_md_baseline.py` with explicit `--driver`, `--firmware`, `--build-metadata`, and a new private `--output-dir`; see [WP-04](reports/WP-04-md-baseline.md) for exact build/run and comparator commands. The wrapper validates the image profile, repeats two cold/cached pairs, emits WP-03 manifests and redacted JSONL projections, and bounds each child process. Its summarized trace defaults to 100,000 retained events. `--full-private-trace --trace-limit 12000000` retains every MMIO read/write value locally; raw traces can contain DSP firmware words and must not be committed or shared. The standalone ROM search path remains relevant only when launching Gearmulator's interactive application directly.

## Measured Gearmulator baseline — 2026-09-23

The pinned MD/MM model runs the local OS 1.63 image through named cold-reset, dual-DSP-boot, firmware-ready, factory-initialized, and no-stimulus idle checkpoints, then repeats startup from the initialized flash/cache. Two full private captures recorded matching SIM and both DSP HI08 event ordering below the finite trace cap. The report publishes only reviewed counts and state/cycle metadata. At the 128-frame sample granularity, the relative completion order of DSP1 and DSP2 is unresolved. This establishes a Machinedrum baseline for Gearmulator only; it does not show an Octatrack boot, target compatibility, physical behavior, or audio parity.

## Next checkpoint

Clean Gearmulator source/build provenance is recorded in [WP-01](work_packets/WP-01-source-provenance.md), profiles in WP-02, and the evidence contract in WP-03. WP-04's measured report is linked above. [WP-05](work_packets/WP-05-octatrack-baseline.md) must establish the unmodified Octatrack emulator baseline independently, after verifying that its local OS came from the pinned distribution archive.

Raw DSP-upload traces can contain firmware words. Keep them under an ignored path and publish only reviewed summaries under the [artifact guidance](../tests/fixtures/README.md).

WP-07's [memory/MMIO report](reports/WP-07-memory-mmio.md) bounds the reference map and provides an untested alias/peripheral plan. A physical clock/decode measurement and octemu alias/MMIO probes remain open. The CPU/DSP audits and [WP-10 architecture decision](work_packets/WP-10-architecture-decision.md) must establish a mechanism that can execute on the physical target before target integration. There is no existing octemu Machinedrum boot profile to select. Advance one named checkpoint with evidence and keep every required firmware transformation explicit and reversible.
