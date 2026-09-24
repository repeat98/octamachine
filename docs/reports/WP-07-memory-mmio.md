# WP-07 — Machinedrum memory and MMIO contract

Date: 2026-09-24

Scope: the pinned Gearmulator Machinedrum model running the local Machinedrum SPS-1UW OS 1.63 image, primary MCF5206E / MCF54455 documentation, and the pinned octemu board model. The bus observations are emulator evidence; no Machinedrum or Octatrack hardware was measured.

## Result

The working source map for the reference model is now explicit. The DSP HI08 windows are `0x00500000` (DSP1 mixer) and `0x00600000` (DSP2 voice producer), not the MAME address-map comments' `0x00400000` / `0x00500000`. The MCF5206E part has 8 KiB SRAM; Gearmulator's 64 KiB allocation is an over-wide emulator backing. The trace also confirms the startup program writes one byte at `MBAR+0x1003`, which the MCF5206E register map does not explain. That address remains a board-decode question.

Clock evidence is bounded rather than resolved to a physical board value: MAME models 25.447 MHz, Gearmulator models 40 MHz, and the NXP part documentation lists 40 and 50 MHz grades. The 128-frame WP-04 trace window is consistent with Gearmulator's 40 MHz model. None of those values establishes the clock fitted to a Machinedrum board.

The source devices touched through the reference idle checkpoint each have a proposed target owner and access contract below. The target-side address maps and alias plan are proposals for the octemu MCF54455 guest. They have not been implemented or executed. Octemu's PC-side RAM windows, catch-all MBAR, and DSP port are emulator instrumentation, not evidence of a physical Octatrack decode.

## Source revisions and evidence

