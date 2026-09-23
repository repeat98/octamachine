# Port plan: Machinedrum firmware on Octatrack

## Goal

Run the **actual Machinedrum firmware** on Octatrack hardware, preserving its sequencer, machines, sound, UI behavior, MIDI behavior, and project semantics as closely as the hardware permits. Prefer compatibility shims and small, documented binary patches over rewriting individual machines. A change is acceptable only when the unmodified behavior is impossible on the target or a measured hardware difference requires it.

The goal is experimental. No current evidence proves that the whole firmware can boot, that its DSP programs fit, or that the Octatrack's panel can express every Machinedrum control. A feasibility gate comes before any flashable build.

## Hardware boundary

| Component | Machinedrum reference | Octatrack reference | Porting question |
| --- | --- | --- | --- |
| Host CPU | ColdFire 5206e (MAME skeleton) | ColdFire MCF5445x (octabam hardware notes) | Can the code execute with address, exception, interrupt, timer, and peripheral translation? |
| Audio DSP | Two DSP56303 chips (MAME skeleton) | Two DSP5636x cores in one DSP56721 (octabam hardware notes) | Which DSP instructions, memory layouts, boot paths, and peripherals differ? |
| Memory/storage | Machinedrum flash, small RAM and battery memory | Octatrack SDRAM and CompactFlash | How can Machinedrum state and firmware data be mapped or emulated durably? |
| Panel/audio/MIDI | Machinedrum-specific devices | Octatrack-specific devices | What translation preserves the firmware's event and display behavior? |

Sources: [MAME Elektron driver](https://github.com/mamedev/mame/blob/master/src/mame/elektron/elektronmono.cpp) and [octabam hardware notes](https://github.com/sambanks/octabam/blob/main/docs/firmware/CHIP.md). The matrix is a starting hypothesis; check each item against the exact firmware and hardware revision under test. The MAME driver is a non-working skeleton and cannot prove compatibility.

```text
Unmodified Machinedrum OS + DSP programs (user-supplied)
                     │
       minimal, recorded transformations if required
                     │
                     ▼
       Machinedrum compatibility layer on Octatrack
       ├─ CPU memory/peripheral/interrupt mapping
       ├─ DSP boot, memory, host-port, and audio mapping
       ├─ panel and MIDI translation
       └─ persistent storage mapping
                     │
                     ▼
           Octatrack hardware or octemu
```

## Work packages and evidence gates

1. **Baseline and provenance.** Record model/revision, Machinedrum OS hash, Octatrack OS version if used as a carrier, source repository commits, and license status. Firmware stays local. Identify whether an independent boot path or an Octatrack OS carrier is required; do not assume octabam's module loader alone can host the Machinedrum OS.
2. **Boot feasibility.** Compare both ColdFire instruction sets, reset vectors, image layout, RAM requirements, address maps, exceptions, interrupts, and peripheral use. Build a read-only analyzer and a compatibility matrix with each instruction/peripheral marked supported, shimmed, patched, or blocked. Boot the same user-supplied Machinedrum image in Gearmulator MD/MM as the behavioral baseline.
3. **Emulator proof.** Extend or configure octemu to load a transformed Machinedrum image in a test mode. Reach a named checkpoint (reset, early initialization, scheduler, panel, then transport) with trace evidence. Add shims only for observed dependencies. Keep octemu changes reviewable and upstreamable.
4. **DSP proof.** Extract the firmware's own DSP boot payloads locally and compare their instruction, memory, and peripheral needs with the Octatrack DSP cores. Run an unchanged payload where possible; log every required relocation or patch. Compare audio and state against Gearmulator MD/MM across multiple machines and effects.
5. **I/O and persistence.** Translate the Octatrack panel, MIDI ports, audio routing, and card-backed storage to the Machinedrum firmware's expected interfaces. Document any unreachable Machinedrum control and how it is exposed on the Octatrack. Verify saved state survives restart.
6. **Image and hardware gate.** Build from user-owned firmware without distributing derived images. Run structural checks, octemu headless scripts, real-time UI and audio tests, and a recovery rehearsal before a hardware flash. Test first on a known hardware revision with backups; record the observed result and faults.

The [compatibility matrix](COMPATIBILITY_MATRIX.md) holds the work items and evidence. PRs should advance one row or one boot checkpoint at a time. A component may be marked **blocked** if direct execution is impossible; the report must say whether a narrow compatibility layer can resolve it. If a full 1:1 port proves infeasible, document the limiting evidence before proposing a reduced scope.
