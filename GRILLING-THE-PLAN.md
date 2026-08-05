# Grilling the Plan

A method for turning a vague ask into an executable plan that survives contact with reality —
by attacking every claim in it, including your own, before anyone builds anything.

Derived from a real planning session ([`CASE-STUDY.md`](CASE-STUDY.md)). Project-agnostic.
Scales from a one-afternoon change to a multi-month rebuild.

---

## The premise

Most plans fail for one of three reasons, and none of them is a bad idea:

1. **They were written against a document instead of a system.** The document was true once.
2. **Nobody counted first.** Scope was estimated from impression.
3. **The author never attacked their own draft.** Everything got reviewed except the plan.

Grilling the Plan is eleven phases that make those three failures expensive to commit and cheap
to catch.

**One rule above all the others:**

> **Adversarial effort spent before building is worth many times the same effort spent after.**
> Three of the eleven phases produce no plan text at all. They only produce corrections. They
> are the highest-value phases.

---

## The precedence ladder — declare it before phase 1

Every project has sources that disagree. Decide the order **now**, write it at the top of the
plan, and say out loud when two sources conflict.

A sane default:

```
1. Operating invariants        (your rules file — how work is run)
2. THE RUNNING SYSTEM          (live code, live config, live data — beats every document)
3. Durable project memory      (decisions already closed)
4. The current plan
5. Handoff / spec documents    (written against a snapshot; assume drift)
```

**Specs sit at the bottom on purpose.** They are the most confident-sounding and the most
likely to be stale.

---

## The eleven phases

### Phase 0 — Acknowledge, flag, stop

Restate the ask in your own words. Name what you still need. Flag anything that would **change
the shape** of the plan. Then stop.

Do not start work at the acknowledgement. The restatement is the cheapest place to find out you
heard it differently.

**Output:** a paragraph, two or three flags, and the five answers below.

#### What kind of plan does this need? — five questions

The scaling table sizes the work. It does not tell you what *kind* of work it is, and that is
the other half. Answer these before phase 1; each switches something on or off, and the answers go at the
top of the plan so the next reader can disagree with them. Size is the sixth axis and the
scaling table below handles it.

The questions are about **properties of the work, not its domain**. A documentation job and a
migration can have identical answers. "Is it software?" is the wrong question and produces the
wrong plan.

| # | Question | If YES | If NO |
|---|---|---|---|
| **1** | Does the thing already exist in some inspectable form — a running system, a live document, a current state? | Rung 2 of the precedence ladder is **that thing**. Phase 3 grills every claim against it. | There is no rung 2. Phase 3 still runs, but it grills your sources **against each other and against the constraints** — and you say so, because a ladder with a hole in it is worse than a ladder you know is short. |
| **2** | Will more than one worker act on this concurrently? | Phases 5 and 7 in full. Ownership and the contended-artefact list are load-bearing. | Phase 7 off — nothing is contended when one worker acts serially. Phase 5 stays **reduced**: folder, owner, status, done-command. Those four are for resumability, not coordination, and a solo worker still forgets. |
| **3** | Are the workers AI agents? | Phases 6 and 8 apply, and so do the templates in `templates/`. | Skip 6 and 8, and ignore the templates entirely — they are scaffolding for a fleet. The phases still work; a person reads the plan instead. |
| **4** | Does "done" produce something that runs, deploys, or is otherwise executed? | Verification order matters: build → promote → restart → gate. Get it wrong and you gate the old artefact. | No ordering to trap you. **"Done" is still a command someone can re-run** — a file test, a grep, a count. Not executable is not the same as not checkable. |
| **5** | Is any step irreversible, or expensive to undo? | Two adversarial passes on those steps, different lenses. Explicit stop-and-ask nodes where a human must decide. | One pass. Escalate on decisions only. |

**Write the answers down.** Five lines at the top of the plan, each naming what it turned on or
off. That table is the thing a reader argues with when they think you scoped it wrong — and it
is the difference between a phase you *decided* not to run and one you forgot.

---

### Phase 1 — Inventory: count before you plan

Fan out **read-only** workers to enumerate what exists. Partition **by file ownership** so none
overlap. Each writes one document to a shared frozen folder.

- Cite `file:line` for every claim.
- **Give counts.** "Several components fetch their own data" is useless; "21 of 49" sizes work.
- Label **CONFIRMED** (you checked it yourself) vs **SUSPECTED** (you inferred it, or were
  told). One vocabulary, used everywhere in this method — an inventory, a finding and a
  claim in a report all take the same two labels, so nobody has to translate.
