# T5 — Ship one filled-in worked example

**Type:** BUILD
**Status:** NOT STARTED
**Blocked by:** T2, T4 · **Blocks:** T6, T7
**Contended files:** `README.md` (T7 applies README edits last, order T2 → T3 → T5 → T7).

## Why this exists

**The repo contains zero completed artefacts.** VERIFIED — `01-INVENTORY.md`. Fourteen files,
2,464 lines, 68 angle-bracket placeholders, and not one filled-in `TASK.md`, not one contradictions
register, not one dependency graph, not one plan.

`CASE-STUDY.md` is not this. It *describes* a 29-file plan in prose — "seven read-only agents",
"9 files, ~3,800 lines", "2,800 lines of prose" — and ships none of it. A reader is told the
artefacts were excellent and shown nothing.

What that costs in practice, from a first run: `TASK.md.template` has 21 placeholders. Several
give no signal at all about what belongs in them —

> `- Do NOT <the specific trap for this task>.`
> `- Do NOT <the pattern that looks helpful and is not>.`
> `| `<skill>` | `<the scar tissue it holds>` |`

Those are prompts to have already understood the method. One filled example answers all three
instantly, and no amount of description does.

## What you own

`examples/` (new directory) and one line in `README.md`'s file table.
You do NOT own `templates/` — that is T6, which consumes your output.

## Steps

1. Read `tasks/T1/DECISIONS.md` and `tasks/T4/`. If Q1 came back **software-only**, the example is
   a small real code change and this task shrinks. If it came back **software-first, degrades**,
   ship **two** examples — one code, one not — because the whole point of that answer is the
   second case.
2. Pick a job that is genuinely **XS or S**. Resist the urge to showcase. The pilot was a
   multi-month rebuild; nobody's first run is.
3. Actually run the method on it. Do not compose an idealised example — compose it and it will
   show, and the method's own README says the case study keeps the wrong turns in on purpose
   (`README.md:143-147`).
4. Commit **every artefact**, including the ugly ones:
   ```
   examples/<name>/
     PLAN.md               the entry point, with its read order
     00-ACK.md             the restatement and the flags
     03-CONTRADICTIONS.md  the register — the phase the method says pays most
     04-SHAPE.md           the actual diagram, in ASCII, in the repo
     09-ENVIRONMENT.md     what was verified and what could not be
     tasks/<ID>/TASK.md    at least two real ones, fully filled, zero placeholders
     FRICTION.md           what was confusing while running it
   ```
5. **Ship the friction log.** It is the highest-trust artefact in the set: a method that publishes
   where it was hard to follow is more credible than one that publishes only successes. The
   README already argues exactly this about the case study — apply it to the example.
6. Add one row to the README file table, and make `QUICKSTART.md` (T2) point at it early.

## Loop

**Converge, cap 2.** Produce the example → have someone who did not write it try to imitate it on
their own task → fix what they could not imitate → they confirm. Exit when an imitator produces a
`TASK.md` with no placeholders left in it.

## Done means

`examples/<name>/` exists and `grep -rc '<[a-z]' examples/` returns **0** placeholder occurrences
in every file. Re-runnable by anyone. A filled example containing placeholders is not an example.

## Do NOT

- Do NOT use the pilot project. It is a third party's live system (see `02-TRIAGE.md` Q4) and it
  is too big to imitate.
- Do NOT idealise. Include the guesses and the dead ends.
- Do NOT ship an example larger than S. The failure mode of examples is intimidation.
- Do NOT start before T4 has settled the scope question — it decides whether you write one example
  or two.

## Outputs

`examples/<name>/**` (in the repo), `FINDINGS.md`, `CHANGES.md`
