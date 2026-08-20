# Operating the plan

[`GRILLING-THE-PLAN.md`](GRILLING-THE-PLAN.md) is about building a plan. This is about being
**inside** one after it has turned out to be wrong — which is where a plan spends most of its life,
and which the method had nothing to say about until a full run made the gap impossible to miss.

> **Where this came from.** One job, run end to end, with two retrospectives written afterwards.
> Every rule in §§1–8 traces to a defect that run actually produced. Nothing there is anticipated.
>
> **§§9 and §10 come from a second, much smaller job** — one landing page onto a production VPS,
> six hand-written briefs, 665 lines, no plan directory, the runner never invoked — and each says
> so where it sits. They are placed *after* the measurement in §8 rather than among the rules they
> resemble, because that measurement counts the first run only. A rule from a different job does
> not get to borrow another job's numbers.

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

## 9 · A defect is not a cause until you remove it

> **Second job.** This and §10 trace to the landing-page deploy named in the preamble, not to the
> reference run measured in §8.

> **The rule.** A defect you found is not the **cause** of a symptom until removing it removes the
> symptom, or restoring it brings the symptom back.

**Two claims, two burdens.** *"X is a defect"* needs only evidence that X exists — a 404 in the
network log, a missing file, a wrong identifier. *"X causes Y"* needs a control test: take X away
and watch Y, or put X back and watch Y. They are different claims with different burdens, and
conflating them is the whole of the error. Existence is cheap and it is not evidence of causation.

**Fixing X stays fine, and is often right.** Vendor the missing file, correct the identifier, close
the 404 — those repairs stand on their own merits and need no causal claim at all. What is
forbidden is **closing the symptom** on the strength of them. Fix the defect; leave the symptom
open until a control test attaches it to something.

**This applies to every defect→symptom attribution, not only the first one found.** The first
plausible defect is simply where people stop looking — it arrives while the symptom is still
unexplained, so it inherits the explanation by default. The fifth gets the same burden, and a
defect found *after* the cause is believed known is no safer: it is the one that gets quietly
folded into a closed bug.

**The incident.** On a deployed landing page a chart failed to redraw. A vendored JS file the page
referenced was genuinely missing — a real 404, confirmed in the network log — and was asserted as
the cause. The control test was one line of work: block the file at the network layer and see
whether the symptom follows. It did not. The chart still redrew, and the browser had never
requested the file in the failing run either. The real cause was elsewhere entirely — a language
switch froze the SVG subtree. Vendoring the missing file was correct. Closing the bug on it would
have shipped the freeze.

**The control test is execution, not inspection** — principle 7, at this level. Reading the code
around X and finding it plausible is not a control. The test is a run of the system with X's state
changed and the symptom observed, and both observations get recorded: what you changed, and what
the symptom did.

**When the control test is not available.** Some defects cannot be restored (the data is gone) or
cannot be removed safely (production, and no reproduction). The rule does not become a licence to
close on a hunch, and it does not block the ledger forever either: write the attribution down as
**unproven**, name the control test you would have run and why you could not run it, and close the
*defect*. The symptom stays open, or is closed as *not reproducible* — which is a different
statement from *fixed*, and the next person needs to be able to tell them apart.

> **You have finished this step when** the amendment that closes the symptom names the control
> test, the state of the defect on each side of it, and what the symptom did on each side. A
> closure that names only the defect is not finished; it is a hypothesis with a resolved status.

---

## 10 · Confirm the artefact before the first edit

Phase 3 already grills the source documents against the running system, and the precedence ladder
already puts **the running system above every document**. Both fire at planning time, once, against
the sources that existed then. **This is the same rule at execution time**, and it belongs here
rather than in the phases because the documents that break at execution time are the ones written
*after* the plan: the brief handed to a worker, the change-set a designer sends on Thursday, the
README inside a vendored bundle. By the ladder those are rung 5. They are read literally by
whoever is holding them.

**The rule.** Before executing an instruction set that names files, identifiers or selectors,
confirm each named thing exists in the artefact you actually have. Not the repo the author was
looking at. The deployed one.

`templates/TASK.md.template` already covers the moment you *notice* — "an owned path that does not
exist, a 'done' that cannot be evidenced: record it in `QUESTIONS.md` and stop. Do not quietly do
the adjacent thing." This is narrower and earlier: **before the first edit, and with no plan
directory in the picture**, which is the case that template never reaches.

### What it caught, in one small deploy

| Instruction, and its author | Named | The artefact actually had |
|---|---|---|
| A vendored bundle's README: edit this file to set the language | `index.php` | `index.html` served; no PHP ever executed — the edit would have landed in a file nobody reads |
| A designer's change instructions, twice, throughout | `index.php` | `index.html` |
| The same change instructions, locating an element | `data-r="headcta"` | the attribute appeared nowhere in the file |

**Three misses, two authors, one deploy** — and **every other identifier in that designer's
change-set was correct**, which is the finding. Miss rate does not correlate with the quality of
the rest of the document, so you cannot spot the bad line by reading around it. You resolve every
name, or you resolve none.

The cost is one grep per identifier. The bundle README cost about four seconds to disprove.

### Three commands, from a brief with no plan directory behind it

Written this way because that is how the reference deploy actually ran. A rule that only fires
inside a tool nobody installed catches nothing.

