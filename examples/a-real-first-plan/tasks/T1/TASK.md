# T1 — Get the four author-only decisions answered

**Type:** ASK
**Status:** NOT STARTED — *update in place*
**Blocked by:** — · **Blocks:** T2, T4, T5, T8 (and Q3 within T3)
**Owner:** the repo author. Nobody else can do this task.

Reduced contract: size S, phase 5 run in reduced form (see `PLAN.md`). No persona, no skills, no
worktree, no fragments.

## Why this exists

Four questions surfaced in phase 3 that cannot be answered from the repository. Three of them
change the *shape* of the remaining work, not its detail. Guessing at them and publishing would
ship a method whose front page says something its author does not believe.

## What you own

Nothing in the repo. This task produces a decision record, not an edit.

## Steps

1. Read `02-TRIAGE.md` bucket B and `03-CONTRADICTIONS.md` C4, C6, C8.
2. Answer each of Q1–Q4 in one paragraph. Not "it depends" — a decision.
3. Write them into `DECISIONS.md` in this folder, dated, one heading per question.
4. For each: name the task it unblocks and any task it *deletes*. Q1 answered "software-only"
   should shrink T5 and T2 — say so explicitly so the downstream tasks get amended rather than
   executed as written.

## The four questions

**Q1 — Is Grillin' for software projects only?**
7 of 11 phases assume code, a repo, commits or a build (`01-INVENTORY.md`). `README.md:32-33`
implies otherwise. Answering "software-only" is a perfectly good answer and makes the job small.

**Q2 — Is the AI agent fleet mandatory, recommended, or optional?**
6 of 7 templates are unusable without one. If it is mandatory, the README's "no install, no
dependencies" claim goes.

**Q3 — At XS, which of phase 10's five outputs are required?**
Phase 10 is on at XS; `SCALING.json` switches its status surface off. The other four
(entry point, kickoff prompt, persistent memory, hand-off list) are unstated.

**Q4 — May the pilot project's details be published?**
`CASE-STUDY.md` names a live web app page count, route count, unbuilt endpoints,
a constant disagreement across three documents, and an unreadable root-owned deploy script.
Public repo = public disclosure. **This blocks T8 outright.**

## Loop

None. This is a decision task; it is done when it is answered.

## Done means

`tasks/T1/DECISIONS.md` exists, dated, with four headings, each carrying an answer and the list of
tasks it unblocks or deletes. Checkable by anyone: four headings, four decisions, no "TBD".

## Do NOT

- Do NOT answer Q4 on the author's behalf.
- Do NOT let Q1 default to "it's general-purpose" because that sounds better. `01-INVENTORY.md`
  counted 7 of 11 phases assuming code. The generous answer is the one that costs the most work.

## Outputs

`DECISIONS.md`
