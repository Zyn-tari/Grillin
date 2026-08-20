# T1 — the timeline: what happened, minute by minute

**Status:** IN PROGRESS
**Owner:** Priya (human, incident commander on the night)
**Blocked by:** — · **Blocks:** T2
**Delivered:** 2026-08-19 09:40, in the incident channel · contract `sha256:4c959cfe2439`

There is no **Agent**, no **Model** and no **Effort** line above, and that is not an omission —
`PLAN.md` declares `**Workers:** human`, and a person has neither. The **Delivered:** line is
what that costs: from the moment it was written, this contract is frozen at the hash beside it.

## What you own

`tasks/T1/TIMELINE.md` — nothing else.

You do not own `tasks/T2/FACTORS.md`. What happened and why it happened are two jobs, and the
second one is Dan's.

## Steps

1. Rebuild the timeline from the channel scrollback, the pager log and the deploy log — not
   from memory. Memory reorders events towards the explanation you hold now, and this document
   is read by people who will never hold it.
2. One row per event: the clock time, what was observed, and who observed it. Six rows is the
   floor for a forty-one minute outage; fewer than that and you are writing a summary.
3. State `Time to detect:` and `Time to mitigate:` on their own lines, in minutes, each showing
   the two clock times you subtracted. Detection came from a customer here, so that number is
   the reason the review is being written at all.
4. Where you cannot establish a time, write `unknown` and say what would settle it. Do not
   smooth the gap: a week later an interpolated timestamp is indistinguishable from a measured
   one, and T2 will build on it either way.

## Done means

```
grep -q 'Time to detect:' tasks/T1/TIMELINE.md &&
grep -q 'Time to mitigate:' tasks/T1/TIMELINE.md &&
test "$(grep -cE '^\| *[0-9]{2}:[0-9]{2}' tasks/T1/TIMELINE.md)" -ge 6
```

Three clauses, and none of them is `test -s`. A file that exists proves somebody created a
file. These fail while the timeline is missing, still fail while it is four rows long, and
only pass on a document that says the two things the review is for.

## If it fails

If the scrollback has been trimmed and six honest rows are not reachable, stop and say so
inside `TIMELINE.md` rather than filling it in, then tell Alex the gate will not go green and
why. Six rows of guesswork is worse than four rows and a stated gap, because the guesswork is
the part T2 builds on.

## Do NOT

- Do NOT name anybody as a cause. Who typed the command is not why it was possible to type it,
  and T2's own gate rejects the phrase outright.
- Do NOT write the fix. An action item that arrives before the contributing factors is the fix
  you already had in mind before the incident.
- Do NOT let this contract be edited now that it has been handed over. Every section from
  **What you own** down is inside the hash on the **Delivered:** line. If it genuinely has to
  change, change it, re-run the hash, and record that it was re-delivered — an amendment
  somebody agreed to is fine, an amendment nobody noticed is the failure.
