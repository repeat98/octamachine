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

## 2026-09-23 — Clean Gearmulator trace build (WP-01)

- Source: Gearmulator MD/MM `8cea0524a75435122c20b669ca114c9ac6509ba2`; recursive sources used for `mdLib`: DSP56300 `1378c43074e6ec22f69f14ed55c21e44c5ccadc1`, AsmJit `3577608cab0bc509f856ebf6e41b2f9d9f71acc4`, mc68k `ace95b3d0a5a332db147244762dda65f9a010b9f`, RmlUi `97bb5921595a0528bd67d61f328885ac19643623`, FreeType `828916527ce4f69af722bce46ce54d289001a0bd`, and dlg `72dfcc858c040c54a6a0b88fcb7e70ee186d3167`.
- Target firmware revision: none used. The parent source was checked out clean at its pin in a temporary detached worktree; the trace patch SHA-256 is `d24558fd0556e21c37eff3a7670d1a076f756224a30bd30fa5ac14f923f50d09`.
- Procedure: applied the patch after `git apply --check`; configured with CMake 4.0.1 and Ninja 1.13.2 on macOS 26.6.2 arm64, Apple Clang 21.0.0, using `BUILD_TESTING=OFF`, JUCE plugins disabled, and other synth targets disabled; ran `cmake --build ... --target mdLib --parallel 4`.
- Observation: CMake configured and Ninja built `mdLib` successfully in 222 steps, producing `libmdLib.a`. The build emitted upstream `-Ofast` deprecation and AsmJit memory-operation warnings. CMake could not detect an Xcode version, and `rclone.conf` was absent; neither was needed for this Ninja library target.
- Octemu prerequisites: `make -C vendor/octemu doctor` found all required and optional tools on the documented macOS host. No octemu setup/QEMU/app build or target firmware execution was run.
- Local source state: the original ignored Gearmulator checkout and nested DSP tree remain modified; the isolated build used clean archive contents at the pinned dependency commits and did not alter those checkouts.
- Limit: this verifies instrumentation compilation only. It does not establish an MD firmware boot, target compatibility, or octemu baseline. See [WP-01 provenance report](reports/WP-01-provenance.md) for the full revision and license inventory.
