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

## Why it's called that

You grill over high heat, fast, standing right there, and you find out in minutes
whether the thing holds together. You smoke low and slow for hours, walk away, and
come back to check the temperature — because the clock lied to you and the meat
didn't.

That is the whole pair.

**Grillin'** puts your plan over high heat *before* anyone builds anything, and you
stand there while it burns off whatever was never true. **Smokin'** runs the thing
for hours without you watching, and when it says it's done you check the temperature
instead of believing it.

Right. That's the last of the barbecue. Here's what they actually do.

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

## What a plan actually looks like

Two files and a folder. That's the whole artefact.

```
my-plan/
├── PLAN.md                 ← the entry point: size, task table, the shaping answers
└── tasks/
    ├── _ROSTER.md          ← which persona runs on which model, and why
    ├── T1/TASK.md          ← one contract per task
    ├── T2/TASK.md
    └── T3/TASK.md
```

**`PLAN.md`** — the door. Anyone starting cold reads this and knows what to pick up:

```markdown
# Make the log parser fast again

**Size:** XS

| ID | Task | Owner | Blocked by |
|---|---|---|---|
| T1 | find out why it is slow — timeboxed | you | — |
| T2 | fix the ranked cause T1 names | you | T1 |
| T3 | prove the fix, against T1's numbers | you | T2 |
```

**`tasks/T1/TASK.md`** — a contract, not a description. The part that matters is
`## Done means`: **a command someone else can run**, which is false before the work and
true after.

````markdown
# T1 — find out why it is slow

**Status:** NOT STARTED
**Owner:** you
**Agent:** `implementer` · **Model:** `claude-sonnet-5` · **Effort:** high
**Blocked by:** — · **Blocks:** T2
**Kind:** research · **Timebox:** 90 minutes

## What you own
`tasks/T1/`

## Steps
1. One question, and it is this one: which operation accounts for most of the
   wall-clock time, on a run you took yourself?
2. Take a measurement before you form an opinion. Record the raw numbers.
3. At 90 minutes, stop and write whatever you have. "Could not establish X"
   is a reportable result, not a failure.

## Done means
```
test -s tasks/T1/FINDINGS.md
```

## Do NOT
- Do NOT fix anything. If the cause is obvious and the fix is one line, it is
  still T2's line.
- Do NOT ship whatever you built to answer the question. That is evidence,
  not the deliverable.
````

Then you run the gate on it:

```bash
$ grillin my-plan --run-gates
```

When something is wrong it names the task, the file and the reason — never "invalid plan":

```
FAIL — owner               T2 names no owner — an orchestrator cannot dispatch it  tasks/T2/TASK.md:1
FAIL — done-checkable      T3's done criterion is prose, not a runnable command
FAIL — paths-disjoint      T2 and T3 can run at the same time and both own 'src/api/'
FAIL — research-task       T1 is a research task and declares no **Timebox:**
```

And when it passes, it tells you what it did **not** check — because a green gate is a
floor, and the floor is low:

```
RESULT: PASS — the plan is structurally operable.
        Not checked: whether it is CORRECT. At 3 task(s) this plan is below the
        4-task floor, so no reader is required — you are the reader.
```

Copy [`examples/one-task-plan/`](examples/one-task-plan/) and change two files, or
[`examples/research-first-plan/`](examples/research-first-plan/) when you don't have the
facts yet. Both pass the gate as shipped, so you can break them on purpose and watch it
complain.

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

## Contributing

One maintainer, issues read in batches, and one rule that matters: **a change that adds a
rule must name the defect it came from.** [`CONTRIBUTING.md`](CONTRIBUTING.md) says what is
wanted, what gets declined and why, and what a check has to prove before it ships.

## What it needs

**python3**, stdlib only, no packages. The method itself needs nothing.

## Licence

**The method is free. The tools are free for noncommercial use.**

| | Licence | What it means |
|---|---|---|
| **The method** — every `.md`, the examples, [`SCALING.json`](SCALING.json), the templates | [CC BY 4.0](LICENSE-DOCS) | Use it anywhere, including commercially and inside a product. Change it. The one condition is **attribution**. |
| **The tools** — [`scripts/`](scripts/), the hooks, the installers, the tests | [PolyForm Noncommercial 1.0.0](LICENSE) | Free for personal, academic, research and non-profit use. **Commercial use needs a licence** — open an issue. |

The rule where a file isn't listed: **if it executes, it's PolyForm. If you read it, it's CC BY.**

### "Is my use commercial?" — the short answer

**If you are one person learning, building your own thing, or trying this out: it's free, and
it stays free. Stop reading here.**

Most of what people worry about isn't restricted at all. **The method is CC BY** — a company
can read it, follow all eleven phases, copy the templates into their internal wiki and ship
software with it, commercially, forever, for nothing. The only condition is saying where it
came from. PolyForm covers the **scripts** and nothing else.

| You are | The tools |
|---|---|
| An individual — hobby, side project, learning, your own product | **Free.** |
| A student, academic, public research body, non-profit, government | **Free**, explicitly, whatever your funding — PolyForm says so in its own text |
| A developer at a company, evaluating this to see if it's any good | **Free.** Trying it is not deploying it |
| A company where this is part of how you ship | **Ask me.** Open an issue titled `licence` |
| A consultancy using it on client work | **Ask me.** |
| Anyone forking it, changing it, teaching it, writing about it | **Free**, noncommercially, and please do |

**Where the line actually is:** not your job title, and not whether your laptop has a company
sticker on it. It's whether an organisation is the beneficiary of the tooling. One engineer
running `smokin verify` on their own branch is an individual. A team standardising on it in
CI is an organisation.

**If you're unsure, you're free until I answer.** Open the issue and keep working — I am one
person and I would rather you used it than waited on me. I have never refused anyone, and the
answer for small teams is going to be yes.

**And if the licence is genuinely the blocker** for something you want to do, say so in the
issue. That's useful information about whether this licence was the right call, and I would
rather hear it than have you quietly walk away.

The split is deliberate. The reasoning is the valuable part and reasoning doesn't stay put —
people who had never read these documents re-invented pieces of them unprompted, which is the
point rather than a leak. A method that only works where it's installed is not a method. So the
method is free and the condition is credit. The tools are the part someone could ship inside a
product, and that's a conversation worth having first.
