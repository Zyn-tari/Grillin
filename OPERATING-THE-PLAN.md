# Operating the plan

[`GRILLING-THE-PLAN.md`](GRILLING-THE-PLAN.md) is about building a plan. This is about being
**inside** one after it has turned out to be wrong — which is where a plan spends most of its life,
and which the method had nothing to say about until a full run made the gap impossible to miss.

> **Where this came from.** One job, run end to end, with two retrospectives written afterwards.
> Every rule below traces to a defect that run actually produced. Nothing here is anticipated.

---

## 1 · The seam

Grillin's own framing is that you *build* a plan and an orchestrator then *operates* it. The
orchestrator of that run put it plainly:

> *"That separation held for about twenty minutes."*

Once phase 2 killed the plan's central premise, the operator became a planner — and had no method,
because all eleven phases are written for the author, before anything runs.

Five failures were reported as separate gaps. They are one gap with five faces:

| Reported as | Actually only happens |
|---|---|
| the gate never reads `PLAN.md` | once the plan changes |
| no rule about the instrument being wrong | instruments get built mid-run |
| containment stops at the step, not the data | derivatives only exist once work starts |
| no re-sizing trigger | only fires when a premise dies |
| repairs produced six new defects | repairing is an execution activity |

**Grillin had no execution-time method.** That is the whole of this document.

---

## 2 · When a premise dies, go back to 0b

Phase 2 exists to kill premises. The sizing table then tells you how much method to run — and it is
consulted exactly once, at the start, before phase 2 has had a chance to change the answer.

**If phase 2 invalidates a load-bearing premise, the shaping answers are stale.** Re-answer them,
date the new set, and leave the old set visible with what killed it.

On the reference run, phase 2 established that the assessing tool could not see images at all. That
forced a measuring instrument to be designed, built, validated, wrapped in an MCP server and
registered. **None of that work had a task.** It was folded into the task whose contract said
*prove the tool can see* — which is scope smuggling, and it happened because there was no rule
saying *stop, this is a different job now*.

> **You have finished this step when** the plan carries two dated sets of shaping answers and a
> sentence naming the finding that invalidated the first.

---

## 3 · A plan changes in writing, or it has not changed

Every amendment carries four things: **what changed · what triggered it · who caught it · when**.
A change recorded only in a status line makes the plan confidently wrong, and a restarted worker
trusts the plan first.

### Contracts freeze when they are handed out

Grillin's briefing model is *every agent receives a directory, not a prompt*. **A human does not
read the directory.**

On the reference run the capture method was rewritten **two and a half hours after** the human had
already satisfied the original version — and the run then recorded the delivery as a deviation,
against wording that did not exist when they did the work. That is not a deviation. It is a
retroactively moved goalpost, and it is the one failure a hash settles outright.

So: a task with a human owner records, at the moment it is handed over,

```
**Delivered:** <date> · contract sha256:<first 12 hex of the contract hash>
```

covering *What you own*, *Steps*, *Done means* and *Do NOT*. `validate-plan.py` recomputes it.
Change the contract afterwards and the gate says so. Amend and re-deliver, or restore it — but you
may not grade someone against a rule they were never given.

**ENFORCED** — `check_frozen_human_contracts`.

---

## 4 · A repair is work, and work does not certify itself

`_RULES.md` §5 already carries the converge loop: *do → verify → **fix** → **confirm the fix, by
someone who did not make it** → re-verify.* It is scoped to task work, and it was never applied to
plan repairs.

On the reference run, **the repair pass was the second-most defect-producing activity in the job** —
six new defects, including gitignoring the style inventory and thereby stripping the tracked
evidence for every count in the deliverable. The precise mirror of the problem being fixed.

The loop's scope is not "task work". It is **any change**, including changes to the plan, the rules
and the gate itself. This is not a new rule; it is the existing rule at its correct size.

---

## 5 · Validate the instrument, separately, first