- End each with **"what I did not verify."**
- Use your cheapest capable model. Inventory is not reasoning work.

This folder is written once and **frozen**. Everything downstream reads it instead of
re-deriving it — that is where the speed comes from.

**Output:** an inventory folder — one document per worker, every claim cited, every category
carrying a number, each labelled CONFIRMED or SUSPECTED, each ending in "what I did not verify".

---

### Phase 2 — Triage what the inventory dug up

Recon always finds defects. Sort them, never absorb them:

| Bucket | Meaning |
|---|---|
| **A — fix during the work** | in files being touched anyway; no semantics change |
| **B — needs a human decision** | product or safety semantics; you do not decide these |
| **C — real but out of scope** | record it, do not schedule it |

Label each **CONFIRMED** or **SUSPECTED**. Spot-check the headline items yourself.

**Why:** without triage a discovery either silently expands scope or gets lost. This makes scope
creep a visible decision instead of a side effect.

**Output:** a triaged defect register — one row per defect: what it is, `file:line`, bucket
A/B/C, and CONFIRMED or SUSPECTED.

---

### Phase 3 — Grill the source documents against the running system ⚑

**The highest-value phase. It produces no plan text.**

Take every load-bearing claim in every spec and check it against the top of the precedence
ladder. Hunt specifically for:

- **Things asserted to exist that do not.** Specs describe intended systems as though built.
- **Staleness.** When was it written? What shipped since? Check its own footnotes — a document
  that cites "the last five rounds" while you are on six is telling you its own age.
- **Cross-document contradiction.** Two specs disagreeing is information. One of them
  disagreeing with the running system is a decision.
- **Unflagged assertions.** The dangerous claim is stated as settled fact in a heading, with no
  caveat, where a reader who starts there never learns it is contested.

Write the contradictions down. **Never resolve one silently** — surface it, state which source
wins by the ladder, and say the ladder is why.

**Output:** a contradictions register — one row per contradiction: the claim, where it was
asserted, what the running system actually says, which source wins, and the ladder rule that
decides it. Expect it to resize the work.

---

### Phase 4 — Shape first: diagram before prose

Produce a **one-screen** dependency graph before any task text. Type every node:

`ASK` (a human decides) · `BUILD` · `REFACTOR` · `RECONSIDER` (decide before building) ·
`VERIFY` · `LOOP`

Get it approved. A wrong diagram costs a minute; the prose it authorises costs hours.

Make `RECONSIDER` nodes real. A node whose legitimate output is *"don't build this"* is a node
doing its job.

**Output:** an approved graph.

**Record what you turned off.** By now two things have switched phases off: the size table, and
the five shaping questions in phase 0, plus the size question. Keep the combined result as one table in the plan —
*phase · on / off / reduced · which answer or size decided it*. The method's whole objection is
to skipping **silently**; a skip with its reason beside it is a decision, and the next reader can
disagree with it.

---

### Phase 5 — Decompose into owned tasks

**One folder per task. Always, and regardless of how many tasks there are** — including at
sizes where the *rest* of this phase is switched off. The scaling table reduces what a `TASK.md`
must contain; it never removes the folder, the owner, the status line or the done-command. Those
four are what an orchestrator needs to dispatch and resume, and a task without them is not a
smaller task, it is an unrunnable one. Three tasks or forty,
the structure does not change — a flat pile of task files is the thing this rule exists to prevent,
because it is where ownership, outputs and status stop being locatable.

```
tasks/
  <ID>/                 one directory per task, named for the id
    TASK.md             the contract — persona, owned files, steps, loop, done, do-NOTs
    FINDINGS.md         what it learned, cited                      (written by the agent)
    CHANGES.md          did / why / risk, if anything changed       (written by the agent)
    QUESTIONS.md        if blocked or diverged                      (written by the agent)
    <FRAGMENT>.ext      edits to files it does not own              (written by the agent)
```

**A task born mid-run gets its folder before its first artefact.** This is where the rule actually
breaks. In the first pilot all twenty-six *planned* folders survived intact — nothing renamed,
nothing merged — while the only loose files at the plan root belonged to tasks created under
pressure mid-wave that never got a directory. The discipline holds for what you decompose up front
and fails for what reality adds later, so `mkdir` is the first act of creating a task, not a
tidying step afterwards.

