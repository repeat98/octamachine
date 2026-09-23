# Boot feasibility: first source audit

This is the initial evidence report, not a current boot-support claim. Use [getting started](GETTING_STARTED.md) for setup and [project status](STATUS.md) for the current queue. The [compatibility matrix](COMPATIBILITY_MATRIX.md) links each unresolved boundary to its owning packet.

## What the local references establish

At the checked out revisions—Gearmulator MD/MM `8cea0524a75435122c20b669ca114c9ac6509ba2`, MAME `d7ffd71ed97831b7f995337d6c5bd1bbb03898af`, and octemu `87000189418c8ca2026dc047bda220b66802809d`—the references provide a useful starting image profile for Machinedrum UW OS 1.63:

- MAME's `elektronmono.cpp` identifies an 8 MiB flash image named `elektron_sps1-1uw_os1.63.bin`, with CRC-32 `3d552c99` and SHA-1 `a872a2f3527063673d6ea6d3080c4c62ef0cadc1`. Its driver maps the MCF5206E and memory but is explicitly marked non-working and no-sound.
- Gearmulator MD/MM's `mdromloader.cpp` accepts only an 8 MiB image whose fingerprint matches its supported OS. `mdtypes.h` identifies the Machinedrum 1.63 FNV-64 fingerprint as `33b7c1a9e29f43fd`.
- Gearmulator's `mdmc.h` and `mdmemorymap.h` document a modeled MCF5206E address space: bootstrap flash at `0x00000000`, patch RAM at `0x00100000`, main RAM at `0x00200000`, SIM at `0x00300000`, DSP HI08 at `0x00500000` and `0x00600000`, internal SRAM at `0x01000000`, and full flash at `0x10000000`. It aliases patch RAM at `0x00700000` and main RAM at `0x20000000`/`0x40000000`.
- Octemu currently creates an Octatrack MCF54455 board with a CFV4e CPU, initializes Octatrack-specific peripherals and two DSP cores, loads raw OS sections at `0x40000400`, and sets the Octatrack stack. It does not currently provide a Machinedrum reset path, MCF5206E SIM, two Machinedrum HI08 devices, or Machinedrum memory map.
- QEMU in octemu also contains the generic `an5206` MCF5206E evaluation board. That is a possible CPU-level trace harness, but it is not the Machinedrum board and does not model the Machinedrum DSPs, flash banking, panel, or audio hardware.

The source descriptions disagree in several load-bearing places. MAME's address-map code comments put DSP HI08 at `0x00400000`/`0x00500000`, while MAME's prose and Gearmulator put it at `0x00500000`/`0x00600000`. MAME maps internal SRAM as 8 KiB (`0x01000000`–`0x01001fff`); Gearmulator allocates 64 KiB (`0x01000000`–`0x0100ffff`) while its `mdmc.h` comment says 8 KiB. MAME configures the CPU at 25.447 MHz; Gearmulator documents its emulated ColdFire clock as 40 MHz. These may reflect comments, board revisions, or emulator choices. Treat them as open questions until a firmware trace or primary hardware source resolves them.

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

The optional Gearmulator instrumentation records MCF5206E accesses to SIM, both DSP HI08 windows, and unmapped/peripheral addresses. Prepare the ignored Gearmulator checkout with `make gearmulator-prepare`, then set `GEARMULATOR_MD_BUS_TRACE` to a writable trace-file path when launching its Machinedrum standalone. Gearmulator searches its public Machinedrum ROM folder and module folders; link the ignored image from `base_firmware/` into its public ROM folder. Setting the working directory alone may not work because the standalone registers its ROM search paths at startup. The trace is capped at 100,000 events by default; override that with `GEARMULATOR_MD_BUS_TRACE_LIMIT`. It does not record ordinary RAM/flash accesses or every CPU instruction.

## Next checkpoint

First establish clean source provenance (WP-01), exact profiles (WP-02), and the capture contract (WP-03). [WP-04](work_packets/WP-04-machinedrum-baseline.md) then uses the same local image in Gearmulator MD/MM to capture cold boot: reset/stack setup, initial MMIO, SIM configuration, both DSP boot streams, and scheduler startup. [WP-05](work_packets/WP-05-octatrack-baseline.md) establishes the unmodified Octatrack emulator baseline independently.

Raw DSP-upload traces can contain firmware words. Keep them under an ignored path and publish only reviewed summaries under the [artifact guidance](../tests/fixtures/README.md).

Resolve the address/size/clock discrepancies in WP-07. The CPU/DSP audits and [WP-10 architecture decision](work_packets/WP-10-architecture-decision.md) must establish a mechanism that can execute on the physical target before target integration. There is no existing octemu Machinedrum boot profile to select. Advance one named checkpoint with evidence and keep every required firmware transformation explicit and reversible.
