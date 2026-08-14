# Your first twenty minutes

You have a vague ask and you want a plan an orchestrator can run. Start here, in order.
Nothing else in this repo is required reading before you begin **building** a plan.

**Before anyone RUNS one, [`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md) is required** — see
§7. An operator briefed from this file alone told their orchestrator to make the adversary a
subagent, which the method forbids, and staffed one reader role where there are two. Neither
mistake is visible from here.

> **What this is.** A planning add-on. You use it to *build* a plan; an orchestrator agent
> then reads that plan and operates it. It is not a checklist you perform.

---

## 0 · Before anything — is it worth it?

| Your job | Do this |
|---|---|
| One obvious change, no ambiguity | **Don't use this.** Just do it. |
| 1–3 tasks, roughly an hour | 0b, then steps 1, 2, 4, 6. Skip 3 and 5. |
| 4–10 tasks, half a day | 0b, then all six steps. |
| More than that | All of it, then read [`GRILLING-THE-PLAN.md`](GRILLING-THE-PLAN.md) properly. |

**0b is never skipped.** It takes two minutes and it is what tells you which of the
rest applies.

The times are for the planning, not the work.

---

## 0b · Five questions that decide the shape

Size tells you how much — that is the sixth question, and step 0 above already asked it.
These five tell you what **kind**. Answer them now — they take two
minutes and they switch parts of this off, which is the point.

They ask about **properties of your work, not what field it is in.** A documentation job and
a server migration can get identical answers.

| | Question | Yes | No |
|---|---|---|---|
| **1** | Does the thing already exist in some form you can inspect? | Step 2 checks every claim against **it**. | Step 2 checks your sources against **each other** — say out loud that there is nothing live to check against. |
| **2** | Will more than one worker act at the same time? | Step 5 matters. Ownership is real. | Skip step 5. Still give every task a folder, owner, status and done-command — that is for *resuming*, not coordinating, and you will forget too. |
| **3** | Are the workers AI agents? | The `templates/` folder is for you. | Ignore `templates/` entirely. Everything else still works; a person reads the plan. |
| **4** | Does "done" produce something that runs or deploys? | Mind the order: build → promote → restart → check. Gate the new thing, not the old one. | No ordering trap. **"Done" is still a command** — `test -f`, a `grep`, a count. Not executable ≠ not checkable. |
| **5** | Is any step hard to undo? | Have someone try to break the plan before you run it, and stop-and-ask where a human must decide. | One review is enough. |

**Write the five answers at the top of your plan.** Anyone who thinks you scoped it wrong
argues with that list — and it is the difference between a step you *decided* to skip and one
you forgot.

---

## 1 · Write down what you were asked — then stop

Restate the ask in your own words. Name what you still need. Flag anything that would change
the **shape** of the plan. Then actually stop and get those answered.

Do not start work here. The restatement is the cheapest place to discover you heard it
differently.

**You have finished this step when** you have a paragraph and two or three flags.

---

## 2 · Attack the documents you were given ⚑

**This is the step that pays.** Everything you were handed — a spec, a brief, a handoff, a
ticket — was written at some point in the past and has been drifting since.

Take each load-bearing claim and check it against the thing itself:

- Something asserted to exist — **does it?**
- When was this written, and what has changed since?
- Do two of your sources disagree? That is information; write it down.
- The dangerous claim is the one stated as settled fact in a heading, with no caveat.

Write the contradictions down. **Never resolve one silently.** Say which source wins and why.

**You have finished this step when** you have a list of contradictions, and it has probably
resized the job.

> Skipping this is the single most common way a plan fails. In the first real run of this
> method the given spec described an API that did not exist.

---

## 3 · Count what you are dealing with

*Skip if your job is 1–3 tasks.*

Enumerate what exists. **Give numbers, not adjectives** — "several components do X" is
useless, "21 of 49" sizes the work. Cite where each claim came from. Label each one
**CONFIRMED** (you checked it yourself) or **SUSPECTED** (you inferred it or were told).
End with *"what I did not verify."*

**You have finished this step when** every category has a number.

---

## 4 · Break it into tasks — one folder each

One folder per task. Always, whatever the count.

**And put `tasks/` somewhere the software you are planning never sees** — its own
repository, or your agent's own directory. **Not `docs/plans/` in the product repo**:
that is tidy, is outside every source tree, and is still wrong. A plan is working
material for the agent layer, not an artefact of the software being planned.

Where plan and code genuinely must share a repo, the gate runs by hand or in *your* CI —
never in that repo's commit hook. **If removing Grillin would break someone's build, it
is in the wrong place.**

```
tasks/
  T1/
    TASK.md      ← the contract
```

**Copy `templates/TASK.md.template` — do not describe its shape to an agent in prose.**
A first-time user paraphrased these fields instead of using the file. The result looked
correct to a human and did not match what the gate parses, and that one substitution
caused most of her first run's findings. The gate reads fields, not intent.

Your `PLAN.md` must also declare **Size:** — one of `XS` (1-3 tasks), `S` (4-10),
`M` (11-25), `L` (26-60), `XL` (61+). The gate fails if the count leaves the band,
because a size nobody enforces is advice: in a watched trial a user asked for
"1-3 tasks, short path" and got 5 with rollback plans.

`TASK.md` needs six things, and an orchestrator will fail without them:

~~~~markdown
# T1 — <short title>

**Status:** NOT STARTED
**Owner:** <who or what does this>
**Agent:** `<persona>` · **Model:** `<claude-opus-5 | claude-sonnet-5>` · **Effort:** <high | xhigh | max>
**Blocked by:** — · **Blocks:** T2

## What you own
<exact paths or areas — one owner per thing, never two>

## Steps
1. <specific, ordered>

## Done means
```
<a command someone else can run>
```

## Do NOT
- <the specific trap for this task>
~~~~

**The `Done means` block is the one people get wrong.** It has to be a *command*, not a
description. "The docs are updated" is not checkable. `test -f CHANGELOG.md` is.

And it must **fail before the work is done**. Run it now: if it already passes, it is not
gating anything, and an orchestrator will mark untouched work complete.

**You have finished this step when** every task has a folder, an owner, and a done-command
that currently fails.

---

## 5 · Which files do two tasks both want?

*Skip if your job is 1–3 tasks.*

Separate workspaces are the easy half. The hard half is this question. There is always at
least one shared thing — a config, a registry, a shared document.

Give each contended thing **one owner**. Everybody else writes what they want changed into
their own task folder, and that one owner applies them.

**You have finished this step when** you have a list of contended files, each with a single
owner.

---

## 6 · Check it, then hand it over

Run the gate:

```bash
./scripts/validate-plan.py <your-plan-dir> --run-gates
```

It fails if a task has no owner, a `Done means` is prose instead of a command, a link points
at nothing, the dependency graph disagrees with itself, or a gate passes before the work is
done. Fix what it finds.

A green gate means the plan is **operable**. It does not mean the plan is **right** — for
that, have someone who did not write it try to break it.

Then write the entry point: one file saying *read these, in this order, then start here*.

**You have finished when** the gate is green and somebody else could start without asking
you a question.

---

---

## 7 · You are not finished — the other half starts now

A green gate means the plan is **operable**. Everything above is how to *build* a
plan. **None of it is how to run one**, and the rules that govern running one are
not optional — they are the half where the expensive mistakes live.

**Read [`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md) before anyone starts work.**
Four things in it are commonly got wrong by people who never opened it, and
every one of these was got wrong by a real operator working from this file alone:

| | |
|---|---|
| **There are TWO reader roles, not one** | A **health checker** runs continuously, in rounds, asking *are the rules being followed?* — contamination is required. An **adversary** runs once, at the end, asking *is the result true?* — contamination is disqualifying. On the reference run the health checker caught ~20 defects. Staffing only the adversary leaves that on the table. |
| **The adversary may not be a subagent** | Not a subagent of the orchestrator, not a continued session. It needs **fresh context** or it is reviewing its own reasoning. §7. |
| **A green gate is the floor, and it is low** | On the run measured end to end the gate caught **2** defects and the readers caught **50**. The gate says operable; it never says correct. §8. |
| **Instruments get proven before they are trusted** | Anything producing evidence other work depends on is checked against a known answer *first*. §5. |

And when a premise the plan rests on turns out to be dead, that is not an
amendment — you re-answer the five shaping questions with a dated new set. §2.

---

## What to read next, and only if you need it

| You want | Read |
|---|---|
| The reasoning behind all of the above | [`GRILLING-THE-PLAN.md`](GRILLING-THE-PLAN.md) |
| *(not optional — see §7 above)* | [`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md) |
| To tick a plan off against a full list | [`templates/GRILL-CHECKLIST.md`](templates/GRILL-CHECKLIST.md) |
| To see it go wrong in real life | [`CASE-STUDY.md`](CASE-STUDY.md) |
| To run a fleet of agents on a codebase | [`templates/_RULES.md.template`](templates/_RULES.md.template) and the other templates — **these assume an AI agent fleet and a code repository.** Ignore them otherwise. |
