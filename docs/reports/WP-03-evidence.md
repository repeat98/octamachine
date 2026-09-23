# WP-03 — Capture and comparison contract

- Date: 2026-09-23
- Owner: Codex
- Branch: `work/wp-03-evidence-contract`
- Status: `in_review`
- Contract version: 1

## Result

Version 1 defines a JSON manifest for each run, a JSON Lines event trace, and a comparison plan stored with both manifests. `scripts/compare_captures.py` validates those inputs and compares a complete reference/candidate pair. It emits machine-readable JSON, reports the first mismatch, and returns distinct statuses for equivalence, divergence, missing input, invalid input, incomplete capture, and capture failure.

The synthetic fixtures in `tests/fixtures/wp-03/` contain invented MMIO events. They exercise ordering and declared numeric tolerance; they are not derived from Machinedrum or Octatrack firmware, emulator output, or hardware.

## Manifest fields

The examples `reference.json` and `candidate.json` are complete version-1 manifests. Each run records:

| Field | Contract |
| --- | --- |
| `schema_version` | Integer `1`; incompatible schema versions fail validation. |
| `run` | Unique `run_id`, shared `scenario_id`, purpose, origin, and UTC start time. Origin is `reference_emulator`, `stock_target_emulator`, `port_candidate`, `physical_board`, or `synthetic`. |
| `run.firmware` | Profile ID, firmware revision, and approved public fingerprints. Complete/incomplete non-synthetic captures need at least one fingerprint; synthetic runs use an explicit no-firmware profile. A failed launch may record an unavailable identity. Keep local artifact hashes or private image paths in local records unless their publication is approved. |
| `run.source_state` | Repository/revision for each source, dirty-tree flag, and patch IDs with SHA-256 digests. Include recursive source revisions when they affect the run. |
| `run.build` | Exact argument vector and toolchain/configuration metadata; use path placeholders where personal paths are unnecessary. |
| `run.initial_state` | One of `cold_boot`, `warm_restart`, `cached_initialization`, or `restored_state`, with a description of RAM, storage, DSP, clock, and random-seed state as applicable. |
| `run.stimuli` | Ordered `sequence`, stable `stimulus_id`, action `kind`, and scheduled `at` time. `at.clock_id` names a declared clock domain; its numeric value uses that domain's unit. Include parameters and operator actions needed to reproduce the input. |
| `run.clock_domains` | Named clocks, each with a unit, origin, and known frequency or `null`. Every event timestamp is a non-negative number in its named domain. Timestamps must not move backwards within one domain. |
| `checkpoint` | Stable checkpoint ID, observable trigger, and positive timeout with units. Record measured triggers and limits; do not invent firmware addresses or timings before observing them. |
| `capture` | Status (`complete`, `incomplete`, or `failed`), trace path/format, complete-record count, expected count if known, limit, dropped count, and stop reason. Failures include a reason and need not have a trace. |
| `comparison` | Stable plan ID, declaration time, and ordered list of event fields to compare. Every field uses exact matching or an explicit absolute numeric tolerance with a unit. |

Each `jsonl-v1` event has a contiguous zero-based `sequence`, `kind`, `clock_id`, and `time`. Sequence is the capture writer's record order; it does not establish causality between unsynchronized clocks. If an event contains a `pc`, it also contains `pc.semantics`: `current_instruction`, `next_instruction`, `faulting_instruction`, `return_address`, or `not_applicable`. MMIO reads/writes include `width_bits` and `endianness`. Values are represented as JSON numbers or strings as appropriate to the event.

Record both scheduled stimulus times and trace timestamps with their clock origins. The comparator does not align unrelated clocks. It only compares `time` when corresponding events use the same clock ID and the two manifests define that clock identically. Otherwise compare semantic event order and fields, or first produce an explicitly justified common time base.

## Completion and comparison rules

