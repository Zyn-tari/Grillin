<h1 align="center">Grillin'</h1>

<p align="center">
  <em>Put the plan in the fire before you put it in the sprint.</em>
</p>

<p align="center">
  <a href="QUICKSTART.md">Quickstart</a> ·
  <a href="#the-eleven-phases">Phases</a> ·
  <a href="OPERATING-THE-PLAN.md">Operating</a> ·
  <a href="#start-here">Files</a> ·
  <a href="templates/GRILL-CHECKLIST.md">Checklist</a> ·
  <a href="CASE-STUDY.md">Case study</a>
</p>

---

Most plans don't fail because the idea was wrong. They fail for one of three
reasons:

- they were written against a **document** instead of a **system**
- nobody **counted** first
- the author never **attacked their own draft**

**Grillin'** is eleven phases that make those three failures expensive to commit
and cheap to catch — plus one script that reads the plan you produced and fails
if an orchestrator could not run it:

```bash
curl -fsSL https://raw.githubusercontent.com/A-Pex97/grillin/main/install.sh -o grillin-install.sh \
  && sh grillin-install.sh
grillin <plan-dir> --run-gates
```

> **Why not `curl … | sh`.** Verified, not assumed: against a private repo the pipe
> form emits `curl: (22) 404` and then **exits 0 having installed nothing** — `curl -f`
> writes an empty body, `sh` runs an empty script, and the pipeline reports success.
> The `&&` form above exits **22** instead, and leaves the script on disk so you can
> read it before running it. A silent no-op that reports success is the exact failure
> this repository has a whole document about.

Then make it run on every commit, **in the repo that holds your plans**:

```bash
cd <your-plans-repo>
curl -fsSL https://raw.githubusercontent.com/A-Pex97/grillin/main/install-hooks.sh -o grillin-hooks.sh \
  && sh grillin-hooks.sh
```

> ### Which repo — read this before you run it
>
> **Grillin runs *on* a plan, from outside it.** Put the gate on your `PATH`; never
> put it in the build, the CI, or the commit path of the project you are planning
> changes to — **that project must be able to build, test and ship with Grillin
> uninstalled.**
>
> **Your plan directory is not part of the software you are planning.** Keep it in
> its own repository, or somewhere the application's build never sees. If plan and
> code must share a repo, the gate still runs by hand or in your own CI — not in
> that repo's commit hook.
>
> The test is one line: **if removing Grillin breaks someone's build, it was
> installed in the wrong place.**

Three of the phases produce no plan text at all — they only produce corrections — and they are the
highest-value phases in the method.

It was extracted from a single real planning session that turned a vague redesign
brief into a 29-file executable plan, and caught roughly **30 errors** along the
way — including several in its own text.

Nothing here is tied to the codebase it came from.