Grillin's entire model is *check the claim against the thing*. It says nothing about the **ruler**
being wrong.

On the reference run a measuring script shattered a gradient background into 24 near-identical
near-blacks, filled every palette slot, and reported *no accent detectable* with a contrast ratio of
1.05:1. **Every individual number was true. The conclusion was worthless.**

What caught it was a fixture with a known answer that the broken version still passed. Nothing in
the method asked for one.

> **The rule.** Anything that produces evidence other work depends on is an instrument. Prove it
> against a known answer **before** the measurements it authorises, and make that proof its gate.

The same rule appeared twice in one run under a second name: a **positive control** — searching for
a tool already known to exist, to prove the search itself worked, so that an empty result meant real
absence rather than a broken query. Same idea, and it is why the tool-missing finding is trustworthy.

**ENFORCED** — `check_instrument_fixture`, for any plan-local script a gate depends on.

---

## 6 · Containment extends to derivatives

Shaping question 5 asks whether any *step* is hard to undo. That protects the capture. It does not
protect the file someone transcribes the capture *into* — and that file is not gitignored, because
it is a findings document and findings documents are the point.

**Containment is a property of the data, not of the step that fetched it.** Whatever rule covers the
raw artefact covers everything derived from it, by default, until someone deliberately clears a
derivative and says why.

**ADVISORY** — a machine cannot tell a transcribed figure from an original one. This one lives or
dies on the reader in §7.

---

## 7 · How to build a reader

The most valuable section here, because it is the only one backed by a number.

### There are two roles and they are not the same role

| | **Health checker** | **Adversary** |
|---|---|---|
| Runs | continuously, in rounds | once, at the end |
| Asks | *are the rules being followed?* | *is the result true?* |
| Reads | everything — plan, tasks, findings, history | the deliverable and its evidence, and **not** the plan's reasoning |
| Contamination | **inevitable, and required** — it cannot enforce process without reading the process | **disqualifying** |
| Found (reference run) | ~20, including every process violation | 30 blocking, 14 non-blocking |

The health checker on that run **disqualified itself** from the adversarial pass, correctly, having
read the plan and half the task files by round two. That is the whole argument: the thing that makes
it good at its job is the thing that makes it useless at the other one.

### Contamination, defined so it can be checked

A reader is contaminated if it has **produced any artefact under review**, or **read the plan's
reasoning** — `PLAN.md`, the findings, the amendment history.

The checkable half is ownership: **the adversary's owner must appear nowhere else in the plan.**

**ENFORCED** — `check_adversary`, at four tasks and above. Below that the method already runs
reduced and a separately-staffed adversary costs more than it returns.

### Staffing

- **Name the adversary in the plan**, as a task, with an owner, like any other work. A role with no
  owner is the role that gets skipped at 2am.
- **Fresh context.** Not a subagent of the orchestrator, not a continued session.
- **Different lens beats a second identical sweep.** A repeat pass re-finds what the first found.
- **Two passes on anything irreversible**, the second with no sight of the first.
- **It does not fix anything.** A reader that repairs what it finds has certified its own work one
  level down, and that is the level nobody watches.

### What a reader returns

Blocking and non-blocking, separately, each citing `file:line`. The orchestrator may overrule a
finding — and must record the overrule where the finding was made. An unrecorded overrule is how a
plan quietly becomes a story about itself.

---

## 8 · The measurement, stated without euphemism

On the reference run, run to completion with every layer active:

| Layer | Defects caught |
|---|---|
| `validate-plan.py`, run on every structural change | **2** |
| Health checker, three rounds | ~**20** |
| Adversarial reader, five passes | **30 blocking**, 14 non-blocking |
| Ground-truth fixture | **1** — and it was the one that would have poisoned the deliverable |

**The machine-checkable layer caught 2. The readers caught 50.**

Three honest caveats: one job, one operator, one domain; the counts are not the same kind of thing
(the gate cannot find a false premise, and the readers cannot run a command on every commit); and
the gate ran continuously while the readers ran in bursts, so this is yield, not rate.