- A complete trace must end on a JSONL record boundary, have no dropped events, and match its expected record count when that count is known. Its stop reason is `checkpoint_reached` or `normal_exit`.
- An incomplete trace records a reason such as `timeout`, `trace_limit`, `user_stop`, `device_error`, `output_error`, or `process_exit`. A missing final newline or partial final JSON record is reported as incomplete. Incomplete data never compares as a pass.
- A failed capture has a `failure_reason`; it is reported separately from a missing file and malformed manifest.
- The two manifests must name the same scenario, checkpoint definition, initial-state mode, ordered stimulus sequence, comparison-plan ID, and comparison rules. Origins, firmware profiles, source revisions, and toolchains are recorded independently because reference and candidate builds may differ.
- Event order is compared strictly by `sequence`. The plan decides which event fields are judged. Exact rules use JSON value equality. `absolute_tolerance` passes only when `abs(reference - candidate) <= tolerance`, and its unit is recorded; relative tolerance is not implicit.
- Set each plan's compared fields and tolerances before interpreting the result. Select tolerances from an observed baseline or an explicit requirement, and explain them in the scenario report. The fixture's `0.1` absolute tolerance is only a boundary-test value for the comparator; it says nothing about firmware behavior. A plan is not evidence that a firmware value is valid.
- The first mismatch reports event index/sequence, field, reference and candidate values, and the applied numeric difference/tolerance. A count mismatch reports the first missing event index. The summary contains no full trace, but first-divergence values may still be sensitive; review output before sharing.

## Tool and outcomes

Run the comparator from the repository root:

```sh
python3 scripts/compare_captures.py \
  tests/fixtures/wp-03/reference.json \
  tests/fixtures/wp-03/candidate.json
```

It prints one JSON summary to stdout with both run IDs, origins, firmware profile IDs, checkpoint ID, plan declaration times, event count, and first divergence. Exit codes are stable for automation:

| Exit | `result` | Meaning |
| ---: | --- | --- |
| 0 | `equivalent` | Every event matched every declared rule and both traces were complete. |
| 1 | `divergent` | A declared event field or event count differs; the first divergence is included. |
| 2 | `missing_input` | A manifest or referenced trace file is absent. |
| 3 | `invalid_input` | JSON/schema/metadata is malformed or internally inconsistent. |
| 4 | `incomplete_trace` | A trace was capped, stopped early, dropped events, or ended mid-record. |
| 5 | `capture_failed` | The capture process recorded a failure reason. |

`make check` runs the reference validator, Python compilation, and `tests/test_compare_captures.py`. The ten test methods cover equivalent values within the fixture tolerance, all four accepted initial-state modes, first divergence, missing trace and manifest, duplicate-key rejection, firmware identity enforcement, capture failure, trace-cap handling, and an incomplete trace with a partial final record. They need no firmware or emulator.

## Use with the named checkpoints

WP-04 and WP-05 should record the exact source/target origin and profile, baseline input identity, source/dependency revisions, patches, initial state, actual stimulus schedule, clock origin, command, and last proved checkpoint. Use CP00 for accepted static image identity and CP10–CP90 only when the corresponding observed behavior and bounded trigger are known. The manifest supports timeout/cap outcomes; this packet does not set Machinedrum/Octatrack PC values, firmware timeouts, register expectations, or runtime tolerances.

For boot comparisons, distinguish a cold boot from warm restart, cached initialization, and restored state. Record reset release and any operator action as ordered stimuli. A PC value states whether it names the current, next, faulting, or return instruction. Do not compare raw cycle counts across different clocks unless a measured mapping justifies it.

## Privacy and reproduction

Keep complete traces, firmware images, DSP uploads, audio, state dumps, and personal paths in ignored local directories. DSP-upload MMIO values can contain firmware words. The checked-in fixtures are authored values, and the test runner creates missing, divergent, failed, and truncated variants only in temporary directories. Review summaries and any trace excerpt before adding it to a PR.

The contract and comparator establish capture integrity and declared-field comparison only. They do not prove that a checkpoint trigger is correct, that an emulator models physical hardware, or that a profile boots.
