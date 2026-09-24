# MD reference tools (imported from octamad, WP-35)

Tools written during octamad's Machinedrum excursion (branch
`machinedrum-phase0`, head `aad3e11`, 23 Sep 2026; octamad is MIT). They
extract and inventory MD OS 1.63 from the user's own update, profile both MD
DSPs in the pinned Gearmulator fork, capture the voice DSP's inputs and
outputs, replay the voice DSP standalone, and relocate its code. Findings and
their confidence are in the [WP-35 report](../../docs/reports/WP-35-octamad-md-import.md).

Changes from octamad: the repository-root depth, the paths in usage text and
comments, and the extractor's docstring. The C++ sources are otherwise
byte-identical. Everything they write goes to ignored `out/`.

| Tool | Does | Needs |
| --- | --- | --- |
| `md_extract.py` | Decodes the MD OS 1.63 update (`.syx`) into five sections, refuses any input or section whose SHA-256 differs from the pins, parses both DSP load images into P/X/Y records, walks the 135 machine descriptors, and writes `out/machinedrum/os163/inventory.json`. `--wav` writes the E12 sample block. `--disasm` disassembles both images. | `base_firmware/Elektron_SPS1-1UW_OS1.63/Elektron_SPS1-1UW_OS1.63.syx`, `vendor/elektron-firmware-tool` built (`make refs`, then its `make`). `--disasm` also needs `vendor/dsp56300` built with `dsp56kDisassemble`. |
| `md_verify_uploads.py` | Reassembles the private trace's HI08 TXH/TXM/TXL writes and compares each source DSP's ordered `(space,address,count,data...)` records with its decoded image. Prints only DSP/window identity, record/word counts, match offsets, clock cycles, boot-prefix metadata, and equality; never prints or writes DSP words. | `md_extract.py` output and one or more complete private WP-04 Gearmulator bus traces. |
| `md_profile.cpp` | Boots the 8 MiB dump in Gearmulator and runs scenarios: `idle`, one machine per id, `load=<16 ids>`, `trace=<id>` (host-port, ColdFire handler and ESSI link traffic), `map=<id>` (record words per encoder), `capture=<ids>` (a producer snapshot plus every record and rendered block, md_replay's input). Writes per-JIT-block cycle counts for both DSPs. | Gearmulator at the pin, with both patches below, JIT build. |
| `md_replay.cpp` | Runs the voice DSP's original loop on a bare DSP56303 from a `capture=` snapshot. It replays the host stream between slots and compares every 32-sample block with the reference. `--reloc` applies `md_relocate.py`'s plan. Env: `MD_REPLAY_FETCH=1|2` (program-fetch counts; interpreter build), `MD_REPLAY_POISON`, `MD_REPLAY_POISON_ONCE`, `MD_REPLAY_FOOTPRINT`, `MD_REPLAY_BLOCKS`, `MD_REPLAY_STATEDIFF`, `MD_REPLAY_OUTDIFF`, `MD_REPLAY_KEEP_OLD`, `MD_REPLAY_WIPE`. | `dsp56kEmu` from the same tree. |
| `md_dis.cpp` | Decodes every address of a snapshot's P ranges, for the relocator's recursive descent. | `dsp56kEmu`. |
| `md_relocate.py` | Moves `P:100000–103db9` and `P:140000–147fff` to new bases and patches every long-form address into them. `--hot` also moves the hottest code units into private P. Writes `<capture>/reloc.txt`. | `out/md_reference/md_dis`, a capture. |
| `md_addrs.py` | Inventories the absolute addresses that executed voice-DSP code references, by kind. | Profile output. |
| `md_analyze.py` | Summarizes a profile: per-engine work (cycles outside the wait loops) and executed code footprint. | Profile output, `inventory.json`, `--disasm` output. |
| `md_mapsummary.py` | Summarizes `map=` runs: which record word each named parameter moves. | `map=` output, `inventory.json`. |

## Build

The two patches live in `patches/gearmulator-md-mm/md-reference/`, outside
the numbered stack that `scripts/prepare_gearmulator.py` applies. They were
checked to apply cleanly on the pinned sources after
`0001-opt-in-md-bus-trace.patch` and `0002-md-baseline-checkpoints.patch`.
Apply them to a **separate** Gearmulator checkout at the pin, so another
packet's trace build is not changed underneath it:

```sh
git -C <gearmulator-copy> apply $PWD/patches/gearmulator-md-mm/md-reference/gearmulator-md-hosttrace.patch
git -C <gearmulator-copy>/source/dsp56300 apply $PWD/patches/gearmulator-md-mm/md-reference/gearmulator-md-exechook.patch
cmake -S <gearmulator-copy> -B out/md_reference -DCMAKE_BUILD_TYPE=Release \
  -DDSP56K_FORCE_INTERPRETER=OFF -Dgearmulator_BUILD_JUCEPLUGIN=OFF \
  -Dgearmulator_BUILD_JUCEPLUGIN_CLAP=OFF -Dgearmulator_SYNTH_OSIRUS=OFF \
  -Dgearmulator_SYNTH_OSTIRUS=OFF -Dgearmulator_SYNTH_VAVRA=OFF \
  -Dgearmulator_SYNTH_XENIA=OFF -Dgearmulator_SYNTH_NODALRED2X=OFF \
  -Dgearmulator_SYNTH_JE8086=OFF \
  -DCMAKE_PROJECT_gearmulator_INCLUDE=$PWD/scripts/md_reference/md_profile.cmake
cmake --build out/md_reference --target md_profile md_replay md_dis -j8
```

For program-fetch counts, build a second tree with
`-DDSP56K_FORCE_INTERPRETER=ON` (octamad used `out/md_reference_interp`). On
`c01_16` and `c1d_16`, octamad's interpreter build was not bit-identical to
the JIT build or the reference, and the cause was not found.

## Typical run

```sh
python3 scripts/md_reference/md_extract.py
python3 scripts/md_reference/md_verify_uploads.py \
  /path/to/private-wp04/cold-a.trace.txt \
  /path/to/private-wp04/cold-b.trace.txt
mkdir -p out/md_profile/cat out/md_profile/cap
out/md_reference/md_profile base_firmware/elektron_sps1-1uw_os1.63.bin out/md_profile/cat 0x10 0x11 ...
python3 scripts/md_reference/md_analyze.py out/md_profile/cat
out/md_reference/md_profile base_firmware/elektron_sps1-1uw_os1.63.bin out/md_profile/cap capture=0x10
out/md_reference/md_replay out/md_profile/cap/c10                  # exit 0: every block bit-identical
python3 scripts/md_reference/md_relocate.py out/md_profile/cap/c10
out/md_reference/md_replay out/md_profile/cap/c10 --reloc
```

## Verification

- **Checked in octamachine (WP-35):** `md_extract.py` reproduced every pinned section hash, both load maps and the 135-descriptor, 50-engine catalog. The patch stack applied cleanly on the pinned sources.
- **Reproduced in octamachine (WP-35 follow-up):** `md_profile`, `md_replay`, and `md_dis` built from the pinned Gearmulator copy. One local `capture=0x10` run produced `c10`; two standalone replays each exited 0 with 33,513 identical 32-sample blocks and zero differences. The [WP-03 manifest](../../docs/reports/WP-35-c10-replay-v1.manifest.json) and its redacted [JSONL summary](../../docs/reports/WP-35-c10-replay-v1.events.jsonl) are checked in. The c10 snapshot and raw logs stay under ignored `out/`.
- **WP-08 upload reconciliation:** run `md_extract.py` first, then `md_verify_uploads.py` on private traces identified as complete by their capture records. The verifier rejects explicit truncation markers, malformed bus rows, a missing DSP pair, unexpected transmit byte order, and any upload that does not exactly match; it does not validate capture-manifest completeness. It reports no payload words and writes no capture-derived files. Keep all `.trace.txt` files local because their values contain firmware data.
- **Run behavior:** `md_profile` writes files directly into its requested output directory and does not create that directory. Create it first with `mkdir -p`, as shown above.
- **Prior evidence:** the other profiles, captures, relocations, and replay results in the WP-35 report remain octamad's measurements from the same Gearmulator pin and code; they were not reproduced in this follow-up.
