# T2 — the contributing factors, labelled by how well we know them

**Status:** NOT STARTED
**Owner:** Dan (human, on-call for payments that week)
**Blocked by:** T1 · **Blocks:** T3

Not handed over yet, so there is no **Delivered:** line and no hash. The freeze starts at
delivery, not at authoring — until then this contract may still be argued with.

## What you own

`tasks/T2/FACTORS.md` — nothing else.

You do not own `tasks/T1/TIMELINE.md`. If it is wrong, say so in your own file and tell Priya.

## Steps

1. Read T1's timeline first. Every factor you write has to be visible in it, or you are
   explaining a different incident.
2. One row per factor, numbered `F1`, `F2`, and so on. Each row carries a label: `CONFIRMED`
   if you ran something that shows it, and then the row quotes the command or query you ran;
   `SUSPECTED` if you reasoned your way to it. Both are respectable. Only one of them is
   evidence.
3. Two factors is the floor. An incident with exactly one cause is an incident nobody has
   finished looking at.
4. "Human error" and "operator error" are not contributing factors, and the gate rejects both
   phrases. What made the wrong action available, plausible, and unnoticed for forty-one
   minutes — those are the factors.

## Done means

```
grep -qE '^\| *F[0-9]+ *\|' tasks/T2/FACTORS.md &&
test "$(grep -cE '^\| *F[0-9]+ *\|' tasks/T2/FACTORS.md)" -ge 2 &&
test "$(grep -cE '^\| *F[0-9]+ *\|' tasks/T2/FACTORS.md)" -eq "$(grep -cE '^\| *F[0-9]+ *\|.*(CONFIRMED|SUSPECTED)' tasks/T2/FACTORS.md)" &&
! grep -qiE 'human error|operator error' tasks/T2/FACTORS.md
```

The negated clause is last on purpose. `! grep -q PHRASE missing-file.md` succeeds, because
the phrase really is absent from a file that does not exist — so a done-command that opens
with a negation is green before the work starts. Put something that must be TRUE in front of
it and the chain fails on the missing file instead, which is what a gate is for.

## Do NOT

- Do NOT rank the factors. Ranking decides where next quarter's effort goes; that is T3's, with
  the person who wrote neither document.
- Do NOT label a factor `CONFIRMED` on the strength of having read something. The gate's
  `confirmed-exercised` check will ask the row for the invocation that produced it, and the
  honest label for an inference is `SUSPECTED`.
