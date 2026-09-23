# Comparison fixtures and private captures

This directory holds **reviewed text metadata and independently authored synthetic fixtures**. Full firmware, extracted DSP programs, transformed images, raw traces/audio, card/NVRAM contents, and private samples/projects remain in ignored local directories.

No runtime comparison corpus is established yet. [WP-03](../../docs/work_packets/WP-03-evidence-contract.md) owns the versioned capture/comparison contract. The checklist below is guidance for reports, not an implemented schema or passing fixture.

## Where artifacts belong

| Artifact | Location / sharing rule |
| --- | --- |
| Machinedrum source dump | Ignored `base_firmware/` |
| Raw MMIO/DSP traces, disassembly, audio, state snapshots | Ignored `out/` or `private/` |
| Transformed images and compiled output | Ignored `out/` or `build/` |
| Synthetic messages/events and reviewed metadata | This directory, with provenance and purpose |
| Human-readable findings | `docs/reports/` when the packet creates its report; link from the research log and compatibility matrix |

A text file is not automatically safe to publish. DSP-upload register values can reproduce firmware payloads; state dumps may include private user data. Share reviewed summaries, counts, identities, and reproduction procedures instead of raw captures.

The root ignore rules do not ignore every possible log or metadata extension. Put raw material in an ignored directory and verify the specific path, for example:

```sh
git check-ignore -v out/md-traces/boot.log
git diff --cached --name-status
```

Ignore rules do not remove a file already tracked by Git. Review the staged diff before committing.

## Metadata checklist

- [ ] Packet ID, run ID/date, and purpose of the scenario.
- [ ] Exact firmware/model profile and approved size/fingerprint metadata.
- [ ] Repository and recursive dependency revisions, patch identities, dirty-tree state, build tools.
- [ ] Origin: source emulator, stock target emulator, port candidate, or physical board.
- [ ] Initial memory/card/NVRAM state; cold boot versus warm restart or cached initialization.
- [ ] Ordered stimuli, units, clock domains, sample rate/gain where relevant, and controlled randomness.
- [ ] Command, checkpoint assertion, timeout, trace cap, dropped events, and stop reason.
- [ ] Expected result, observation, comparison alignment, declared tolerances, and first divergence.
- [ ] Outcome: passed, failed, incomplete, skipped, or blocked, with a reason.
- [ ] Local artifact hashes/roles and reproduction steps; exclude payload contents and unnecessary personal paths.

Follow the plan's [evidence contract](../../docs/PORT_PLAN.md#evidence-and-comparison-contract). Missing firmware, an unfinished script, and a truncated trace must not become a passing result. Specify what each checkpoint actually proves.

## Synthetic fixture review

State how a fixture was authored or generated, the contract it exercises, and the expected outcome. Include relevant malformed, missing, or truncated cases when implementing a validator. Keep fixtures small enough for a reviewer to inspect.

Before submission, confirm that any example bytes are independently authored and that no firmware, captured DSP words, or private project content was copied into the fixture.
