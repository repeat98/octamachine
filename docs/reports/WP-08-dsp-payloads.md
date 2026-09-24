# WP-08 — Machinedrum DSP load images and HI08 uploads

Date: 2026-09-24

Scope: the local Machinedrum SPS-1UW OS 1.63 update, its decoded DSP load records, and repeated Gearmulator MD/MM startup traces. The comparison reads private trace values in process and emits only reviewed metadata. It is reference-emulator evidence, not physical-board evidence.

## Result

The two update sections were reconciled with the host-port uploads in both cold and cached startup instances from two independent WP-04 full-trace runs. All eight source-DSP streams contain one exact, ordered match for their decoded load-record stream. The images are distinguished by the observed HI08 window: section 1 is sent to DSP2 at `0x00600000`; section 2 is sent to DSP1 at `0x00500000`. The transfer order is DSP2 first, DSP1 second. No firmware words, extracted image, raw trace, or word hash is included.

Each device first receives a short DSP boot block whose entry PC is `P:0x000100`. The pinned Gearmulator `DspBoot` model consumes a length, an address, and that many program words, then changes the HI08 callback to the running DSP. The trace-derived block lengths are 183 words for DSP2 and 153 for DSP1. One further host word appears between each boot block and the image records; its role is not identified. The matched records are byte-for-byte/word-for-word exact after that point.

## Provenance and method

| Input | Revision / identity | Use |
| --- | --- | --- |
| Machinedrum update | SPS-1UW OS 1.63; public update SHA-256 `a58cd61f2efacfb07add0c643162fb4365c30e73831f2021c17b4aa3b42cabd5` | Local input only; the pinned extractor rejects any other update. |
| Gearmulator MD/MM | `8cea0524a75435122c20b669ca114c9ac6509ba2` | Source model and WP-04 full bus traces. |
| Recursive ColdFire peripheral model | `mc68k` `ace95b3d0a5a332db147244762dda65f9a010b9f` | HI08 TXH/TXM/TXL assembly and ICR byte-order behavior. |
| Recursive DSP model | `dsp56300` `1378c43074e6ec22f69f14ed55c21e44c5ccadc1` | `DspBoot::hdiWriteTX` length/address/data sequence and callback completion. |
| Repeated boot traces | WP-04 private full traces; two independent processes, each with cold and cached instances | Values are read locally and never copied into tracked output. See the [WP-04 baseline](WP-04-md-baseline.md). |

The extractor expands the five update sections and validates their pinned SHA-256 digests. It parses each DSP section as little-endian 24-bit words with a four-word section header, ordered `(space, address, count, data...)` records, and a two-word trailer. `md_verify_uploads.py` uses the same load-image parser, reconstructs the source HI08's 24-bit transmit words from the bus writes, and compares the ordered record stream in memory. The reference HI08 ICR sets big-endian TX order during both matched uploads; the values arrive as H:M:L and match the numeric 24-bit words from the little-endian section files.

The verifier reports the record-stream position in the host word stream, the DSP boot-prefix size/entry PC, the cycle range, the endianness mode, and the number of trailing host words. It prints no payload values and does not write a transformed trace. It requires the matched records to use big-endian TX order and rejects explicit truncation markers, malformed bus rows, an incomplete DSP1/DSP2 pair for a trace instance, ambiguous matches, wrong DSP associations, and missing matches. Capture-record completeness is established separately; the script does not parse WP-03 manifests or infer that an arbitrary EOF is truncated.

## Payload identity and upload boundary

Payload names here follow the measured source ports. “A” and “B” are local labels for this report, not target-core assignments.

| Payload | Observed source port and role | Update section | Records / P, X, Y words | Section image words | Exact record-stream words | DSP boot block; record-stream position | Record-stream model cycles | Trailing host words in the WP-04 trace |
| --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: |
| A | DSP2, `0x00600000`; Gearmulator producer / voice DSP | Section 1; SHA-256 `e1d845a772f87b04e1681130f3e3eab2db20dc4d047489375a3be93870c591bc` | 135; P 234,714, X 13,130, Y 1,868 | 250,123 | 250,117 | 183 program words at `P:0x000100`; 185 host words including the length and address; one further word; match at host word 186 | `40,732,233–44,968,113` | 7 |
| B | DSP1, `0x00500000`; Gearmulator mixer/main DSP | Section 2; SHA-256 `0fd8b64a4cef976c07f246ab543294c263b08f543ebff8f8415811d29e434c06` | 58; P 18,489, X 66, Y 88 | 18,823 | 18,817 | 153 program words at `P:0x000100`; 155 host words including the length and address; one further word; match at host word 156 | `46,328,113–46,684,375` | 534 |

“Section image words” includes the DSP load-image header and trailer. “Exact record-stream words” includes each record's space, address, count, and data words, but excludes that framing. Match positions are zero-based host-word indices. The larger host-stream suffixes extend into firmware startup and are not classified as additional load records here.

