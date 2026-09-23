# WP-35 report — Machinedrum evidence imported from octamad

Date: 2026-09-23. Packet: [WP-35](../work_packets/WP-35-octamad-md-import.md).

## Origin and how far it can be trusted

octamad is the user's working copy of [octabam](https://github.com/sambanks/octabam) (MIT). On branch `machinedrum-phase0` (head `aad3e11`, 23 Sep 2026; local, not published), it tried to host Machinedrum voices inside the stock Octatrack OS. That is a narrower goal than this repository's. Its measurements of the Machinedrum itself do not depend on that goal, and they cover what WP-06 through WP-10 and WP-14 through WP-17 need to know first. The tools that produced them are imported in [`scripts/md_reference/`](../../scripts/md_reference/README.md).

| Property | Value |
| --- | --- |
| Reference emulator | Gearmulator MD/MM `8cea0524a75435122c20b669ca114c9ac6509ba2`, the same pin as `references.json`. The DSP56300 submodule is `1378c43`, the revision WP-01 records. Instrumented with the two patches in `patches/gearmulator-md-mm/md-reference/`. |
| Firmware | MD SPS-1UW OS 1.63. The user's update `.syx` has SHA-256 `a58cd61f2efacfb07add0c643162fb4365c30e73831f2021c17b4aa3b42cabd5` (Elektron's public release). The 8 MiB dump matches Gearmulator FNV-64 `33b7c1a9e29f43fd`. |
| Execution origin | Every runtime number is from the MD reference emulator. Nothing here ran on octemu, on an Octatrack DSP model, or on hardware. |
| Cycle counts | From the emulator's cycle model, not hardware. |
| Evidence contract | The runs predate WP-03 and have no version-1 manifests. They are **prior evidence**: good for choosing what to measure and how, not for checking an acceptance item. |

Markers follow octamad's usage:

- **measured**: observed in the reference, by static parsing, or by disassembly, as stated;
- **inferred**: reasoned from measurements and not tested;
- **retracted**: an earlier octamad statement that a later measurement disproved.

## Summary for the port

1. **Both MD DSP programs run mostly from external memory, and the Octatrack's DSP has none.** Engine code, tables and working buffers sit at `0x100000–0x14ffff` in a unified external RAM. The DSP56721 has only on-chip memory: 92 K words per core plus a 64 K-word shared window (octabam `docs/firmware/CHIP.md`, from the datasheet and reference manual). Direct execution at the original addresses is impossible, so relocation is a required adaptation. *(measured / source documented)*
2. **Relocating the voice DSP's code is mechanical and was demonstrated.** Every external-address operand is a long form, patchable in place: 987 words. Six captures that together cover all 50 core engines replay bit-identically after the move. The placement was a test placement, not an OT layout. *(measured, reference)*
3. **The E12 sample block (201,804 words) cannot share on-chip DSP memory with the rest.** Its delivery needs a separate mechanism. *(measured sizes; mechanism open)*
4. **Cycle budgets fit on paper.** The voice DSP's busiest 10 ms with 16 voices is ~1,650 cycles/sample of work. The mixer's is a constant ~1,850. The MD's DSPs run at 2,304 cycles/sample; one OT core has 4,532. Code fetched from the shared window costs ~+80 %, and moving hot code into private P recovers most of it. *(measured in the reference; target timing unmeasured)*
5. **The ColdFire→DSP interface is traced and small.** Per-voice records are pushed through host command `0x12`. The voice DSP's inputs are its records and its resident state, and its output is 32-sample blocks per voice. *(measured)*
6. **The engine handlers on the ColdFire are pure functions.** They have no MAC/EMAC instructions, no hardware access and no calls, which is the easiest case for WP-06. *(measured, static)*

## Firmware container and DSP load images (WP-08)

- **measured:** The update `.syx` holds 14,684 data messages of 112 bytes. Each carries 64 bytes as 2+7+7-packed 16-bit words, addressed by a 6-nibble counter from flash offset `0x4000`. A `7F` trailer gives the total, 939,744 bytes, which equals the decoded length. `mischa85/elektron-firmware-tool` decodes this "pre-ELE" container and its aPLib-variant sections, and all checksums verify.
- **measured:** The decoded stream sits byte-identical in the 8 MiB dump at `0x4000`. The dump adds the bootloader (`0x0000–0x3fff`) and 6.75 MiB of data (`0x100000–0x7c0000`).
- **measured:** There are five sections:

