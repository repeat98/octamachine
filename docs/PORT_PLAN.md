# Port plan: Machinedrum firmware on Octatrack

## Goal and fidelity contract

Run the **actual Machinedrum host firmware and its original DSP programs** on Octatrack hardware, as close to 1:1 as possible. Preserve the original machines, effects, sequencer, parameter behavior, UI state, MIDI, sampling, and saved-state semantics. Prefer direct execution with small, evidenced adaptations at hardware boundaries. A fresh implementation of drum voices does not fulfill this goal.

Feasibility is still open. Related CPU and DSP families do not establish binary compatibility, peripheral equivalence, or enough real-time capacity. A successful PC emulator experiment must lead to a mechanism that can execute on the selected Octatrack hardware.

Every adaptation must identify the original behavior, measured target constraint, smallest proposed change, affected code/data or interface, and regression evidence. Keep an adaptation ledger from WP-10 onward. Timing, precision, routing, control reachability, and persistence are observable behavior; none is silently exempt from fidelity. Reduced feature scope or a broader rewrite requires a recorded maintainer decision before changing the plan.

## How to use this plan

- Read [project status](STATUS.md) for present evidence, active work, and the next queue.
- Choose one [packet below](#work-packet-index); its file is authoritative for status, acceptance checklist, owner, and prompt history.
- Dispatch it with the [agent handoff template](templates/AGENT_HANDOFF.md). Split large packets into bounded children with the [work packet template](templates/WORK_PACKET.md).
- Follow [AGENTS.md](../AGENTS.md) for branches, commits, pushes, and PRs. Update the packet and status after **every work prompt**, including investigations that reach a blocker.
- Put technical observations in the [research log](RESEARCH_LOG.md) and conclusions in the [compatibility matrix](COMPATIBILITY_MATRIX.md). Those documents hold evidence; packet records hold execution status.

A packet can take several prompts. Each prompt needs a completed/remaining checklist and continuation notes. A roadmap entry, compiled harness, or merged documentation PR does not establish a firmware checkpoint.

## Established baseline

These starting facts come from the existing [boot feasibility audit](BOOT_FEASIBILITY.md) and [research log](RESEARCH_LOG.md), through commit `0e8e42b`.

| Area | Established | Still needed |
| --- | --- | --- |
| Repository | Contributor workflow, reference index, ignored private inputs, pinned octemu source, separate emulator patches | Reproduction from clean recursive source checkouts |
| MD input | Local 8 MiB image matches documented UW OS 1.63 fingerprints | Exact source model/profile and runtime baseline |
| Reset | Static audit gives PC `0x0000000c`, initial SP `0`; bootstrap configures control registers | Runtime reset and stack initialization trace |
| Trace support | Gearmulator bus instrumentation compiled as mdLib on Apple Silicon with `BUILD_TESTING=OFF` | Clean recursive build and captured run; prior nested DSP changes prevent claiming clean reproduction |
| Target | octemu models MCF54455/CFV4e and loads OT OS sections at `0x40000400` | Unmodified OT baseline and explicit Machinedrum target profile |
| Port | No Machinedrum boot on Octatrack or octemu demonstrated | CPU, DSP, I/O, persistence, audio, and hardware gates below |

Audit revisions: Gearmulator MD/MM `8cea0524a75435122c20b669ca114c9ac6509ba2`; octemu `87000189418c8ca2026dc047bda220b66802809d`; MAME `d7ffd71ed97831b7f995337d6c5bd1bbb03898af`. They identify historical evidence. A pin change needs a reason and affected baseline reruns. MAME is non-working/no-sound; Gearmulator is a reference model whose hardware fidelity must also be assessed.

## Hardware and execution boundary

| Boundary | Machinedrum starting model | Octatrack starting model | Question to answer |
| --- | --- | --- | --- |
| Host execution | MCF5206E firmware | MCF54455 / CFV4e in octemu | Instructions, privilege, control registers, exceptions, alignment, memory attributes |
| DSP execution | Two DSP56303 programs | Two DSP5636x cores in a DSP56721 | Instructions/arithmetic, P/X/Y memory, overlays, interrupts, cycles |
| Host-to-DSP | Machinedrum HI08 transactions | Target DSP host interfaces | Boot, width/endianness, readiness, interrupts, backpressure |
| Audio | Original inter-DSP and audio-device topology | Target DSP, codec, serial interfaces | Rates, clock ownership, channel count, word format, routing, latency |
| Panel | Machinedrum protocol and controls | Octatrack panel/display transport | Startup, event order, display semantics, all control functions |
| State | Flash, RAM, persistent regions in source models | Target memory/storage | Capacity, addresses, durability, compatibility, failure recovery |

WP-02 selects exact hardware variants. Source-model facts are not universal board specifications.

WP-07 resolves known discrepancies: MAME's HI08 comments use `0x00400000/0x00500000`, while its prose and Gearmulator use `0x00500000/0x00600000`; SRAM is modeled as 8 KiB versus 64 KiB; configured CPU clocks are 25.447 MHz versus 40 MHz. Explain each disagreement with evidence, or carry it as an unresolved constraint.

### Architecture decision before integration

WP-10 selects a path using WP-06 through WP-09 evidence:

| Candidate | What must be demonstrated |
| --- | --- |
| Independent boot of adapted MD firmware | Reset/vectors, memory ownership, interrupts, target initialization, image loading, recovery |
| MD firmware hosted by an OT carrier | Concrete execution environment, scheduling/resource ownership, interrupt/device arbitration, DSP ownership, sufficient memory/cycles |
| Additional translation or emulation on target | Specific implementation and measured budget under target constraints; a desktop process cannot supply the missing hardware mechanism |

octabam's module loader is a research/tooling lead. Its existence alone does not prove it can host another complete firmware.

Every address alias, peripheral trap, interrupt translation, or DSP bridge must say **where it executes on real hardware**. Emulating an MCF5206E board inside octemu may explain the source firmware, but does not prove a port to the Octatrack's CPU and peripherals.

The decision returns `go`, `conditional-go` with bounded prerequisites, or `no-go` with limiting evidence. A no-go report can complete its research packet; it cannot clear an implementation gate. Resolve conditional prerequisites before dependent implementation. Reopen the decision if measurements invalidate its assumptions.

## Milestones and exit gates

Gates describe outcomes, not dates or completion percentages. Project status links the evidence used to clear each gate. All required packet criteria and the shared definition of done apply.

| Gate | Required outcome | Packets | Exit evidence |
| --- | --- | --- | --- |
| G0 — Reproducible baselines | Agreed profiles and repeatable reference runs | WP-00–05 | Clean provenance, input manifests, MD boot capture, unmodified OT headless/UI capture |
| G1 — Port feasibility | Hardware-realizable CPU/DSP/peripheral design | WP-06–10 | Instruction/map audits, payload inventory, budgets, accepted architecture with no blocking condition |
| G2 — Execution primitives | Target boot, host services, original DSP payloads, panel transport, live audio | WP-11–18 | Reversible transforms; CP10–CP50; component tests and explicit remaining stubs |
| G3 — Firmware behavior | Integrated boot, controls, sequencing, MIDI/SysEx, state, UW, machines/effects, load/fault behavior | WP-19–28 | CP60–CP90, reference comparisons, fidelity coverage, repeatable regression report |
| G4 — Hardware readiness | Local candidate and board-specific recovery plan | WP-29 | Deterministic image/manifest, structural/emulated load checks, recovery rehearsal and stop conditions |
| G5 — Hardware evidence | Controlled startup and parity on the selected physical target | WP-30–31 | Run authorization, board/candidate identity, measured startup, audio/timing/state/endurance |
| G6 — Reproducible delivery | Another contributor reproduces the supported port profile | WP-32 | Independent reproduction, supported profiles, source/tooling release instructions, limitations |
| Optional extension | Another source or target variant | WP-33 | Separate profile; repeat affected gates and retain original baseline |

G2 primitives may use labeled synthetic stimuli or peer models for isolation. G3 must use the integrated firmware path for claimed behavior. G5 establishes physical Octatrack behavior.

### Named checkpoints

WP-03 defines exact triggers, capture fields, expected evidence, and timeouts. Until measured, do not invent firmware PC addresses, durations, register values, or numerical tolerances.

| ID | Observable checkpoint | Required distinction |
| --- | --- | --- |
| CP00 | Image/profile accepted: size, digest, layout, reset interpretation | Static input identity versus execution |
| CP10 | Reset executes and establishes valid stack/control state | Reference reset versus target bootstrap |
| CP20 | Required memory and vectors are usable | Modeled mapping versus realizable target mapping |
| CP30 | Host timer and interrupt primitives work | Probes versus integrated firmware scheduling |
| CP40 | Both DSP uploads complete their expected handshake | Upload acknowledgment versus correct execution |
| CP50 | Both payloads execute with inter-core and serial audio activity | Activity versus sound/timing fidelity |
| CP60 | Stable ready state with scheduler and panel handshake | Screenshot/quiet trace versus demonstrated readiness |
| CP70 | Scripted transport, note, control actions produce expected transitions | Headless/UI agreement and reference event ordering |
| CP80 | Changed state survives save, restart, reload | RAM reuse versus durable persistence |
| CP90 | Declared stress workload completes within budgets | Host playback speed versus guest cycles/physical timing |

Each result names its origin: MD reference emulator, unmodified OT emulator, port under the target emulator profile, or physical hardware. Compare matching initial states and stimuli. On failure report the last proved checkpoint and first divergent event.

## Work packet index

Linked files contain scope, starting sources, deliverables, acceptance checklists, and next action. Dependencies require accepted evidence; source reading and tool preparation may happen earlier. Status lives in the packet files to avoid a conflicting second table here.

WP-00–33 define the port roadmap. Maintenance packets track supporting repository work and do not add technical prerequisites to that roadmap.

| Packet | Result area | Depends on | Gate |
| --- | --- | --- | --- |
| [WP-00](work_packets/WP-00-planning-and-status.md) | Planning, status, and agent handoff | — | G0 |
| [WP-01](work_packets/WP-01-source-provenance.md) | Reproduce source and dependency provenance | — | G0 |
| [WP-02](work_packets/WP-02-target-profiles.md) | Define firmware and target hardware profiles | — | G0 |
| [WP-03](work_packets/WP-03-evidence-contract.md) | Define captures, checkpoints, and comparisons | — | G0 |
| [WP-04](work_packets/WP-04-machinedrum-baseline.md) | Capture the Machinedrum reference boot | WP-01, WP-02, WP-03 | G0 |
| [WP-05](work_packets/WP-05-octatrack-baseline.md) | Capture Octatrack boot in headless and UI modes | WP-01, WP-02, WP-03 | G0 |
| [WP-06](work_packets/WP-06-coldfire-compatibility.md) | Audit ColdFire execution compatibility | WP-04, WP-05 | G1 |
| [WP-07](work_packets/WP-07-memory-and-mmio.md) | Reconcile memory, MMIO, and clock contracts | WP-04, WP-05 | G1 |
| [WP-08](work_packets/WP-08-dsp-payload-inventory.md) | Extract and identify DSP boot payloads locally | WP-02, WP-03, WP-04 | G1 |
| [WP-09](work_packets/WP-09-dsp-feasibility.md) | Assess DSP instruction and resource fit | WP-05, WP-08 | G1 |
| [WP-10](work_packets/WP-10-architecture-decision.md) | Choose a hardware-realizable port architecture | WP-06, WP-07, WP-09 | G1 |
| [WP-11](work_packets/WP-11-image-transforms.md) | Build a reversible local image transformation pipeline | WP-10 | G2 |
| [WP-12](work_packets/WP-12-target-bootstrap.md) | Reach target reset, vectors, and memory setup | WP-05, WP-10, WP-11 | G2 |
| [WP-13](work_packets/WP-13-host-peripherals.md) | Adapt host interrupts, timers, and essential peripherals | WP-07, WP-12 | G2 |
| [WP-14](work_packets/WP-14-dsp-host-bridge.md) | Adapt DSP upload and host-port handshakes | WP-08, WP-09, WP-12, WP-13 | G2 |
| [WP-15](work_packets/WP-15-dsp-payload-a.md) | Run original DSP payload A | WP-10, WP-14 | G2 |
| [WP-16](work_packets/WP-16-dsp-payload-b.md) | Run original DSP payload B | WP-10, WP-14 | G2 |
| [WP-17](work_packets/WP-17-audio-and-intercore.md) | Connect DSPs, serial audio, and target routing | WP-15, WP-16 | G2 |
| [WP-18](work_packets/WP-18-panel-protocol.md) | Bridge panel startup and event transport | WP-07, WP-12, WP-13 | G2 |
| [WP-19](work_packets/WP-19-integrated-boot.md) | Reach complete firmware idle and transport startup | WP-13, WP-14, WP-17, WP-18 | G3 |
| [WP-20](work_packets/WP-20-control-surface.md) | Map the full control surface and UI | WP-18, WP-19 | G3 |
| [WP-21](work_packets/WP-21-sequencer-and-midi.md) | Preserve sequencer and real-time MIDI behavior | WP-19 | G3 |
| [WP-22](work_packets/WP-22-sysex-and-transfers.md) | Preserve SysEx, configuration, and bulk transfers | WP-21 | G3 |
| [WP-23](work_packets/WP-23-persistent-storage.md) | Map durable firmware state to target storage | WP-10, WP-19 | G3 |
| [WP-24](work_packets/WP-24-uw-sampling.md) | Preserve UW sampling and audio-input behavior | WP-17, WP-20, WP-23 | G3 |
| [WP-25](work_packets/WP-25-machine-and-effects-parity.md) | Compare machine families and effects | WP-17, WP-19, WP-21 | G3 |
| [WP-26](work_packets/WP-26-realtime-budget.md) | Measure real-time load and resource limits | WP-20, WP-21, WP-22, WP-23, WP-24, WP-25 | G3 |
| [WP-27](work_packets/WP-27-faults-and-restarts.md) | Exercise faults, restarts, and state recovery | WP-23, WP-26 | G3 |
| [WP-28](work_packets/WP-28-integrated-regression.md) | Assemble the repeatable integration gate | WP-20, WP-21, WP-22, WP-24, WP-25, WP-26, WP-27 | G3 |
| [WP-29](work_packets/WP-29-image-and-recovery-gate.md) | Package a local candidate and rehearse recovery | WP-11, WP-28 | G4 |
| [WP-30](work_packets/WP-30-hardware-bringup.md) | Perform controlled hardware bring-up | WP-29 | G5 |
| [WP-31](work_packets/WP-31-hardware-parity.md) | Compare hardware sound, timing, state, and endurance | WP-30 | G5 |
| [WP-32](work_packets/WP-32-release-and-handoff.md) | Prepare a reproducible contributor release | WP-28, WP-29, WP-31 | G6 |
| [WP-33](work_packets/WP-33-additional-variants.md) | Extend to another firmware or hardware variant | WP-32 | Optional |
| [WP-34](work_packets/WP-34-contributor-documentation.md) | Improve README, setup, and contributor documentation | WP-00 | Maintenance |
| [WP-35](work_packets/WP-35-octamad-md-import.md) | Import the octamad Machinedrum evidence and tools | — | Maintenance |

### Dispatch order and splitting

1. Start WP-01, WP-02, and WP-03: reproducible source, exact profiles, capture contract.
2. Capture WP-04 and WP-05 independently after their prerequisites. Do not patch the port to compensate for an unreproduced reference boot.
3. Audit host execution (WP-06), maps/peripherals (WP-07), and DSP inventory/fit (WP-08 → WP-09). Combine findings in WP-10.
4. Follow WP-11 → WP-12 → WP-13 → WP-14. WP-15 and WP-16 can study separate original payloads. WP-18 can proceed alongside DSP work after its prerequisites.
5. Integrate DSPs in WP-17 and reach firmware idle in WP-19. UI (WP-20), sequencing (WP-21), and storage (WP-23) can advance with agreed interfaces. SysEx, UW, and sound comparisons follow their dependencies.
6. Combine functional coverage before WP-26 through WP-29. Hardware work and independent reproduction follow G4.

This is a dependency plan, not permission to assign several agents to the same files. Each active packet has one owner. Agree interface/schema changes before parallel work, assign ownership of shared files, and have the integrating owner reconcile them.

Split broad packets such as machine-family parity, control mapping, and fault campaigns when one prompt cannot produce a coherent reviewed result. Use child IDs such as `WP-25-A`, each with one family/behavior, outputs, dependencies, and checklist. Register children in their parent and the index. Parent criteria remain open until child evidence covers them.

Keep IDs stable when discoveries require new packets. Record reasons for dependency changes and check for cycles. Optional variants never silently replace the baseline. Narrow scope only when remaining criteria are explicitly assigned elsewhere or deferred by the maintainer.

## Evidence and comparison contract

### Reproduction record

Every technical result provides these fields in a text report/manifest. WP-03 turns the contract into capture/comparison tooling.

| Field | Required content |
| --- | --- |
| Identity | Packet/run ID, date, source/target profile, firmware revision and approved fingerprints |
| Source state | Revisions including recursive dependencies, patch digests, dirty-tree state, build configuration/toolchain |
| Initial state | Cold/warm reset, memory/NVRAM/card initialization, clocks/rates, DSP state, RNG/seed if controllable |
| Stimulus | Ordered script/MIDI/panel/audio actions, timestamps with units/clock, live operator actions |
| Capture | Checkpoint triggers, event types/width/endianness, PC semantics, limits, dropped events, stop reason, timeout |
| Comparison | Reference identity, alignment, fields compared, tolerances declared before interpreting results |
| Outcome | Pass/fail/blocked/skipped, first divergence, resource usage, uncertainty, reproduction commands |
| Artifacts | Ignored local paths, hashes and reviewed metadata, report/adaptation links |

A comment is source documentation. A trace observes one model or device. An inferred explanation remains an inference until supported by a probe or independent source. Preserve both sides of a discrepancy.

### Fidelity dimensions

| Dimension | Default comparison | Evidence needed for an exception |
| --- | --- | --- |
| Host state/protocols | Exact deterministic values, order, messages, transitions | Documented nondeterminism or necessary adaptation |
| DSP arithmetic/audio | Exact digital output under established equivalent deterministic conditions; otherwise stated numerical metrics | Precision/rate/clock differences, alignment/error method, measured behavior consequences |
| Sequencer/MIDI timing | Intervals, ordering, jitter, drift, clock/transport response | Baseline variability and specific clock/latency constraint |
| Panel/display | Same logical operations and reachable states with explicit physical mapping | Different geometry/control count; documented alternative gesture |
| Persistent state | Semantic round trip and exact bytes where format unchanged | Versioned adaptation with round-trip/failure-recovery evidence |
| Resource fit | Peak memory, stack, DSP allocation, cycles, queue depth, deadlines | Explicit headroom limits and unmeasured worst cases |

Set pass thresholds per scenario before candidate comparison. Report worst cases and typical behavior. Plausible audio, a matching screenshot, or a quiet log alone is insufficient.

### Private artifacts and public review

Keep images, extracted DSP programs, transformed images, raw traces, recorded audio, card/NVRAM contents, and private samples/projects in ignored locations. **DSP-upload MMIO values can contain firmware words**; text traces also need review before publication. Public fixtures are synthetic or reviewed metadata exposing no proprietary payload.

Reviewers must be able to inspect adapters, reproduce synthetic checks, and understand claims without firmware. Missing private input is skipped or blocked, never passed. Use contributor-local path placeholders instead of personal paths where possible.

## Validation layers

| Layer | Inputs | Establishes | Does not establish |
| --- | --- | --- | --- |
| Public scaffold | Checked-in files | `make check`: reference validation and Python compilation | Firmware execution |
| Public synthetic tests | Generated headers/messages/opcodes/state scenarios | Transform rejection, parsers, controlled adapter behavior | Full boot or payload fidelity |
| Private MD baseline | MD image and clean Gearmulator | Reference traces/behavior in that model | Guaranteed physical MD fidelity |
| Private OT baseline | OT image and clean octemu | Target emulator works headless and with UI | MD compatibility |
| Private port regression | Approved images, manifests, scripts, target profile | Emulated boot, behavior, audio, state, bounded workload | Physical clocks, analog behavior, recovery |
| Interactive session | Same candidate and panel/audio UI | Gesture reachability and live integration issues | Quantitative parity without captures |
| Hardware campaign | Selected board, approved candidate, recovery assets | Physical behavior, deadlines, I/O, endurance | Untested boards or firmware |

Separate octemu host playback/pacing artifacts from guest DSP behavior. Slower diagnostic runs and half-speed mode cannot pass a real-time deadline. Record host elapsed time and guest timing when relevant. Add meaningful implementation tests in the owning packets; private firmware must not become a public CI prerequisite.

## Risks and decision triggers

| Risk | Owner | Required response |
| --- | --- | --- |
| Unsupported CPU instruction/control register/exception | WP-06, WP-12 | Target-executable adaptation and budget; reopen WP-10 if behavior cannot be preserved |
| Source addresses cannot be mapped/intercepted | WP-07, WP-10 | Concrete mapping or patch/translation mechanism before accepting emulator shims |
| DSP precision/memory/overlays/cycles do not fit | WP-08–09, WP-15–17 | Identify limiting resource and smallest evidenced adaptation |
| Carrier competes for interrupts, memory, DSPs, audio | WP-10, WP-13, WP-17 | Demonstrate ownership/arbitration or revise boot strategy |
| Physical clocks/channels/serial topology differ | WP-07, WP-17, WP-31 | Record fidelity impact before rate/channel compromises |
| Panel functions unreachable or events reordered | WP-18, WP-20 | Full control inventory and accessible mapping |
| State loss on reset/card failure | WP-23, WP-27 | Fault injection and last-valid-state recovery |
| Emulator shortcuts hide dependencies | WP-04–05, WP-28 | Enumerate stubs; corroborate critical behavior with hardware or primary sources |
| Distribution restrictions | WP-01, WP-32 | Record licenses; publish permitted artifacts only; octemu documents a combined-binary distribution restriction |
| Unproved hardware recovery | WP-29–30 | Explicit uncertainty and run-specific maintainer direction before changing hardware |

## Source guide

These are starting paths in optional local checkouts, not promises about installation or revision. Verify source state in WP-01.

| Area | Starting points |
| --- | --- |
| Image audit/references | `scripts/audit_md_image.py`, `references.json`, `scripts/references.py`, `patches/` |
| MD CPU/memory/boot | `vendor/gearmulator-md-mm/source/elektron/md/mdLib/`: `mdmc.*`, `mdsim.*`, `mdmemorymap.h`, `mdromloader.*`, `mdromdata.*` |
| MD DSP/panel/state | Same `mdLib/`: `mdhardware.*`, `mddsp.*`, `mdpanel.*`, `mdfrontpanel.*`, `mdstate.*`, `mdflash.*`, `mdrampacking.h`, MIDI/SysEx code |
| OT CPU/DSP | `vendor/octemu/src/board/`: `ot-board.c`, `ot-dsp-port.c`, `ot-dsp-shim.cc`, `ot-dsp56k.cc`; patched QEMU tree |
| OT panel/storage/scripts | Same board directory: `ot-panel-uart.c`, `ot-panel-wire.h`, `ot-ata.c`; `vendor/octemu/src/script.c`, `src/main.c` |
| OT research | `vendor/octabam/docs/firmware/`: CHIP, DSP, KERNEL, PANEL, MIDI, ARCHITECTURE |
| Image/harness/recovery | `vendor/octabam/docs/remixer/`: HARNESS, FAILURE_MODES, EMU, PLACEMENT, TOOLING, FLASHING |
| Destination code | `src/image/` local transforms; `src/compat/` hardware adapters; `src/dsp/` original-payload compatibility; `tests/fixtures/` reviewed metadata |

Repository links are in the [README upstream table](../README.md#upstream-work). For unresolved hardware questions consult primary CPU/DSP/device manuals and record revision plus section/page. An emulator comment alone is not a hardware specification.

## Status lifecycle and prompt bookkeeping

| State | Meaning |
| --- | --- |
| `waiting` | Prerequisite packets/gates have not passed; preparation may proceed |
| `ready` | Dependencies accepted, scope understood, required inputs available or an explicit input-discovery step exists |
| `in_progress` | Named owner actively advances the packet |
| `blocked` | Specific missing input/decision/access/technical condition prevents progress; name the unblock action |
| `in_review` | Pushed branch delivered for ingestion; evidence available or draft explicitly names remaining gaps |
| `done` | Acceptance criteria and shared definition of done satisfied; accepted/merged |
| `deferred` | Maintainer explicitly postponed/removed scope, with reason and impact |

A waiting dependency is not automatically a technical blocker. A done claim identifies accepted PR/commit and evidence. Transitions never erase prompt history or unchecked criteria.

At the start of every work prompt, read the packet/status, inspect the working tree, reconcile prior PR merges, and record owner/branch. At the end:

1. Check acceptance items only when proved.
2. Update the current handoff: completed work, remaining work, blockers, evidence, precise next action.
3. Append a dated history entry with **completed [x] and remaining [ ] items**, commands/results (including skips), conclusions, delivery reference.
4. Update `STATUS.md`: active work, gate changes, next queue, cross-cutting blockers. Update research/matrix for changed technical knowledge.
5. Include records in the prompt's scoped commit/push. Final reply reports packet/status, completed/remaining work, verification, commit/branch/push and PR outcome.

Pure questions/read-only status requests need an accurate checklist in the reply, without an empty commit. Research that changes project knowledge, blocked attempts, and continuations require durable entries even if no production code changes.

Use the enclosing commit as the prompt delivery reference and retrieve its hash after committing. Do not create recursive bookkeeping commits to embed a commit's own hash. The next work prompt records the previous hash/PR and reconciles merged status. Preserve other owners' entries when resolving shared-document conflicts.

## Definition of done

- [ ] Result/scope match the accepted brief; each acceptance item has evidence or an approved scope decision.
- [ ] Dependencies and gate conditions pass; no hidden stub supplies claimed behavior.
- [ ] Relevant checks have outcomes, including negative cases and unavailable inputs; `make check` passes.
- [ ] Adaptations have reasons and regression evidence; research log/matrix reflect new conclusions.
- [ ] Packet checklist, handoff, prompt history, and project status are current.
- [ ] Diff contains intended, permitted files; firmware and private captures remain ignored.
- [ ] Scoped commits are pushed, PR explains evidence/limitations, review and CI requirements are met.
- [ ] Change is accepted/merged; next status reconciliation records acceptance and releases dependent work.

Incomplete work can be a useful committed handoff on a draft PR. Keep unchecked items visible. Opening or merging a PR alone does not prove a technical gate. Hardware flashing remains a separate explicit authorization step after G4.
