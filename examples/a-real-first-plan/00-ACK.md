# Phase 0 — Acknowledge, flag, stop

**Output the method asks for:** "a paragraph and two or three flags."

---

## The restatement

Grillin' is an eleven-phase planning method that currently lives in a private GitHub repo
(`git@github.com:Zyn-tari/Grillin.git`) and has been run exactly once, by the person who wrote it,
on the project it was extracted from. The job is to close the gap between *"the author can run
this"* and *"a stranger can clone this, follow it, and end up holding a real plan"* — and then
make it public. That is documentation, sequencing and four or five decisions. It is not a code
change; there is nothing to build, no tests, no deploy.

Success is not "the README is clearer". Success is a stranger producing a plan artefact and being
able to name the file that told them to do it.

---

## Flags — things that change the shape of the plan

**FLAG 1 — Is Grillin' for software projects only?**
This changes the entire scope. Every phase except 0 and 4 assumes code: phase 1 wants `file:line`
citations, phase 5 wants file ownership and git branches, phase 7 wants worktrees, phase 8 wants
a fan-out to time, phase 9 wants scripts and repositories, phase 10 wants persistent agent memory.
The precedence ladder's rung 2 is literally "live code, live config, live data".

If the answer is **yes, software-only**, the fix is one honest sentence in the README and the
work shrinks. If the answer is **no, it's a general planning method**, then a non-software mode
has to be written and that is a much bigger job than this plan covers.

I hit this immediately — this plan is itself a non-code job, and I had to reinterpret rung 2 of
the precedence ladder to proceed at all. I guessed. The guess is in `PLAN.md`. The author has to
confirm or correct it. Task **T4**.

**FLAG 2 — Grillin' assumes you are orchestrating a fleet of AI agents.**
This is not stated anywhere in the README, which sells it as "a method, not a framework: no
install, no dependencies, no lock-in". But phase 1 is "fan out read-only workers", phase 6 is
about agent context decay and compaction boundaries, phase 8 compares agent orchestration
substrates, and four of the seven templates (`_HERDR`, `_AWARENESS`, `awareness.sh`,
`hooks.json`) are *only* meaningful if you are running a managed agent fleet. A solo human planner
cannot use half of this repo.

That is a legitimate and even interesting scope — but a stranger has to learn it from the README,
not from bouncing off `_HERDR.md.template`. Task **T4** decides; **T2** states it up front.

**FLAG 3 — the case study publishes a third party's system.**
`CASE-STUDY.md` describes a live web app: ~24 routed pages, 72 API routes, five
prior rounds of defect work, ~30 endpoints in a spec that were never built, three documents
disagreeing about a shared configuration constant, a deploy script that was root-owned and unreadable. This repo is
currently private. Making it public publishes that. I have no way to know whether that is cleared.
This is a hand-off, not a task — it blocks **T8**.

---

## What I still need

- Answers to the four questions in `02-TRIAGE.md` bucket B.
- Whether "publish" means *flip the repo public*, or *flip it public and announce it somewhere*.
  I planned the first. If it is the second, add a task; the plan does not currently contain one.

---

## Stopping here

Per the method: I did not start work at the acknowledgement.

**Except I did.** I could not produce this acknowledgement without first reading all fourteen
files, and reading them *is* phase 3. In a job whose subject matter is a set of documents, phase 0
and phase 3 are not separable — you cannot restate the ask without having grilled the artefact,
because the artefact is the ask. Recorded in `FRICTION.md` as F-04.
