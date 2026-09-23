# Compatibility matrix

This table tracks technical evidence. Packet lifecycle and completed/remaining work live in the [packet records](PORT_PLAN.md#work-packet-index) and [project status](STATUS.md).

| Evidence status | Meaning |
| --- | --- |
| unknown | No supporting evidence recorded |
| source documented | A source or model describes the behavior; target compatibility remains unmeasured |
| conflicting evidence | Sources or observations disagree; the difference needs resolution |
| measured | A named observation exists; read its scope and origin before drawing a compatibility conclusion |
| shim needed | A measured difference requires adaptation |
| patched | An adaptation exists with linked scope and verification; this alone does not establish full parity |
| blocked | An identified incompatibility prevents the stated result; the report names the limiting evidence |

Link every conclusion to a dated report or research-log entry. Distinguish static inspection, emulator observation, and physical measurement. CPU-family similarity and successful compilation do not establish executable compatibility.

## Boundaries and next evidence

| Boundary | Evidence status | Evidence / next measurement | Owning packets |
| --- | --- | --- | --- |
| Capture manifest and comparator | measured (synthetic) | Version-1 validator/comparator passes synthetic equivalent, divergent, missing, failed, and incomplete cases; no firmware capture is established. See the [WP-03 report](reports/WP-03-evidence.md). | [WP-03](work_packets/WP-03-evidence-contract.md), [WP-28](work_packets/WP-28-integrated-regression.md) |
| MD UW OS 1.63 image identity | measured | Local ignored image matches the 8 MiB size, MAME CRC/SHA-1, and Gearmulator FNV-64; see the [WP-02 profile report](reports/WP-02-target-profile.md) and [profile metadata](../tests/fixtures/machinedrum-sps1uw-os1.63.profile.json). | [WP-02](work_packets/WP-02-target-profiles.md) |
| MD UW hardware variant | source documented | Gearmulator's pinned Machinedrum profile selects the MKII board-ID strap. The local image does not identify a physical MKI/MKII or +Drive unit; see [WP-02](reports/WP-02-target-profile.md). | [WP-02](work_packets/WP-02-target-profiles.md), [WP-04](work_packets/WP-04-machinedrum-baseline.md) |
| Octatrack target emulator profile | source documented | octemu pins an Octatrack MKII/MCF54455 profile and expects OS 1.40C; the extracted local section lacks its source archive, and physical hardware remains unidentified. See [WP-02](reports/WP-02-target-profile.md). | [WP-02](work_packets/WP-02-target-profiles.md), [WP-05](work_packets/WP-05-octatrack-baseline.md) |
| Reset vectors and bootstrap bytes | measured | Static PC `0x0000000c`, initial SP zero, bootstrap control-register setup. Runtime reset/stack initialization remains open. | [WP-04](work_packets/WP-04-machinedrum-baseline.md), [WP-12](work_packets/WP-12-target-bootstrap.md) |
| Host CPU requirements | source documented | MD models select MCF5206E; octemu selects CFV4e. Compare executed instructions, exceptions, privilege, and control state. | [WP-06](work_packets/WP-06-coldfire-compatibility.md) |
| Host memory map and MMIO | conflicting evidence | MAME's HI08 map comments disagree with its prose and Gearmulator addresses. Reconcile traces and primary documentation. | [WP-07](work_packets/WP-07-memory-and-mmio.md) |
| Internal SRAM size | conflicting evidence | MAME maps 8 KiB; Gearmulator allocates 64 KiB despite an 8 KiB comment. Establish accessed ranges and physical constraints. | [WP-07](work_packets/WP-07-memory-and-mmio.md) |
| Interrupts, timers, scheduler, clock | conflicting evidence | MAME configures 25.447 MHz; Gearmulator models 40 MHz. Trace divisors, interrupt semantics, and scheduling. | [WP-07](work_packets/WP-07-memory-and-mmio.md), [WP-13](work_packets/WP-13-host-peripherals.md) |
| Original DSP programs on target cores | source documented | Source: two DSP56303s; target: two DSP5636x cores in a DSP56721. Inventory actual instructions, memory, interfaces, and resource needs. | [WP-08](work_packets/WP-08-dsp-payload-inventory.md), [WP-09](work_packets/WP-09-dsp-feasibility.md) |
| DSP audio routing and sample rate | unknown | Compare inter-core streams, clocks, word packing, channels, and generated buffers. | [WP-17](work_packets/WP-17-audio-and-intercore.md), [WP-25](work_packets/WP-25-machine-and-effects-parity.md) |
| Panel keys, encoders, LEDs, display | unknown | Capture startup/events, then establish complete target control reachability. | [WP-18](work_packets/WP-18-panel-protocol.md), [WP-20](work_packets/WP-20-control-surface.md) |
| MIDI, sequencing, SysEx | unknown | Compare firmware state transitions, clock/event timing, and transfers. | [WP-21](work_packets/WP-21-sequencer-and-midi.md), [WP-22](work_packets/WP-22-sysex-and-transfers.md) |
| Persistent state and UW samples | unknown | Define durable target mapping and save/restart/sampling comparisons. | [WP-23](work_packets/WP-23-persistent-storage.md), [WP-24](work_packets/WP-24-uw-sampling.md) |
| Image delivery and recovery | unknown | Choose a feasible boot strategy, validate a local candidate, and establish board-specific recovery. | [WP-10](work_packets/WP-10-architecture-decision.md), [WP-29](work_packets/WP-29-image-and-recovery-gate.md) |

Source identities, pins, and unresolved discrepancies are recorded in [boot feasibility](BOOT_FEASIBILITY.md) and the [research log](RESEARCH_LOG.md). No new runtime measurement is implied by assigning a packet owner to a row.
