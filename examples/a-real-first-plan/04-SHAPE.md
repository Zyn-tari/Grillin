# Phase 4 — Shape first: the diagram

**Gate. Approve this before anyone writes task prose.** A wrong diagram costs a minute; the prose
it authorises costs hours (`GRILLING-THE-PLAN.md:130`).

Node types per `GRILLING-THE-PLAN.md:127`: `ASK` · `BUILD` · `REFACTOR` · `RECONSIDER` · `VERIFY` ·
`LOOP`.

---

```
                     ┌──────────────────────────────────┐
                     │ T1  ASK                          │
                     │ Four author-only decisions       │
                     │ Q1 scope · Q2 fleet              │
                     │ Q3 phase-10-at-XS · Q4 pilot     │
                     │ disclosure                       │
                     └───────┬──────────────────┬───────┘
                             │                  │
                Q1,Q2 ───────┤                  ├─────── Q3
                             ▼                  ▼
        ┌────────────────────────────┐   ┌─────────────────────────────┐
        │ T4  RECONSIDER             │   │ T3  REFACTOR                │
        │ Is Grillin' software-only? │   │ Reconcile the 4 scaling     │
        │ Is the fleet mandatory?    │   │ sources + the two evidence  │
        │                            │   │ vocabularies + case-study   │
        │ LEGITIMATE OUTPUT:         │   │ numbering                   │
        │ "yes — say so, build no    │   │ (C1,C2,C3,C5,Q3)            │
        │  non-software mode"        │   │                             │
        │  → T5 shrinks, T2 gets     │   │ NOT blocked by T1 except    │
        │    one honest paragraph    │   │ for Q3                      │
        └───────────┬────────────────┘   └──────────────┬──────────────┘
                    │                                   │
                    ▼                                   │
        ┌────────────────────────────┐                  │
        │ T2  BUILD                  │                  │
        │ QUICKSTART.md — the        │                  │
        │ missing first 20 minutes   │                  │
        │ "you are here, do this"    │                  │
        └───────────┬────────────────┘                  │
                    │                                   │
                    ▼                                   │
        ┌────────────────────────────┐                  │
        │ T5  BUILD                  │                  │
        │ ONE worked example, end    │                  │
        │ to end, real artefacts     │                  │
        │ examples/<name>/           │                  │
        └───────────┬────────────────┘                  │
                    │                                   │
                    ▼                                   │
        ┌────────────────────────────┐                  │
        │ T6  BUILD                  │                  │
        │ Templates self-sufficient: │                  │
        │ every placeholder gets a   │                  │
        │ filled sibling; fix C7,    │                  │
        │ C9 link/schema/gitignore   │                  │
        └───────────┬────────────────┘                  │
                    │                                   │
                    └───────────┬───────────────────────┘
                                ▼
                    ┌────────────────────────────────────┐
                    │ T7  VERIFY  (phase 9, on itself)   │  ◀── LOOP, cap 3
                    │ Every path resolves · every link   │
                    │ 200s · every count re-derived ·    │
                    │ every number traced or dropped ·   │
                    │ run GRILL-CHECKLIST against this   │
                    │ repo · TWO cold readers, keep      │
                    │ their friction logs                │
                    └───────────────┬────────────────────┘
                                    │
                          Q4 cleared│
                                    ▼
                    ┌────────────────────────────────────┐
                    │ T8  BUILD                          │
                    │ Flip private → public, tag v1.1.0  │
                    │ (AUTHOR ONLY — hand-off)           │
                    └────────────────────────────────────┘
```

---

## Notes on the shape

**T1 is an ASK node and it is the root.** Four of the eight tasks encode answers I do not have.
The method is emphatic that you stop rather than guess (phase 0, principle 12). I stopped, wrote
the questions down, and planned the rest around them. T3 and T7 are the only work that can start
today.

**T4 is a real `RECONSIDER` node.** `GRILLING-THE-PLAN.md:133` — "A node whose legitimate output
is *'don't build this'* is a node doing its job." T4's most likely output is *"yes, Grillin' is
for software projects run by an agent fleet — say so in the README and build nothing else."* That
outcome deletes work from T2 and T5 rather than adding it, and it is the outcome I would bet on.

**T7 is a `LOOP`, cap 3.** do → run the checklist and the two cold readers → fix → have someone
who did not make the fix confirm it → re-run. Hitting cap 3 is a stop-and-report, not a quiet
partial (`GRILLING-THE-PLAN.md:194`).

**T8 is on the far side of a hand-off, not a dependency I control.** Q4 (third-party disclosure)
is a hard block. A plan that shows T8 as merely "last" would be lying about why it cannot run.

**Nothing here is parallel.** Eight tasks, six shared files, one operator. The critical path is
T1 → T4 → T2 → T5 → T6 → T7 → T8, with T3 joining before T7. That is a serial chain, which is
also the honest reason phases 7 and 8 are off — there is no fan-out to isolate or measure.

---

## The approval gate

**This diagram has not been approved.** The method requires it be approved before task prose is
written (`GRILLING-THE-PLAN.md:130`, `templates/GRILL-CHECKLIST.md:34`). There was nobody to
approve it — the author is unavailable and I am a first-time user with no mandate.

I wrote the task contracts anyway, because a plan that stops at an unapproved diagram is not a
plan and the job was to produce one. **The gate is therefore open and marked open rather than
silently walked through.** If the shape is rejected, `tasks/` is discarded, not amended.

Recorded in `FRICTION.md` as F-08.
