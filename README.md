<h1 align="center">Grillin'</h1>

<p align="center">
  <em>Put the plan in the fire before you put it in the sprint.</em>
</p>

<p align="center">
  <a href="#the-eleven-phases">Phases</a> ·
  <a href="#start-here">Files</a> ·
  <a href="#scaling-it-down">Scaling</a> ·
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
and cheap to catch. Three of the phases produce no plan text at all — they only
produce corrections — and they are the highest-value phases in the method.

It was extracted from a single real planning session that turned a vague redesign
brief into a 29-file executable plan, and caught roughly **30 errors** along the
way — including several in its own text.

Nothing here is tied to the codebase it came from. It is a method, not a
framework: no install, no dependencies, no lock-in.

---

## Start here

| File | What it is |
|---|---|
| **[`index.html`](index.html)** | **The visual map.** Open in any browser. Interactive — pick a project size and watch which phases turn on. |
| [`GRILLING-THE-PLAN.md`](GRILLING-THE-PLAN.md) | The method. Eleven phases, sixteen principles, the scaling model, anti-patterns. |
| [`CASE-STUDY.md`](CASE-STUDY.md) | Where it came from — the arc in order, including the steps that went wrong. |
| [`SCALING.json`](SCALING.json) | Machine-readable. Feed it to tooling, or hand it to an agent as a planning brief. |
| [`templates/GRILL-CHECKLIST.md`](templates/GRILL-CHECKLIST.md) | **Print this.** Tick it against any plan before handing it over. |
| [`templates/TASK.md.template`](templates/TASK.md.template) | Starting point for a task contract. |
| [`templates/_RULES.md.template`](templates/_RULES.md.template) | Starting point for the shared agent contract. |
| [`templates/_HERDR.md.template`](templates/_HERDR.md.template) | Rules for the **secondary** substrate — named agents in a managed terminal session. |
| [`templates/_AWARENESS.md.template`](templates/_AWARENESS.md.template) | Reminders, not gates — putting the frame back when a worker has narrowed onto one task. |
| [`templates/awareness.sh.template`](templates/awareness.sh.template) | The state reporter the reminders call. Never touches the plan; always exits 0. |

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
