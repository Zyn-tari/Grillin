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

### Phases 0–4 run in plan mode, and leaving it is the approval

The premise above says three phases produce no plan text at all and are the highest-value
phases. That has always been an honour system. Nothing stopped a worker in phase 1 from
"just fixing" the thing it was sent to count, and phase 1's whole value is that its output is
frozen and nobody acted on it — a count taken after somebody started changing things is not a
count of what existed.

**Where the harness has a plan mode, use it, and the honour system becomes a mechanism.** Claude
Code's is the reference implementation: while it is on, the tool layer refuses writes, so the
read-only claim is enforced by the thing running the tools rather than promised by the thing
using them. Leaving plan mode is a single, explicit, human-approved act — which is exactly the
boundary phase 4 needed and never had. Phase 5 is the first phase that writes; it is also the
first phase that should be outside plan mode.

| | Without plan mode | With it |
|---|---|---|
| Phases 0–4 write nothing | agreed | enforced by the tool layer |
| Phase 4 → 5 is a decision point | implied by the phase numbering | an explicit approval a person gives |
| A phase-1 worker "just fixes" something | discovered later, in the diff | refused at the tool call |

This is principle 11 applied to the method itself: a rule a machine cannot check is a preference,
and until a harness could enforce this one it was a preference. Two things follow. The phases are
unchanged — plan mode is not a new phase and does not move a boundary that already existed; it
makes an existing boundary real. And **the gate cannot see any of this.** No artefact records
which mode a phase ran in, so `validate-plan.py` has no check for it and will never have one;
it is listed among the advisory rules in `OPERATING-THE-PLAN.md` for that reason.

On a harness with no plan mode, phases 0–4 are agreed rather than enforced, exactly as before.
Say which one you had. A plan whose reader assumes enforcement it did not have is worse off than
one that knows the inventory was taken on trust.

---

### Phase 0 — Acknowledge, flag, stop

Restate the ask in your own words. Name what you still need. Flag anything that would **change
the shape** of the plan. Then stop.

Do not start work at the acknowledgement. The restatement is the cheapest place to find out you
heard it differently.

**Then interview, rather than guessing.** The restatement finds the misunderstandings you can see.
An interview finds the ones you cannot — the edge case nobody mentioned, the constraint that is
obvious to the requester and invisible to you, the tradeoff that has already been decided
somewhere else. Where the harness has a structured question tool, use it; Claude Code's is
`AskUserQuestion`, and the published shape of the request is:

> I want to build [brief description]. Interview me in detail using the AskUserQuestion tool.
> Ask about technical implementation, UI/UX, edge cases, concerns, and tradeoffs. Don't ask
> obvious questions, dig into the hard parts I might not have considered. Keep interviewing until
> we've covered everything, then write a complete spec.

Two rounds, not one: the first before anything is shaped, the second after phase 4 has a diagram
and before phase 5 writes a single task. The questions are different at those two points, and a
plan that asks them all at the start asks half of them too early to be answerable.

**Multiple choice beats an open question here.** An open question is answered with what the
requester happens to think of; a small set of named options with their consequences is answered
with a decision, and the rejected options are then written down as rejected rather than never
considered. Where a question has a conventional answer, pick it, say which you picked, and keep
going — an interview that stops on every routine judgment is a questionnaire.