The capture order is visible in the repeated model-cycle intervals: DSP2's record stream completes before DSP1's begins. For each image, cold and cached traces and both independent processes report the same record-stream offsets, cycle intervals, boot prefix, and suffix counts. Cross-checking against the opposite section finds no swapped DSP/image match.

## Load maps and memory spaces

The rows below are contiguous runs merged from adjacent records. They retain each DSP memory-space tag and record order; they are not file offsets or a physical board decode.

### Payload A — DSP2 / section 1

| Space and inclusive range | Words |
| --- | ---: |
| P `0x000000–0x000023` | 36 |
| P `0x000060–0x000063` | 4 |
| P `0x000024–0x00003e` | 27 |
| P `0x000064–0x0003e1` | 894 |
| X `0x000202–0x00024a` | 73 |
| X `0x000256` | 1 |
| Y `0x000140–0x000782` | 1,603 |
| Y `0x0007ff` | 1 |
| X `0x140000–0x1420ff` | 8,448 |
| P `0x142100–0x145d37` | 15,416 |
| X `0x146000–0x1471ff` | 4,608 |
| P `0x147200–0x1475ff` | 1,024 |
| Y `0x147e00–0x147f07` | 264 |
| P `0x100000–0x1025c4` | 9,669 |
| P `0x102600–0x10268f` | 144 |
| P `0x102700–0x102765` | 102 |
| P `0x102780–0x1027d5` | 86 |
| P `0x102800–0x10284f` | 80 |
| P `0x102880–0x1028b9` | 58 |
| P `0x1028c0–0x135205` | 207,174 |

The E12 sample region is the subrange `P:0x103dba–0x135205` (201,804 words; image-derived metadata from WP-35). No sample bytes or waveform were produced or committed in this packet.

### Payload B — DSP1 / section 2

| Space and inclusive range | Words |
| --- | ---: |
| P `0x000000–0x000a07` | 2,568 |
| X `0x000640–0x000641` | 2 |
| X `0x000648–0x000687` | 64 |
| Y `0x000100–0x00014f` | 80 |
| Y `0x0001c2–0x0001c9` | 8 |
| P `0x140000–0x143978` | 14,713 |
| P `0x14398d–0x143cbf` | 819 |
| P `0x143dc0–0x143e6a` | 171 |
| P `0x100000–0x1000d9` | 218 |

The Gearmulator DSP model allocates P and X/Y address spaces separately, then bridges shared external SRAM at DSP address `0x020000` and above. Thus a P range and an X/Y range at external addresses describe views of the model's shared backing; retain the P/X/Y tags instead of flattening them into one guessed address space. This is the emulator's memory model, not a physical RAM overlay measurement.

## Reproduction

Run from a local octamachine checkout with the user's matching OS 1.63 update and built `vendor/elektron-firmware-tool`. Keep both the trace paths and all generated output private:

```sh
python3 scripts/md_reference/md_extract.py \
  --syx /path/to/your-private/Elektron_SPS1-1UW_OS1.63.syx
python3 scripts/md_reference/md_verify_uploads.py \
  /path/to/private-wp04/cold-a.trace.txt \
  /path/to/private-wp04/cold-b.trace.txt
```

The extraction was repeated three times in the WP-08 worktree. Each run accepted the pinned update and five section hashes; stdout, all five extracted sections, and `inventory.json` were identical. The existing synthetic load-parser tests verify record decoding and reject a truncated record, missing trailer, and wrong header. `make check` runs those tests without reading firmware.

The private verifier run found eight exact record-stream matches: both source DSPs, both cold/cached instances, and both independent full-trace processes. Payload A always matched section 1 at host word 186; payload B always matched section 2 at host word 156. The source port order and TX byte order were stable across all eight matches.

## Limits and next work

- Measurements cover only the Gearmulator MD/MM model and local OS 1.63. They do not prove electrical HI08 wiring on a Machinedrum board.
- The `P:0x000100` bootstrap entry and prefix lengths are trace measurements interpreted using Gearmulator's `DspBoot` code. The single pre-record word and trailing words are not decoded.
- The DSP load-image framing is validated by the extractor, but this comparison deliberately matches the ordered load records inside it. It does not assign separate host-port meanings to the four-word header or two-word trailer.
- No DSP image, upload value, raw trace, or sample content is committed. P/X/Y map ranges, public pinned hashes, counts, entry metadata, and equality outcomes are the reviewed artifacts.
- No target-side DSP56721 execution, target memory fit, audio comparison, ported bootstrap, or physical hardware test was performed. WP-09 owns DSP feasibility; the host-port bridge remains later WP-14/WP-17 work.

## Repository validation

`make check` passed: nine reference repositories validated, Python scripts compiled, and all 20 tests passed. `git diff --check` passed. The two full-trace processes both verified exact records without writing trace-derived output.
