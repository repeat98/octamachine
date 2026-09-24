# WP-06 ColdFire probes

These independently authored probes contain no firmware or captured machine
state. Build and run the CPU-model comparisons with:

```sh
python3 tests/probes/wp06/run.py \
  --cc /path/to/m68k-elf-gcc \
  --qemu /path/to/qemu-system-m68k
```

The QEMU binary must include the `an5206` test machine. `-kernel` loads each
ELF at its link entry; the machine provides RAM at address zero for vectors and
the runner reads the synthetic result block through the HMP monitor. This
does not exercise device reset-vector fetch, board peripherals, or physical
silicon.

## Arithmetic, traps, privilege, and VBR

`cpu_compat.S` checks signed long and unsigned word multiply, stack push/pop,
`TRAP #0`/`RTE`, the two-longword exception frame, and a user-mode privileged
`MOVEC` to VBR. It also sets a deliberately unaligned VBR and records which
synthetic vector-table handler QEMU selects. Both the source-side `m5206` and
target-side `cfv4e` models return the same result block for the supported
operations. The MCF5206E manual says the lower 20 VBR bits are forced to zero;
the current QEMU models instead use the raw value. This is a QEMU finding, not
a physical Octatrack measurement.

The saved exception frames and stack pointers are written only to the
firmware-free result block. A normal trap uses an eight-byte frame and `RTE`
restores the pre-trap stack pointer. A user-mode VBR write takes a privilege
exception.

`alignment_endian.S` checks aligned and odd-address byte, word, and long RAM
accesses, including an odd-address long store. Both CPU models return the
expected big-endian values for the synthetic data. This is a QEMU RAM result;
it does not establish physical or MMIO alignment behavior.

`interrupt_mask.S` uses the AN5206 model's timer source at level 4. With SR.I
set to 5, it confirms that the timer is pending while the handler count remains
zero; lowering SR.I to 3 delivers exactly one interrupt. The `m5206` and
`cfv4e` models match on this level-sensitive case. The generic AN5206 board
does not expose the MCF5206E external edge-sensitive level-7 input, so that
special case remains untested.

## CAS and code-coherence probes

The cas_model.S probe assembles a real CAS.L instruction using the 68020
encoding. The m68020 control model swaps the synthetic memory value from
0x12345678 to 0x87654321; m5206 and cfv4e take the installed illegal
instruction vector before changing memory. This confirms the pinned QEMU
models' CAS feature gap. It does not show that the physical MCF54455 lacks CAS
or that the Machinedrum firmware executes it.

The self_modifying_code.S probe executes MOVEQ #1, writes the MOVEQ #2 opcode
over that RAM instruction, then calls the address again. Both ColdFire models
return 1 before the write and 2 after it. This exercises TCG translated-code
invalidation for an overlapping guest store; it does not model the physical
instruction cache or cache-control register effects.

The cache_control.S probe runs CPUSHL.L in supervisor mode, writes CACR,
then attempts a CACR read. Both ColdFire models return from CPUSHL and the
write, then take vector 4 on the read. The handler records the unchanged
synthetic memory sentinel. Pinned QEMU source marks CPUSHL as a no-op and
stores CACR writes; this probe does not measure physical cache effects or
establish firmware use.

The user_privilege_cache.S probe selects user-mode CPUSHL, CACR write, or
CACR read cases. On both models, CPUSHL and MOVEC D0-to-CACR take vector 8;
MOVEC CACR-to-D1 takes vector 4 because the ColdFire profiles do not enable
that read path. Each handler records one exception, the stacked PC, exception
frame value, frame SP, and an unchanged 0x13579bdf sentinel. In all six runs,
the stacked PC matches the selected instruction and the frame SP is 0x7ef8
from the pre-exception 0x7f00. This is pinned-QEMU exception behavior only.
It does not establish physical privilege or cache behavior.

## Target-only user stack and startup MOVEC probes

`stack_eusp.S` initializes distinct supervisor and user stacks, enters user
mode, takes a trap, and returns through `RTE`. The runner tries both the
MCF54455 manual's CACR[EUSP] bit (`0x20`) and QEMU's source-defined bit
(`0x10`). The manual assigns EUSP to bit 5; QEMU switches stacks on bit 4. With
the manual bit, the current model keeps one active stack; with the QEMU bit,
it switches to the separate user stack. The source MCF5206E is an ISA_A core
with one A7 stack pointer, so this is a target-model extension and does not
show that Machinedrum firmware needs dual stacks.

`unimplemented_movec.S` writes ACR0 and ACR1, then separately attempts
RAMBAR0 and MBAR. The current QEMU `cfv4e` helper has a no-op `TODO` for ACR
writes and aborts on the latter registers. This reproduces the model gap with
small synthetic ELFs; it does not establish whether the exact startup values
are required by the physical target. That depends on the target memory/cache
map and belongs in WP-07.

## Reproduce the Machinedrum startup summary

For the actual source-side startup trace, prepare the pinned Gearmulator source
as described in [Getting Started](../../../docs/GETTING_STARTED.md#machinedrum-reference-emulator)
and [WP-04](../../../docs/reports/WP-04-md-baseline.md). The preparation step
applies `0003-opt-in-coldfire-execution-summary.patch` after the existing
trace/checkpoint patches. Build `mdPanelReadinessFirmwareTest`, then run it
with a locally supplied OS 1.63 image:

```sh
env -u GEARMULATOR_MD_BUS_TRACE \
  -u GEARMULATOR_MD_BUS_TRACE_ENABLED \
  GEARMULATOR_MD_EXEC_SUMMARY=/private/tmp/wp06-execution-summary.txt \
  GEARMULATOR_MD_EXEC_SUMMARY_LIMIT=100000 \
  GEARMULATOR_MD_FIRMWARE_BIN=/path/to/your-local-md-os-1.63.bin \
  /path/to/mdPanelReadinessFirmwareTest >/dev/null 2>&1
cat /private/tmp/wp06-execution-summary.txt
```

The opt-in summary records only instruction categories, control-register
names, and counts. It writes no program counters, opcodes, register values,
MMIO values, firmware bytes, or instruction-by-instruction trace. Keep the
firmware and Gearmulator build local. The panel-readiness driver runs its cold
and cached startup checks; the 100,000-instruction cap is reached during the
cold run, before the later cached phase. `GEARMULATOR_MD_EXEC_SUMMARY_LIMIT`
can be raised for a longer aggregate; the 1,000,000-instruction summary and
two representative runtime scenarios are recorded in the [WP-06 report](../../../docs/reports/WP-06-coldfire.md).

The startup and runtime profiles observe Gearmulator only. They do not exercise
the Octatrack QEMU board or prove hardware compatibility. In particular,
QEMU's `an5206 -kernel` path starts directly at the ELF entry; reset-vector
behavior remains unresolved.