**Output:** a paragraph, two or three flags, the answers to the interview, and the five answers
below.

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
- **Status the requester can read without asking** — never narrated in a conversation. This is
  **two artefacts**, and conflating them is a documented defect: a curator planning at XS read
  one name, found it switched off in the scaling table, and added the wrong thing. So they get
  different names, here and everywhere:
  - **Task status lines** — the `**Status:**` line inside each `tasks/<ID>/TASK.md`. Required by
    principle 13 at **every size, XS included**, and never switched off by the scaling table.
    Reading them is a glob over `tasks/*/TASK.md`, not a question to a worker.
  - **A published status surface** — a separate, derived artefact: one page or file the requester
    opens. This is what the scaling table means by *published status surface*, it **turns on at
    L**, and it is in XS's `leaveOff` list. At XS the status lines *are* the surface, and a page
    rendering three of them is ceremony. Build one earlier only if the requester will not glob.

  The cheapest way to keep a *published* surface true is to derive it from the status lines, on
  the write that updates them: that write is the only *work-shaped* event a harness offers, and
  it costs the worker nothing because the surface is never shown to it.
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
| **XS** | 1–3 | Phases 0, 3, 9, **10** — the precedence ladder, the document grill, the environment check, the entry point. No fan-out, no skills, no isolation. ~1 hour of planning. |
| **S** | 4–10 | + Phase 1 (2–3 recon workers), + a triage register, + Phase 4's approved diagram, + **Phase 5 reduced** (folder, owner, status, done-command, and still a model and an effort — no persona, no skills, no fragments), 1 skill, branches only. |
| **M** | 11–25 | + full recon fan-out, + Phase 5 **full** task contracts (persona, skills, fragments), 3–5 skills, worktrees, **integrator**, + substrate measurement (Phase 8), adversarial pass. |
| **L** | 26–60 | + waves with merge gates, + long-clock loops, + a published status surface, two adversarial passes. |
| **XL** | 61+ | + sub-orchestrators per track, + a plan-of-plans. Re-run Phase 3 per track. |

**Two things never scale down.** At every size, from a one-line fix upward:

- **Phase 3** — grill the documents against the running system.
- **Phase 9** — verify the environment the plan assumes.

They are the cheapest phases and they catch the most expensive errors.

---

## The shared authoring rules — they hold with or without a plan directory

The phases above build a plan directory. Most work never gets one. The rules below are the part
that does not depend on having one: they hold for a plan, for a single delegated brief
([`templates/BRIEF.md.template`](templates/BRIEF.md.template)), and for the skeleton in the next
section. They live here so that there is one copy — a rule published in four places becomes four
different rules. Where something is already enforced or already written down in this repository,
this section **cites** it and does not restate it.

Read the register honestly: outside a plan directory almost nothing here is machine-checked. Where
a check exists it is named. Where none exists that is said out loud, and the rule is a standard you
hold yourself to, not a gate you can hide behind.

The incidents below were bought elsewhere — on a run of hand-written briefs against a live server,
and on two long-form builds whose costs were recorded at the time. They are reproduced as evidence
for the rules they bought, not as measurements of this repository. Where a number appears, it is
theirs.

### What a declaration owes the worker

**Lead with consequence, not activity.** State the problem as what happens, and where the work
exists because something already went wrong, say what went wrong — the same rule a task contract
carries ([`templates/TASK.md.template`](templates/TASK.md.template)). Every brief in the sample led
with consequence: *the deploy itself is small; the risk is entirely in what else is on that box.*
That sentence is what makes a worker careful.

**Then say what done is NOT.** Name the boundary the work stops short of. `Done means` is the
positive gate; this is its complement, and leaving it out is how scope grows quietly. One brief
said *ready for a URL — not connected to one*, because "deploy the site" without that sentence
licenses a worker to go and find a domain.

**State the mechanism, not the prohibition.** A rule is written with the mechanism that causes it,
never with the syntax it forbids. "Be careful with the web server" prevents nothing. The mechanism
does: no default server is declared anywhere on the box, so the first server block loaded for a
port becomes the implicit default; the config directory loads alphabetically; a file named
`newsite` sorts before `zz-app` and would silently become the catch-all for the whole machine.
**A worker that understands why the file is named `zz-` will not rename it in a later job. One that
was only told the name, will.**

Three riders travel with that rule:

- **Say "silently" when it applies.** A failure that announces itself is a bug; a failure that does
  not is a trap, and the word is the difference between the two.
- **One trap per block, never merged.** Two traps in one paragraph cannot be checked off
  separately, and a worker checks off what it can see.
- **Every prohibition carries its reason where the reason is not obvious.** *Do not restart the
  service; validate the config, then reload — a reload does not drop the live sites' connections, a
  restart does.* An unexplained prohibition gets reasoned around by a capable worker under
  pressure. An explained one does not.

