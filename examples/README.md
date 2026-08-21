# The shipped examples: one that fails, one that passes, one worked by people

| | |
|---|---|
| [`a-real-first-plan/`](a-real-first-plan) | A genuine first attempt. **Fails, with 49 findings.** Read it to see how finished a broken plan feels. |
| [`minimal-passing-plan/`](minimal-passing-plan) | The smallest plan that passes cleanly. **A fixture, not a specimen** — do not copy it as a model. |
| [`human-worker-plan/`](human-worker-plan) | **A plan whose workers are people, not agents.** Three named humans write an incident review. Shows `**Workers:** human`, task files with no model or effort, no roster — and the frozen contract that is the price of the exemption. |

One of each is the minimum needed to tell a working validator from a broken one, which is the rule
[`OPERATING-THE-PLAN.md`](../OPERATING-THE-PLAN.md) §5 applies to every other instrument.

`human-worker-plan/` is the third shape, and it is here because it was missing. Grillin supports a plan
worked by people — [`QUICKSTART.md`](../QUICKSTART.md) §0b question 3 asks it outright — and until now
nothing shipped that demonstrated it. Three first-time users hit the model floor on a plan of people
independently, and two of them stopped running the gate at all, which is the expensive failure: a gate
that is wrong about a case people really have gets discarded whole, taking the twenty checks that were
right with it. Later, both curators planning human-worked jobs assembled their contracts by hand, and one
had to open [`tests/test-human-workers.sh`](../tests/test-human-workers.sh) to find out what the
declaration buys and costs. That answer now lives in
[`human-worker-plan/README.md`](human-worker-plan/README.md), in one paragraph.

---

## A real first plan, and what the gate said about it

The first version of this repository contained **zero completed artefacts** — sixty-eight
template placeholders and a case study that *described* a plan without shipping any of it.
A first-time user put it plainly: *"every time I wanted a worked example I got a
description."*

This is the example. It is not a polished specimen.

---

## What this is

`a-real-first-plan/` is a genuine plan produced by someone using this method for the first
time, with no author available and no prior exposure to it. **Unedited except for one thing:**
when the repository moved to the Zyn-tari organisation, the old account name was rewritten
wherever it appeared, including in this plan's own inventory of what it found. Nothing else was
touched — not a task, not a finding, not the licence line it recorded seeing at the time, which
was MIT and is now PolyForm. Its defects are the author's. The job was *"plan the
work to make this repo usable by a stranger, then publish it."* They worked from the repo
alone.

`a-real-first-plan-GATE-REPORT.txt` is what [`scripts/validate-plan.py`](../scripts/validate-plan.py)
says about it. **It fails, with 49 findings.**

Both are here on purpose.

## Why ship a plan that fails

Because it is what a competent first attempt actually looks like, and because the failures
are the instructive part:

- **Six of eight tasks name no owner.** The plan reads as complete. An orchestrator cannot
  dispatch a single one of those six.
- **Five tasks state a done criterion in prose.** One says *"Checkable by anyone"* and gives
  nothing to run — which is the exact self-deception the rule exists to catch.
- **Three done-commands are unanchored.** They pass from the author's directory and throw
  `FileNotFoundError` from anywhere else. One of them is green *before any work is done* — an
  orchestrator would run it, see success, and mark an untouched task complete.
- **The dependency graph disagrees with itself** in three places, and five tasks are blocked
  by identifiers that are not tasks.
- **Four links point at files that do not exist**, including a `_RULES.md` the plan relies on.

Every one of those is invisible while reading the plan. They surface the moment something
tries to *run* it, which is the entire argument for having a gate rather than a checklist.

## What it also shows working

Don't read it as a disaster. The parts of the method that carry their weight are visible too:

- Phase 3 turned an expected three tasks into eight — four of them exist only because
  grilling the source documents found things that were not true.
- The root task is an **ASK** node that halts rather than guessing, and says so in writing.
  A plan that stops on a decision only a human can make is a plan working correctly.
- The plan declares its own uncertified state instead of claiming completeness.

## How to use it

Read `a-real-first-plan/PLAN.md` and one task, then read the gate report next to it. The gap
between how finished the plan feels and what the gate finds is the thing worth internalising.

Then run it yourself:

```bash
./scripts/validate-plan.py examples/a-real-first-plan --run-gates
```

It should fail. When you write your own plan, that same command should pass — and passing
means *operable*, not *correct*. Correctness still needs someone who did not write it trying
to break it.
