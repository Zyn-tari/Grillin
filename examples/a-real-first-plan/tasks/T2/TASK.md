# T2 — Write `QUICKSTART.md`: the missing first twenty minutes

**Type:** BUILD
**Status:** NOT STARTED
**Blocked by:** T1 (Q1, Q2) · **Blocks:** T5
**Contended files:** `README.md` — you may edit it, but T7 applies README edits last in order
T2 → T3 → T5 → T7. Emit your README change as a diff in this folder if T3 is in flight.

## Why this exists

A stranger who clones this repo reads **865 lines before their first action** and there is no file
telling them what that action is (`01-INVENTORY.md`, VERIFIED). The README's "Start here" table
lists thirteen files and orders them by *what they are*, not by *when you need them* — it opens
with `index.html`, a visual map, which tells you about the method rather than what to do.

I hit this personally. It took me roughly fifteen minutes and three files to work out that the
first concrete action is *"restate the ask and write down a precedence ladder"*. The method
contains that answer. It does not lead with it.

## What you own

`QUICKSTART.md` (new, at repo root) and the "Start here" section of `README.md`.
You do NOT own `GRILLING-THE-PLAN.md` — that is T3.

## Steps

1. Read `tasks/T1/DECISIONS.md`. Q1 and Q2 determine paragraph one of the quickstart: who this is
   for and what they need. Do not start before it exists.
2. Write `QUICKSTART.md` around exactly one question: **what do I type first?** Target: a reader
   is doing something by minute five and holding a written artefact by minute twenty.
3. It must contain, in this order:
   - who this is for, and who it is not for (from Q1/Q2 — one honest paragraph, no hedging)
   - **the sizing decision first**, because everything else depends on it: count your tasks, pick
     XS/S/M, and go to the phase list for that size. Do not make the reader read eleven phases to
     discover they need four.
   - the XS path written out concretely: phase 0, phase 3, phase 9, phase 10 — what each produces,
     with a sentence of what it looks like when done
   - a pointer to the worked example (T5) — one line, prominent
   - what to do when a phase does not apply to your job. **This is the gap that hurt most.** A
     first-timer who cannot tell whether a step applies stops; tell them to log it and continue.
4. Amend `README.md`'s "Start here" table so `QUICKSTART.md` is row one and is marked as the
   entry point. `index.html` moves down.
5. Do not exceed 120 lines. A quickstart that needs a quickstart has failed.

## Loop

**Converge, cap 2.** Write it → hand it to someone who has not read the repo → they attempt an XS
plan for a task of their own → fix what stalled them → *they* confirm, not you. Exit when a cold
reader gets to a written artefact without asking a question. Hitting cap 2 is a stop-and-report:
if two cold readers stall in the same place, the problem is the method, not the quickstart, and
that is a finding for T4, not another rewrite.

## Done means

A named person who had not previously seen Grillin' produced a plan artefact using only
`QUICKSTART.md`, and their transcript is in this folder. Not "the quickstart reads well."

## Do NOT

- Do NOT explain what the method is *about*. That is the README's job and it does it well.
- Do NOT send the reader to `index.html` first. It is a map, not a starting move.
- Do NOT restate the eleven phases. Link them.
- Do NOT write it before T1 answers Q1 and Q2 — the first paragraph is downstream of both.

## Outputs

`QUICKSTART.md` (in the repo), `FINDINGS.md`, `CHANGES.md`, the cold-reader transcript.