**Ownership is stated in full, by path, even where it feels obvious.** One owner per file (see the
principles above and [`templates/_WORKTREES.md.template`](templates/_WORKTREES.md.template)); name
the neighbours by path and say they are not yours; and say that a defect found in something you do
not own is **reported, not fixed**. Inside a plan directory the rules file carries this once for
everybody. Outside one there is no rules file, so it goes in full into every artefact — which is
why the sample briefs converged on a single containment sentence and repeated it verbatim in every
follow-up.

**The artefact carries the instructions, not the history of the instructions.** Rationale is a note
to the author. A brief, a contract or a skeleton that arrives carrying its own reasoning is longer,
and the parts that matter are harder to find inside it. Keep the reasoning in the template and in
this section; delete it from the copy you send.

**Two kinds of repetition, and only one of them is a duplicate.** A rule restated across surfaces an
author maintains is a duplicate: the copies drift, and the second one becomes a second rule. A rule
restated *inside a single artefact handed to a reader with no history* is not — it is redundancy
placed where attention decays. So: repeat the decision point inside the "do not" list, because it
is the one a worker forgets forty minutes in; and re-state the rails in a follow-up instead of
pointing back at the first instruction — *same rails as before: nothing outside `<path>`, validate
then reload, re-run the neighbour check at the end.* Two lines, and they survive a fresh context
that never saw the first instruction. **Do not delete these as duplicates.** They are the
exception, and this paragraph is the reason.

### Facts, and what a fact costs to write down

**A row of established fact carries the command that established it, not the assurance that it was
checked.** "Both names already resolve to 203.0.113.10; I checked" is a claim. `dig +short
newsite.example.com` → `203.0.113.10` is a fact, and the difference is that a reader can run the
second one. Inside a plan this is the bar `check_confirmed_is_exercised` in
[`scripts/validate-plan.py`](scripts/validate-plan.py) holds you to; see the enforcement register in
[`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md) §11. **Nothing enforces it outside a plan
directory** — no gate reads a brief and no gate reads a skeleton — so on those surfaces it is an
authoring standard and nothing more.

**Anything you believe but did not run is not a missing row. It is a task.** It belongs in the
declared reads, for the worker to establish, never in the table of established fact. A belief
promoted to a fact is the one defect nothing downstream can catch, because everything downstream
treats that table as ground.

**The table exists to buy back the worker's first twenty tool calls.** Without it a worker
rediscovers which server is running, which runtime exists, and what else is on the machine — all of
which the author already knew. Inside a plan the same instruction reads *cite the inventory that
briefs you; do not re-derive it* ([`templates/TASK.md.template`](templates/TASK.md.template)).

**Rows naming a file or an identifier are checked against the artefact actually deployed** — not
against the bundle, the spec, or whoever wrote the request. Already owned, with the three incidents
that bought it, by [`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md) §10 · *Confirm the artefact
before the first edit*. Cited, not repeated.

**Where the machine you are on is not the machine the work lands on, say so and give both paths.**
Two briefs in one afternoon lost time to a worker looking for a file on the wrong host. A path with
no host attached reads as local, always.

### Evidence tiers: two labels, and why not three

Grillin's vocabulary is two labels — **CONFIRMED** (you checked it yourself) and **SUSPECTED** (you
inferred it, or were told) — defined once in *Phase 1 — Inventory* above and used everywhere: an
inventory row, a review finding and a claim in a report all take the same two.

Methods that grade sources more finely usually run three tiers: *sourced* (citable, with a locator
and a date), *preliminary* (backed by a capture but not independently checkable by the audience),
and *unverified* (belief, to be resolved or cut before ship). Map those in; do not adopt them:

- *sourced* → **CONFIRMED**
- *preliminary* → **SUSPECTED**
- *unverified* → **SUSPECTED**

