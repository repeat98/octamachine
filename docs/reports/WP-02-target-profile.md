# WP-02 — Firmware and target profiles

- Date: 2026-09-23
- Owner: Codex
- Branch: `work/wp-02-target-profiles`
- Status: `in_review`

## Result

The selected source firmware is the Machinedrum SPS-1UW OS 1.63 raw flash image. The ignored local image matches the published 8 MiB size and all three reference fingerprints used by the project. The reference execution profile is Gearmulator MD/MM at its recorded pin, whose source selects the MKII board-identification strap; this is emulator configuration, not identification of a physical Machinedrum.

The target profile is provisionally the Octatrack MKII board declared by the pinned octemu source, with OS 1.40C as the expected firmware profile. A local extracted Octatrack main-OS section exists, but its original distribution archive is absent, so the section's provenance is not verified. No physical Octatrack revision or carrier is identified. The profile is emulator-only and the physical hardware gate remains closed.

The machine, sequencer, panel, MIDI, UW sampling, and persistence inventory below is documented behavior from Elektron's OS 1.63 manual. It is the baseline to measure in later packets, not a claim that the current port or emulator has passed those behaviors.

## Source firmware identity

| Field | Selected profile | Evidence and limits |
| --- | --- | --- |
| Product/model label | Machinedrum SPS-1UW | The canonical image name in MAME and Gearmulator identifies SPS-1UW. The OS 1.63 manual covers SPS-1UW and MKII variants; the image fingerprint alone does not identify a physical board revision. |
| Firmware | OS 1.63 | Gearmulator accepts the 8 MiB image only when its FNV-64 fingerprint matches the OS 1.63 constant. The official manual is explicitly for operating system 1.63. |
| Input format | Raw full-flash `.bin`, no update container | The image is 8,388,608 bytes and matches the emulator's required image size. The package also contains a SysEx updater file, but that file was not used or parsed for this profile. |
| Reference fingerprints | MAME CRC-32 `3d552c99`; MAME SHA-1 `a872a2f3527063673d6ea6d3080c4c62ef0cadc1`; Gearmulator FNV-64 `33b7c1a9e29f43fd` | `python3 scripts/audit_md_image.py /path/to/your-machinedrum-flash.bin --json` reported all three matches for the local ignored image. Its local SHA-256 is intentionally not published, consistent with the existing image-audit record. |
| Reset image facts | Initial SP `0x00000000`; reset PC `0x0000000c` | Static image inspection only. No runtime boot or stack-initialization trace is claimed. |

MAME's pinned source names the 8 MiB image `elektron_sps1-1uw_os1.63.bin`. Gearmulator's pinned `mdtypes.h` and `mdromloader.cpp` record and enforce the OS 1.63 fingerprint. The local byte image remains under ignored `base_firmware/`; it and the local update package are not included in this PR. The profile metadata contains public reference fingerprints, not a path to a private input.

## Reference and target board profiles

| Role | Profile | State |
| --- | --- | --- |
| Machinedrum reference | Gearmulator MD/MM `8cea0524a75435122c20b669ca114c9ac6509ba2`, `MachineModel::Machinedrum`; its pinned source enables the MKII Port A identification loopback | Selected emulator profile. The local physical Machinedrum model, MKI/MKII revision, and +Drive status are unknown. Firmware behavior remains unmeasured until WP-04 captures a run. |
| Octatrack target emulator | octemu `87000189418c8ca2026dc047bda220b66802809d`; `ot-board.c` identifies an Octatrack MKII MCF54455 board, descriptor v2 | Source-documented target profile. The pinned `Makefile` and `fetch-os.sh` select OS 1.40C and expect distribution ZIP SHA-256 `370c55a3dad3996b8e4b46400a205066fdaf185ad4d0255a3a3f835060573ff0`. |
| Local Octatrack input | Ignored `vendor/octemu/out/os/main.bin` exists at 1,112,560 bytes | The original `OCTATRACK_OS1.40C_dist.zip` is absent from the workspace. The existing extracted section may be stale or locally derived; its exact origin and firmware identity are unverified. WP-05 must reacquire or otherwise verify the expected distribution before treating it as a baseline. |
| Physical target/carrier | Not identified in the repository or available profile records | Provisional emulator-only profile. No physical board revision, carrier requirements, recovery path, or hardware run is established. Keep the physical gate closed. |

The Octatrack profile identifies octemu's emulated board, not a physical Octatrack guarantee. The selected OS distribution hash is the expected hash in the pinned fetch script; it is not a hash verification of the local `main.bin` section.

## Documented OS 1.63 feature inventory

