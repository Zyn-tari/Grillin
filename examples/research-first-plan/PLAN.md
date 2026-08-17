# The plan you write when you do not have the facts yet

**Size:** XS

Three tasks. The first one goes and finds out; the other two stay honestly
unscoped until it reports.

Use this shape when the thing is real but you cannot reach it — no access, not
your machine, or it does not exist yet and will before the work starts — or when
the request names a symptom nobody has measured. That is the third answer to
shaping question 1, and it is the common one for anybody planning work they will
not personally do.

**The rule this example exists to show: do not plan around the hole, and do not
fill it with a guess.** T2 below is deliberately vague, and that is not sloppiness
— its content cannot be written honestly before T1 lands. A task you cannot write
yet is a task you should not be writing yet.

**T1 is graded on the findings it writes, never on what it found.** "I understand
it now" is not checkable by anyone. `test -s tasks/T1/FINDINGS.md` is false before
the work and true after, and it stays true when the honest answer turns out to be
*could not establish* — which is a result, not a failure, and often the one that
saves the most time.

Below four tasks Grillin runs reduced: no separately-staffed adversary, no
collision step. You are the reader.

| ID | Task | Owner | Blocked by |
|---|---|---|---|
| T1 | find out why it is slow — timeboxed | you | — |
| T2 | fix the ranked cause T1 names | you | T1 |
| T3 | prove the fix, against T1's numbers | you | T2 |

**Answers to the five shaping questions**

1. **Does the thing exist in a form you can inspect?** It exists; this planner
   cannot reach it. Hence T1 — phase 1's count and phase 9's environment check
   are not skipped and not faked, they are T1's steps.
2. **More than one worker at once?** No. Ownership is still declared, for
   resuming.
3. **Are the workers AI agents?** Yes here. If they are people, write
   `**Workers:** human` at the top of this file.
4. **Does done produce something that runs?** Yes — T3 gates on a measurement.
5. **Anything hard to undo?** No. If T1 finds otherwise, that changes this
   answer, and a changed answer is an amendment, not a status note.