The third tier is not adopted because nothing can grade it. The CONFIRMED boundary is checkable —
an invocation is quoted or it is not — and that is exactly what makes two labels worth having. A
middle tier adds a label no machine can separate from the one below it, which makes it a preference
wearing a vocabulary's clothes. The cost of the collapse is already recorded in
[`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md) §12: *told* and *inferred* land in the same bucket.
If your project needs to tell them apart, write the distinction into the row's own text rather than
inventing a third label the gate cannot see.

### Freshness is a separate question from accuracy

A source can be primary, correctly quoted, dated — and silently superseded. Accuracy asks *did you
copy it right*; freshness asks *is it still true*, and a document can answer the first perfectly
while failing the second. This is not the precedence-ladder claim above: the ladder ranks *kinds* of
source and warns that specs go stale. Freshness is a property of one source you have already decided
to trust.

So for anything living — a running config, a price, an org process, an API surface, a wiki page —
**state how still-true gets confirmed, and state it as an action**: *re-run the capture the week of
ship*, *a fresh interview outranks document age*, *re-read the config on the box before the first
edit*. A CONFIRMED row is confirmed **as of the moment its command ran**. Nothing in this method
re-ages it for you.

### Decision points: write both branches before the reading is taken

A decision point is what keeps a small instruction from authorising a large irreversible act. One
brief asked for a site "in PHP" on a server with no PHP runtime. The brief had pre-decided both
branches — deploy static if the `.php` is a shim, stop and report if it is genuinely load-bearing —
because *installing a language runtime on a production server running someone else's live service is
not something to do inside an instruction that said "deploy this landing page."*

Two rules follow, and they are the whole of it:

- **Write both branches, not just the stop.** A gate with only the stop branch written reads as
  discouragement. A worker that knows exactly what to do on the good branch will not talk itself
  onto the bad one.
- **Price the stop.** Say what stopping costs — *it costs you one message* — or the worker weighs a
  stop as failure and proceeds. An unpriced stop is not a gate; it is a warning.

**Assign the meaning before you take the reading.** Whichever branch a measurement selects, decide
what each possible reading *means* while you are still writing, not while you are looking at it. A
worker that knows what a reading means before taking it cannot rationalise the reading afterwards —
and neither can you. Where the whole job is to find out *why* something is broken, the decision
point **is** the stop: report first, change nothing.

### Proving you broke nothing, and proving you did something

These are two different proofs and they need two different commands.

**Broke nothing: the identical command, before and after.** Run it, record the output, do the work,
run the byte-identical command again, and put both outputs in the report. A reading taken only
afterwards proves nothing, because nobody can say what it was before. This began as a formality — a
two-host check run before and after a config reload — and stopped being one on the certificate job,
where the tool rewrites the server config in place as a side effect of doing its actual work. The
reading that looked like ceremony was the only thing watching the file that changed itself.

**Did something: the proof command must fail before the work is done.** Already written down and
already enforced — the `Done means` rule in [`QUICKSTART.md`](QUICKSTART.md) §4, and
`check_gates_fail_first` in [`scripts/validate-plan.py`](scripts/validate-plan.py). It appears here
as a heading and nothing more, because a brief has no gate to catch it for you.

**A cause is not established by making the symptom go away.** A control test is required before a
symptom is attributed to a cause — owned by [`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md) §9 · *A
defect is not a cause until you remove it*. Cited, not repeated.

