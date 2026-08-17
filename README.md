<h1 align="center">Grillin'</h1>

<p align="center">
  <em>Put the plan in the fire before you put it in the sprint.</em>
</p>

<p align="center">
  <a href="QUICKSTART.md">Quickstart</a> ·
  <a href="#the-eleven-phases">Phases</a> ·
  <a href="OPERATING-THE-PLAN.md">Operating</a> ·
  <a href="#the-files">Files</a> ·
  <a href="templates/GRILL-CHECKLIST.md">Checklist</a> ·
  <a href="CASE-STUDY.md">Case study</a>
</p>

---

## What it is

**Grillin turns a vague ask into a plan an agent can actually execute — and then attacks
that plan until it stops lying to you.**

Most plans don't fail because the idea was wrong. They fail because they were written
against a **document** instead of a **system**, because nobody **counted** first, or
because the author never **attacked their own draft**.

Two things ship here:

- **A method.** Eleven phases and sixteen principles. It is prose; you can follow it with
  a text editor and nothing installed. Three of the phases produce no plan text at all —
  only corrections — and they are the ones that pay.
- **A gate.** One script that reads the plan you produced and fails if an orchestrator
  could not run it. 23 checks, zero dependencies, fail-closed. It validates its own config
  and is itself proven against a fixture with a known answer, because a validator that
  passes everything catches nothing.

What comes out is a directory: a `PLAN.md`, and a `tasks/<ID>/TASK.md` per task. Markdown,
nothing else. No library, no service, no dependency added to whatever you were planning.

## And a brother: Smokin

Grillin builds the plan and stops. Something has to *run* it, and for a long time that
something was a conversation — which dies, taking the state with it.

[**Smokin**](https://github.com/A-Pex97/smokin) is an idempotent tick that reads a plan
directory off disk, dispatches whatever is ready across any agent CLI, re-runs each task's
own done-command as an independent second opinion, and renders a surface a human can read.
It holds no state in memory, so nothing is lost when it stops.

> **Grillin answers *is this plan operable?*  Smokin answers *is it running, and where?***
>
> Grillin owns what a plan **declares**. Smokin owns what actually **happens**. Neither
> reaches into the other's half, and that boundary is enforced by a test that feeds both
> the same config files and requires them to agree.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/A-Pex97/grillin/main/install.sh -o grillin-install.sh \
  && sh grillin-install.sh
grillin <plan-dir> --run-gates
```

Then make it run on every commit, **in the repo that holds your plans**:

```bash
cd <your-plans-repo>
curl -fsSL https://raw.githubusercontent.com/A-Pex97/grillin/main/install-hooks.sh -o grillin-hooks.sh \
  && sh grillin-hooks.sh
```

> Not `curl … | sh`, and this was verified rather than assumed: against a private repo the
> pipe form prints `curl: (22)` and then **exits 0 having installed nothing**. The `&&`
> form fails properly and leaves the script on disk so you can read it first.

> ### Which repo — read this before you run it
>
> **Grillin runs *on* a plan, from outside it.** Put the gate on your `PATH`. Never put it
> in the build, the CI, or the commit path of the project you are planning changes to —
> that project must be able to build, test and ship with Grillin uninstalled.
>
> **Your plan directory is not part of the software you are planning.** Keep it in its own
> repository, or somewhere the application's build never sees.
>
> The test is one line: **if removing Grillin breaks someone's build, it was installed in
> the wrong place.**

## The one number

On the first job run end to end with every layer active, the gate caught **2** defects and
the human-and-agent readers caught **50**.

The layers catch disjoint classes — structure here, meaning there — so **a green gate is a
floor, and the floor is low.** That is why the most valuable check in the script does
nothing except refuse to pass a plan with nobody staffed to attack it, why `CONFIRMED`
means *exercised* and has to quote the invocation that produced it, and why there is a
second document about being inside a plan after it turns out to be wrong:
[`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md).

## The eleven phases