| # | Content | Bytes | Notes |
| --- | --- | ---: | --- |
| 0 | ColdFire MAIN OS | 404,766 | Linked at `0x200000`. Startup sets SP `0x300000`, copies 2,466 bytes to internal SRAM `0x01000088`, clears BSS `0x262400..0x2b7148` and jumps to `0x213a0c`. An aPLib depacker is at `0x248394`; its caller is not located. |
| 1 | DSP load image: voice DSP (producer) | 750,369 | 135 load records: P 234,714, X 13,130, Y 1,868 words. |
| 2 | DSP load image: mixer | 56,469 | 58 load records: P 18,489, X 66, Y 88 words. |
| 3 | Factory data bank | 524,288 | Names such as `TRX MD`. *Inferred* to be kits/patterns. |
| 4 | Factory data bank | 524,288 | Names such as `TRX UW BET…`. *Inferred* to be UW factory content. |

- **measured:** Load image format: little-endian 24-bit words; header `3 0x24 4 0`; then `(space, address, count, words…)` records, with space 0/1/2 = P/X/Y; a closing `3 0x24`. Both images parse exactly to their last word. `tests/test_md_extract.py` covers the parser with synthetic images.
- **measured:** Load map of section 1, the voice DSP (runs merged; `md_extract.py` prints them):
  - low P `0–3e1`, X `202–256` and Y `140–7ff` (each with gaps);
  - external X `140000–1420ff` and `146000–1471ff`;
  - external P `142100–145d37`, `147200–1475ff` and `100000–1028b9`, and the run `1028c0–135205` (code, tables and the E12 samples);
  - external Y `147e00–147f07`.
- **measured:** Load map of section 2, the mixer: P `0–a07`, `140000–143e6a` and `100000–1000d9`, plus small low X and Y. The mixer's code also sits in external memory.
- **Not done:** this is the load-image view. WP-08's first criterion needs the observed HI08 upload streams reconciled with these records. A cheap first check is word counts: section 1 is 250,123 words and section 2 is 18,823, including headers.

## DSP identities (WP-08, WP-07)

- **measured, source:** Gearmulator's `mdhardware.cpp` constructs DSP1 as `m_dspMixer` (HI08 `0x00500000`) and DSP2 as `m_dspProducer` (HI08 `0x00600000`, `mdmemorymap.h`).
- **measured, reference:** Each DSP runs code that only its own image contains. Section 1 runs on the producer, which is the voice DSP, and section 2 on the mixer.
- **measured, static:** The MAIN OS code copied into internal SRAM contains interrupt handlers (`rte`) that access `0x600004`, the voice DSP's host port. This is firmware-side evidence for Gearmulator's `0x500000/0x600000` in the WP-07 HI08 dispute, against MAME's `0x400000/0x500000` map comment. It is not yet a trace of the mixer's port.
- Naming these payload A and B is WP-08's decision.

## Engine catalog (WP-25)

- **measured, static:** 135 machine descriptors of 86 bytes each, at MAIN OS image offset `0x4ef55` (address `0x24ef55`). The decoded part is a 24-bit handler pointer, the machine ID, the family and name, eight 4-character parameter names, eight defaults and eight flag bytes; the remaining 29 bytes are undecoded. The core synthesis catalog has **50 engines**:

| Family | IDs | Machines |
| --- | --- | --- |
| GND | `0x00–0x03` | EMPTY, SN, NS, IM |
| TRX | `0x10–0x1d` | BD SD XT CP RS CB CH OH CY MA CL XC B2 S2 (14) |
| EFM | `0x20–0x27` | BD SD XT CP RS CB HH CY (8) |
| E12 | `0x30–0x3f` | BD SD HT LT CP RS CB CH OH RC CC BR TA TR SH BC (16) |
| P-I | `0x40–0x48` | BD SD MT ML MA RS RC CC HH (9) |
| INP | `0x50–0x55` | GA GB FA FB EA EB |
| MID | `0x60–0x6f` | 01–16 |
| CTR | `0x70 0x71 0x78–0x7b` | AL 8P RE GB EQ DX (RE/GB/EQ/DX drive the master effects) |
| ROM / RAM | `0x80–0xbf` | ROM 01–48, RAM R1–R4 and P1–P4 |