**Say which half.** Be accurate over reassuring: where something is half-done, name the half. The
register is [`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md) §8 · *The measurement, stated without
euphemism*. "Fixed X; Y not verified" is a result. "Should be working now" is not.

### Handing something back: reports, and commands a person will paste

**Number the reporting contract.** The list of what the report must contain is numbered so the
worker can check its own report against it before sending, and so the author can see at a glance
which item is missing. An unnumbered list of expectations is read once and satisfied approximately.

**Name the exact output path and the exact notification command.** A report written to a path nobody
reads is not a report. Where the job has no plan directory the report *is* the resumption artefact —
the only continuous record the work has — which is why it is never optional.

**Follow-up work appends to the report; it never rewrites it.** Say it in those words, because
"write the report" reads as "write the file" to a worker that did not write the first one, and
overwriting it is the no-directory equivalent of losing the plan directory. Append under a new
dated heading and leave what is there.

**Never hand a person a command with a placeholder in it.** Assume it will be pasted without being
read around, because it was: a `sed` command containing `YOURDOMAIN.com` was run literally,
placeholder and all, and a vhost went live serving `server_name YOURDOMAIN.com`. If the real value
is not known yet, write the command with the value **visibly missing** and the words "fill this in"
— never a plausible-looking fake. A fake that looks real is indistinguishable from a value, and
that is the entire failure.

### F1 · Starve the inputs, and declare the exceptions

**Declare what each worker reads — and name what it must not read.** The must-not list is the part
people leave out and it is the part that pays. Two long-form builds held to the same standard —
73,000 words and 60,000 words — cost about 10M tokens and about 2.9M. Check the direction before
crediting the gap to size: the longer build is the expensive one, but 22% more words did not buy
3.4x the cost. The difference was not thinking, it was re-reading: a 700 KB research corpus pulled
in forty-odd times. Slice shared material into per-worker packs of roughly 12–25 KB, so each worker
reads its own slice, the conventions, one exemplar and the captured ground truth — and nothing
else.

The other half of this is not cost. An instruction that says *read those four files in full; do not
read the asset files, the vendored library, or the video — you do not need their contents in order
to host them* is preventing a specific failure: a 14 MB video read into context is a job that dies
at step four **for reasons that look like model error**. That failure signature is why the list is
worth writing, because it does not present as "read too much."

**This is an authoring convention, not a containment rule, and the two point in opposite
directions.** Containment restricts where a worker may **write** and deliberately leaves reading
open — the *Phase 5* principle above, and
[`templates/_RULES.md.template`](templates/_RULES.md.template) §2a · *Containment*, which wins on any
disagreement with a task. Nothing enforces a must-not-read list. Starvation is a budget and a focus
decision the **author** makes when packing the work: it **narrows** that open read permission rather
than revoking it. Say which one you mean — a worker that reads "must not read" as a containment
boundary will report a legitimate lookup as a violation.

**Order the read list, and put the deciding file last.** Where one of the declared reads is what
settles a decision point, name it as the decision point and place it at the end, so the worker
arrives at the gate having already read what informs it. A list in arbitrary order is a list read in
arbitrary order.

**Two exceptions are lawful. Both are declared, never improvised:**

1. **Cross-reference-bound units get an explicit read-list of finished peer units.** Where a unit
   must reconcile against others — a budget against the aims it funds, a timeline against everything
   on it, a summary against what it summarises — name the finished peers it may read.
2. **A cross-cutting thread gets a continuity bible.** Where something must surface across
   non-adjacent units, write one short file every worker reads regardless of its group. Checking the
   seams alone catches breaks only at group boundaries, and a thread does not run along them.

Anything that is not one of those two stays starved. An exception a worker granted itself is not an
exception; it is the corpus coming back.

### F2 · A number, or the reference to measure

*Give counts, not adjectives* is already stated for inventory work in *Phase 1* above. The general
form is stronger and applies to every declaration: **every quality word either carries a number or
names a reference a worker can measure before starting.** "More visuals, less dense" steered nothing
until it was measured off the best existing page and became *≤130 words per visual component, ≤3
consecutive paragraphs, ≤22 KB per section — checked by script.* Where you cannot give the number,
name the thing to measure and make measuring it the first task.

**Numbers go in the medium's own units** — not in the units that are convenient to count, and not in
whatever the tool happens to emit. A count is a proxy for a limit, and a proxy is worth exactly what
its correlation is worth.

**Gate the quantity the limit is actually expressed in.** *Which* quantity that is, is the authoring
decision: make it before anyone builds the gate, because a gate can only measure what it was pointed
at. Measuring the wrong quantity once the gate exists is instrument validity, and
[`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md) §5 · *Validate the instrument, separately, first*
owns that, with the worked case. Cited, not repeated.

**On a migration or a rewrite, number the source corpus too** — percent of legacy units triaged,
merged, retired. Counting only what you produced leaves the old material unmeasured, and silence is
where old material disappears: nobody deletes it, it simply never appears in a number and so is
never missed.

### F3 · Groups, seams, barriers, and ending the chain

