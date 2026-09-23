# Research log

Record findings as dated entries. Each entry should state the upstream repository and commit, target firmware version, exact command or capture procedure, observation, and what remains uncertain.

## 2026-09-23 — Initial survey

- octabam provides an Octatrack 1.40C image builder, DSP module model, offline renderer, and ColdFire/DSP emulator paths. Its hardware research and image tooling are useful references; whether its image builder can carry a full Machinedrum OS remains unproven.
- Gearmulator MD/MM is a fork of Gearmulator that runs Machinedrum and Monomachine firmware. It can serve as the behavior and audio reference for a user-supplied ROM.
- MAME's `elektronmono.cpp` is a hardware skeleton marked non-working and no-sound. It may inform hardware questions but cannot validate audio.
- The Machinedrum and Octatrack use different ColdFire generations and different DSP hardware: MAME documents a 5206e plus two DSP56303 chips; octabam documents an MCF5445x plus two DSP5636x cores in a DSP56721. This makes a literal image copy unlikely to boot without mapping and shims. Instruction and memory compatibility have not yet been measured.
- The starting workspace contained local reference checkouts, which were copied into ignored `vendor/` for research. `vendor/octemu` is pinned as a submodule at `87000189418c8ca2026dc047bda220b66802809d`. The local octemu checkout had pre-existing uncommitted SDRAM alias and pacing changes; they are preserved as the separate `patches/octemu/0001-sdram-alias-and-interactive-pace.patch`, while the submodule pin refers to its committed upstream state. No firmware was added to this repository. Compatibility measurements remain open.

## 2026-09-23 — Boot image and board profile

- The checked out Gearmulator MD/MM source identifies Machinedrum OS 1.63 as an 8 MiB image with FNV-64 `33b7c1a9e29f43fd`; the MAME skeleton records CRC-32 `3d552c99` and SHA-1 `a872a2f3527063673d6ea6d3080c4c62ef0cadc1` for its OS 1.63 image.
- The Gearmulator model supplies concrete MCF5206E memory and peripheral addresses. Octemu presently loads an Octatrack MAIN OS at `0x40000400`, so it cannot directly boot a Machinedrum flash image. QEMU's generic AN5206 machine may help test early ColdFire execution, but it lacks the Machinedrum board and dual DSP wiring.
- Source discrepancies need resolution before implementing the board: MAME's map comments place DSP HI08 at `0x00400000`/`0x00500000`, while its prose and Gearmulator use `0x00500000`/`0x00600000`; MAME maps 8 KiB internal SRAM while Gearmulator allocates 64 KiB despite an 8 KiB comment; MAME configures 25.447 MHz while Gearmulator models a 40 MHz CPU clock.
- The ignored `base_firmware/` dump matches the public 8 MiB Machinedrum UW OS 1.63 reference by MAME CRC-32/SHA-1 and Gearmulator FNV-64. Its reset PC is `0x0000000c`; its initial SP is zero. Static bootstrap disassembly shows ColdFire control-register setup before normal stack use. This is not yet a runtime boot trace.
- Added a read-only image auditor and an opt-in Gearmulator bus trace patch for SIM, DSP HI08, and unmapped/peripheral accesses. The patched Gearmulator `mdLib` compiles successfully on the local Apple Silicon host with tests disabled; the runtime trace has not yet been run. Firmware remains ignored and is not included in this repository.