- **measured, reference:** All 50 core engines sound when triggered alone. TRX-S2 is nearly silent at its defaults (RMS 0.00004), so do not read silence there as a port failure.
- **measured, reference:** 325 of the 352 named parameters move a voice-record word, usually one word each (`md_profile map=<id>`, `md_mapsummary.py`). Two engines, GND-NS and TRX-S2, sent no trigger record in the harness; their trigger travels another way.
- **Unmapped parameters:** GND-IM UVAL, TRX-BD RAMP, TRX-CP HARD, EFM-BD MFB, EFM-XT CLIC, EFM-CP MDEC, EFM-HH FB, EFM-CY HPF, E12-OH DEC, E12-SH DEC, E12-BC BC, P-I BD/MT/ML HARD, P-I-SD RVOL, and P-I RC/CC/HH AG. *Inferred*: these act over time rather than in the trigger record.

## DSP load in the reference (WP-09, WP-26)

- **measured, reference model:** Each MD DSP56303 runs at 101.6064 MHz, which is 2,304 cycles per 44.1 kHz sample.
- **measured:** The voice DSP spends most of its time waiting. Two waits take 2,240 of 2,304 cycles at idle:
  - a two-`nop` delay inside nested `do` loops, `P:100092–100098`;
  - a port-C poll, `P:bb–bf`.

  The mixer's wait is a DMA poll at `P:3c–44`. "Work" below is every cycle outside those loops.

| Scenario | Voice DSP, avg | Voice DSP, busiest 10 ms | Mixer, avg |
| --- | ---: | ---: | ---: |
| Idle | 61 | 89 | 1,846 |
| One engine on track 1, 8 hits in 2 s | 74–182 | 102–212 | 1,846–1,850 |
| 16 tracks: the 16 heaviest engines | 1,590 | 1,651 | 1,849 |
| 16 tracks: all-TRX kit | 1,536 | 1,590 | 1,849 |
| 16 tracks: all-E12 kit | 1,484 | 1,508 | 1,849 |

- **measured:** The mixer's ~1,850 cycles are constant, independent of voices and engines. *Inferred*: most of it is the master effects. The mixing share has not been separated out.
- **measured:** Executed code, by walking each executed block to its first flow change:
  - voice DSP: ~10.5 K words in total; 10,326 of them are engine code for the 50 engines (TRX 3,843, P-I 3,969, EFM 1,841, E12 1,413, GND 142);
  - mixer: ~2.3 K words.

  These are well below the image sizes.

## ColdFire → voice DSP interface (WP-14, WP-13)

From `md_profile trace=<id>` with the host-trace patch.

- **measured:** Every packet to the voice DSP is host command vector `0x12`, which feeds DMA5 through the handler at `P:12` → `P:e8`. A packet is `[destination][count−1][words…]`; the destination word is written before the command. An earlier grouping that attached it to the previous packet is corrected.
- **measured:** Idle voices receive short packets addressed to `0x840 + 0x40·voice`, about 1,800 packets a second in total.
- **measured:** A voice with news gets its record. The length is engine-specific: TRX-BD sends 16 words, GND-SN 7. A trigger flag appears on the trigger packet only (TRX-BD `0x11`, GND-SN `0x02`, the DSP-side engine number). The ColdFire resends the record about 114 times a second while the voice sounds.
- **measured:** Values arrive already mapped for the DSP. Ten encoder detents move TRX-BD's pitch word from `b54` to `c29` in uneven steps.
- **measured:** The mixer gets its own stream: vector `0x12` packets of 10, 11, 12, 13 or 22 words, and vector `0x10` packets of 1–3 words. That is about 10,000 packets a second, not decoded.
- **measured, static:** The packets are pushed from interrupt handlers in the SRAM code, not from the update loop.

## ColdFire side: handlers and the per-frame voice update (WP-06, WP-07)