**Overlap is the default; a barrier is a declaration.** Work starts the moment its own input lands.
A full stop belongs only where a stage genuinely needs everything — assembly, and any unit that must
reconcile against near-final peers. **The barrier that actually stops dispatch is the dependency
edge** — a task's `**Blocked by:**` and `**Blocks:**` fields, checked by `check_graph` in
[`scripts/validate-plan.py`](scripts/validate-plan.py). Declare it there and nowhere else, so the
declaration has one home. The wave table in
[`templates/_WORKTREES.md.template`](templates/_WORKTREES.md.template) §1 · *The waves* is the
human-readable schedule of those edges, and `**Wave:**` itself is parsed by nothing — it sits in
[`templates/TASK.md.template`](templates/TASK.md.template)'s NOT-PARSED register. A stop that exists
only as a wave row is a stop no orchestrator can see: it reads the graph, finds nothing blocking, and
dispatches straight through the full stop you thought you had declared.

**Group correlated units under one worker — two or three, not more.** It is cheaper, and units
inside a group flow into each other because one hand wrote them.

**The seams between groups are where joins break, so name them and give each one an owner.** A seam
is not a barrier and it is not a file boundary. A barrier says *nothing proceeds until this is
done*; a
seam says *these two finished things have to meet, and meeting is work somebody has to be assigned.*
Usually the assembler owns every seam and reads across all of them. Ownership by file settles who
may write; seam ownership settles who is answerable for a join that no file boundary covers.

> **A naming collision worth avoiding.** [`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md) §1 is
> titled *The seam* and means something else entirely — the boundary between building a plan and
> operating one. If you use the word in a plan, say which seam you mean.

**End the chain out loud.** Say what happens after the last reader, in the declaration, in words:
*after the checker, no re-verification — present.* A chain with no stated end acquires one more
review, because the last worker cannot tell that it is last. Naming the terminal step is what stops
verification expanding into the delivery slot.

### F4 · Output a script can eat

**Require an exact output form, and say so in the worker's own instruction.** Any part of the
finished work that *can* be built mechanically from structured worker output should be: judgement
for agents, assembly for scripts. Gatherers writing under an exact per-unit heading form turn
slicing into packs into a zero-cost script; a term list emitted in a fixed shape is harvestable by
sweep. A form invented per worker is a form somebody reads by hand, forever.

Grillin already grades one task type on the shape of what it writes: `check_research_task` in
[`scripts/validate-plan.py`](scripts/validate-plan.py) holds a research task to its findings file
rather than to its activity, and [`templates/TASK.md.template`](templates/TASK.md.template) fixes
the order that file answers in. The rule here extends that beyond research tasks; it does not
replace it.

**Every gathering task ends each topic with a "What this does NOT achieve" block.** Then the
finished work's honesty section *assembles itself* out of independent admissions, instead of being
composed at the end by whoever is least willing to write it.

> This is not the same object as the whole-document *What this does not solve* register that
> [`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md) §12 and
> [`templates/BRIEF.md.template`](templates/BRIEF.md.template) each carry. Those are one section,
> written once, read by a person. This is one small block **per topic**, written by the worker that
> did the topic, and consumed by an assembly script. Keep both, and do not converge the wording —
> a script that collects on the phrase will start collecting the wrong ones.

**A findings report has a form too: location · the exact current text · the exact corrected text ·
the evidence.** Report-only workers emit findings; one owner applies them — the same shape the
principles above already require for a contended file. Give that owner **explicit decline rights:
it may reject a finding, with a stated reason, logged.** A reader checking one dimension in
isolation is sometimes wrong, and an applier with no right to refuse either ships the wrong fix or
argues about it somewhere nobody keeps.

---

## The skeleton — many workers, one artefact, no plan directory

Grillin's phases produce a plan directory, and a plan directory is the right answer for work that
outlives the conversation that started it. Two rungs below it, it is the wrong answer — and
shipping only the top rung is how a method gets skipped rather than scaled. The ladder:

| What you have | What to use |
|---|---|
| One job, one worker, and you are present while it runs | [`templates/BRIEF.md.template`](templates/BRIEF.md.template) — one delegated task, no plan around it |
| Many workers building **one artefact**, and you are still present | **the skeleton below** — a declaration, not a directory |
| Work that outlives the conversation: several tasks, dependencies between them, or anything a fresh context must resume from disk | the phases above, and a plan directory |

The skeleton is a **declaration**. It says what gets made, what it is measured against, what counts
as ground truth, who does what, what each of them may read, and when to stop — and it says all of
that before anyone builds anything, which is this document's premise applied to a job too small to
carry a directory. It has no folder, no status file, no done-command a gate can parse, and nothing
validates it. The moment you find yourself adding a status field, a dependency between two of its
workers, or an owner column, you are writing a plan directory in the wrong file: stop and go up a
rung.

**Going up a rung: where each slot lands.** The rung above carries the fields the gate reads, plus a
register of the ones it does not. Several slots below have no field waiting for them there, and a
slot with no address becomes a differently-named heading in every plan — so put them here:

| Skeleton slot | Where it goes in a plan directory |
|---|---|
| `BAR` · `EXEMPLAR` | `PLAN.md`, above the task table. Where no exemplar exists, building one by hand is the **first task**, with its own folder, because everything downstream of it gates on it. |
| `GROUND TRUTH`, with its freshness rule | `PLAN.md`, and the capture itself becomes a task the makers declare in `**Blocked by:**`. |
| `SCAFFOLD` | The tasks' own `## Done means` commands, which exist and fail before any worker runs (`check_gates_fail_first`). |
| `NUMBERS` · `Must not read` · `OUTPUT SHAPE` | Per-task fields — already in [`templates/TASK.md.template`](templates/TASK.md.template)'s NOT-PARSED register. |
| `Seams: [N] between groups, owned by [who]` | `## What you own` on the integrator's task. A seam no task holds is a seam with no owner. |
| `END THE CHAIN` · `PRESENT` | `PLAN.md`'s closing section — `examples/a-real-first-plan/PLAN.md` calls it *Definition of done for the whole plan*. |

Nothing in that table is checked by anything. `PLAN.md` above the task table is free-form, which is
exactly why the slot needs naming: the gate will not tell you the exemplar was never declared.

For a job smaller than a single brief, use the **Pocket version** in
[`QUICKSTART.md`](QUICKSTART.md) rather than trimming this one down.

Every rule the skeleton leans on is in *The shared authoring rules* above. The slots are
tool-independent: where a slot names a tier of worker, read it as *top / mid / small* in whatever
you run — and a team with no agents in it at all can still run this pipeline, because the fences and
the gates carry more of the value than the parallelism does.

Copy from here down.