The source for this inventory is the [Elektron Machinedrum manual for OS 1.63](https://www.elektron.se/wp-content/uploads/2024/09/machinedrum_manual_OS1.63.pdf). It states that its operating instructions cover the MKI and MKII family and lists their material differences. These entries are documentation evidence only; no feature has been measured in a firmware run for WP-02.

| Area | Selected MKII UW baseline documented by the manual | Evidence status and deferred scope |
| --- | --- | --- |
| Boot | OS in flash; the selected image's reset PC is in the bootstrap flash window. The static audit finds an initial zero stack pointer and bootstrap control-register setup. | [Existing static image audit](../BOOT_FEASIBILITY.md#local-image-audit--2026-09-23). Cold boot, stack setup, DSP boot, and scheduler startup belong to WP-04. |
| Machines and effects | 16 tracks; four MD-synth families and 46 audio-generating machines; five track effects per track; four stereo master effects; 64 kits. | Manual pp. 2–3 and 86. +Drive models expand to 8192 kits; this capacity and behavior are conditional and deferred until presence is established. |
| Sequencer | 128 patterns up to 64 steps, 32 songs, swing/slide/accent, up to 64 parameter locks per step, and real-time control. | Manual p. 86. +Drive models support 4096 songs. MKI patterns are limited to 32 steps; MKI is a deferred hardware profile. |
| Panel | 128×64 backlit LCD; 16 trig keys, track-selection wheel, data-entry knobs, bank/pattern/kit controls, and transport/edit keys. | Manual pp. 4–7 and 86. Panel startup and event behavior remain unmeasured. |
| MIDI | MIDI In/Out/Thru; MIDI can trigger patterns and songs; the manual documents full MIDI support and 384 MIDI-CC-controllable parameters. SysEx covers kits, patterns, songs, globals, and OS updates. | Manual pp. 35–36, 63–70, and 86. Timing, ordering, and transfer behavior belong to later baseline packets. |
| UW sampling | Real-time sampling with RAM machines; sample transfer uses MIDI Sample Dump Standard. The MKII UW profile has four RAM machines, 2.5 MB sampling memory, and 48 ROM slots per sample bank. | Manual pp. 70–75 and 86–87. No sample was loaded or recorded. MKI UW has two RAM machines, 2.0 MB, and 32 slots; MKII +Drive models list 6144 ROM slots, and that capacity is not assumed. |
| Persistence | Kits, patterns, songs, and globals live in battery-backed memory. A fitted +Drive adds 128 snapshots and linked sample banks; a snapshot includes patterns, kits, songs, and globals. | Manual pp. 3 and 63–79. Save/restart, sample-bank, and failure-recovery behavior remain unmeasured. +Drive presence is unknown. |

## Variants and boundaries

- The chosen source firmware identity is SPS-1UW OS 1.63. Gearmulator's pinned Machinedrum profile presents MKII board identification, so MKII UW limits are the working reference profile for the next source baseline.
- The local firmware fingerprint does not identify the physical Machinedrum board or +Drive installation. The manual lists MKI UW limits separately: 32-step patterns, two RAM machines, 2.0 MB sample memory, and 32 sample slots. Do not generalize MKII results to MKI.
- +Drive-equipped and non-+Drive machines have distinct storage capacities and snapshot/sample-bank behavior. The installed variant is not identified; +Drive-specific behavior remains outside the selected measured baseline until a profile is available.
- Non-UW Machinedrum models, other OS revisions, and Monomachine are deferred. Their firmware and feature differences are not represented by this selected profile.
- The Octatrack MKII emulator profile is provisional for all physical work. The local OS section lacks its source archive, and the physical board/carrier revision has not been identified.

## Reproduction and next use

1. Keep an entitled raw Machinedrum dump in ignored `base_firmware/` and run `python3 scripts/audit_md_image.py /path/to/your-machinedrum-flash.bin --json`.
2. Require the 8 MiB size, MAME CRC-32/SHA-1, and Gearmulator FNV-64 matches recorded above before using it for the selected OS 1.63 source profile.
3. Before the Octatrack baseline, restore or reacquire the pinned OS 1.40C distribution and verify the expected distribution checksum with octemu's `make os` path. Keep the OS and extracted section ignored.
4. Use WP-04 for a bounded Machinedrum cold-boot trace and WP-05 for an unmodified Octatrack baseline. Keep physical startup and parity claims closed until the actual target hardware and recovery requirements are identified.

## Sources

- [Elektron Machinedrum User's Manual, operating system 1.63](https://www.elektron.se/wp-content/uploads/2024/09/machinedrum_manual_OS1.63.pdf), especially pp. 2–7, 35–36, 63–87.
- [MAME Machinedrum/Monomachine driver at `d7ffd71`](https://github.com/mamedev/mame/blob/d7ffd71ed97831b7f995337d6c5bd1bbb03898af/src/mame/elektron/elektronmono.cpp) for the image identifier, machine outline, and its documented model assumptions.
- [Gearmulator MD/MM ROM identity at `8cea052`](https://github.com/joelanders/gearmulator-md-mm/blob/8cea0524a75435122c20b669ca114c9ac6509ba2/source/elektron/md/mdLib/mdtypes.h), [ROM loader](https://github.com/joelanders/gearmulator-md-mm/blob/8cea0524a75435122c20b669ca114c9ac6509ba2/source/elektron/md/mdLib/mdromloader.cpp), and [MKII board-ID setup](https://github.com/joelanders/gearmulator-md-mm/blob/8cea0524a75435122c20b669ca114c9ac6509ba2/source/elektron/md/mdLib/mdmc.cpp).
- [octemu board profile at `8700018`](https://github.com/markandrus/octemu/blob/87000189418c8ca2026dc047bda220b66802809d/src/board/ot-board.c), plus its pinned [OS fetch script](https://github.com/markandrus/octemu/blob/87000189418c8ca2026dc047bda220b66802809d/scripts/fetch-os.sh) and [Makefile](https://github.com/markandrus/octemu/blob/87000189418c8ca2026dc047bda220b66802809d/Makefile).
