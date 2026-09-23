# Research log

Record findings as dated entries. Each entry should state the upstream repository and commit, target firmware version, exact command or capture procedure, observation, and what remains uncertain.

## 2026-09-23 — Initial survey

- octabam provides an Octatrack 1.40C image builder, DSP module model, offline renderer, and ColdFire/DSP emulator paths. Its hardware research and image tooling are useful references; whether its image builder can carry a full Machinedrum OS remains unproven.
- Gearmulator MD/MM is a fork of Gearmulator that runs Machinedrum and Monomachine firmware. It can serve as the behavior and audio reference for a user-supplied ROM.
- MAME's `elektronmono.cpp` is a hardware skeleton marked non-working and no-sound. It may inform hardware questions but cannot validate audio.
- The Machinedrum and Octatrack use different ColdFire generations and different DSP hardware: MAME documents a 5206e plus two DSP56303 chips; octabam documents an MCF5445x plus two DSP5636x cores in a DSP56721. This makes a literal image copy unlikely to boot without mapping and shims. Instruction and memory compatibility have not yet been measured.
- The starting workspace contained local reference checkouts, which were copied into ignored `vendor/` for research. `vendor/octemu` is pinned as a submodule at `87000189418c8ca2026dc047bda220b66802809d`. The local octemu checkout had pre-existing uncommitted SDRAM alias and pacing changes; they are preserved as the separate `patches/octemu/0001-sdram-alias-and-interactive-pace.patch`, while the submodule pin refers to its committed upstream state. No firmware was added to this repository. Compatibility measurements remain open.
