# T3 — the review and the sign-off

**Status:** NOT STARTED
**Owner:** Alex (human, staff engineer, on neither rotation that week)
**Blocked by:** T2 · **Blocks:** —

## What you own

`tasks/T3/REVIEW.md` — nothing else.

You do not own `tasks/T1/TIMELINE.md` or `tasks/T2/FACTORS.md`. Repairing the document you are
judging is how a review becomes a rewrite nobody reviewed.

## Steps

1. Read T1 and T2 the way a stranger will in six months: with none of the context, and looking
   for the sentence that only makes sense if you were there.
2. Write `**Verdict:** accept` or `**Verdict:** send back` on its own line, with the reason
   underneath. "Send back" is the half that makes the sign-off mean anything; a review that can
   only accept is a countersignature.
3. Action items numbered `A1`, `A2`, and so on. One row each: what changes, a named person who
   has agreed to it, and a date in `YYYY-MM-DD`. An action with no date is a wish, and an
   action owned by "the team" is owned by nobody.
4. If T2 ranked nothing, rank it here — in the open, with the reason. That is the one judgement
   this review is allowed to make that the other two documents may not.

## Done means

```
grep -qE '^\*\*Verdict:\*\* (accept|send back)' tasks/T3/REVIEW.md &&
grep -qE '^\| *A[0-9]+ *\|' tasks/T3/REVIEW.md &&
test "$(grep -cE '^\| *A[0-9]+ *\|' tasks/T3/REVIEW.md)" -eq "$(grep -cE '^\| *A[0-9]+ *\|.*[0-9]{4}-[0-9]{2}-[0-9]{2}' tasks/T3/REVIEW.md)" &&
! grep -qiE '^\| *A[0-9]+ *\|.*(TBD|unassigned|the team)' tasks/T3/REVIEW.md
```

A person's task is checkable too. Nothing above executes the review — it grades the document
the review produces, clause by clause: there is a verdict, there is at least one action, every
action carries a date, and no action is parked on nobody.

## Do NOT

- Do NOT fix what you find. Send it back and say what is missing; the fix belongs to whoever
  owns the document.
- Do NOT accept it because the review meeting is on Thursday. A date is not a finding.
- Do NOT take an action item yourself to make the table look complete. Every row here is a
  promise somebody made out loud.
