# WP-06 — ColdFire execution compatibility

**Status:** partial; WP-06 remains `in_review` while acceptance gaps remain.

## Result

The source-side Machinedrum startup executes control-register setup early, and
the target-side CFV4e QEMU model has specific gaps around those operations.
Independent probes show that the current `m5206` and `cfv4e` models agree on a
small set of arithmetic, stack, trap, exception-return, and privilege cases.
They also expose two QEMU-only differences from NXP's manuals: VBR alignment is
not enforced, and the MCF54455 EUSP bit is defined at a different position.

This is a CPU-model audit, not a hardware-realizability decision. It does not
establish that all executed Machinedrum code runs on the Octatrack, that the
target's startup register values can be discarded, or that a complete port
boots.

## Source profile and method

| Input | Revision/profile |
| --- | --- |
| Machinedrum source | Gearmulator MD/MM `8cea0524a75435122c20b669ca114c9ac6509ba2`; recursive `mc68k` `ace95b3d0a5a332db147244762dda65f9a010b9f`, DSP56300 `1378c43074e6ec22f69f14ed55c21e44c5ccadc1` |
| Machinedrum firmware | Local Machinedrum SPS-1UW OS 1.63 image, matching WP-02's public size/CRC-32/SHA-1/FNV-64 fingerprints; image bytes and local SHA-256 remain private |
| Reference startup | `mdPanelReadinessFirmwareTest` from WP-04, which passes its blank-flash and cached-firmware readiness checks |
| Startup counter patch | [`0003-opt-in-coldfire-execution-summary.patch`](../../patches/gearmulator-md-mm/0003-opt-in-coldfire-execution-summary.patch); SHA-256 `e336bfb11875a95886ba798004e2bb3597659804631ea829b0c7d638d9aaf7f6` |
| Target CPU source | octemu `87000189418c8ca2026dc047bda220b66802809d`; QEMU base `e8d693e12af9cbb89d724baadfcc08559669e279` plus its 13 octemu patches |
| Target test machine | QEMU `an5206` test board with `m5206` and `cfv4e` CPU models; the Octatrack board is not used by these probes |