```
MAKE: [what · for whom · in what final form]

BAR: same level as [the same-kind artefact — or a different-kind artefact that demonstrates the
properties — or the properties alone, if neither exists].
That means: [property] · [property] · [property]
EXEMPLAR: [path to ONE finished unit every worker receives — confirmed yours to share. If none
exists, building it by hand is the first task, scheduled as work, because it gates everything
downstream of it.]

NUMBERS: [floors and ceilings in the MEDIUM'S OWN units · the quantity each limit is actually
expressed in, gated in that quantity (a rendered cap is render-then-count) · on a migration or
rewrite: % of the legacy corpus triaged / merged / retired · every figure traceable to a
measurement]
[Any quality word with no number: name the reference, and measuring it is the first task.]

GROUND TRUTH: [captures · fixtures · datasets · transcripts · primary documents], captured
BEFORE anyone builds. Quote verbatim from the capture, or re-derive and mark it as re-derived.
Never retyped from memory.
Labels: CONFIRMED (an invocation is quoted) · SUSPECTED (inferred, or told).
Freshness: [how still-true gets confirmed, as an action, for every living source].
Gaps stated in the work itself: [what cannot be established here, and what is cited instead].

SCAFFOLD (all of it before the first worker): the conventions every worker follows · the
exemplar file · the gates, created AND pointed at the new work (per-unit: [cmd] · assembly:
[cmd] · [medium gate]: [cmd]), each smoke-tested once on a known-bad input · unit naming:
[scheme — binding, because the gates key off it] · layout: [where captures, packs, units and
tools live]

PIPELINE — one block per role; every role gets one job and one fence:
- Gatherers: [N] × [tier] at [effort]. Job: [topics + depth] → [path], written under per-unit
  headings in the exact form [## §NN], each topic ending with a "What this does NOT achieve"
  block. Reads: [its own slice]. Must NOT read: [what]. Fence: they do NOT build the product.
- Makers: [N] × [tier — top where the job is adjudicating between conflicting sources, mid
  where it is building from settled input] at [effort]. Read ONLY: the conventions, the
  exemplar, ground truth, their own pack. Must NOT read: the corpus, each other's units
  (exceptions declared in HANDOFFS). Grouping: correlated units share one maker, max [2–3].
  Each unit passes [unit gate] before returning. Fence: they do NOT touch [the frame / other
  units].
- Mechanical workers (if any): [N] × small tier, no persona. Job: the compile-from-record parts
  ([what]), straight from the captures. Fence: no judgement calls.
- Assembler: persona: [name — the goal in one sentence]. Writes [the frame / opening / closing],
  combines, and owns the [N] seams between maker groups. Fence: format and fit, NOT facts; never
  overwrites a maker's substance. Delegation: [may it spawn report-only workers? may it choose
  their tiers?]
- Checker: persona: [name — the goal]. Method by claim type: [rerun … · recompute … ·
  claim-fidelity against …]. Report-only shards emit findings as [location · exact current text ·
  exact corrected text · evidence]; the Checker applies every fix personally and may decline a
  finding with a stated, logged reason. Reads ground truth, NOT the makers' inputs. Fence:
  information only, not shape or style.

HANDOFFS: [Gatherer → its own Maker the moment it lands; no waiting on siblings.]
Barrier at [the Assembler], and before any unit that reconciles against near-final peers
([which ones]) — those get an explicit read-list: [which finished units].
Cross-cutting threads: continuity bible at [path], read by every Maker regardless of group.
Seams: [N] between groups, owned by [who], read end to end.
END THE CHAIN: after [the Checker] — no re-verification. Present.

PRESENT: lands at [where] · copies to [where] · revisions keep the same [target], never a new
one. Presenting is part of the build, not an afterthought.

CONSTRAINTS: [don't-touch list: systems, files, owned content] · [hard stops that reject the
work unread] · [approval gates]
TRAPS: see [path to the DOMAIN-labelled standing ledger] — pointed at, never retyped here.

APPETITE: [budget, in the denominator that actually dominates this job — agent tokens, studio
hours, freelancer days, licence fees] · worker cap: [N] · wall-clock tolerance: [what] ·
[run-to-done | ask first at [which points]] · EXTERNAL DEADLINES: [the delivery date] AND every
approval step between "done" and "delivered", each with its lead time — [who needs it, how
early]. The real deadline is usually not the final one: a review that needs the packet five
business days early IS the deadline.
```

**A note on the last slot.** APPETITE is a *declaration* — what you are willing to spend, and when
the thing must be delivered. Writing the deadline as a chain of approval steps rather than as a
single date has two consequences worth naming.

First, **every approval step is a person in the work**, and a person's step is not a slower version
of a worker's step: it does not settle on its own, it settles when somebody acts. Grillin's
vocabulary for that already exists — `**Owner:** … human` — and what declaring it does to a task is
owned by [`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md) §10a · *The two ways a person is in the
plan, and they are not the same*. A gatekeeper with a lead time is that same shape, declared up front
instead of discovered at the end.

Second, **the declared budget and the measured spend are two different numbers.** Declaring one does
not measure the other, and nothing in this repository reconciles them. If you need the actuals they
come from whatever executed the work, not from this file — and a plan that quotes a spend it did not
measure is doing the thing *Phase 1* forbids.

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
| Close a symptom on a defect you never controlled for | the missing vendor file really was a 404, and blocking it left the chart still redrawing |
| Send a research task out without a timebox | research with no exit condition is not finished, it is abandoned, and later |