| Source | Revision or document | Use |
| --- | --- | --- |
| Gearmulator MD/MM | `8cea0524a75435122c20b669ca114c9ac6509ba2` | Reference model map and modeled 40 MHz host clock; see its [`mdmemorymap.h`](https://github.com/joelanders/gearmulator-md-mm/blob/8cea0524a75435122c20b669ca114c9ac6509ba2/src/elektron/md/mdLib/mdmemorymap.h) and [`mdhardware.cpp`](https://github.com/joelanders/gearmulator-md-mm/blob/8cea0524a75435122c20b669ca114c9ac6509ba2/src/elektron/md/mdLib/mdhardware.cpp). |
| MAME | `d7ffd71ed97831b7f995337d6c5bd1bbb03898af` | Skeleton map, 25.447 MHz clock, and conflicting HI08 comments in [`elektronmono.cpp`](https://github.com/mamedev/mame/blob/d7ffd71ed97831b7f995337d6c5bd1bbb03898af/src/mame/elektron/elektronmono.cpp). |
| Octatrack emulator | octemu `87000189418c8ca2026dc047bda220b66802809d` | Target PC-model map and DSP bridge: [`ot-board.c`](https://github.com/markandrus/octemu/blob/87000189418c8ca2026dc047bda220b66802809d/src/board/ot-board.c), [`ot-dsp-port.c`](https://github.com/markandrus/octemu/blob/87000189418c8ca2026dc047bda220b66802809d/src/board/ot-dsp-port.c), and [`ot-dsp-shim.cc`](https://github.com/markandrus/octemu/blob/87000189418c8ca2026dc047bda220b66802809d/src/board/ot-dsp-shim.cc). |
| Source CPU | [MCF5206E User's Manual](https://www.nxp.com/docs/en/data-sheet/MCF5206EUM.pdf), especially §§2, 5–6, 8–14 and Appendix A | Bus widths, SRAM, SIM register definitions, timers, UART, M-Bus, and peripheral map. |
| Source CPU speed grades | [NXP MCF5206E product page](https://www.nxp.com/products/MCF5206E) | Documents 8 KiB SRAM and available 40 / 50 MHz parts. This is a part capability, not a board-clock measurement. |
| Target CPU | [MCF54455 Reference Manual](https://www.nxp.com/docs/en/reference-manual/MCF54455RM.pdf) | MMU / TLB capability used in the proposed alias plan. |
| Executed reference trace | WP-04 private full traces, two cold and two cached reference instances | Address, direction, width, and event counts only. Raw trace values, firmware, and local disassembly remain private. See the [WP-04 baseline report](WP-04-md-baseline.md). |
| Static firmware evidence | Local OS 1.63 image inspected in place; WP-35 report for related image facts | Reset setup and SRAM vector/code placement summarized below. Firmware bytes and disassembly are not included. |

The WP-04 source trace patch records MMIO access address, width, direction, and model cycle. The reviewed analysis discarded payload values and program-counter samples. Counts below are from the full local traces; the underlying traces are not part of this repository.

## Machinedrum source map

Addresses in this table describe the Gearmulator model and the source firmware's virtual/bus view. Aliases share modeled backing storage; this table is not a physical board decode.

| Source address | Modeled size / use | Evidence and proposed target treatment |
| --- | --- | --- |
| `0x00000000–0x000fffff` | Bootstrap/low flash alias | Gearmulator aliases the first MiB of the full flash image here. The octemu loader currently enters its own OS directly at `0x40000400`; it does not fetch the Machinedrum reset vectors. A dedicated source reset trampoline and ROM mapping are still needed. |
| `0x00100000–0x001fffff`; alias `0x00700000–0x007fffff` | 1 MiB patch RAM | Map both guest ranges to one reserved SDRAM backing so reads and writes remain coherent. Make it writable and executable while the source bootstrap and OS use it. |
| `0x00200000–0x002fffff`; aliases `0x20000000–0x200fffff`, `0x40000000–0x400fffff` | 1 MiB main RAM | Map all three guest views to the same target SDRAM bytes. The firmware's initial stack pointer is `0x00300000`, one byte past this source range; the first pushed longword is within the range. Keep code/data writable and executable until cache and copy behavior is verified. |
| `0x00300000–0x0030ffff` | Source SIM at `MBAR=0x00300000` | Route to a source-compatibility MMIO dispatcher. Do not forward these addresses to MCF54455-native registers. One write at offset `+0x1003` is still unresolved and must trap/log until the source board decode is identified. |
| `0x00500000–0x00500007` | DSP1 HI08 host port, mixer | Back with a host-port bridge that preserves access width and HI08 state. |
| `0x00600000–0x00600007` | DSP2 HI08 host port, voice producer | Back with the same bridge contract but select the voice DSP. The firmware ISR statically accesses `0x00600004`; the runtime trace exercises this eight-byte window. |
| `0x01000000–0x01001fff` | 8 KiB MCF5206E internal SRAM | Map vectors and SRAM-resident code/data to dedicated writable, executable target backing. The image sets VBR to `0x01000000`, configures RAMBAR there, and copies code to `+0x88`; the static structures examined end at `+0x1af4`. Full executed SRAM range coverage is still open. |
| `0x01000000–0x0100ffff` | Gearmulator's 64 KiB SRAM allocation | Emulator implementation detail. It conflicts with NXP's 8 KiB part specification and MAME's `0x01000000–0x01001fff` map. Do not reproduce the 64 KiB size as hardware. |
| `0x10000000–0x107fffff` | 8 MiB full flash mapping | Keep source guest flash separate from target CS1 storage. No CPU bus memory-access trace or NOR command sequence was captured, so array reads, command behavior, persistence, and target backing are not established here. WP-23 owns persistence semantics. |

### HI08 window discrepancy

The MAME driver prose and Gearmulator's source identify DSP1/mixer at `0x00500000` and DSP2/voice producer at `0x00600000`. MAME's address-map comments instead place them at `0x00400000` and `0x00500000`. The repeated WP-04 Gearmulator traces contain accesses to both `0x00500000` and `0x00600000`, including DSP2 host-port traffic; there were no events at `0x00400000`. WP-35 static firmware analysis independently finds an ISR access at `0x00600004`. For the reference model and source firmware contract, use `0x00500000` / `0x00600000`. The actual Machinedrum board's electrical decode remains a hardware/schematic question.

Each modeled HI08 port occupies eight bytes. Trace instrumentation observed byte and word accesses; no 32-bit access appeared in the MMIO trace. The MCF5206E manual describes the 32-bit data bus and 8-, 16-, and 32-bit transfers; the trace's observed operand widths should be preserved by an adapter rather than widened opportunistically.

## Peripheral activity through reference idle

The full WP-04 trace spans construction through firmware-ready; idle itself is a later state/cycle snapshot. The first 128-frame cold sample window is bounded by Gearmulator model cycle `116,106`. Counts below are per cold or cached labeled instance and exclude access values.

| Region / access | First 128-frame window | Full trace per labeled instance | Proposed target owner and semantics |
| --- | ---: | ---: | --- |
| SIM `+0x0000–+0x00ff`, reads / writes | 15,563 / 74 byte reads; 21 word writes | 2,591,231 / 2,005,115 | Source-compatibility dispatcher. Preserve register width, read/write side effects, reset state, and source interrupt masks; native MCF54455 SIM/INTC must not receive source offsets directly. |
| DSP1 HI08 `0x00500000`, reads / writes | 156 byte reads; 1 byte and 312 word writes | 6,336 / 38,772 | Mixer side of a two-core host bridge. Preserve the HI08 byte/word protocol and status effects. |
| DSP2 HI08 `0x00600000`, reads / writes | 500 byte reads; 1 byte, 372 word writes, and 2 word reads | 28,058 / 500,627 | Voice side of the same bridge. Preserve selected-core identity and source interrupt/ready semantics. |
| Unclassified `MBAR+0x1003`, byte write | One write of zero | One write in each cold/cached instance | Board-decode latch or explicit unknown-address fault/log in the compatibility layer. It is not a documented MCF5206E SIM register. |
| MCF5206E CPU DMA registers `+0x0200–+0x0254` | None | None | No source CPU-DMA owner is required by this idle trace. Do not confuse this with the DSP-internal DMA observed in WP-35. Revisit only if later features exercise it. |
| M-Bus/I²C registers `+0x01e0–+0x01f0` | None | None | No source M-Bus owner is required by this idle trace. Later feature evidence may add one. |

Within SIM, the trace touches these documented groups:

| Source SIM offsets / fields | Observed role | Proposed target behavior |
| --- | --- | --- |
| `+0x17`, `+0x1c`, `+0x1d`, `+0x1f`, `+0x20`, `+0x36` | External IRQ4, timer 1/2 ICR, UART1/2 ICR, and interrupt mask | Keep source register state and source interrupt priority/vector behavior in the compatibility layer; assert target exceptions using the target INTC only after the source-to-target vector mapping is explicit. |
| Chip-select groups `+0x64–+0x92` (CS0–CS3) and `+0xa0–+0xaa` (CS5) | Base, mask, and control register accesses; paired `+0x04/+0x06` halves appear as word accesses | Store source-visible configuration and decode only the mapped regions this report lists. Avoid letting source chip-select setup reconfigure physical MCF54455 chip selects. |
| `+0xc6`, `+0xca` | DRAM controller configuration and pin assignment register | Preserve readable/writable source state in the dispatcher. No evidence here supports using these writes to configure target SDRAM hardware. |
| Timer 1 `+0x100/+0x104/+0x10c/+0x111`; timer 2 `+0x120/+0x124/+0x12c/+0x131` | Mode, reference, counter, and event/status access | Implement source counter, status-clear, and interrupt timing semantics over target PIT/DTIM or a cycle service. The exact timer input clock and divider on hardware remain open. |
| UART1 `+0x140–+0x170`; UART2 `+0x180–+0x1b0` | Mode, status/clock select, command, RX/TX, port/auxiliary, interrupt, and baud-register accesses; status reads are frequent | Provide source register/FIFO/status semantics and route each serial function only after board wiring is known. Octemu's UART0 is MIDI, UART1 is its panel link, and UART2 is a crossfader model; these are target-model endpoints, not proof of source pin correspondence. |
| `+0x1c5`, `+0x1c9` | Parallel-port data and direction registers | Maintain source GPIO state in the compatibility layer; map output side effects to target GPIO/panel services only when the board function is established. |

### Post-ready initialization and idle trace

WP-04's original raw MMIO trace ended at firmware-ready, so a second bounded capture was made in a disposable copy of the pinned Gearmulator tree. The test disabled tracing through startup, enabled it immediately after each firmware-ready checkpoint, and stopped after the corresponding no-stimulus idle checkpoint. A local tracer variant retained only per-instance address, width, direction, and counts; it discarded all access values and did not write per-access records. The cold and cached intervals in the same driver process were repeated in a second process. Both runs reached the WP-04 idle frame/cycle checkpoints and produced identical checkpoint metadata and all 43 aggregate rows.

| Source region | Late access offsets, direction, and width | Cold blank-flash count | Cached-flash count | Proposed target owner |
| --- | --- | ---: | ---: | --- |
| Timers | `W2 +0x104,+0x10c`; `W1 +0x111`; `R2/W2 +0x124`; `R2 +0x12c`; `W1 +0x131` | 46,006 | 28,418 | Source timer service backed by a target PIT/DTIM or cycle service, preserving source counter/status/interrupt behavior. |
| UART2 | `R1 +0x184`; `W1 +0x18c,+0x194` | 119,456 | 99,694 | Source UART register/FIFO model routed to an identified target serial service. This is not proof of the physical UART wiring. |
| DSP1 HI08 | `W1 +0x01`; `R1 +0x02`; `R2/W2 +0x04,+0x06` | 7,635,077 | 4,731,637 | Mixer side of the selected-core host-port bridge. |
| DSP2 HI08 | `W1 +0x01`; `R2/W2 +0x04,+0x06` | 940,182 | 791,214 | Voice side of the selected-core host-port bridge. |

The complete bounded intervals contained 8,740,721 cold and 5,650,963 cached source peripheral accesses. No other source MMIO family was accessed after firmware-ready in either idle window: there were no late SIM interrupt/configuration, UART1, parallel-port, CPU-DMA, M-Bus, or unknown `MBAR+0x1003` accesses. Combining these address-only summaries with the full WP-04 reset-to-ready traces inventories the source peripheral families exercised through both reference idle checkpoints. This remains one emulator model and one firmware profile; it is not a physical board census.

Gearmulator's MMIO trace does not capture ordinary RAM or flash-array transactions. WP-04 records a dirty-flash state after factory initialization, but that does not identify a NOR command sequence. No flash command decoder behavior is claimed by this packet.

## Clock contract

| Claim | Evidence | Interpretation |
| --- | --- | --- |
| 25.447 MHz | MAME's skeleton CPU declaration at its pinned revision | Emulator clock choice; not a physical measurement. |
| 40 MHz | Gearmulator `g_ucClockHz` / modeled host clock | Reference-model clock. The first 128-frame window reaches `116,106` modeled ColdFire cycles; 128 frames at 44.1 kHz and 40 MHz is about `116,100` cycles, within six cycles of the observed model count. |
| 40 and 50 MHz | NXP MCF5206E product documentation lists available part grades | Silicon speed options. The source board's oscillator/clock input and divider are unknown. |
| 264 MHz system / 132 MHz bus | octemu target board constants | PC-model settings only; not a physical Octatrack measurement and not evidence of source-to-target cycle parity. |

Use the 40 MHz model when reproducing WP-04 reference traces. Before assigning physical cycle budgets, measure the Machinedrum MCF5206E clock input or a timer/UART interval with a known programmed divisor, after board identity is available. The physical clock remains unresolved.

## Octatrack target model and instrumentation boundary

At the pinned octemu source revision, the PC board model defines:

| Target physical/model address | Model allocation | Relevance and overlap |
| --- | --- | --- |
| `0x00000000–0x0000ffff` | 64 KiB low RAM | Loader/board model storage; do not identify it with Machinedrum reset flash without a guest translation or reset adapter. |
| `0x10000000–0x100fffff` | 1 MiB CS1 battery-backed project-state RAM | Same numerical base as Machinedrum's 8 MiB flash. An identity map would alias two different devices and is invalid. |
| `0x20000000–0x20000fff` | 4 KiB custom DSP host-port MMIO | One selected-core path to the model's two DSP56721 cores. Core selection is a separate board register; it is not a pair of direct source HI08 windows. |
| `0x40000000+` | SDRAM; OS image loaded at `0x40000400`; default board RAM size 256 MiB | PC-side backing for the target OS and proposed source aliases. This is octemu's board allocation. |
| `0x80000000–0x80007fff` | 32 KiB model SRAM | PC-side board window; not a mapping of the source MCF5206E SRAM. |
| `0xfc000000–0xfc0fffff` | MCF54455 MBAR catch-all, with modeled native devices overlaid | PC-side register instrumentation. Native INTC, UARTs, PIT/DTIM, eDMA and other devices have target-specific offsets and side effects. Source SIM offsets must go through a compatibility layer. |

The DSP bridge exposes HDI24-style behavior: an 8-bit TXH latch plus 16-bit payload transfers, selected-core state, data/status registers, and HREQ interrupt wiring. The Machinedrum instead presents two separate 8-byte HI08 windows. A source-to-target bridge must choose the corresponding target core, preserve byte/word accesses and data packing, and reproduce ready/interrupt side effects. MMU aliases alone cannot provide those operations.

These RAM windows, catch-all MBAR and DSP bridge are PC emulator devices. A physical target design still needs the Octatrack schematic/board identity and proof of actual address decode and signal routing. The MCF54455 MMU is a silicon feature, but the aliases below remain untested in octemu and on hardware.

## Proposed source-to-target memory plan

The MCF54455 manual describes a 64-entry full-associative Harvard TLB: 32 instruction and 32 data entries. Its documented page sizes include 4 KiB, 8 KiB, 1 MiB and 16 MiB. This is sufficient to describe aliases in principle. It does not prove the firmware's MMU setup, physical-memory capacity, cache behavior, or physical Octatrack board path.

| Machinedrum guest virtual region | Proposed target SDRAM backing | Attributes / reason |
| --- | --- | --- |
| Main RAM `0x00200000–0x002fffff` and aliases `0x20000000–0x200fffff`, `0x40000000–0x400fffff` | One 1 MiB backing at `0x40000000` | All aliases point to identical bytes. Read/write/execute for bootstrap code and OS until code-copy/cache tests pass. Initial SP is `0x00300000`; the first decrement lands inside this mapping. |
| Patch RAM `0x00100000–0x001fffff` and alias `0x00700000–0x007fffff` | One 1 MiB backing at `0x40100000` | Coherent aliases, writable and executable while source code uses the region. |
| SRAM `0x01000000–0x01001fff` | Dedicated 8 KiB backing slice at `0x40200000` | Writable and executable for vector table, copied handler/code at `+0x88`, and data. Preserve VBR `0x01000000`. The checked static structures fit; dynamic bounds remain to be measured. |
| Full flash `0x10000000–0x107fffff` plus bootstrap alias `0x00000000–0x000fffff` | Reserved 8 MiB SDRAM backing beginning at `0x40300000`, or a dedicated immutable ROM/device model | Guest mappings preserve one flash image and the low-MiB alias. Keep it separate from octemu's physical CS1 `0x10000000` project-state window. Flash write/persistence semantics need later evidence. |

The physical backing addresses are illustrative for an independent guest boot with the stock Octatrack OS loader/OS absent; they are not a reservation already made in code. The default octemu loader places the Octatrack OS at `0x40000400`, inside the candidate main-RAM backing at `0x40000000`. A carrier/co-resident design must allocate source backing around the live target OS, its stack, and other board carve-outs; this report has no evidence that those physical SDRAM regions are free. Check capacity and all owners before implementation. For every executable writable mapping, source instruction and data translations must resolve to the same bytes; during the first compatibility probes, use cache-inhibited mappings or explicitly synchronize/invalidate target instruction cache after writes. Keep instruction-TLB and data-TLB permissions/backing consistent.

Map `0x00300000` source SIM and both HI08 windows to the compatibility MMIO dispatcher/bridge, not to target MCF54455-native addresses. In particular, the Machinedrum's guest RAM alias at `0x20000000` must translate to SDRAM, while its guest HI08 windows at `0x00500000` / `0x00600000` translate to the octemu model-bus DSP port at `0x20000000`. These guest virtual ranges need separate MMU mappings; identity mapping would send RAM accesses to the DSP port. Unknown source-space accesses must fault or produce reviewed diagnostics rather than falling through to the target MBAR catch-all. The unexplained `0x00301003` byte write is a specific guard case. Avoid large MMU pages that span an MMIO/device boundary or make unrelated alias backing overlap.

## Open measurements and next actions

1. Identify the Machinedrum board revision and verify physical HI08 decode and the `MBAR+0x1003` write against a schematic or a bus/hardware trace.
2. Measure the MCF5206E input clock or a known-divisor timer/UART interval on that board; do not select between 25.447 and 40 MHz from emulator settings alone.
3. Capture an executed SRAM address census over cold reset, initialization, and interrupt load to bound use within 8 KiB.
4. Add source-side full-memory/flash tracing or focused probes before specifying NOR command and persistence behavior.
5. In octemu, prototype alias coherence, executable code copy, vector fetch, stack push, unknown MMIO faulting, and selected-core host-port conversion separately. This report does not claim any of those probes passed.

## Repository validation

`make check` passed: nine reference repositories validated, Python scripts compiled, and all 20 tests passed. `git diff --check` passed. No repository code or test fixtures were added in WP-07.
