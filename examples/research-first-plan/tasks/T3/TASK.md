# T3 — prove it, against T1's numbers

**Status:** NOT STARTED
**Owner:** you
**Agent:** `implementer` · **Model:** `claude-sonnet-5` · **Effort:** high
**Blocked by:** T2 · **Blocks:** —

## What you own

`tasks/T3/`

## Steps

1. Re-run **the identical measurement T1 ran** — the same command, on the same
   input. A different measurement compared against T1's numbers is not a
   comparison, it is two unrelated readings printed next to each other.
2. Put both readings in `RESULT.md` verbatim, T1's and yours. Not the delta:
   whoever reads this needs to be able to disagree with your arithmetic.
3. If it did not improve, say so plainly and stop. An unimproved result is a
   finding about T1's ranking, and it belongs back at T1's question — not
   absorbed by trying the next candidate here, which is T1's work happening in
   the wrong task with no timebox on it.

## Done means

```
test -s tasks/T3/RESULT.md
```

## Do NOT

- Do NOT change the code here. If T2 was wrong, that is a result to report, and
  repairing it inside the task that grades it is self-certification.
- Do NOT re-run only the fast path. Measure the same thing T1 measured, including
  the parts you expect to be unchanged — that is how you find out you broke
  something else on the way.
