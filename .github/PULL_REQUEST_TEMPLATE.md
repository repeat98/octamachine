## Goal and scope

Packet ID and record link:

Packet status (`in_review` for delivered work), gate/milestone, and issue:

What changed? Which dependencies are accepted, and which criteria does this PR satisfy?

## Completed and remaining checklist

- [ ] Completed criteria are checked and linked to evidence in the packet record.
- [ ] Remaining criteria, blockers, and the next action are explicit (keep incomplete work in draft).
- [ ] Packet handoff and dated prompt history were updated for each work prompt.
- [ ] `docs/STATUS.md` reflects current work and gate evidence.

Completed work:

Remaining work and exact next action:

## Evidence

| Check | Command / fixture | Result |
| --- | --- | --- |
| `make check` | | |
| Host render or oracle comparison (if relevant) | | |
| Octabam image/emulator gate (if relevant) | | |
| Octemu headless or UI run (if relevant) | | |
| Hardware test (if relevant) | | |

Source commits, firmware versions, target hardware, measured tolerances, and remaining unknowns:

Mark unavailable checks skipped/blocked with a reason. `make check` does not establish runtime firmware compatibility.

## Provenance

- [ ] No firmware, ROM, extracted DSP payload, flash image, private project, or raw capture is included (DSP-upload traces may contain firmware words).
- [ ] Third-party code and data have an identified source and compatible license.
- [ ] Setup or architecture docs changed where needed.