**That folder is what the working agent receives.** Not a prompt with the task pasted into it —
the directory itself. Everything the agent needs to start is inside it, and everything it produces
goes back into it. The folder is both the inbox and the outbox.

Three things follow from that, and they are the reason it is a structural rule rather than a
convention:

- **Self-contained.** If a fact is needed to do the task and is not in the folder or cited from
  the frozen inventory, the briefing failed. There is no ambient context to fall back on.
- **Resumable.** A worker that lost its context re-reads one directory and has the contract, its
  own findings so far, and its status line. This is principle 14 made concrete: the task survives
  the conversation because the task was never in the conversation.
- **Addressable.** Status, progress and ownership are all derivable by globbing `tasks/*/TASK.md`
  — which is exactly what the state reporter does. Break the layout and the awareness layer goes
  blind.

Each `TASK.md` is a **contract**, not a description:

| Element | Why |
|---|---|
| **Persona** | a professional identity with a habit of mind — it visibly changes what gets noticed |
| **Exactly the files it owns** | one owner per file, always |
| **The evidence already gathered** | cite the inventory sections; it reads instead of re-deriving |
| **Steps** | specific, ordered, referencing real paths |
| **A loop** | exit condition **and** an iteration cap; a fix is confirmed by someone who did not make it |
| **Done means** | evidence someone else can check — never "it works" |
| **An explicit do-NOT list** | including the universal one |
| **Output contract** | what it writes and where |

**Own by file, not by task.** When several jobs touch one file, that file gets one owner who
receives all of them. File contention — not compute — is what limits parallelism.

**Every loop has a cap, and hitting it is a stop-and-report, never a silent partial.**

**Output:** N task contracts.

---

### Phase 6 — Extract recurring context into skills

When the same warning appears in five task files, it belongs in a skill.

Group by **category of work**, not by task: money/safety-critical paths · schema and migrations ·
the API contract · the design system · adversarial review · deploy and verification · read-only
recon.

Each skill carries the project's **scar tissue** — the bugs that actually shipped, the
conventions, the traps — not generic best practice. Generic advice is already in the model.

Each task declares which skills to load **before its first tool call**. Context loaded after work
begins has already missed the decisions it existed to inform.

**Loading once is not enough, because context decays.** A worker forty tool calls into task 14 has
a context full of task 14; the plan around it has been crowded out or summarised away. That is not
disobedience, it is **attentional narrowing** — the work is being done correctly and the shape it
sits in is gone.

The fix is not to load more up front. It is to put the frame back at the moments it is most likely
to have gone: at a session start, when a worker finishes, and — most valuably — **immediately
before a compaction**, which is the literal instant of forgetting and the only moment where
injected state ends up *inside* the summary rather than being what the summary drops.

One rule governs whether any of that lands: **a reminder that repeats is wallpaper; a reminder
that reports is news.** Re-pasting the rules is ignored by the third firing. A line computed from
disk — statuses, commits, amendments — differs every time and keeps being read.

Rules for this: [`templates/_AWARENESS.md`](templates/_AWARENESS.md.template), with a starting
implementation in [`templates/awareness.sh`](templates/awareness.sh.template).

**Skills accrete during the run, not only before it.** The scar tissue that matters most is the
incident you just had. In the pilot a live mail incident became a permanent never-rule the same
day — folded into the skills and the memory, not filed in a lessons document. Treat the skill set
as something the work edits, on the same standing loop that keeps the plan true.

**Output:** a small set of skills; one line per task referencing them; a state reporter wired to
the boundaries.

---

### Phase 7 — Design isolation, then find the collision

Separate directories are the easy half.

The hard half: **list the files that many tasks want.** There are always some — a build script,
a schema file, a registry, a route table, a shared client. Several branches editing one file is
several conflicts resolved by whoever merges last. That is the same collision, relocated to
merge time.

**The fix:** contended files get a **single owner**. Everyone else emits a *fragment* into their
own folder — the exact lines to add, with a note on where. One **integrator** applies fragments
in merge order and writes no feature code.

Also:
- Workers work in isolated copies; **the deployed/live checkout is never a workspace.**
- **Read anywhere; write only in your worktree and your task folder.**
- A worker that spots a defect it does not own **records it and moves on.** Drive-by fixes give a
  branch changes nobody reviewed.
