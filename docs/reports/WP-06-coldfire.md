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
| Machinedrum source | Gearmulator MD/MM `8cea0524a75435122c20b669ca114c9ac6509ba2`; recursive `mc68k` `ace95b3d0a5a332db147244762dda65f9a010b9f` |
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
| Alignment, endianness, atomic operations, cache effects, and self-modifying code | Not exercised by the startup prefix or the current probe, beyond VBR alignment. | **Unresolved.** |

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

- **Direct execution:** the source CPU's basic arithmetic, stack operations,
  and fixed-frame exception pattern match the tested target CPU model cases.
  This does not prove every firmware instruction or handler.
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
  representative executed runtime/engine instruction coverage, data
  alignment/endian/atomic behavior, cache/self-modifying-code behavior, and
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

`python3 tests/probes/wp06/run.py --cc /opt/homebrew/bin/m68k-elf-gcc --qemu /private/tmp/octamachine-md-import/vendor/octemu/vendor/qemu/build/qemu-system-m68k` passed, including the level-4 SR.I test. The source summary patch passed a clean-apply dry run against the WP-04 Gearmulator source tree; its instrumented driver rebuilt and exited 0 with the cold/cached readiness checks. `make check` passed: nine reference validations, Python script compilation, and 20 tests.

WP-06 remains `in_review`. External level-7 stimulus is absent from the pinned test-board interfaces; reset-vector fetch is bypassed by the ELF loader and absent from the pinned CPU reset implementation. Register adaptations and runtime handler coverage remain open, with the target manual showing where the source and target control-register maps differ. The next packet can use WP-04/WP-05 evidence to reconcile memory and MMIO while these precisely bounded CPU-model gaps remain open.