- **measured, static:** Every core engine's descriptor handler is a pure function `f(record*, params*)`: 44 distinct ones, 32–586 bytes each, about 11 KB in all.
  - Each reads eight 16-bit parameters and writes the record's 32-bit fields with shifts, `mulu.w`/`muls.l` and lookups in about ten tables at `0x2462e8–0x24da14`.
  - `m68k-elf-objdump -m m68k:5206e` shows no calls, no MAC/EMAC and no hardware access.
  - *Inferred*: they run unchanged on the OT's ColdFire once their table addresses are relocated. WP-06 must still confirm ISA_A→CFV4e compatibility for the exact instructions.
- **measured, trace + static:** The handlers have one caller, a per-frame voice update at `0x20ad9a` to about `0x20b600`. It loops over the 16 tracks, and per track it:
  1. computes level/pan-like values (*inferred* from the arithmetic);
  2. calls the handler through a RAM pointer table at `0x29f27c`, filled when a machine is assigned. The output record goes to internal SRAM `0x010015b4 + 84·track`, and the parameter block steps 48 bytes per track;
  3. does trigger bookkeeping in a per-track flag at `0x01001510`.
- *Inferred from disassembly:* the voice update's helpers.
  - `0x204c94` is the per-track LFO tick. Its state is in SRAM at `0x01000f8e`, 36 bytes per track, and it has an 8-entry waveform function table at `0x2523ee`.
  - `0x2069bc` applies an LFO value. It reads the destination from the live kit (`0x700022`/`0x700023`) and writes `value >> 7` into the live parameter array at `0x2ad8a6 + 24·track`. Modulation therefore acts before the handler builds the record.
  - `0x209e52` is a kit load. It copies `0x460` bytes into the live kit at `0x70000a`, whose machine IDs sit at `0x7001aa`, and runs only when `0x261a3e` ≥ 0.
- **For WP-07:**
  - The SRAM structures located so far end near `0x01001af4`. That is consistent with the 8 KiB internal SRAM that MAME maps, but it is not an access census, so it does not rule out 64 KiB.
  - The live kit at `0x700000+` lies in the range Gearmulator names `g_patchOsAlias`.

## Voice DSP → mixer link (WP-17)

- **measured:** The voice DSP sends the mixer 16 words per sample period over ESSI0. A 2.2 s trace logged 1,354,752 words in 84,672 samples.
- **measured:** The stream has a **512-word period: 32 samples × 16 voices, voice-major**. Each voice's 32 samples go out contiguously, and track 1 is words 0–31 of each period. With only track 1 playing, no other position is ever non-zero. Decoded as audio, track 1's words are the traced hits.
- *Inferred*: the mixer applies level, pan and sends per voice, and runs the master effects.
- *Inferred, target:* the OT's two cores share one package and the 64 K window. octabam links them through shared memory, and its cross-core race history (`docs/effects/XBUS.md`) is the warning for any replacement ring.

## The voice DSP runs outside the Machinedrum (WP-15/WP-16 precursor)

- **measured, disassembly:** The voice loop, `P:64–e7`, walks the 16 slots once per 32-sample period. For slot `v`:
  1. The record is at `Y:0x800 + 0x40·v`, and the current engine at `y:$153+v`.
  2. A non-zero word 0 is a trigger carrying the DSP engine number. If the engine changed, the loop first calls **init** from the table at `0x145af5`. It then calls **trigger** from `0x145bb6` and clears word 0.
  3. Every period it calls **render** from `0x145c77`, which writes 32 samples into the double buffer `Y:0x100`/`0x120` (`m7 = $1f`). DMA0 sends that buffer to the link. The three tables have 193 entries each.
  4. After slot 0's render the loop waits for frame sync on port C bit 1 (`P:bb–bf`). It then re-arms DMA2 to receive from ESSI0 into the X ring at `x:$243` (`m0 = $ff`), and stores DMA1's position in `x:$256`.
  5. It writes its slot to the host every fourth slot (`P:73`).
- **measured, `md_replay`:** A bare DSP56303, loaded from a `capture=` snapshot, runs the original loop and replays the host stream between slots. It needs no host port, ESSI, DMA or ColdFire. Blocks bit-identical to the reference:

| Capture | Machines | Plain replay | Relocated replay |
| --- | --- | --- | --- |
| c10 | TRX-BD | 33,513 / 33,513 | 33,513 / 33,513 |
| c10_3 | TRX-BD, TRX-S2, PI-CC | 33,508 / 33,508 | 33,508 / 33,508 |
| c01_16 | GND ×3, TRX ×13 | 33,513 / 33,513 | 33,513 / 33,513 |
| c37_16 | E12 ×9, P-I ×7 | 33,504 / 33,504 | 33,504 / 33,504 |
| c1d_16 | TRX-S2, EFM ×8, E12 ×7 | 31,555 / 33,506 | same blocks |
| c47_2 | PI-CC, PI-HH | 33,415 / 33,502 | same blocks |

- **measured:** All 50 engines ran in these captures. The two partial captures differ only in slot 0, identically with and without relocation. The engines concerned (TRX-S2 and PI-CC) are exact on tracks 2 and 3.
  - *Inferred* cause: the host's packet for slot 0 arrives while slot 0 renders, and the replay applies host writes only between slots.
  - Replaying the writes at their cycle would test this.
- **measured:** The comparison detects changes. Altering the pitch word in all 1,428 slot-0 records changes 1,249 of slot 0's blocks and no other slot's.
- **Lesson:** a record's 64 words mix host input with voice state. For example, engine `0x44` keeps its sample pointer in word 12. A replay that wrote the reference's record words hid a relocation fault. Replay the host stream instead.

## Relocation (WP-09, WP-10, WP-11)

- **measured:** Engine code lives only in `P:100000–103db9` and `P:140000–147fff`. It never calls into low P, where only the MD main loop and vectors live (`P:0–e7`). No PC-relative branch crosses between the two regions.
- **measured:** Every external-address operand is a long form, so it can be patched in place without changing any instruction's length. `md_relocate.py` moved the two regions to `0x3b000` and `0x30000` in the emulator's bridged memory and filled the old regions with `0xa5a5a5`. It patched 987 words:
  - 342 loop ends;
  - 425 routine-table entries;
  - 113 displacements;
  - 104 `#>` immediates;
  - 1 absolute operand;
  - 2 jump targets.

  Its recursive descent found 13,712 instructions (15,753 words) from 206 entry points, covering every word the profiles executed. The replay results are in the table above.
- **measured:** The engines also use low memory through **short-form operands**, which cannot be repointed without changing instruction lengths: `X:0–0x27` and `Y:0–7` at hundreds of sites. Long forms reach `X:0x66–0xff`, `Y:0xfa–0xff` and `Y:0x140`/`0x142`. Records are reached through `r6` only.
  - *Inferred, for this repository:* if the payload owns its core, as in an independent boot, low memory stays where it is and needs no swap.
  - Under an OT carrier it collides with stock, which uses `X:0` for audio and scratches `X:0x20–0xff`. Only 36 words must survive between periods (next section).
- **retracted:** a value scan of working RAM for pointers into the code regions found only smooth sine values near their zero crossings, and patching them corrupted samples. Live-state patches are guesses until a replay confirms them.
- **Not done:** relocating the mixer image; a placement at real OT addresses; execution on a DSP5636x model.

## Memory one voice DSP needs (WP-09)

Measured with `md_replay` on the six captures:

- `MD_REPLAY_FOOTPRINT` lists the words that change between periods;
- `MD_REPLAY_POISON` fills ranges with garbage, per period or once, and a capture that stays bit-identical does not read that range.

| What | Words | Notes |
| --- | ---: | --- |
| Engine code | 15,621 | `P:100000–103db9` 9,746 + `P:140000–147fff` 5,875 |
| Tables read inside the code regions | 23,186–28,061 | loaded X data (`0x140000–0x1420ff`, `0x146000–0x1471ff`), P-resident data, routine tables; per-gap granularity overstates |
| Sine table | 32,768 | built at boot at `0x148000`, read as **both X and Y** (32 `x:` and 8 `y:` sites) |
| P-I delay buffers | 1,536 per P-I voice, up to 24,576 | `0x135600 + 0x600·slot`, zeroed at boot |
| Voice blocks | 1,024 X + 1,024 Y | `0x800 + 0x40·slot`, through `r6` |
| Low-memory state carried between periods | 36 | `X:0xa0–0xbf`, `Y:0x1e–0x21` |
| Scratch within a period | 256 X + 320 Y | the rest of `X:0–0xff` and `Y:0–0x13f` |
| E12 samples | 201,804 | see below |

Notes on the table:

- The sine is the MD's own arithmetic, not image data. The init seeds 0 and `0x648` (sin(2π/32768)) and runs a 48-bit recurrence for `0x7ffe` steps.
- The tables split by family:
  - `0x140000–0x1420ff` is read by every family;
  - about 8.5 K words in `0x142291–0x144efb` only by E12/P-I;
  - 4.9 K words in `0x100885–0x101e9f` only by GND/TRX.
- Unused gaps total 4,629 words.

*Inferred*, against the target:

- **Voice DSP without samples.** Code, tables and the sine come to ~71–76 K words, and ~73–78 K with the voice blocks, plus up to 24.6 K of P-I buffers. That is more than one core's 92 K private once the buffers are counted, so part must go in the shared window. The mixer needs its own core.
- **The sine is read in both X and Y.** Only the shared window aliases P/X/Y. The alternative is two copies, one in private X and one in Y, which requires the sine to be read-only after boot. That is not measured; a write watch after boot would settle it.
- **Samples.** The E12 samples bring the total past the whole DSP56721's 2 × 92 K + 64 K = 248 K words, before the mixer. So they are the one piece that must come from ColdFire memory.
- **Memory map.** Stock OT uses the default OMR map, with 8 K P per core. The larger-P maps in `CHIP.md` (up to 36 K P / 32 K X / 24 K Y) are an untested lever that an independent boot is free to use, because stock's 48 K Y constraint no longer applies.

## Program fetch from the shared window (WP-09, WP-26)

- **source documented:** The DSP5672x has no instruction cache. Code executed from the shared window pays one wait state per program fetch, and none for X/Y data (NXP AN3653 §2.4–2.5).
- **measured, fetch-counted:** octamad used an interpreter build with `MD_REPLAY_FETCH=1`. A `rep` counts as one fetch, and a `do` body is fetched once per iteration. The empty slot's pacing busy-wait is excluded. Worst 10 ms, per sample:

| Capture | Engine cycles | Words fetched | With +1 per fetch |
| --- | ---: | ---: | ---: |
| c10 | 142 | 74 | ~215 |
| c10_3 | 329 | 241 | ~570 |
| c01_16 | 966 | 807 | ~1,770 |
| c37_16 | 1,131 | 996 | ~2,130 |
| c47_2 | 1,215 | 988 | ~2,200 |
| c1d_16 | 1,263 | 1,021 | ~2,280 |

- **measured:** Fetches are concentrated.
  - The hottest 1,024 words carry 89–94 % of each capture's fetches, and the hottest 2,724 carry 97–100 %.
  - Union over the six captures for 80/90/95 % coverage: 1,900 / 2,764 / 4,820 words. All executed engine code is 11,392 words.
- **measured:** `md_relocate.py --hot` splits the code into 239 independently movable units and packs 32 of them into 2,724 words of private P. That required re-pointing 22 two-word relative displacements. All captures stay bit-identical. Window fetches per sample fell:
  - c01_16: 807 → 520;
  - c37_16: 996 → 502;
  - c1d_16: 1,021 → 359;
  - c47_2: 988 → 246.
- **Caveats:**
  - The hot set was chosen and measured on the same captures.
  - octamad's interpreter build differed from the JIT build and the reference on c01_16 and c1d_16, for an unexplained reason.
  - DSP5636x cycle timing of this code is unmeasured.

## E12 sample block (WP-09, WP-25)

- **measured:** `P:103dba–135205`, 201,804 words, each holding two signed 12-bit samples.
  - It is 21 samples laid back to back, each followed by `0x88` words that no descriptor covers.
  - The descriptors are at `P:103d7b`, as triples `[start word, length in samples, 0]`. Each start equals the previous start + length/2 + `0x88`, and the last one ends at `0x135206` exactly.
  - Total: 397,896 samples, 9.02 s at 44.1 kHz.
- **measured:** E12 engines read samples through these descriptors. Moving the block's first 774 words with the code broke E12 voices.
- **Not done:** the machine-to-sample mapping; listening to the block (`md_extract.py --wav`).
- ROM/RAM machines play user samples, which are user data and not in the update. They are WP-24's concern.

## Adaptation ledger candidates for WP-10

These are inputs to WP-10's ledger, not decisions.