```sh
# 1 · every path the instructions name — does it exist here?
grep -ohE '[A-Za-z0-9_./-]+\.(html|php|js|css|json|md|toml|ya?ml)' BRIEF.md | sort -u |
  while read -r f; do [ -e "$f" ] || echo "ABSENT  $f"; done

# 2 · every backticked identifier or selector — does it appear in what you will edit?
grep -ohE '`[^`]+`' BRIEF.md | tr -d '`' | sort -u |
  while read -r id; do grep -rqF -- "$id" dist/ || echo "ABSENT  $id"; done

# 3 · the arithmetic invariant — run it before the edit and again after
grep -c '<a ' dist/index.html
```

They over-report: a prose word in backticks is not an identifier, and a false ABSENT costs you a
glance. The output you are reading is the ABSENT lines, and a run with no ABSENT lines is the
result you wanted, not a run that failed to work.

> **You have finished this step when** every file, identifier and selector named in the instructions
> has been resolved against the artefact, and the ones that did not resolve are named in writing
> **before** the first edit — not fixed silently. A silent substitution of `index.html` for
> `index.php` is a plan change that never got written down; see §3.

### The second technique: find the arithmetic invariant and test it

Existence checks are one grep per name and tell you nothing about whether the author's *model* of
the artefact is right. The cheap corroboration is arithmetic.

That designer's change-set implied a number. The file held **11** anchor elements; the instructions
removed **7**; the spec said **4** should remain. `11 − 7 = 4` agreed. One subtraction corroborated
the entire map of the file without reading it line by line — and, better, made the result
**falsifiable afterwards**: count the anchors when you are done, get 4, or the edit is wrong.

> **You have finished this step when** you have written down either the invariant — the count, where
> it came from, and what it should be afterwards — or one line saying the instructions imply none.
> Without that line, a reader who looked and found nothing is indistinguishable from one who never
> looked, and this is the only technique in the section whose omission leaves no trace.

It is §5's positive control aimed at the instruction set instead of at the instrument, and it is the
reason a diff whose line count does not match the spec is a signal and not a curiosity.

### The limit, stated plainly

**This catches identifiers that are absent. It cannot catch an identifier that is present and means
something different.** Had that site contained an `index.php` that simply was not the file being
served, the preflight would have passed and the edit would still have gone nowhere. A selector
matching three nodes where the author meant one passes on existence and fails only the arithmetic; a
selector matching exactly one wrong node passes both. Presence answers *is this name in the
artefact* — never *is this the thing the author meant*. That second question is the reader's, §7.

The same deploy produced the mirror failure, and §9 is that failure. **Present is not the same as
responsible, and absent is not the same as to blame.** Preflight buys you the existence column of
the table and nothing else.

**ADVISORY** — and it will stay advisory. The identifiers live in prose the gate never reads, in
documents that frequently do not exist when the plan is authored.

---

## 10b · How you learn a worker finished

**Do not write a `wait-for-agent.sh`.** Operators keep writing one — a script per agent,
backgrounded one shell each, polling for a name to go quiet. It works, and it re-implements
per site the question the execution layer is already the authority on.

This is the boundary rule doing its job. *Which* tasks exist, who owns them, and what "done"
means are declarations, so they are this document's and the gate's. *Has this one finished*
is execution, so it is Smokin's:

```bash
smokin wait <plan> --task T4      # blocks until T4 settles; returns on the event
smokin run  <plan>                # or drive the whole plan and be told when it stops
```

`wait` returns the moment the task settles rather than on a clock, `5` at once if the task is
owned by a person — it will never settle on its own — `4` if the plan halts underneath it, and
`3` on `--timeout`. It starts nothing and holds no state.

**And a task a person owns is never dispatched to a model.** The gate and the runner use one
definition of who counts as a person — `is_human_owned` in `scripts/validate-plan.py`, which
Smokin copies character for character and asserts against this file in its own tests. Declare
it with `**Owner:** human` on the task, or `**Workers:** human` in `PLAN.md` for a plan whose
people have job titles rather than the literal word. Such a task is *parked*: the fleet keeps
running every other ready task around it and stops only when the work left is yours.

---

## 11 · What is actually enforced

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
| A closed symptom cites its control test | ADVISORY | — |
| Instructions are preflighted against the artefact | ADVISORY | — |
| A task whose failure has two readings carries `## If it fails` | ADVISORY | — · frozen with the contract when present |
| A person's task is not dispatched to a model | **ENFORCED, ELSEWHERE** | `smokin` `route()` clause 0, on this file's `is_human_owned` |

---

## 12 · What this does not solve

~~**Nothing in this repository runs the gate.**~~ **Closed.** It used to be true, and it was the
largest open item in the method: `validate-plan.py` was documentation with an exit code, so every
ENFORCED row above was *enforceable*, not *enforced*. Three things now run it, and they fail
differently on purpose:

| | Runs | Skippable |
|---|---|---|
| [`.githooks/pre-commit`](.githooks/pre-commit) | every commit, on any plan directory the commit touches | yes — `GRILLIN_SKIP=1`, which **logs the skip**, because a skip nobody can see is indistinguishable from a pass |
| [`.github/workflows/gate.yml`](.github/workflows/gate.yml) | every push and PR | no |
| `templates/hooks.json.template` | agent session start | it is a reminder, not a gate |

> **In which repository.** The one that holds your **plans**, and that is not a product
> repository. Grillin runs *on* a plan, from outside it.
>
> **"Beside the code" is not good enough, and this is the correction that matters.** A
> plan directory at `docs/plans/` is tidy, is outside every source tree, and is still
> wrong: a plan is working material for the agent layer, not an artefact of the software
> being planned. It ships with nothing, it is read by nobody on the receiving team, and
> its presence gives a product repo a reason to know Grillin exists. Keep plans in their
> own repository, or under your agent's own directory — somewhere the product's build,
> CI and reviewers never see.
>
> Where plan and code genuinely must share a repo, the gate runs by hand or in *your*
> CI — never in that repo's commit hook. The test does not change: **a product repo has
> to build, test and ship with Grillin uninstalled.**
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
