# WP-35 — Import the octamad Machinedrum evidence and tools

- Status: `in_review`
- Owner: repeat98 (agent-assisted)
- Branch: `work/wp-35-octamad-md-import`
- Updated: 2026-09-23
- Depends on: none (maintenance; it adds no prerequisite to WP-00–33)
- Gate: maintenance
- Accepted delivery: pending

## Result

This repository holds octamad's Machinedrum excursion: a report that places each finding under the packet that owns it, and the tools that produced it. Contributors to WP-06–10 and WP-14–17 can start from measured MD DSP identities, interfaces, memory and cycle needs, and a proven relocation method, instead of rediscovering them.

## Scope and starting points

The source is octamad branch `machinedrum-phase0`, head `aad3e11` (23 Sep 2026). That is the user's MIT-licensed octabam working copy, local and unpublished. Its tools ran against the same Gearmulator pin as `references.json` (`8cea052`) and the same MD OS 1.63 input.

- Owned files/interfaces: `docs/reports/WP-35-octamad-md-import.md`, `docs/work_packets/WP-35-octamad-md-import.md`, `scripts/md_reference/`, `patches/gearmulator-md-mm/md-reference/`, `tests/test_md_extract.py`, and a pointer entry in each waiting packet the evidence feeds.
- Outside this packet: checking any other packet's acceptance item; the WP-04 capture tooling and its patch stack; the architecture decision itself (WP-10).
- Required inputs/access: the user's `Elektron_SPS1-1UW_OS1.63.syx` and 8 MiB dump in ignored `base_firmware/`; `vendor/elektron-firmware-tool` built. The C++ tools need a separate Gearmulator checkout at the pin.

## Deliverables

- [WP-35 report](../reports/WP-35-octamad-md-import.md): findings with measured/inferred/retracted markers and provenance, adaptation-ledger candidates for WP-10, and what octamad did not do.
- [`scripts/md_reference/`](../../scripts/md_reference/README.md): the extractor, profiler, standalone voice-DSP replay, disassembler, relocator and analysis scripts, with build and run notes.
- `patches/gearmulator-md-mm/md-reference/`: the exec-hook and host-trace patches, outside the numbered stack.
- `tests/test_md_extract.py`: synthetic tests for the DSP load-image parser.

## Acceptance checklist

- [x] The report maps every imported finding to its owning packet, keeps octamad's measured/inferred/retracted distinctions, and names origin, pin and firmware for each.
- [x] The tools are imported with provenance. `md_extract.py` reproduces the pinned section hashes, both load maps and the 50-engine catalog in this repository, and the patches apply cleanly on the pinned sources after `0001` and `0002`.
- [x] The load-image parser has synthetic tests that pass under `make check`, including truncated and malformed images.
- [x] Each affected waiting packet links the evidence in its handoff, with no acceptance item checked on its strength.
- [ ] `md_profile`/`md_replay` are rebuilt in this repository, and one capture (`c10`) replays bit-identically under a WP-03 manifest.
- [ ] Merged after review and required checks.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Keep unchecked criteria visible across prompts.

## Current handoff

- Completed: report, tools, patches, test and packet pointers, on `work/wp-35-octamad-md-import`.
- Remaining: rebuild the C++ tools here and wrap one replay in a WP-03 manifest; then review and merge.
- Next action: build `md_profile md_replay md_dis` per `scripts/md_reference/README.md` in a separate Gearmulator checkout. Then run `md_profile … capture=0x10` and `md_replay out/md_profile/cap/c10`, and expect exit 0.
- Waiting on: none.
- Blockers: none.
- Evidence: [WP-35 report](../reports/WP-35-octamad-md-import.md); the commands below.
- Delivery: enclosing commit on `work/wp-35-octamad-md-import`; PR pending.

## Prompt history

### 2026-09-23 / prompt 1 — fold the octamad Machinedrum findings into octamachine

- Request: carry the findings of octamad's Machinedrum excursion into this repository to speed up the port. Another agent was working in the main checkout (WP-04), so this work was done in a separate worktree from `origin/main`.
- Starting state → ending state: new → `in_review`.
- Owner / branch: repeat98 (agent-assisted) / `work/wp-35-octamad-md-import`.
- Completed:
  - [x] Wrote the WP-35 report from octamad's `docs/proposals/MACHINEDRUM_MACHINE.md` §12 and commits `a2d2898..aad3e11`, re-framed for a whole-firmware port and mapped to packets.
  - [x] Imported the tools, changing only root depth, paths and a docstring (checked by diff), plus both patches.
  - [x] Added synthetic load-image parser tests.
  - [x] Added prior-evidence pointers to WP-06, WP-07, WP-08, WP-09, WP-10, WP-14, WP-15, WP-16, WP-17, WP-25 and WP-26, and registered WP-35 in the plan index.
- Remaining:
  - [ ] Rebuild the C++ tools here and reproduce `c10` under a WP-03 manifest.
  - [ ] Review and merge.
- Changed files: see Owned files above, plus `docs/PORT_PLAN.md` (index row), `docs/STATUS.md`, `docs/RESEARCH_LOG.md`, `docs/COMPATIBILITY_MATRIX.md` (edits kept away from the in-flight WP-04 hunks) and the eleven packet files.
- Verification:
  - `python3 scripts/md_reference/md_extract.py` — pass. `.syx` and all five section SHA-256 pins verified; section 1: 135 records (P 234,714 / X 13,130 / Y 1,868 words); section 2: 58 records (P 18,489 / X 66 / Y 88); 135 descriptors, 50 core engines.
  - `git apply` in order `0001`, `0002` (in review), `gearmulator-md-hosttrace.patch`, `gearmulator-md-exechook.patch` on clean pinned sources (`mdLib` `8cea052`, `dsp56kEmu` `1378c43`) — all apply.
  - `python3 -m unittest tests.test_md_extract` — 4 tests pass.
  - `make check` — see the delivery commit's check run.
  - Not run: the C++ builds, profiles and replays. Their numbers are octamad's (same pin, same code) and are labelled prior evidence.
- Findings: see the [report](../reports/WP-35-octamad-md-import.md). The most consequential for WP-10: both MD DSP programs execute from external RAM, and the DSP56721 has none; relocation of the voice DSP's code is demonstrated bit-identical in the reference; the E12 samples cannot be DSP-resident alongside the rest.
- Blockers: none.
- Next action: see Current handoff.
- Delivery: enclosing commit on `work/wp-35-octamad-md-import`; PR pending.
