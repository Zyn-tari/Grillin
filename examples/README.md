# Two examples: one that fails, one that passes

| | |
|---|---|
| [`a-real-first-plan/`](a-real-first-plan) | A genuine first attempt. **Fails, with 51 findings.** Read it to see how finished a broken plan feels. |
| [`minimal-passing-plan/`](minimal-passing-plan) | The smallest plan that passes cleanly. **A fixture, not a specimen** — do not copy it as a model. |

One of each is the minimum needed to tell a working validator from a broken one, which is the rule
[`OPERATING-THE-PLAN.md`](../OPERATING-THE-PLAN.md) §5 applies to every other instrument.

---

## A real first plan, and what the gate said about it

The first version of this repository contained **zero completed artefacts** — sixty-eight
template placeholders and a case study that *described* a plan without shipping any of it.
A first-time user put it plainly: *"every time I wanted a worked example I got a
description."*

This is the example. It is not a polished specimen.

---

## What this is

`a-real-first-plan/` is a genuine, unedited plan produced by someone using this method for
the first time, with no author available and no prior exposure to it. The job was *"plan the
work to make this repo usable by a stranger, then publish it."* They worked from the repo
alone.

`a-real-first-plan-GATE-REPORT.txt` is what [`scripts/validate-plan.py`](../scripts/validate-plan.py)
says about it. **It fails, with 51 findings.**

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