The source startup counter patch is opt-in. With a local OS 1.63 image, the
WP-04 panel-readiness driver exits successfully after its cold and cached
checkpoints. The counter stops after the first 100,000 executed source CPU
instructions. It reports only instruction categories, control-register names,
and counts; it records no PCs, opcodes, register/MMIO values, firmware bytes,
or per-instruction trace. The reproduction command is in
[`tests/probes/wp06/README.md`](../../tests/probes/wp06/README.md#reproduce-the-machinedrum-startup-summary).

The first 100,000 instructions contain ten `MOVEC` writes: VBR ×2, CACR ×2,
ACR0 ×2, ACR1 ×2, RAMBAR ×1, and MBAR ×1. Two instructions write the status
register. No `RTE`, `TRAP`, `RESET`, `STOP`, or USP/stack-mode instructions
appear in this interval. This is a bounded prefix of startup, not a complete
firmware instruction census. WP-35's separate static scan of 44 engine
handlers found no MAC/EMAC, direct hardware access, or calls; it does not
establish their executed instruction coverage.

## Expanded executed source profile

To extend coverage without retaining instruction traces, the startup counter
patch was applied in a separate Gearmulator clone at the revisions above,
after WP-04 patches `0001`/`0002`. WP-35's host-trace and DSP execution-hook
patches were applied only for `md_profile`; the resulting `md_profile` and
`mdPanelReadinessFirmwareTest` binaries were built locally. The startup driver
was run with a 1,000,000-instruction summary limit. Single-engine
assignment/eight-hit profiles ran for all 50 core synthesis engine IDs across
GND, TRX, EFM, E12, and P-I. Three additional assignment profiles covered
INP-GA (`0x50`), MID 01 (`0x60`), and CTR-AL (`0x70`). Trigger/encoder trace
profiles ran for GND-SN (`0x01`), TRX-BD (`0x10`), TRX-SD (`0x11`), EFM-BD
(`0x20`), E12-BD (`0x30`), P-I-BD (`0x40`), INP-GA (`0x50`), MID 01 (`0x60`),
and CTR-AL (`0x70`), adding three families beyond the five core synthesis
families. Each scenario used a
1,000,000,000-instruction counter ceiling and the local Machinedrum OS 1.63
image. Output directories, firmware, detailed DSP/host traces, and
address-bearing handler rows remain under `/private/tmp`.

The scenarios are reproducible with the local image and binaries as follows;
all destinations must be created first. The capture directories are private
because `trace=0x10` writes firmware-derived host, link, memory, and handler
address data.

```sh
env -u GEARMULATOR_MD_BUS_TRACE \
  -u GEARMULATOR_MD_BUS_TRACE_ENABLED \
  GEARMULATOR_MD_EXEC_SUMMARY=/private/tmp/wp06-execution-summary-1m.txt \
  GEARMULATOR_MD_EXEC_SUMMARY_LIMIT=1000000 \
  GEARMULATOR_MD_FIRMWARE_BIN=/path/to/local-md-os-1.63.bin \
  /path/to/mdPanelReadinessFirmwareTest >/dev/null 2>&1

mkdir -p /private/tmp/wp06-md-profile-engine10 /private/tmp/wp06-md-profile-trace10
GEARMULATOR_MD_EXEC_SUMMARY=/private/tmp/wp06-exec-summary-engine10.txt \
  GEARMULATOR_MD_EXEC_SUMMARY_LIMIT=1000000000 \
  /path/to/md_profile /path/to/local-md-os-1.63.bin \
  /private/tmp/wp06-md-profile-engine10 0x10
GEARMULATOR_MD_EXEC_SUMMARY=/private/tmp/wp06-exec-summary-trace10.txt \
GEARMULATOR_MD_EXEC_SUMMARY_LIMIT=1000000000 \
  /path/to/md_profile /path/to/local-md-os-1.63.bin \
  /private/tmp/wp06-md-profile-trace10 trace=0x10
```

The bare-ID assignment invocation was run for all core synthesis IDs
`0x01–0x03`, `0x10–0x1d`, `0x20–0x27`, `0x30–0x3f`, and `0x40–0x48`; `0x00` is
the empty machine. The additional INP/MID/CTR assignment runs used `0x50`,
`0x60`, and `0x70`. Trace profiles were run for the nine IDs listed above.
The per-engine instruction totals do not attribute execution to each of the
44 distinct ColdFire descriptor handlers.

The startup readiness driver exited 0 after its cold and cached checks. Its
summary reached the 1,000,000 instruction cap and reported 10 `MOVEC` writes
(VBR ×2, CACR ×2, ACR0 ×2, ACR1 ×2, RAMBAR ×1, MBAR ×1), two status-register
writes, and no counted `RTE`, `TRAP`, `RESET`, `STOP`, or USP/stack-mode
instructions in that prefix.

| Core engine ID | Engine | Executed instructions | `RTE` | `TRAP` |
| --- | --- | ---: | ---: | ---: |
| `0x01` | GND-SN | 562,282,775 | 139,329 | 12 |
| `0x02` | GND-NS | 562,293,738 | 139,470 | 12 |
| `0x03` | GND-IM | 562,154,785 | 139,422 | 12 |
| `0x10` | TRX-BD | 562,290,551 | 139,161 | 12 |
| `0x11` | TRX-SD | 562,231,801 | 139,231 | 12 |
| `0x12` | TRX-XT | 562,177,565 | 139,244 | 12 |
| `0x13` | TRX-CP | 562,142,768 | 139,275 | 12 |
| `0x14` | TRX-RS | 562,178,453 | 139,324 | 12 |
| `0x15` | TRX-CB | 562,087,831 | 139,238 | 12 |
| `0x16` | TRX-CH | 562,230,949 | 139,309 | 12 |
| `0x17` | TRX-OH | 562,299,674 | 139,306 | 12 |
| `0x18` | TRX-CY | 562,298,425 | 139,286 | 12 |
| `0x19` | TRX-MA | 562,237,184 | 139,272 | 12 |
| `0x1a` | TRX-CL | 562,183,289 | 139,211 | 12 |
| `0x1b` | TRX-XC | 562,215,141 | 139,236 | 12 |
| `0x1c` | TRX-B2 | 562,228,240 | 139,028 | 12 |
| `0x1d` | TRX-S2 | 562,182,759 | 139,497 | 12 |
| `0x20` | EFM-BD | 562,249,453 | 139,272 | 12 |
| `0x21` | EFM-SD | 562,217,247 | 139,261 | 12 |
| `0x22` | EFM-XT | 562,182,333 | 139,193 | 12 |
| `0x23` | EFM-CP | 562,175,300 | 139,274 | 12 |
| `0x24` | EFM-RS | 562,179,286 | 139,261 | 12 |
| `0x25` | EFM-CB | 562,204,349 | 139,282 | 12 |
| `0x26` | EFM-HH | 562,259,015 | 139,285 | 12 |
| `0x27` | EFM-CY | 562,259,594 | 139,269 | 12 |
| `0x30` | E12-BD | 562,158,592 | 139,236 | 12 |
| `0x31` | E12-SD | 562,241,406 | 139,230 | 12 |
| `0x32` | E12-HT | 562,220,016 | 139,247 | 12 |
| `0x33` | E12-LT | 562,203,280 | 139,256 | 12 |
| `0x34` | E12-CP | 562,171,169 | 139,247 | 12 |
| `0x35` | E12-RS | 562,248,495 | 139,219 | 12 |
| `0x36` | E12-CB | 562,241,526 | 139,246 | 12 |
| `0x37` | E12-CH | 562,134,310 | 139,235 | 12 |
| `0x38` | E12-OH | 562,160,865 | 139,209 | 12 |
| `0x39` | E12-RC | 562,158,173 | 139,226 | 12 |
| `0x3a` | E12-CC | 562,321,559 | 139,253 | 12 |
| `0x3b` | E12-BR | 562,295,320 | 139,237 | 12 |
| `0x3c` | E12-TA | 562,263,765 | 139,252 | 12 |
| `0x3d` | E12-TR | 562,233,899 | 139,245 | 12 |
| `0x3e` | E12-SH | 562,283,269 | 139,233 | 12 |
| `0x3f` | E12-BC | 562,216,042 | 139,214 | 12 |
| `0x40` | P-I-BD | 562,301,574 | 139,271 | 12 |
| `0x41` | P-I-SD | 562,215,407 | 139,235 | 12 |
| `0x42` | P-I-MT | 562,147,964 | 139,228 | 12 |
| `0x43` | P-I-ML | 562,229,061 | 139,318 | 12 |
| `0x44` | P-I-MA | 562,307,581 | 139,353 | 12 |
| `0x45` | P-I-RS | 562,278,002 | 139,284 | 12 |
| `0x46` | P-I-RC | 562,223,834 | 139,238 | 12 |
| `0x47` | P-I-CC | 562,234,393 | 139,239 | 12 |
| `0x48` | P-I-HH | 562,211,064 | 139,242 | 12 |

Three additional assignment profiles completed below the ceiling: INP-GA
(`0x50`) at 562,183,361 instructions (`RTE` 139,402; `TRAP` 12), MID 01
(`0x60`) at 562,194,086 (`RTE` 139,508; `TRAP` 12), and CTR-AL (`0x70`) at
562,162,921 (`RTE` 139,445; `TRAP` 12).

| Trigger/encoder trace engine | Executed instructions | `RTE` | `TRAP` | Handler-range entries | Buckets |
| --- | ---: | ---: | ---: | ---: | ---: |
| `0x01` GND-SN | 559,631,603 | 137,933 | 6 | 3,472 | 2 |
| `0x10` TRX-BD | 559,651,805 | 137,761 | 6 | 3,440 | 2 |
| `0x11` TRX-SD | 559,752,802 | 137,876 | 6 | 3,584 | 2 |
| `0x20` EFM-BD | 559,750,509 | 137,921 | 6 | 3,552 | 2 |
| `0x30` E12-BD | 559,692,448 | 137,847 | 6 | 3,488 | 2 |
| `0x40` P-I-BD | 559,777,600 | 137,918 | 6 | 3,600 | 2 |
| `0x50` INP-GA | 559,644,338 | 138,014 | 6 | 3,355 | 1 |
| `0x60` MID 01 | 560,135,090 | 138,194 | 16 | 3,680 | 2 |
| `0x70` CTR-AL | 559,619,278 | 138,051 | 6 | 3,408 | 2 |

All nine trace scenarios recorded 24 `MOVEC`-to operations (VBR/CACR ×6
each, ACR0/1 ×4 each, RAMBAR/MBAR ×2 each), around 1.014 million move-to-SR
operations, around 77 thousand move-from-SR operations, and no RESET, STOP, or
other counted control-register writes. The trace counter records transitions
into the source descriptor-handler PC range and groups them by handler and
return address. Only aggregate counts are reported; no address rows are
published. The 50 assignment runs cover the core synthesis IDs; the nine
traces add representative activity across all eight source engine families.
These source-model runs do not attribute handler buckets to each descriptor,
compare the firmware instruction stream with the target CPU, cover
cache/atomic behavior, or establish physical compatibility.

## Independent CPU-model probe

Run the firmware-free probe from the repository root:

```sh
python3 tests/probes/wp06/run.py \
  --cc /opt/homebrew/bin/m68k-elf-gcc \
  --qemu /private/tmp/octamachine-md-import/vendor/octemu/vendor/qemu/build/qemu-system-m68k
```

The ELF uses QEMU's `an5206` test board, 4 MiB of synthetic RAM, and a fixed
result block. Its `-kernel` loader sets PC directly to the ELF entry, so this
command does not test reset-vector fetch. It builds and runs `cpu_compat.S` on
both `m5206` and `cfv4e`, plus a level-4 timer-interrupt test and target-only
EUSP and startup-MOVEC probes.

Observed output on both main CPU models:

| Probe behavior | `m5206` and `cfv4e` result |
| --- | --- |
| Signed long / unsigned word multiply, then stack push/pop | Success marker `0xc0def00d`; arithmetic check passes |
| `TRAP #0` frame | Handler SP `0x7ef8` from initial `0x7f00`; frame is eight bytes; `RTE` restores SP to `0x7f00` |
| User-mode privileged `MOVEC` to VBR | Privilege exception; handler sees SP `0x7ef8`; `RTE` returns to user code |
| Deliberately unaligned VBR | Both QEMU models select the synthetic handler at the raw, unaligned base |

The full field values for the two synthetic frames and saved PCs are read from
the probe's result block and compared by the runner. The probe includes no
firmware-derived data. The agreement covers only these instructions and
exception cases.

The interrupt probe raises a level-4 timer request while SR.I is 5, confirms
the timer request is pending without entering its handler, then lowers SR.I to
3 and confirms exactly one handler entry. Both CPU models match. The QEMU
AN5206 board does not expose the MCF5206E external edge-sensitive level-7
input, so the manual's unmaskable-level-7 special case remains untested.

The new firmware-free `alignment_endian.S` probe writes `0x12345678` at an
even address, then reads a byte, aligned/odd words, aligned/odd longs, and
round-trips `0xa1b2c3d4` through an odd-address long store. Both `m5206` and
`cfv4e` return the expected big-endian values: byte `0x12`, words `0x1234` and
`0x3456`, longs `0x12345678` and `0x34567800`, and odd-store readback
`0xa1b2c3d4`. The probe catches bus/address errors and returns a distinct
failure marker. This establishes only the pinned QEMU models' behavior for
these synthetic RAM accesses; it does not establish physical bus timing or
all device-memory alignment rules.

## CAS and code-coherence runtime probes

The firmware-free cas_model.S probe assembles a real CAS.L instruction using
68020 syntax. On the AN5206 QEMU machine, the m68020 control model changes
the synthetic word from 0x12345678 to 0x87654321 and returns success. The
m5206 and cfv4e models instead take the installed illegal-instruction vector
(marker 0xbad00004) and the trap handler reads back the unchanged 0x12345678 target word. The control model validates the
opcode and test path; the result measures the pinned QEMU model feature sets,
not physical MCF54455 support or Machinedrum firmware use.

The self_modifying_code.S probe first executes MOVEQ #1 at a RAM address,
writes the MOVEQ #2 opcode over it, and calls the address again. Both m5206
and cfv4e return 1 before the write and 2 afterward. This demonstrates that
the pinned QEMU TCG path executes the replacement instruction after an
overlapping guest store. It does not model physical instruction-cache
behavior or establish whether the firmware modifies code at runtime.

### Cache-control instruction and CACR model paths

The firmware-free cache_control.S probe executes CPUSHL.L in supervisor
mode, writes 0x00000001 to CACR, and attempts to read CACR back. Both m5206
and cfv4e return from CPUSHL and the CACR write, then take the illegal-
instruction vector on the CACR read. The handler records that the synthetic
memory sentinel remains 0x13579bdf. The probe uses the raw MOVEC CACR-to-D1 encoding (0x4e7a, 0x1002), confirmed against GNU as for 68020;
GNU as rejects this read form for the ColdFire assembler
target.

This matches the pinned source paths: CPUSHL translator bodies are no-ops,
cf_movec_to stores CACR, and m68k_movec_from only returns CACR for 68020,
68030, 68040, or 68060 feature profiles. The runtime result describes pinned
QEMU model behavior. It does not measure physical cache effects, prove
physical CACR readability, or establish firmware use.

## Pinned QEMU source inspection and runtime follow-up

The exact QEMU base e8d693e12af9cbb89d724baadfcc08559669e279 was fetched into
a temporary audit checkout and all 13 octemu QEMU patches applied there. The
initial source inspection was static; the runtime follow-up below built and
ran that patched source on the AN5206 QEMU board model.

- In target/m68k/cpu.c, the m5206 and cfv4e initializers enable their ColdFire
  ISA feature sets but do not enable M68K_FEATURE_CAS; the feature is set in
  the separate 68020 initialization path. The CAS.L runtime probe corroborates
  this exact QEMU model gap: a 68020 control executes it, while both ColdFire
  configurations take vector 4. This does not establish physical silicon
  support or firmware use.
- In target/m68k/helper.c::cf_movec_to, CACR writes update the saved CACR
  value and call the stack-switch helper, while ACR0–ACR3 writes are marked
  TODO. In target/m68k/translate.c, the cache push/invalidate and instruction
  touch handlers have privilege checks but no cache operation body. This
  source review does not establish whether the Machinedrum firmware executes
  any of those paths.
- QEMU TCG maintains a conservative translated-code extent for each page and
  invalidates overlapping translation blocks after guest stores. octemu patch
  0008-tcg-skip-notdirty-walk-for-codeless-pages.patch skips the walk only
  when a page has no translated code or the store is provably outside that
  extent; overlapping stores still reach invalidation. This is emulator code
  coherence, not a model of MCF54455 instruction-cache behavior or proof that
  the source firmware modifies code at runtime.

Build and runtime verification: make -C vendor/octemu setup completed and
built the pinned DSP56300 archives. QEMU compiled through step 1,472 of 1,473 with
QEMU_EXTRA_CONFIGURE=--disable-werror, then the stock final link failed on this Ubuntu 26.04/GCC setup: octemu patch 0011 adds -lc++ and
the extracted GLib/Pixman development links exposed missing runtime/private
libraries. I completed the ignored generated QEMU build tree with a local
build.ninja link adjustment: omitted -lc++ because the GCC C++ driver links
libstdc++, added the pinned DSP build's libvtuneSdk.a and -ldl, added GLib's
static private libraries (sysprof-capture, pcre2, and atomic), and resolved
Pixman to the installed runtime library. Direct Ninja linking then succeeded.
No tracked octemu source or submodule pointer changed. The resulting binary
lists both an5206 and octatrack machines; ldd reports no unresolved runtime
libraries.

The expanded firmware-free runner passed on this binary. Its CAS control and
ColdFire results and the self-modifying-code results are recorded above. The
exact local command was: python3 tests/probes/wp06/run.py --cc
/home/jannikassfalg/.local/bin/m68k-elf-gcc --qemu
/home/jannikassfalg/octamachine/vendor/octemu/vendor/qemu/build/qemu-system-m68k.
The Linux generated-link adjustment is local to this build tree and is needed
to reproduce this build with the current host toolchain.

## Findings and classification

| Behavior | Evidence and result | Classification |
| --- | --- | --- |
| Multiply, basic stack operations, `TRAP`, `RTE`, and privilege exception | Synthetic firmware-free probe returns identical results on the `m5206` and `cfv4e` QEMU models. The NXP ColdFire programmer's manual describes the fixed two-longword frame and `RTE` restoration. | **Direct in the tested emulator cases.** Broader firmware/runtime coverage remains open. |
| VBR alignment | Both the MCF5206E and MCF54455 manuals say the low 20 VBR bits are not implemented and vector tables are 1 MiB-aligned. Both current QEMU models instead use the raw VBR value and select the unaligned synthetic vector table. QEMU's `cf_movec_to` assigns the value directly. | **Identified emulator mismatch on both profiles.** Keep the source and target vector tables 1 MiB-aligned; the firmware's actual VBR value and physical behavior still need measurement. |
| Optional target USP stack | MCF54455 CACR[EUSP] is documented at bit 5 (`0x20`). QEMU defines `M68K_CACR_EUSP` as `0x10`. `stack_eusp.S` leaves the user SP unchanged with `0x20`, while the model switches to the user SP with `0x10`. | **Identified emulator mismatch.** The source MCF5206E model has one A7 stack pointer; no source dependency on the target-only dual-stack feature was observed in the startup prefix. |
| ACR0/ACR1 | Actual startup writes both registers twice. The pinned QEMU `cf_movec_to` has a `TODO` and ignores ACR0–ACR3 writes. The synthetic MOVEC sequence reaches its next instruction without refusal. | **Target model gap.** Whether these startup writes change cache/address behavior on hardware is unresolved; WP-07 must map their values and effects before choosing a shim. |
| RAMBAR and MBAR | Actual MCF5206E startup writes RAMBAR at MOVEC Rc `0xC04` and MBAR at `0xC0F`, once each. The MCF54455 manual documents its single SRAM RAMBAR at Rc `0xC05`; its core register table does not list the source MBAR encoding. Separate synthetic target ELFs execute the preceding ACR writes and make QEMU abort on source Rc `0xC04` and `0xC0F`. | **Register-map mismatch plus model gap.** The target has a RAMBAR facility, but not at the source encoding. Whether the source writes can be removed or translated depends on their operands and effects, which have not been recorded publicly; WP-07 must map these writes before selecting an adaptation. |
| Reset and vector fetch | WP-04 records the Gearmulator reset checkpoint. The MCF54455 manual specifies SSP from address `0x00000000` and PC from `0x00000004` on reset. In the pinned QEMU CPU reset path, PC is set to zero with a TODO to fetch it; `an5206 -kernel` bypasses this path and starts at the ELF entry. A `system_reset` attempt did not reach the expected vector entry. | **Unresolved in QEMU.** No reset-vector equivalence claim. |
| Interrupt masking and priority | Synthetic level-4 timer probe: with SR.I=5, the timer request is pending and no handler runs; lowering SR.I to 3 delivers exactly one handler. Both QEMU CPU models match. Both processor manuals document the non-maskable, edge-sensitive level-7 exception. In the pinned QEMU source, interrupt acceptance uses only `SR.I < pending_level`; `m68k_set_irq_level` stores a level and clears it when lowered, without an edge latch. The Octatrack board wires modeled device sources through two INTCs and exposes no separate external level-7 input. | **Measured for level 4; level 7 is a QEMU model gap and has no board stimulus.** Hardware interrupt behavior remains unresolved. |
| Data alignment and byte order | New synthetic probe performs aligned and odd-address byte/word/long RAM reads and an odd-address long write. `m5206` and `cfv4e` both produce the same expected big-endian values. | **Direct in these QEMU RAM cases.** Physical behavior and device-memory accesses remain unmeasured. |
| CAS, CPUSHL, CACR access, and self-modifying code | A 68020 control executes CAS.L; m5206/cfv4e take vector 4 and preserve the CAS target. Both ColdFire models execute supervisor CPUSHL.L, accept a CACR write, and take vector 4 on CACR read. Both also execute replacement RAM code after an overlapping guest store. | **Pinned-QEMU decode and register paths measured; cache effects, firmware use, and physical behavior remain open.** |

### Exception and privilege details

The [ColdFire Family Programmer's Reference Manual](https://www.nxp.com/docs/en/reference-manual/CFPRM.pdf)
describes the two-longword exception frame and `RTE` return in §11.1.2.
The synthetic probe confirms an eight-byte frame and SP restoration in both
QEMU CPU models. A user-mode `MOVEC` causes a privilege exception in both
models. Therefore any runtime register shim must execute in supervisor mode;
this probe does not locate a legal patch site or prove that a firmware handler
can provide the shim.

The MCF5206E manual documents its single A7 programming model, VBR's 1 MiB
alignment, RAMBAR at MOVEC Rc `0xC04`, and MBAR at `0xC0F`. The MCF54455
manual documents the same 1 MiB VBR alignment and CACR[EUSP] at bit 5 in
§6.3.1; the QEMU probe exposes a mismatch between that manual and its internal
bit definition, not a silicon measurement. The target manual documents ACR0–3
at Rc `0x004`–`0x007` and its single RAMBAR at `0xC05`. These facilities are
supervisor-only. A user-mode `MOVEC` privilege exception was reproduced in
both QEMU CPU models. The target core register table does not list source
MBAR Rc `0xC0F`.

Both device manuals specify the level-7 request as edge-sensitive and
unmaskable. The pinned QEMU CPU accepts an interrupt only when SR.I is below
the pending level. Its interrupt input API stores a level and clears the
pending request when the input is lowered; it has no edge-pending state. The
`an5206` board has no external level-7 pin, and the Octatrack board connects
its modeled device sources to two MCF interrupt controllers. The current test
boards therefore cannot reproduce the manual's external edge-latched case.

## Port impact and next evidence

- **Tested CPU instructions:** firmware-free probes show matching results on
  the tested m5206 and cfv4e QEMU cases for multiply, stack operations,
  fixed-frame TRAP/RTE, privilege handling, and the sampled level-4 interrupt.
  A CAS.L control runs on m68020 while both ColdFire models take vector 4; a
  RAM code write is observed by both models on the next call. These are QEMU
  model results. Gearmulator profiles do not compare source instructions with
  the target CPU or prove broad equivalence.
- **Bounded adaptation candidate:** keep any Machinedrum vector table on a
  1 MiB boundary. Both processor manuals require that layout; the actual
  firmware VBR operands and physical exception behavior remain unmeasured.
- **Register adaptation candidate:** the target supports CACR and ACR0–3 at
  the same MOVEC encodings as the source, though the current QEMU model does
  not implement their effects. The source RAMBAR write uses Rc `0xC04`; the
  target RAMBAR is at `0xC05`. The source MBAR write uses Rc `0xC0F`, which is
  absent from the target core register table. No write is proposed as a no-op:
  the startup operands and hardware effects remain to be mapped in WP-07.
- **Emulator blocker:** current octemu QEMU source does not faithfully model
  VBR alignment, ACR writes, either target RAMBAR encoding, source MBAR writes,
  the documented EUSP bit, or edge-sensitive non-maskable level 7. That limits
  emulator validation; it is not evidence that the physical MCF54455 cannot
  execute supported instructions or use its documented control registers.
- **Mechanism constraints checked:** a host-side image rewrite is a candidate
  only after the source register operands and effects are mapped and a real
  target loading path is established. A runtime trap/register shim must use a
  valid 1 MiB-aligned vector table and execute privileged control-register
  handling in supervisor mode. No safe patch site or complete mechanism is
  selected in WP-06; architecture selection remains in WP-10.
- **Unresolved:** reset-vector fetch, external edge-sensitive level-7 behavior,
  broad executed runtime/engine instruction coverage, cache-control effects,
  whether firmware uses CAS or modifies code, device-memory alignment, and
  physical target behavior.

No physical Machinedrum or Octatrack was tested. No trap patch, instruction
relocation, or runtime control-register shim was implemented. The candidate
mechanisms are bounded by the documented target facilities and privilege
rules above; selecting and implementing one remains open for WP-10.

## References

- [MCF5206E User's Manual](https://www.nxp.com/docs/en/data-sheet/MCF5206EUM.pdf): §3.2.4 status register and edge-sensitive level 7; §3.2.4.2 VBR; §3.3 exception processing; §5.3.2 RAMBAR at Rc `0xC04`; §7.2.1 MBAR at Rc `0xC0F`; §4.4 CACR and ACR0/1.
- [ColdFire Family Programmer's Reference Manual, Rev. 3](https://www.nxp.com/docs/en/reference-manual/CFPRM.pdf): §1.5 processor programming model and VBR; §3.2 interrupt mask; §11.1.2 exception frame.
- [MCF54455 Reference Manual](https://www.nxp.com/docs/en/reference-manual/MCF54455RM.pdf): §3.2.3 stack pointers, §3.2.5 PC, §3.2.8 VBR, §3.2.9 status/interrupt mask, §3.2.10 RAMBAR at Rc `0xC05`, §3.3.4.15 reset exception, §6.3.1 CACR[EUSP], and §6.3.2 ACR0–3.
- Pinned octemu source `87000189418c8ca2026dc047bda220b66802809d` / QEMU base `e8d693e12af9cbb89d724baadfcc08559669e279`: `target/m68k/helper.c::cf_movec_to`, `target/m68k/op_helper.c::m68k_cpu_exec_interrupt`, `target/m68k/helper.c::m68k_set_irq_level`, `hw/m68k/an5206.c::an5206_init`, `hw/m68k/mcf5206.c::m5206_mbar_update`, `hw/m68k/mcf_intc.c::mcf_intc_update`, and `hw/m68k/ot-board.c::octatrack_init`.
- QEMU source at the pinned base: [`helper.c`](https://gitlab.com/qemu-project/qemu/-/blob/e8d693e12af9cbb89d724baadfcc08559669e279/target/m68k/helper.c) (`cf_movec_to`, `m68k_switch_sp`), [`cpu.h`](https://gitlab.com/qemu-project/qemu/-/blob/e8d693e12af9cbb89d724baadfcc08559669e279/target/m68k/cpu.h) (`M68K_CACR_EUSP`), [`cpu.c`](https://gitlab.com/qemu-project/qemu/-/blob/e8d693e12af9cbb89d724baadfcc08559669e279/target/m68k/cpu.c) reset, and [`an5206.c`](https://gitlab.com/qemu-project/qemu/-/blob/e8d693e12af9cbb89d724baadfcc08559669e279/hw/m68k/an5206.c) test-machine setup. octemu carries 13 local QEMU patches on that base.
- [WP-04](WP-04-md-baseline.md) supplies the reference boot driver and reset checkpoint; [WP-35](WP-35-octamad-md-import.md) supplies the static engine-handler census.

## Verification and remaining work

Verification: the current expanded run.py suite passed with the local pinned QEMU binary, including the existing arithmetic/exception, alignment, interrupt, EUSP, and MOVEC probes plus CAS, self-modifying-code, and CPUSHL/CACR model-path cases. The source summary patch passed a clean-apply dry run against the WP-04 Gearmulator source tree; its instrumented driver rebuilt and exited 0 with the cold/cached readiness checks. On an isolated clone at Gearmulator 8cea0524a75435122c20b669ca114c9ac6509ba2 with recursive mc68k ace95b3d0a5a332db147244762dda65f9a010b9f, the JIT md_profile target built and all listed engine scenarios completed below the 1,000,000,000-instruction summary ceiling. Their aggregate totals are recorded above; raw trace products remain private. This prompt's make check passed: nine reference repositories validated, Python scripts compiled, all 20 tests passed, and git diff --check passed.

WP-06 remains in_review. The one-million startup prefix, assignment/eight-hit profiles for all 50 core synthesis IDs plus three additional engine families, and nine trigger/encoder traces extend only Gearmulator-side coverage. Pinned QEMU source inspection and synthetic probes cover CAS, overlapping RAM code writes, supervisor CPUSHL decode, and CACR write/read paths; cache-control effects remain incomplete. External level-7 stimulus is absent from the pinned test-board interfaces; reset-vector fetch is bypassed by the ELF loader and absent from the pinned CPU reset implementation. Register adaptation still depends on mapping source operands/effects against the WP-07 reviewed memory map. No physical CPU or register behavior is established.
