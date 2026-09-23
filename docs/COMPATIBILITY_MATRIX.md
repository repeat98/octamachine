# Compatibility matrix

Use this as a living evidence table. Status values: `unknown`, `source documented`, `conflicting evidence`, `measured`, `shim needed`, `patched`, or `blocked`. Link each conclusion to a dated research-log entry or reproducible trace. Do not mark a component compatible from CPU-family similarity alone.

| Boundary | Status | Evidence / next measurement |
| --- | --- | --- |
| Machinedrum UW OS 1.63 image identity | measured | Local ignored image matches 8 MiB size, MAME CRC/SHA-1, and Gearmulator FNV-64; see [boot feasibility](BOOT_FEASIBILITY.md). |
| Reset vector and early boot path | measured | Reset PC is `0x0000000c` in bootstrap flash and initial SP is zero; static bootstrap inspection only, runtime trace still needed. |
| ColdFire 5206e instructions on MCF5445x | source documented | MAME and Gearmulator select MCF5206E; octemu selects CFV4e. Verify instruction, exception, privilege, and timing behavior at boot checkpoints. |
| Host memory map and MMIO | conflicting evidence | MAME's DSP HI08 comments disagree with its map code and Gearmulator addresses; reconcile against firmware traces and hardware docs. |
| Internal SRAM size | conflicting evidence | MAME maps 8 KiB; Gearmulator allocates 64 KiB despite an 8 KiB comment. Determine what the tested firmware actually accesses. |
| Interrupts, timers, scheduler, and clock | conflicting evidence | MAME configures 25.447 MHz; Gearmulator models a 40 MHz ColdFire clock. Trace divisors and timing against hardware. |
| DSP56303 program on DSP56721 cores | source documented | Machinedrum has two DSP56303s; Octatrack uses two DSP5636x cores in DSP56721. Check actual firmware instructions, memory, host ports, serial links, and boot protocol. |
| DSP audio routing and sample rate | unknown | Compare generated buffers, clocking, and output mapping. |
| Panel keys, encoders, LEDs, and LCD | unknown | Inventory Machinedrum events and Octatrack controls; design a reversible mapping. |
| MIDI input/output and SysEx | unknown | Trace firmware expectations and Octatrack peripheral paths. |
| Battery memory, flash, and project storage | unknown | Define card-backed persistence and restart tests. |
| Image delivery and recovery | unknown | Establish a safe boot strategy before hardware testing. |
