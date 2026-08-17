# T2 — fix the cause T1 ranked first

**Status:** NOT STARTED
**Owner:** you
**Agent:** `implementer` · **Model:** `claude-sonnet-5` · **Effort:** high
**Blocked by:** T1 · **Blocks:** T3

## What you own

`tasks/T2/`

<!-- THIS TASK IS DELIBERATELY UNDER-SPECIFIED, and leaving it that way is the
     point of the example. The path it changes is not known until T1 reports, so
     writing one here would be a guess that later reads as a decision. Fill in
     the owned path and the steps when T1 lands, and record that as an amendment
     — what changed, what triggered it, when. A plan that silently acquires
     detail is a plan nobody can review. -->

## Steps

1. Read `tasks/T1/FINDINGS.md` first. If it says *could not establish*, *stop* —
   this task's premise died, and re-answering shaping question 1 is the move, not
   picking the most plausible-looking candidate and starting.
2. Change the one thing T1 ranked first. Only that one.
3. Fixing a defect T1 found is fine on its own merits. **Closing the slowness on
   it is not** — that is T3's job, and it needs a measurement, not a plausible
   story. A defect is not a cause until removing it removes the symptom.

## Done means

```
test -s tasks/T2/CHANGES.md
```

## Do NOT

- Do NOT change anything T1 did not rank. Two changes in one task means neither
  is measurable, and T3 cannot tell you which one worked.
- Do NOT edit `tasks/T1/FINDINGS.md`. It is the record you are being judged
  against; a fix that edits its own baseline proves nothing.
- Do NOT declare victory here. You have made a change, not an improvement.
