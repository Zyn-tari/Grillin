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

**Output:** a paragraph and two or three flags.

---

### Phase 1 — Inventory: count before you plan

Fan out **read-only** workers to enumerate what exists. Partition **by file ownership** so none
overlap. Each writes one document to a shared frozen folder.

- Cite `file:line` for every claim.
- **Give counts.** "Several components fetch their own data" is useless; "21 of 49" sizes work.
- Label **VERIFIED** (read it) vs **REPORTED** (inferred).
- End each with **"what I did not verify."**
- Use your cheapest capable model. Inventory is not reasoning work.

This folder is written once and **frozen**. Everything downstream reads it instead of
re-deriving it — that is where the speed comes from.

**Output:** an inventory folder, with counts.

---

### Phase 2 — Triage what the inventory dug up

Recon always finds defects. Sort them, never absorb them:

| Bucket | Meaning |
|---|---|
| **A — fix during the work** | in files being touched anyway; no semantics change |
| **B — needs a human decision** | product or safety semantics; you do not decide these |
| **C — real but out of scope** | record it, do not schedule it |

Label each **VERIFIED** or **REPORTED**. Spot-check the headline items yourself.

**Why:** without triage a discovery either silently expands scope or gets lost. This makes scope
creep a visible decision instead of a side effect.

**Output:** a triaged defect register.

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

**Output:** a contradictions register. Expect it to resize the work.

---

### Phase 4 — Shape first: diagram before prose

Produce a **one-screen** dependency graph before any task text. Type every node:

`ASK` (a human decides) · `BUILD` · `REFACTOR` · `RECONSIDER` (decide before building) ·
`VERIFY` · `LOOP`

Get it approved. A wrong diagram costs a minute; the prose it authorises costs hours.

Make `RECONSIDER` nodes real. A node whose legitimate output is *"don't build this"* is a node
doing its job.

**Output:** an approved graph.

---

### Phase 5 — Decompose into owned tasks

One folder per task. Each is a **contract**, not a description:

| Element | Why |
|---|---|
| **Persona** | a professional identity with a habit of mind — it visibly changes what gets noticed |
| **Exactly the files it owns** | one owner per file, always |
| **The evidence already gathered** | cite the inventory sections; it reads instead of re-deriving |
| **Steps** | specific, ordered, referencing real paths |
| **A loop** | exit condition **and** an iteration cap |
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

**Output:** a small set of skills; one line per task referencing them.

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

Then match substrate to shape: wide independent fan-out and long-running isolated work have
different answers, and *deterministic cross-agent control flow* is the only thing that justifies
paying a concurrency penalty.

**Write the choice — and the rejected alternative — into the plan**, because the next operator
will otherwise reach for the structured-looking tool.

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
- **A status surface** the requester can read without asking — published, not narrated.
- **Hand-off items you cannot do yourself**, stated explicitly rather than silently skipped.
- **A warm restart, not just a cold one.** The entry point tells a fresh worker what the plan
  *is*; it must also let one that is halfway through establish *where it got to*. See
  [Keeping the plan true while it runs](#keeping-the-plan-true-while-it-runs).

**Output:** an executable plan.

---

## Fourteen principles, portable

1. **Declare precedence before you start.** Say out loud when sources disagree.
2. **Count before you plan.** Numbers size work; impressions don't.
3. **Documents drift; running systems don't.**
4. **Shape before prose.** Reject a diagram, not a chapter.
5. **Own by file, not by task.**
6. **Contended files get one owner; everyone else emits a fragment.**
7. **Evidence is execution, not inspection.** *A call that returns 409 is evidence; "the code
   looks right" is not.*
8. **Never certify your own work.** Structural, not preference.
9. **Every loop has a cap.** Hitting it is a stop-and-report.
10. **Measure constraints; never quote them.** Name what a limit governs.
11. **Recurring context becomes a skill, loaded first.**
12. **Escalate on decisions, not on findings.** A review returning findings is the process
    working. Fix them and continue. Stop only for genuine semantic ambiguity, a closed decision
    reopening, a fix that is itself a product decision, or a loop hitting its cap.
13. **The plan is the artefact of record.** Execution amends it. A status file reports progress;
    it never holds a correction the plan lacks.
14. **Assume amnesia.** Anything that lives only in a conversation is already gone. Progress,
    decisions and corrections must be reconstructable from the repository alone.

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
| **XS** | 1–3 | Phases 0, 3, 9. No fan-out, no skills, no isolation. ~1 hour of planning. |
| **S** | 4–10 | + Phase 1 (2–3 recon workers), + Phase 4 diagram, 1 skill, branches only. |
| **M** | 10–25 | + Phase 5 full contracts, 3–5 skills, worktrees, **integrator**, adversarial pass. |
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
| Record a deviation only in the status file | the plan becomes confidently wrong, and a restarted worker trusts it first |
| Keep progress in the conversation | a clear or a compaction erases it, and the work gets re-done or skipped |
| Turn a review finding into a stop-gate | fixing specified defects is execution |
| Ship a plan with no entry point | nobody can start it |
