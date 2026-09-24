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

`interrupt_mask.S` uses the AN5206 model's timer source at level 4. With SR.I
set to 5, it confirms that the timer is pending while the handler count remains
zero; lowering SR.I to 3 delivers exactly one interrupt. The `m5206` and
`cfv4e` models match on this level-sensitive case. The generic AN5206 board
does not expose the MCF5206E external edge-sensitive level-7 input, so that
special case remains untested.

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