- Branches carry their own findings and change-index, so a revert months later is still legible.

**Output:** an isolation model, a contended-file table, an integrator role.

---

### Phase 8 — Choose the execution substrate by measurement ⚑

Do not pick the tool that *looks* structured. Measure.

- Time a real fan-out on each candidate. Record **effective parallelism**, not the advertised
  cap.
- Check what actually binds: CPU? memory? API latency? If load stays low while concurrency
  stays capped, the limit is admission control, not the machine — and more hardware buys
  nothing.
- **Name what a limit governs before it shapes the plan.** A real number scoped to the wrong
  thing looks authoritative and silently shrinks the work.
- If a constraint is cheap to measure, measure it instead of quoting it.
- **Then check the instrument.** A number from a tool nobody has verified is a quote with extra
  steps. The pilot's blur-performance tool over-counted, and the over-count was found only because
  someone questioned the tool rather than the result.

Then match substrate to shape: wide independent fan-out and long-running isolated work have
different answers, and *deterministic cross-agent control flow* is the only thing that justifies
paying a concurrency penalty.

**Write the choice — and the rejected alternative — into the plan**, because the next operator
will otherwise reach for the structured-looking tool.

#### Two substrates worth measuring against each other

Most methods assume the first of these. The second is worth a real trial before you rule it out.

**Programmatic fan-out** — a script spawns workers, collects returns, and the orchestrator never
sees the middle. Cheap, deterministic control flow, trivially repeatable. Its cost is *blindness*:
a worker stuck on an approval prompt is indistinguishable from a worker thinking, until it times
out. You cannot intervene in a running worker, only wait for it.

**A managed terminal session** — real panes, named agents, queryable lifecycle
(`working` / `idle` / `blocked` / `done` / `unknown`). Costs a pane per agent and needs the
orchestration written rather than scripted. It buys two things the first cannot: **`blocked` is
observable**, so a stalled agent is a fact rather than a timeout; and **the fleet outlives the
conversation**, so an orchestrator that loses context recovers the roster with one query instead
of losing the fleet.

What to measure, since neither answer is universal:

| Measure | Why it decides |
|---|---|
| Effective parallelism, both substrates | the advertised cap is not the number |
| Wall-clock on the same real fan-out | not a synthetic benchmark |
| Time-to-detect a stalled worker | the second substrate's core claim |
| Orchestrator tokens spent watching | visibility is not free |
| Recovery cost after a context loss | pairs with principles 13 and 14 |

Rules for the second substrate, if you take it: [`templates/_HERDR.md`](templates/_HERDR.md.template).

**Output:** tool per phase, with measurements.

---

### Phase 9 — Verify the environment the plan assumes ⚑

Before anyone executes, check that the world the plan describes exists:

- Every path the plan names — does it resolve, and in which repository?
- Every script — present? readable? **A failed read is not proof of absence.** Check permissions
  and ownership before declaring something missing.
- Network topology, credentials, remotes, quotas — assumed or verified?
- Which machine actually holds the database, the web server, the test harness?

In the source session this phase found **four errors in the plan's own text**, written by the
author who had spent the session warning about exactly this.

**Output:** corrections to the plan, applied at source.

---

### Phase 10 — Ship the door with the building

- **One entry point** with an explicit read order.
- **A paste-ready kickoff prompt.**
- **Persistent memory updated** so a cold start lands on this plan, not on last month's work.
- **A status surface** the requester can read without asking — published, not narrated. The
  cheapest way to keep one true is to derive it from the status lines principle 13 already
  requires, on the write that updates them: that write is the only *work-shaped* event a harness
  offers, and it costs the worker nothing because the surface is never shown to it.