| # | Original behavior | Target constraint | Smallest candidate change | Evidence so far | Evidence still needed |
| --- | --- | --- | --- | --- | --- |
| 1 | Both DSP programs execute from, and read tables in, external RAM at `0x100000+` | The DSP56721 has no external memory | Relocate each region by an offset; patch long-form operands in place | Voice DSP: 987 words, bit-identical in 6 captures (test placement) | Mixer relocation; a real OT placement; execution on a DSP5636x model |
| 2 | Unified external RAM read as X and Y at one address (the sine) | P/X/Y alias only in the 64 K window | Place in the window, or duplicate into private X and Y | Footprint and poison measured | Whether the sine is written after boot |
| 3 | E12 samples resident in DSP P | They do not fit with the rest in 248 K words | Deliver from ColdFire SDRAM | Sizes, descriptor format | Mechanism, bandwidth, latency; nothing measured |
| 4 | Code fetched from external RAM at MD timing | The window costs +1 wait per P fetch, and there is no I-cache | Hot code in private P; a larger-P OMR map | Fetch counts; hot move bit-identical | DSP5636x timing; an OMR map-switch probe |
| 5 | Producer→mixer link over ESSI0, 512-word periods | The OT cores share a window | A shared-memory ring with explicit synchronization | Stream format measured | Synchronization design; octabam's XBUS race history applies |
| 6 | Pacing by frame sync (port C bit 1) and DMA polls | The OT's frame timing comes from its own ESAI/host path | Re-point the wait conditions | Wait-loop PCs measured | The OT-side frame source (WP-17) |
| 7 | ColdFire SRAM ISRs drive HI08 at `0x600004` (and the mixer's port) | The OT's ColdFire↔DSP interface differs | A host bridge (WP-14) | Static access observed; packet framing traced | The mixer stream decode; target host-port semantics |
| 8 | Engine handlers at `0x2xxxxx` read OS tables | The OT's ColdFire memory map differs | Copy the handlers, relocate the table addresses | Pure-function census (static) | Executed-instruction compatibility (WP-06) |

## Not done by octamad

- **Reconciliation:** no reconciliation of HI08 upload streams with the load images (WP-08).
- **Mixer:** the mixer stream is not decoded, and the mixing/master-effect split of its ~1,850 cycles is not measured.
- **Runtime checks:** no per-engine X/Y data-access profile, no runtime confirmation of the LFO reading, and no time-based trace of the 27 unmapped parameters.
- **E12:** no E12 machine-to-sample map.
- **Target execution:** nothing ran on an Octatrack model: not octemu, not a DSP56721 configuration, not hardware. octamad's next step, running under its `dsp_host`, was not reached.
- **Low-memory swap:** octamad's carrier-specific design (swap 36 low-memory words around a batch of renders) is untested.

## Retractions carried over

- "TRX 13, 49 engines" → TRX 14, 50 engines (descriptor table).
- Sample block starting at `P:1040c0` (9.12 s) or `P:1028c0` (9.40 s) → `P:103dba`. The 6 K words below `0x1040c0` are code, including the hottest per-sample loop.
- Voice DSP code ~6.9 K words → ~10.5 K (the retracted figure had skipped code that was taken for sample data).
- "The voice code fits the shared window" counted code only. With tables and the sine, one voice DSP needs ~71–76 K words.
- Live-pointer patching of working RAM from a value scan was removed (see Relocation).
- Replays that wrote reference record words were superseded by host-stream replay (see the lesson above).

## Reproduction

The tools and build steps are in [`scripts/md_reference/README.md`](../../scripts/md_reference/README.md). Checked on this branch:

- `python3 scripts/md_reference/md_extract.py` passes. It verified the `.syx` and all five section SHA-256 pins, printed both load maps and the 135-descriptor, 50-engine catalog, and wrote `out/machinedrum/os163/inventory.json`.
- The patch stack applies cleanly to clean pinned sources (`mdLib` at `8cea052`, `dsp56kEmu` at `1378c43`), in order: `0001`, the in-review `0002`, `gearmulator-md-hosttrace.patch`, then `gearmulator-md-exechook.patch`.
- `python3 -m unittest tests.test_md_extract`: 4 synthetic tests pass.
- Not re-run here: the C++ builds, the profiles, the captures and the replays. Their numbers are octamad's, from the same pin and the same code.
