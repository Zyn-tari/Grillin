# T1 — find out why it is slow

**Status:** NOT STARTED
**Owner:** you
**Agent:** `implementer` · **Model:** `claude-sonnet-5` · **Effort:** high
**Blocked by:** — · **Blocks:** T2
**Kind:** research · **Timebox:** 90 minutes — see step 5 for what happens when it runs out

## What you own

`tasks/T1/`

## Steps

1. **One question, and it is this one:** which single operation accounts for most
   of the wall-clock time, on a run you took yourself? Not "why is it slow" —
   that is a topic, not a question, and a research task with a topic never ends.
2. Locate the thing. Record how you found it — the command, not the conclusion.
   If you cannot locate it, that is the finding: write it and stop.
3. Take a measurement before you form an opinion. Record the raw numbers.
4. Rank what you found. A number you measured is CONFIRMED and quotes the command
   that produced it. Anything you inferred, read, or were told is SUSPECTED, and
   it stays SUSPECTED in T2 until something exercises it.
5. **At 90 minutes, stop and write whatever you have.** Reaching the timebox
   without an answer is a reportable result, not a failure: write "could not
   establish X", what you ruled out and how, and what it would take. T2 is
   planned from that just as readily as from an answer — better, than from a
   guess dressed as one.

## Done means

```
test -s tasks/T1/FINDINGS.md
```

## Do NOT

- Do NOT fix anything. If the cause is obvious and the fix is one line, it is
  still T2's line — a research task that starts editing has stopped measuring,
  and nobody can tell afterwards which numbers came from before the change.
- Do NOT ship whatever you built to answer the question. A profiling harness, a
  scratch script, a patched copy: that is evidence, and it is the most tempting
  thing in the repository. It is not the deliverable.
- Do NOT widen the question. A second question is a second task.
- Do NOT write a cause you did not measure. "Probably the regex" is a hypothesis;
  label it SUSPECTED or leave it out.