But the direction is not in doubt, and it should change where the effort goes. **The layers catch
disjoint classes** — structural defects here, semantic ones there — and Grillin had spent nearly all
of its written mechanism on the class that yields 2. That is why the highest-value check added in
this round does nothing except refuse to pass a plan that has nobody staffed to attack it.

---

## 9 · What is actually enforced

Honest accounting. A rule a machine cannot check is a preference.

| Rule | Status | Check |
|---|---|---|
| `PLAN.md` and `tasks/` agree on tasks and edges | **ENFORCED** | `check_plan_source_of_truth` |
| An uncontaminated adversary is staffed | **ENFORCED** | `check_adversary` |
| CONFIRMED means exercised, and cites the invocation | **ENFORCED** | `check_confirmed_is_exercised` |
| A human's contract freezes on delivery | **ENFORCED** | `check_frozen_human_contracts` |
| Instruments are proven against a known answer | **ENFORCED** | `check_instrument_fixture` |
| An irreversible task names a runnable way back | **ENFORCED** | `check_rollback_real` — lifted from project-base |
| Concurrent tasks do not own the same path | **ENFORCED** | `check_paths_disjoint` — lifted from project-base |
| A run without `--run-gates` cannot report success | **ENFORCED** | exit 2, INCOMPLETE |
| Re-answer 0b when a premise dies | ADVISORY | — |
| Repairs go through the converge loop | ADVISORY | — |
| Containment extends to derivatives | ADVISORY | — |
| Amendments are dated and attributed | ADVISORY | — |

---

## 10 · What this does not solve

~~**Nothing in this repository runs the gate.**~~ **Closed.** It used to be true, and it was the
largest open item in the method: `validate-plan.py` was documentation with an exit code, so every
ENFORCED row above was *enforceable*, not *enforced*. Three things now run it, and they fail
differently on purpose:

| | Runs | Skippable |
|---|---|---|
| [`.githooks/pre-commit`](.githooks/pre-commit) | every commit, on any plan directory the commit touches | yes — `GRILLIN_SKIP=1`, which **logs the skip**, because a skip nobody can see is indistinguishable from a pass |
| [`.github/workflows/gate.yml`](.github/workflows/gate.yml) | every push and PR | no |
| `templates/hooks.json.template` | agent session start | it is a reminder, not a gate |

> **In which repository.** The one that holds your **plans** — which is usually not the
> one you are planning changes to, and must never be the same one. Grillin runs *on* a
> plan, from outside it. A product repo has to build, test and ship with Grillin
> uninstalled, so its commit path, CI and build must never depend on it.
>
> This paragraph exists because the passage above was persuasive in the wrong direction.
> An agent read it, correctly understood that the committed hook closes the method's
> largest open defect, and wired a plan gate into an application's `pre-commit` config —
> having *first* declined to run `install-hooks.sh` because it spotted that
> `core.hooksPath` would clobber that project's existing hooks. It was careful about
> *how* and was never once prompted to ask *whether*. Every caveat in this method pointed
> at the prose; the one artefact that reaches into someone's project carried none.

Both the hook and CI **calibrate before they gate**: the known-good fixture must exit 0 and the
known-bad example must exit 1. A validator that passes everything catches nothing, and that failure
is silent unless something tests for it. CI additionally mutation-tests each check, so one that
quietly stops firing fails the build rather than passing everything.

**The adversary is staffed but not scoped.** The gate can prove the owner is clean. It cannot prove
the reader looked at the right things, or looked hard.

**Contamination is checked by ownership only.** An adversary whose owner is unique can still have
been handed the plan's reasoning in its prompt. That is a discipline, not a check.

**Three confidence levels are still two labels.** CONFIRMED now means *exercised* and is checked for
an invocation, but *told* and *inferred* both collapse into SUSPECTED. Whether that third level earns
its cost is unproven.