- **Hand-off items you cannot do yourself**, stated explicitly rather than silently skipped.
- **A warm restart, not just a cold one.** The entry point tells a fresh worker what the plan
  *is*; it must also let one that is halfway through establish *where it got to*. See
  [Keeping the plan true while it runs](#keeping-the-plan-true-while-it-runs).

**Output:** an executable plan.

---

## Sixteen principles, portable

1. **Declare precedence before you start.** Say out loud when sources disagree.
2. **Count before you plan.** Numbers size work; impressions don't.
3. **Documents drift; running systems don't.**
4. **Shape before prose.** Reject a diagram, not a chapter.
5. **Own by file, not by task.**
6. **Contended files get one owner; everyone else emits a fragment.**
7. **Evidence is execution, not inspection.** *A call that returns 409 is evidence; "the code
   looks right" is not.*
8. **Never certify your own work — and a second pass earns its cost only as a different lens.**
    Structural, not preference. In the first pilot the two passes mostly found *disjoint* things
    because they attacked from different angles; on one task pass A returned PASS and pass B found
    a confirmed high-severity defect. On another, pass B added nothing. So: a second pass with
    fresh context or a different lens pays for itself; a second identical sweep does not.
9. **Every loop has a cap.** Hitting it is a stop-and-report.
10. **Measure constraints; never quote them — then check the instrument, and label the
    conditions.** Name what a limit governs. A measurement is only as good as the thing taking it
    and the conditions it was taken under: the pilot's performance tool over-counted, and its
    headline concurrency figures turned out to come from two different workloads on different
    runs — a safe *direction* and an unearned *magnitude*.
11. **Recurring context becomes a skill, loaded first.**
12. **Escalate on decisions, not on findings.** A review returning findings is the process
    working. Fix them and continue. Stop only for genuine semantic ambiguity, a closed decision
    reopening, a fix that is itself a product decision, or a loop hitting its cap.
13. **The plan is the artefact of record.** Execution amends it — and so do the rules, the
    skills and the durable memory, because a correction that lands in only one of them leaves the
    others wrong. Write a **deviation** the moment it happens; **close-out facts** legitimately
    batch at a boundary, because they do not exist until the boundary. A status file reports
    progress; it never holds a correction the plan lacks.
14. **Assume amnesia.** Anything that lives only in a conversation is already gone. Progress,
    decisions and corrections must be reconstructable from the repository alone.
15. **Name every agent by role.** An unnamed fleet is addressable only by opaque handles, and a
    role name still means something when the model tier changes.
16. **A reminder that repeats is wallpaper; a reminder that reports is news.** Re-pasting rules
    trains an agent to skip injected text. Compute the reminder from current state and it stays
    worth reading.

---

## The three inward-facing rules

Most methods point outward. These point at you, and they are where the value concentrated:

**Grill your own artefact last and hardest.** Your plan is a document. Documents drift.

**When you are challenged, verify before you defend.** In the source session a challenge was
factually wrong — and checking revealed a *real* defect underneath it, in observability rather
than in the thing being challenged. Defending would have missed it; conceding would have fixed
the wrong thing.

**State your own errors plainly and fix them at source.** Not in a log of incidents — in the
document that was wrong. Capture the *pattern*, not the event: "I cited a limit scoped to the
wrong thing" is a pattern; "the number was 4 not 2" is an incident. Then search for the same
wrong claim everywhere else, because a bad fact is usually written down more than once.

---

## Keeping the plan true while it runs

The three rules above are about the plan you write. This one is about the plan you are *inside*,
and it is the phase-3 problem pointed at your own artefact: **documents drift, and the one most
likely to drift is the plan, because the work is what moves it.**

Every project discovers things mid-execution. A task splits in two. A decision that was open
closes. A path was wrong. The tempting place to put those is the status artefact — the file
tracking progress — because that is the file you are already updating.

That is the wrong file. The status artefact is read by whoever is *watching*. The plan is read by
whoever is *working* — including an agent that just lost its context and is deciding what to do
next. A plan that no longer describes the work is worse than no plan: it is confidently wrong,
and it is the first thing a restarted worker trusts.

**So: amend the plan in place. Then leave a dated entry saying what changed and why, referenced
both ways** — the plan points at the reason, the record points at the clause.

> **This is not the incident log the anti-patterns warn about.** The difference is substitution
> versus receipt. A lessons file recording *"the path was wrong"* while the plan still contains
> the wrong path is a **substitute** — the document that was wrong stayed wrong. A record saying
> *"Wave 3 grid amended: task added, decision closed — see §Wave 3"* is a **receipt** for a fix
> that already happened. Keep the receipt. Never let it stand in for the fix.

**The loop is wider than the plan file.** A correction usually belongs in more than one place:
the plan clause it changes, the rules that let it happen, the skill that should have warned, and
the durable memory the next session starts from. Landing it in one and not the others is how a
decision gets re-litigated three waves later. The pilot ran this as a standing loop —
*receipt → fold into the plan → update the rules and memory in place → the next wave briefs from
the corrected set* — which is why its twelve waves each started from a plan that was true rather
than a plan that was original.

**Gates drift too, and a changed gate is an amendment.** Mid-pilot the whole verification baseline
was replaced — a 58-test suite retired for a 16-test smoke suite, and the expected numbers
redefined with it. If that lands without a receipt, "the gates pass" quietly means something
different than it did last week and nobody can say when it changed. Record what the gate was, what
it became, and why.

**Orientation precedes action.** A worker resuming mid-plan does not start at task 1; it starts by
establishing where it is — task statuses, the gates, the commit log, the working tree. This costs
a minute and is the difference between resuming and re-doing. It is also the only defence against
the quieter failure: a *summarised* context, where the worker feels oriented and is reasoning from
a lossy copy, so a correction discovered at task 4 silently stops being true by task 12.

The test for all of it is one question: **if every conversation ended right now and a new worker
cloned the repository, could it tell what was done, what was in flight, and what had changed since
the plan was written?** If the answer needs a person, the plan is not resumable yet.

---

## Scaling

The phases don't change. **What you turn on does.** See [`SCALING.json`](SCALING.json) and the
interactive map in [`index.html`](index.html).

| Size | Tasks | Turn on |
|---|---|---|
| **XS** | 1–3 | Phases 0, 3, 9, **10**. No fan-out, no skills, no isolation. ~1 hour of planning. |
| **S** | 4–10 | + Phase 1 (2–3 recon workers), + Phase 4 diagram, + **Phase 5 reduced** (folder, owner, status, done-command — no persona, no skills, no fragments), 1 skill, branches only. |
| **M** | 10–25 | + Phase 5 **full** contracts (persona, skills, fragments), 3–5 skills, worktrees, **integrator**, adversarial pass. |
| **L** | 25–60 | + waves, + long-clock loops, + published status surface, two adversarial passes. |
| **XL** | 60+ | + sub-orchestrators per track, + a plan-of-plans. Re-run Phase 3 per track. |

**Two things never scale down.** At every size, from a one-line fix upward:

- **Phase 3** — grill the documents against the running system.
- **Phase 9** — verify the environment the plan assumes.

They are the cheapest phases and they catch the most expensive errors.

---

## Anti-patterns

| Don't | Because |
|---|---|
| Start work at the acknowledgement | the restatement is where mismatched understanding surfaces |
| Plan from a spec without checking it | specs describe intended systems as though built |
| Estimate scope from impression | "several" is not a number |
| Write task prose before the shape is approved | you will rewrite all of it |
| Let one worker review its own output | it will certify it |
| Assign work by task when tasks share files | last writer wins, silently |
| Quote a documented limit | it may govern something else |
| Treat a failed read as proof of absence | check permissions first |
| Log lessons in a growing incident file | fix the document that was wrong |
| Re-inject the same static reminder every turn | it becomes wallpaper, and teaches that injected text is skippable |
| Block a tool call to fix a lost frame | narrowing is not disobedience; denial does not restore the shape |
| Treat one independent review as sufficient | a second pass with fresh context overturned all five branches in the pilot |
| Let the agent that fixed a defect confirm the fix | that is self-certification, one level down |
| Change a gate or its baseline without a receipt | "the gates pass" silently stops meaning what it did |
| Schedule a deletion before its replacements are verified | teardown is where you discover the predecessors nobody finished |
| Keep task files loose, or share one folder between tasks | containment, the output contract and the status glob all key on `tasks/<ID>/` and break together |
| Run a second identical sweep and call it a second pass | it re-finds what the first found; only a different lens or fresh context pays |
| Absorb a recurring violation at integration instead of fixing its cause | the pilot's integrator silently cleaned up out-of-folder writes seven times and the cause was never fixed |
| Leave an ambient indicator stale | the pilot's title read one wave for the entire run — an indicator that never updates is worse than none, because it is believed |
| Record a deviation only in the status file | the plan becomes confidently wrong, and a restarted worker trusts it first |
| Keep progress in the conversation | a clear or a compaction erases it, and the work gets re-done or skipped |
| Run a fleet of identically-named agents | they are addressable only by opaque handles, and terminal titles become the only clue to purpose |
| Treat an agent's `unknown` state as done | unknown means unclassified, not finished |
| Turn a review finding into a stop-gate | fixing specified defects is execution |
| Ship a plan with no entry point | nobody can start it |
