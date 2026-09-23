# Compatibility matrix

Use this as a living evidence table. Status values: `unknown`, `measured`, `shim needed`, `patched`, or `blocked`. Link each conclusion to a dated research-log entry or reproducible test. Do not mark a component compatible from CPU-family similarity alone.

| Boundary | Status | Evidence / next measurement |
| --- | --- | --- |
| Machinedrum image format and reset vector | unknown | Inspect a user-supplied image locally; record hashes and section layout. |
| ColdFire 5206e instructions on MCF5445x | unknown | Diff instruction use and exception behavior at actual boot checkpoints. |
| Host memory map and MMIO | unknown | Trace Gearmulator MD/MM boot, compare with Octatrack map. |
| Interrupts, timers, scheduler, and clock | unknown | Record initialization and timing behavior in both emulators. |
| DSP56303 program on DSP56721 cores | unknown | Check instructions, P/X/Y allocation, host interface, ESSI/ESAI, and boot protocol. |
| DSP audio routing and sample rate | unknown | Compare generated buffers, clocking, and output mapping. |
| Panel keys, encoders, LEDs, and LCD | unknown | Inventory Machinedrum events and Octatrack controls; design a reversible mapping. |
| MIDI input/output and SysEx | unknown | Trace firmware expectations and Octatrack peripheral paths. |
| Battery memory, flash, and project storage | unknown | Define card-backed persistence and restart tests. |
| Image delivery and recovery | unknown | Establish a safe boot strategy before hardware testing. |
