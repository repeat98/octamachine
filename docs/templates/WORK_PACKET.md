# Work packet template

Copy this to `docs/work_packets/WP-<ID>-<short-name>.md` for new work, a bounded child packet, or maintenance outside an existing packet. Replace placeholders and remove these introductory instructions. Register the packet in the [plan index](../PORT_PLAN.md#work-packet-index), its parent if any, and the status queue when dispatchable. Keep IDs stable.

Use the [status lifecycle](../PORT_PLAN.md#status-lifecycle-and-prompt-bookkeeping). Initial state is ready only when prerequisites pass or the first step explicitly discovers required inputs; otherwise waiting. Child acceptance must contribute to a named parent criterion.

---

# WP-<ID> — <Observable result>

- Status: `waiting | ready | in_progress | blocked | in_review | done | deferred` (choose one)
- Owner: <name or unassigned>
- Branch: <branch or unassigned>
- Updated: <YYYY-MM-DD>
- Depends on: <linked packet IDs and required accepted evidence, or none>
- Parent: <linked parent ID if applicable>
- Gate: <G0–G6, Optional, or maintenance>
- Accepted delivery: <PR/commit once merged; otherwise pending>

## Result

<One concrete observable outcome. Say what would be possible or known when this packet succeeds.>

## Scope and starting points

<Compatibility boundary, profile, sources and exact revisions to inspect, relevant existing evidence.>

- Owned files/interfaces: <bounded paths; agree ownership of shared files>.
- Outside this packet: <work reserved for another packet>.
- Required inputs/access: <local firmware profile, source checkout, tools, hardware if applicable>.
- Child packets: <links and criteria they cover, if split>.

## Deliverables

- <Code/tool/report path and purpose>.
- <Reproduction commands, synthetic fixture, or reviewed metadata>.
- <Evidence needed by the next packet>.

## Acceptance checklist

- [ ] <Observable criterion plus evidence location>.
- [ ] <Relevant failure/negative case or fidelity comparison>.
- [ ] <Dependencies and required checkpoints demonstrated>.
- [ ] <No hidden stub, missing-input skip, or unproved assumption in the claim>.

The shared [definition of done](../PORT_PLAN.md#definition-of-done) also applies. Keep unchecked criteria visible across prompts.

## Current handoff

- Completed: <short current summary; detailed evidence below>.
- Remaining: <specific unchecked work>.
- Next action: <one reproducible command or concrete investigation>.
- Waiting on: <dependency evidence, if any>.
- Blockers: <specific condition, owner/unblock action; or none>.
- Evidence: <report links, commands, approved metadata; keep raw proprietary captures local>.
- Delivery: <branch/PR or enclosing commit; reconcile accepted hash on the next prompt>.

## Prompt history

Append one entry for **every work prompt**, including research, partial work, and blocked attempts. Retain earlier entries. Use a suffix if several prompts share a date.

### <YYYY-MM-DD / prompt N> — <request summary>

- Request: <what this prompt asked for>.
- Starting state → ending state: <states; explain blocked/deferred transitions>.
- Owner / branch: <name / branch>.
- Completed:
  - [x] <specific completed action and evidence>.
- Remaining:
  - [ ] <specific next criterion or unresolved work>.
- Changed files: <scoped paths; distinguish findings-only work>.
- Verification:
  - `<command>` — <pass/fail/skipped, key result, reproducible environment>.
  - <Required gate not run and reason; skip is not pass>.
- Findings: <observations versus inferences; link research/matrix updates>.
- Blockers: <condition and unblock action, or none>.
- Next action: <precise handoff step>.
- Delivery: <enclosing commit on branch; PR link if already known, otherwise pending>.

The enclosing commit contains this entry. Obtain its hash with `git log -1 --format=%h -- docs/work_packets/<packet-file>.md` after committing and report it in the final reply. Do not make an extra commit just to embed its own hash. Before the next work prompt, reconcile the previous delivery and any merge/CI result.
