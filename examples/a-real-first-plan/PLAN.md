# PLAN — Make Grillin' cloneable by a stranger, then publish it

**Status:** DRAFT — awaiting approval at the shape gate (see `04-SHAPE.md`)
**Method used:** Grillin' (`~/grillin`), size **S**
**Planner:** first-time user of the method, no access to its author
**Date:** 2026-08-03

---

## Read order (phase 10 — the door)

1. **This file** — precedence, size call, the task list, the kickoff prompt.
2. `00-ACK.md` — what I understood the ask to be, and the three flags that change its shape.
3. `03-CONTRADICTIONS.md` — **read this before doing any task.** It is the phase-3 register and
   it resized the work. Six of the eight tasks exist because of it.
4. `01-INVENTORY.md` — the frozen count of what the repo actually contains. Nobody re-derives it.
5. `02-TRIAGE.md` — defects found during the inventory, sorted A/B/C. **Bucket B is blocking:
   four decisions only the author can make.**
6. `04-SHAPE.md` — the dependency graph. Approve this before anyone writes task prose.
7. `09-ENVIRONMENT.md` — what I verified about the world this plan assumes, and what I could not.
8. `tasks/` — one folder per task.

**Warm restart:** if you are resuming, read `CHANGELOG.md` first, then task statuses
(`grep -h '^\*\*Status:' tasks/*/TASK.md`), then come back to step 3.

---

## Precedence ladder (phase 0 — declared before anything else)

Adapted from the method's default. There is no running code here, so rung 2 is re-pointed at the
only thing that plays the same role: **what a stranger actually experiences when they try to use
the repo.**

```
1. The author's stated intent for what Grillin' is for   (the only thing I cannot verify — see flags)
2. THE ARTEFACT AS SHIPPED — the seven .md/.json/.html files and seven templates, as a
   stranger reads them, plus the observed friction of a first-time run
3. Closed decisions already visible in git history
4. This plan
5. README.md and CASE-STUDY.md as descriptions of the method
```

**Rung 5 sits below rung 2 on purpose.** README.md is marketing copy for the method; the method
files are the method. Where they disagree, the files win and the README is the thing to fix. This
already fired once: `GRILLING-THE-PLAN.md` and `README.md`/`SCALING.json`/`index.html` disagree
about which phases XS turns on. See `03-CONTRADICTIONS.md` C1.

---

## Size call: S (4–10 tasks, "half a day" of planning)

Counted, not estimated: **8 tasks** (`04-SHAPE.md`). That is squarely S.

`SCALING.json` says S turns on phases **0, 1, 2, 3, 4, 9, 10** and leaves off worktrees,
integrator, waves, long-clock loops.

**Deviation from the method, declared:** S does not turn on **phase 5** (decompose into owned
tasks) — but S is defined as *4–10 tasks*, and nothing else in the method tells you where those
tasks are written down. I ran phase 5 in reduced form anyway: one folder per task, a short
contract in each, no personas, no skills, no fragments. Skipping it would have produced a diagram
and no plan. Logged in `FRICTION.md` as F-11.

**Phases deliberately off:**

| Phase | Off because |
|---|---|
| 6 — skills | Eight tasks, one operator. There is no recurring warning appearing in five task files. |
| 7 — isolation / contended files | Real, but tiny: three files are contended (see below) and one person is editing them serially. A branch is sufficient; a worktree fleet is not. |
| 8 — substrate measurement | There is no fan-out to measure. Substrate is "one human with an editor". Recorded as a decision, not skipped silently — the method requires the rejected alternative be written down, and the rejected alternative is "spin up parallel agents", rejected because eight documentation tasks that all touch the same six files have no parallelism to extract. |

**Contended files, recorded even though phase 7 is off** (this cost two minutes and the method is
right that it is the part people skip):

| File | Wanted by | Owner |
|---|---|---|
| `README.md` | T2, T3, T5, T7 | whoever runs T7 applies all edits last, in that order |
| `GRILLING-THE-PLAN.md` | T3, T4 | T3 lands first; T4 rebases onto it |
| `SCALING.json` + `index.html` | T3 | single owner — these two must change together or the map lies |

---

## The tasks

Full contracts in `tasks/<ID>/TASK.md`. Summary:

| ID | Title | Type | Blocked by | Why it exists |
|---|---|---|---|---|
| T1 | Get the four author-only decisions answered | ASK | — | Four things I cannot decide. Publishing without them ships a guess. |
| T2 | Write `QUICKSTART.md` — the missing first 20 minutes | BUILD | T1 | There is no "do this first". A stranger lands on eleven phases and no starting move. |
| T3 | Reconcile the four scaling sources | REFACTOR | — | `GRILLING-THE-PLAN.md` disagrees with the other three about XS. |
| T4 | Decide whether Grillin' is software-only, and say so | RECONSIDER | T1 | Legitimate output is *"yes, software-only, state it in the README"*. |
| T5 | Ship one filled-in worked example | BUILD | T2, T4 | Zero of 14 files contain a completed artefact. The templates are 68 placeholders. |
| T6 | Make the templates self-sufficient | BUILD | T5 | Placeholders like `<the specific trap for this task>` give a first-timer nothing. |
| T7 | Grill the repo against itself before publishing | VERIFY | T2–T6 | Phase 9 pointed at the artefact. Never scales down. |
| T8 | Flip it public and cut v1.1.0 | BUILD | T7 | The actual publish. |

---

## Definition of done for the whole plan

Not "the README reads well". This:

> A person who has never seen Grillin', given only the clone URL, can within 30 minutes produce a
> written plan artefact for a real task of their own — and can point at the file that told them
> to do each thing they did.

Evidence someone else can check: **run it on two people who have not seen the repo, and keep their
friction logs.** If either of them asks the author a question that the repo should have answered,
that question is a defect and goes in the triage register, not in a reply.

---

## Kickoff prompt (paste-ready)

```
You are picking up the Grillin' publication plan.

Read, in this order:
  PLAN.md            — this is the entry point; the read order is at the top
  03-CONTRADICTIONS.md — read before doing anything; it is why most tasks exist
  02-TRIAGE.md       — bucket B is four questions only the repo author can answer

Then: check tasks/*/TASK.md status lines. Start with the lowest-numbered task whose
status is NOT STARTED and whose blockers are all DONE.

T1 is an ASK task. If it is not DONE, do not start T2, T4 or T5 — they encode
answers you do not have yet. T3 and T7 are unblocked by it.

Do not edit ~/grillin. All work happens on a branch of a clone.
If reality diverges from this plan, amend PLAN.md and add a dated line to
CHANGELOG.md pointing at the clause. The changelog is a receipt, not a substitute.
```

---

## Hand-off items I cannot do myself

Stated explicitly rather than silently skipped, per phase 10.

1. **The four bucket-B decisions** (`02-TRIAGE.md`) — author only.
2. **Flipping the GitHub repo from private to public** — I have no credentials and would not use
   them if I did.
3. **Recruiting the two cold-start testers** for the definition of done.
4. **Deciding whether the pilot's numbers may be published.** `CASE-STUDY.md` describes a live
   web app app, its route counts, its defect history and a shared-constant disagreement. That
   is a real third party's system. I flagged it; I cannot clear it.

---

## Status surface

`STATUS.md` in this folder, derived from the status lines in `tasks/*/TASK.md`. Regenerate with:

```
grep -H '^\*\*Status:' tasks/*/TASK.md
```

Not maintained by hand. At eight tasks a script to do this would cost more than it saves.