| # | Phase | Produces |
|---|---|---|
| 0 | Acknowledge, flag, stop | precedence declared |
| 1 | Inventory — count before you plan | counts, not impressions |
| 2 | Triage what the inventory dug up | a defect list, kept separate |
| 3 | **Grill the source docs against the running system** ⚑ | *corrections only* |
| 4 | Shape first — diagram before prose | a shape you can argue with |
| 5 | Decompose into owned tasks | one owner per file |
| 6 | Extract recurring context into skills | tacit knowledge, written down |
| 7 | Design isolation, then find the collision | the contended-file list |
| 8 | **Choose the execution substrate by measurement** ⚑ | a number, not a preference |
| 9 | **Verify the environment the plan assumes** ⚑ | *corrections only* |
| 10 | Ship the door with the building | an entry point |

⚑ = produces no plan text. These are the ones that pay.

**It scales down.** Running eleven phases on a one-hour change is its own anti-pattern.
Small change (1–3 tasks): run **0, 3, 9, 10**. Real project (10–25 tasks): run all eleven.
**Phases 3 and 9 never scale down** at any size — cheapest to run, most expensive to skip.

## Start here

**New to agentic coding? → [`WORKING-WITH-CLAUDE-CODE.md`](WORKING-WITH-CLAUDE-CODE.md).**
Habits before method. No Grillin required.

**Planning a real job? → [`QUICKSTART.md`](QUICKSTART.md).** Twenty minutes, six steps, in order.

## The files

| File | What it is |
|---|---|
| **[`QUICKSTART.md`](QUICKSTART.md)** | **Start here.** What to do, in order, with the times. |
| [`GRILLING-THE-PLAN.md`](GRILLING-THE-PLAN.md) | The reasoning. Eleven phases, sixteen principles, scaling, anti-patterns. |
| **[`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md)** | **The other half** — being inside a plan after it turns out to be wrong. Every rule traces to a defect a real run produced. |
| [`CASE-STUDY.md`](CASE-STUDY.md) | Two runs: the one that produced the method, and the one that broke it. |
| [`SCALING.json`](SCALING.json) | Machine-readable. Hand it to an agent as a planning brief. |
| [`index.html`](index.html) | Visual map. **Download and open locally** — GitHub renders it as source. |

**Examples** — copy one and change it:

| | |
|---|---|
| [`examples/one-task-plan/`](examples/one-task-plan/) | The smallest plan that is still a plan. |
| [`examples/research-first-plan/`](examples/research-first-plan/) | **When you don't have the facts yet.** The first task goes and gets them; the rest stay honestly unscoped. |
| [`examples/`](examples/) | A real first plan by a first-time user, and the gate report that fails it with 26 findings. |

**Templates** — of the eleven, seven assume a fleet of AI agents against a code repository
and two are specific to a terminal multiplexer. If that isn't you, use the method and the
gate and ignore those. These two need no fleet at all:

| | |
|---|---|
| [`templates/GRILL-CHECKLIST.md`](templates/GRILL-CHECKLIST.md) | **Print this.** Tick it against any plan before handing it over. |
| [`templates/BRIEF.md.template`](templates/BRIEF.md.template) | **One delegated task, no plan around it** — for the job you're present for, where what comes back is a report. |

The rest — [`TASK.md`](templates/TASK.md.template), [`_RULES.md`](templates/_RULES.md.template),
[`_ROSTER.md`](templates/_ROSTER.md.template), [`_WORKTREES.md`](templates/_WORKTREES.md.template),
[`_HERDR.md`](templates/_HERDR.md.template), [`_AWARENESS.md`](templates/_AWARENESS.md.template),
[`awareness.sh`](templates/awareness.sh.template), [`herdr-monitor.sh`](templates/herdr-monitor.sh.template),
[`hooks.json`](templates/hooks.json.template) — are the execution scaffolding.

**Scripts** — two are for your work, two are Grillin checking itself:

| script | run it on | answers |
|---|---|---|
| **[`scripts/validate-plan.py`](scripts/validate-plan.py)** | **your plan** | is this plan operable? |
| [`scripts/check-index.py`](scripts/check-index.py) | **your index + shards** | do an index and the files it points at still agree? |
| `scripts/check-drift.py` · `scripts/check-boundary.py` | *this repo only* | Grillin checking its own surfaces |

## What it needs

**python3**, stdlib only, no packages. The method itself needs nothing.

## Licence

[MIT](LICENSE).