**And there is a brother.** Grillin builds the plan and stops — something else has to run it, and
for a long time that something else was a conversation, which dies. [**Smokin**](https://github.com/A-Pex97/smokin)
is an idempotent tick that reads a plan directory off disk, dispatches what is ready across any
agent CLI, re-runs each task's own done-command as a second hand, and renders a surface a human can
read. Grillin answers *is this plan operable?*; Smokin answers *is it running, and where is it?*

**And one number, because it should change how you use this.** On the first job run
end to end with every layer active, the gate caught **2** defects and the human-and-agent
readers caught **50**. The two layers catch disjoint classes — structure here, meaning
there — so a green gate is a floor, and the floor is low. That is why the most valuable
check in the script does nothing except refuse to pass a plan with **nobody staffed to
attack it**, why `CONFIRMED` now means *exercised* and must quote the invocation that
produced it, and why there is a second document about being inside a plan after it turns
out to be wrong: [`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md).

**What it needs.** The method itself needs nothing — it is prose and you can follow
it with a text editor. The gate needs **python3** (stdlib only, no packages). The
templates in `templates/` are a different matter: six of the seven assume you are
running **a fleet of AI agents against a code repository**, and one is specific to a
named terminal multiplexer. If that is not your situation, use the method and the
gate and ignore those — they are the execution scaffolding, not the planning method.

---

### Which of these are for you

Three scripts ship here and only two are usable on your own work. An operator
who had just built an index-plus-shards changelog found `check-drift.py`,
correctly identified that they had made a drift generator, and could not point
it at anything — it is hardcoded to this repo. That was not their mistake.

| script | run it on | what it answers |
|---|---|---|
| [`scripts/validate-plan.py`](scripts/validate-plan.py) | **your plan** | is this plan operable? |
| [`scripts/check-index.py`](scripts/check-index.py) | **your index + shards** | do an index and the files it points at still agree? |
| `scripts/check-drift.py` | *this repo only* | Grillin checking its own surfaces |
| `scripts/check-boundary.py` | *this repo only* | Grillin checking its own entry points |

`check-index.py` exists because splitting a long file into an index plus shards
is the right move and creates a second place holding the same facts. It checks
that every linked shard exists, that none is orphaned, that the index's name for
a shard appears **verbatim** as a heading inside it — the pair a status hook
keys on, and the one most likely to be tidied on one side only — and that any
stated count still holds.


## Start here

**New to Claude Code itself? → [`WORKING-WITH-CLAUDE-CODE.md`](WORKING-WITH-CLAUDE-CODE.md).**
Habits before method — what actually goes wrong, and the six habits that fix it. No Grillin required.

**Ready to plan a real job? → [`QUICKSTART.md`](QUICKSTART.md).** Twenty minutes, six steps, in order.

After that, in roughly the order you need them:

| File | What it is |
|---|---|
| [`WORKING-WITH-CLAUDE-CODE.md`](WORKING-WITH-CLAUDE-CODE.md) | **Before any of this.** For someone new to Claude Code who wants to work better with it. Assumes you can program; assumes nothing about agents. |
| **[`QUICKSTART.md`](QUICKSTART.md)** | **Start here.** What to actually do, in order, with the times. |
| [`GRILLING-THE-PLAN.md`](GRILLING-THE-PLAN.md) | The reasoning behind it. Eleven phases, sixteen principles, the scaling model, anti-patterns. |
| **[`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md)** | **The other half.** Being inside a plan after it turns out to be wrong — re-entry, amendments, frozen contracts, validating the instrument, and how to build a reader. Every rule traces to a defect a real run produced. |
| [`examples/one-task-plan/`](examples/one-task-plan/) | **The smallest plan that is still a plan.** One task. Copy it when the alternative is a four-line shell loop you will not keep. |
| **[`examples/`](examples/)** | **A real first plan** by a first-time user, and the gate report that fails it with 26 findings. |
| [`CASE-STUDY.md`](CASE-STUDY.md) | **Two runs.** The one that produced the method, and the one that broke it — where the 2-versus-50 number comes from. |
| [`SCALING.json`](SCALING.json) | Machine-readable. Feed it to tooling, or hand it to an agent as a planning brief. |
| [`templates/GRILL-CHECKLIST.md`](templates/GRILL-CHECKLIST.md) | **Print this.** Tick it against any plan before handing it over. |
| [`templates/TASK.md.template`](templates/TASK.md.template) | Starting point for a task contract. Carries the `Reader:` and `Delivered:` lines the gate checks. |
| [`templates/_RULES.md.template`](templates/_RULES.md.template) | Starting point for the shared agent contract. |
| [`templates/_ROSTER.md.template`](templates/_ROSTER.md.template) | **Which model runs which persona, at what effort, and why.** Real model identifiers, never tier words; effort never below `high`. |
| [`templates/herdr-monitor.sh.template`](templates/herdr-monitor.sh.template) | Fleet state on disk — `state.json` plus a sequence-numbered transition log. Pings on change, and a cleared orchestrator resumes from a sequence number. |
| [`templates/_HERDR.md.template`](templates/_HERDR.md.template) | Rules for the **secondary** substrate — named agents in a managed terminal session. |
| [`templates/_AWARENESS.md.template`](templates/_AWARENESS.md.template) | Reminders, not gates — putting the frame back when a worker has narrowed onto one task. |
| [`templates/awareness.sh.template`](templates/awareness.sh.template) | The state reporter the reminders call. Never touches the plan; always exits 0. |
| [`index.html`](index.html) | Visual map of the phases. **Download and open locally** — GitHub renders it as source. |
| [`install.sh`](install.sh) · [`install-hooks.sh`](install-hooks.sh) | One-line install, and the hook that makes the gate run on every commit. |
| [`scripts/check-drift.py`](scripts/check-drift.py) | The surfaces publish the same facts four times. This fails when they disagree — it has already fired twice for real. |
| **[`scripts/validate-plan.py`](scripts/validate-plan.py)** | **The gate.** Sixteen checks. Zero deps, fail-closed, validates its own config, and proven against [`examples/minimal-passing-plan`](examples/minimal-passing-plan) — a fixture with a known answer, because the gate is an instrument too. |
| [`templates/hooks.json.template`](templates/hooks.json.template) | The wiring. Start with the pre-compaction hook — the rest can wait. |
| [`templates/_WORKTREES.md.template`](templates/_WORKTREES.md.template) | Phase 7's artefact — waves, worktrees, and the contended-file list with owners. |

---

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

---

## Scaling it down

The method is not all-or-nothing. Most work is small, and running eleven phases
on a one-hour change is its own anti-pattern.

**Small change — 1–3 tasks, ~1 hour:** run phases **0, 3, 9, 10**. Declare
precedence, grill the spec against the running system, verify the environment,
ship an entry point. Skip the rest.

**Real project — 10–25 tasks, 1–2 days:** run all eleven. Recon fan-out, task
contracts, skills, worktrees, an integrator, measured tool choice.

**At any size:** phases **3 and 9 never scale down.** They are the cheapest
phases and they catch the most expensive errors.

---

## The parts most people skip

**The contended-file list.** Separate workspaces are the easy half of isolation.
The hard half is asking *which files do many tasks want?* — because several
branches editing one file is several conflicts resolved by whoever merges last.
That is the same collision, relocated to merge time. Every project has these
files; most plans discover them at merge.

**Grilling your own artefact.** Your plan is a document, and documents drift. In
the source session, checking the plan's own assumptions found wrong paths, a file
reported missing that was merely unreadable, and an assumed network route that did
not exist — all written by the author who had spent the session warning about
precisely that.

**Verifying before defending.** When challenged, check first. In the source
session a challenge was factually wrong — and checking revealed a real defect
underneath it, in a different place entirely. Defending would have missed it;
conceding would have fixed the wrong thing.

**Measuring the substrate instead of assuming it.** Phase 8 says pick the
execution substrate by measurement, and most methods quietly assume the first of
two. **Script-and-collect** is cheap and deterministic, and blind in the middle —
a worker stuck on an approval prompt looks exactly like one that is thinking,
until it times out. **A managed terminal session** costs a pane per agent and
buys two things the other cannot: `blocked` becomes an observable state rather
than a timeout, and the fleet outlives the conversation that started it, so an
orchestrator that loses context recovers the roster with one query. Neither wins
universally. Measure both on the same real fan-out, and measure
*time-to-detect-a-stall*, not only wall-clock.

**Reminding without nagging.** A worker deep in task 14 has not disobeyed the
plan, it has lost sight of it — its context is full of task 14. Blocking a tool
call does not restore that shape. Putting the frame back does, but only if the
reminder is *computed from current state*; static text becomes wallpaper by its
third firing and teaches the agent that injected text is skippable. The highest-value
moment to fire one is immediately **before a compaction** — the literal instant of
forgetting, and the only point where injected state lands *inside* the summary
instead of being what the summary drops.

**Keeping the plan true while it runs.** A plan is written once and then reality
moves — a task splits, a decision closes, an assumption proves false. The
tempting place to record that is the status file, because that is the file you
are already updating. It is the wrong file: the status file is read by whoever is
*watching*, and the plan is read by whoever is *working* — including a worker that
just lost its context. Deviations amend the plan itself; the changelog is a
receipt for that fix, never a substitute for it.

---

## Why the failures are still in it

[`CASE-STUDY.md`](CASE-STUDY.md) keeps the wrong turns in on purpose. A method
that only records what went right is not a method, it is a highlight reel. The
phases are **descriptive, not invented** — each one is a thing that actually
happened, in the order it happened, with the correction it produced.

---

## Using it with an agent

[`SCALING.json`](SCALING.json) is the whole method as structured data —
`phases`, `scaling`, `neverScaleDown`, `principles`, `antiPatterns`,
`taskContract`. Hand it to a coding agent as a planning brief, or drive tooling
from it.

The two templates pair with it: [`_RULES.md.template`](templates/_RULES.md.template)
is the shared contract every agent gets, and [`TASK.md.template`](templates/TASK.md.template)
is the per-task contract that names the owner, the files, and the definition of
done.

---

## License

[MIT](LICENSE) — © 2026 A-Pex97.

Copy the templates into your own projects, private or otherwise. Keep the
copyright notice; that is the whole obligation.

<sub>Derived from one planning session, 2026-07-31.</sub>
