# Working with Claude Code — a practical guide for your first month

You already know how to program. You know what a transaction is, why a migration needs a rollback,
and why you don't trust a query you haven't run. **None of that changes here.** What changes is that
you are no longer the one typing, and almost every mistake people make with Claude Code comes from
not updating their instincts for that one difference.

This guide is about the working habits, not the features. It assumes you have Claude Code installed
and have asked it to do a few things.

> **About this repository, so nobody is confused later.** Grillin — the thing this file lives in — is
> a *planning* method. It produces documents that describe work; it is not a framework you build your
> application on top of, and your app should ship with Grillin uninstalled. Sections 7 and 8 are
> where it becomes relevant. Everything before that is true whether or not you ever use it.

---

## 1 · What you are actually working with

It is easy to assume this is a smarter autocomplete. It isn't, and that assumption is the source of
half the frustration.

Claude Code is a program that can **read your files, run shell commands, edit code, and look at the
output of what it just ran** — in a loop, on its own, until it decides it is finished. Think of it
less like a code-completion box and more like a contractor you have given a terminal and repository
access to.

That reframing carries real consequences:

| If you think it is… | You will… | And this happens |
|---|---|---|
| autocomplete | type a vague sentence and wait | you get confident work on the wrong problem |
| a search engine | ask "where is X?" and trust the answer | it tells you what it *found*, not what is *true* |
| a contractor | describe the outcome, the constraints, and how you'll check | you get work you can actually verify |

The third row is the whole guide.

---

## 2 · The one concept that explains most surprises: context

Everything Claude Code knows *right now* — your files it has read, the commands it ran, what you
said ten minutes ago — sits in one working memory called the **context window**. It is finite. When
it fills up, older material is compressed into a summary and the details are gone.

The closest thing you already know is a **database session**. Session variables and temp tables are
real and useful, and they vanish when the connection drops. Nobody would store the result of a
month's work in a temp table. That is exactly the mistake people make in conversation with an agent.

**The rule that follows from this is the most useful rule in the guide:**

> If a decision matters after this conversation, it has to end up **in a file in the repository**.
> Not in the chat. A conversation is a session, not a table.

This is why experienced users write things down constantly — the goal, the constraints, what "done"
means, what was tried and rejected. Not ceremony. Durability.

There is a practical corollary: **assume the agent has amnesia.** If a fresh session, given only your
repository, could not work out where things stand, then your progress lives somewhere fragile.

---

## 3 · Four ways it goes wrong, and what they look like

These are not hypotheticals. Each is a real incident, described plainly.

### 3.1 It says the work is done, and the work is not done

The most common one. You get a confident summary: "I've implemented the migration and verified it
works." Nothing ran. The summary describes intent, not outcome.

**Why it happens:** producing a convincing report is a different skill from doing the job, and
nothing forces the two to match unless you force it.

**The habit that fixes it:** ask for *evidence*, not a report. "Run it and show me the actual
output." A pasted test result you can read is worth more than three paragraphs of confidence.

### 3.2 The check passed because the check could not run

A real one, and it is nasty because it looks like success. A script called a binary that was not
installed. The shell printed `not found` and exited with status **127**. The surrounding code treated
"non-zero" as "the check ran and reported a clean failure."

Same shape, different clothes: a command was piped straight into a shell — `curl … | sh`. The URL
404'd because the repository was private, so the download was *empty*, so the shell ran *nothing*,
and exited **0**. Success. Nothing had been installed.

**The lesson, and it generalises far beyond agents:** an exit code tells you whether a process ran,
not whether it did anything. **Silence that resembles success is the worst outcome available** — much
worse than a loud failure, because nobody investigates it.

**The habit:** before you trust a check, make it fail on purpose once and confirm it *says so*. This
takes thirty seconds and it is the highest-value thirty seconds in this document.

### 3.3 It reads a name as proof of a thing

An agent surveyed a codebase and reported 21 modules as dead. They were live re-export shims with
**34 importers** between them. Deleting them would have broken the build.

Nothing was hallucinated. The files existed, and nothing imported them *directly*. The mistake was
inferential: a re-export is a usage pattern that does not look like usage textually.

The same class again: a tool's capability was recorded as CONFIRMED because the description string
appeared inside the compiled binary. The tool could not actually do the thing. **Reading a string is
not calling a function.**

**The habit:** for anything you'd have to undo painfully — deletions, schema changes, "this is
unused" — ask *how it was established*, not just *what was concluded*. "Show me the command you ran
that proves nothing imports this."

### 3.4 It loses the thread on a long job

Halfway through a large task the plot changes: the agent starts re-solving something it already
solved, or forgets a constraint you set forty minutes ago. This is section 2 arriving in person — the
context filled up and the early detail was summarised away.

**The habit:** break long work into pieces that each fit comfortably in one sitting, with a written
contract per piece. It is the same instinct as keeping transactions short.

---

## 4 · Six habits that make the difference

Everything above collapses into these.

**1. Say what "done" means as a command, not as a sentence.**
"The dashboard should be faster" is unfalsifiable. `npm run bench -- --p95 < 400` is not. If you can't
express your success criterion as something that exits zero or non-zero, you haven't decided what you
want yet — and the agent will decide for you.

**2. Prove the check fails before you trust that it passed.**
Section 3.2. Break it deliberately, once. If it still passes, your check is decorative.

**3. Never let the thing that did the work be the thing that certifies it.**
This is code review, and the reason is identical: the author's blind spots are in both the work *and*
the review of it. Start a *fresh* session, give it the requirement and the result but not the
reasoning, and ask it to find what's wrong. In one measured project, the mechanical checks caught
**2** defects and independent readers caught **50** — and they were *different* defects. Neither
layer substitutes for the other.

**4. Say what must not be touched.**
Agents are helpful, and helpfulness expands scope. "Fix the login bug. Do not touch the migrations,
do not reformat files you aren't changing, do not add dependencies." Constraints are cheap to write
and expensive to omit.

**5. Give each task exactly one owner and one output.**
If two pieces of work can both edit `config.py`, you have relocated a merge conflict to the most
expensive possible moment. One task, one owner, one named output file.

**6. Write the plan down before the work starts, in the repository.**
Not because process is virtuous — because of section 2. The plan is the thing that survives when the
conversation doesn't.

---

## 5 · The vocabulary, in plain terms

You will meet these words. None of them are complicated.

| Term | What it actually means |
|---|---|
| **agent** | the loop: read → decide → run a tool → look at the result → repeat |
| **tool** | something the agent can call — read a file, run a command, search, fetch a URL |
| **context / context window** | its working memory for this conversation. Finite. Section 2 |
| **compaction** | when that memory fills, older detail is replaced by a summary. Lossy, by design |
| **subagent** | a second agent started by the first, with its own fresh memory. Useful for "go read 40 files and tell me the conclusion" without filling *your* memory with 40 files |
| **hook** | a command that runs automatically at some moment — after a file is written, before a commit. Like a database trigger |
| **MCP** | a standard way to plug external tools in (your database, your ticket tracker) so the agent can use them |
| **model** | which Claude is doing the work. Bigger models reason better and cost more |
| **effort** | how hard it thinks before answering. Higher costs more and helps on genuinely hard problems, not on routine ones |
| **gate** | a check that must pass before work is considered finished. Your CI is a gate |
| **receipt vs. verdict** | *receipt* = the worker's claim that it finished. *verdict* = someone else re-running the check. Section 3.1 is the gap between them |

---

## 6 · How much structure does this job need?

Structure is a cost. Pay it where it earns its keep.

| The job | What to do |
|---|---|
| Change one file. Fix a typo. Explain some code | Just ask. Any process here is overhead |
| One feature, a few files, one sitting | Say what done means as a command. State what not to touch. Ask for the output |
| A day or more, many files, several stages | Write a short plan file first: the goal, the pieces, who owns what, how each piece is checked |
| Several agents working at once, over days | You want a real method. This is where Grillin is for |

**Most work is in the first two rows.** If you take one thing from this guide, take section 4's first
three habits and stop there.

---

## 6b · The skill that runs before this one

Claude Code ships a `brainstorming` skill, and it is the step in front of Grillin, not a
competitor to it. It classifies a request into one of three paths and refuses to write
anything until you have approved a design. Grillin cannot do that job: this method starts
once you have decided *what* to build, and its gate checks structure — a plan about entirely
the wrong problem passes every one of the 24 checks.

**The seam, and it matters.** On its architectural path that skill finishes by invoking its
own `writing-plans` skill. Do not let it. Grillin **is** the plan-writing method; running
both gives you two plans in two formats and no answer about which one an orchestrator obeys.
Take these from brainstorming:

- the **classification** — spike, bounded, or architectural
- the **questions**, asked one at a time, about purpose and constraints and success criteria
- the **2–3 approaches** with trade-offs, and the recommendation
- the **approval** — an explicit yes before any file exists

and then come to `QUICKSTART.md` step 1 instead of `writing-plans`.

**What Grillin does with it.** A plan of four tasks or more must record the outcome, or the
gate refuses it:

```
**Brainstormed:** architectural · approved 2026-08-19
```

At XS it is advisory — the band is data in `SCALING.json`, not a number written into the
checker, which is the mistake `check_persona_model` is still making.

**And one warning specific to agents.** The failure this guards is not laziness, it is
fluency: an agent handed a one-line ask will produce a beautiful, complete, internally
consistent plan directory in a single turn, and nothing about the artefact will look wrong.
The shipped example `examples/a-real-first-plan` is a real first-time user hitting exactly
this — its `04-SHAPE.md` says, in its own words, *"This diagram has not been approved… I wrote
the task contracts anyway."* That plan is this repository's **known-bad** calibration fixture,
and `check_brainstormed` is now one of the reasons it fails.

---

## 7 · Where Grillin fits

Grillin is a method for the fourth row: **writing a plan that several agents can execute without
colliding, and that survives everyone forgetting everything.** It gives you templates for the plan
and the tasks, and a script that reads your plan and refuses it if it isn't operable — every task has
an owner, every dependency resolves, every "done" is a runnable command, no two concurrent tasks own
the same file, and somebody is staffed to attack the result.

Two honest limits, stated up front:

- **It checks structure, not quality.** It cannot tell you whether your plan is a *good* plan. That's
  the independent reader's job, and the 2-versus-50 measurement in section 4 is why the method cares
  more about staffing that reader than about any structural rule.
- **It runs *on* a plan, from outside it.** Your application never imports it, never depends on it,
  and should build fine with Grillin uninstalled. If an agent starts adding Grillin concepts to your
  application's architecture, it has misread what it is — that has happened, which is why this
  paragraph exists.

The companion, **Smokin**, is for actually running such a plan across several agents. Its one idea is
the same as section 2's: there is no long-running coordinator holding state in memory. A command
reads the plan off disk, dispatches what is ready, records what came back, and exits. Kill everything
and run it again, and it reconstructs the same picture from the files.

---

## 8 · A worked example

**The request:** "Make the reports page faster."

**What a beginner sends:**

> The reports page is slow, can you speed it up?

What comes back is plausible, wide-ranging, and unverifiable. Some of it is probably an index you
didn't need and a cache you now have to reason about.

**What the same request looks like after a month:**

> The reports page takes ~4s to first byte for accounts with >50k rows. Target: under 1s at p95.
>
> - Start by measuring, not changing: show me where the time actually goes for account 1182.
> - Then propose a fix and tell me what you expect it to save, before you write it.
> - Done means `scripts/bench-reports.sh 1182` prints a p95 under 1000ms. Run it before your change
>   too, so we both have the baseline.
> - Do not add a caching layer, do not change the API response shape, do not touch other endpoints.
> - Nothing in `migrations/` without showing me the migration first.

Every line of that is one of the six habits. It took ninety seconds longer to write, it is
falsifiable, and you can hand the result to a fresh session and ask "did this actually work?"

---

## 9 · What to do this week

1. Take a task you'd normally describe in a sentence, and write the "done means" as a **command**.
2. Deliberately break one check you rely on, and confirm it *fails loudly*. Fix it if it doesn't.
3. Once, on something that matters, open a **fresh** session and ask it to find what's wrong with
   work you already accepted. Notice how much of what it finds the first session could not have found.
4. Move one thing you've been keeping in the conversation — a constraint, a decision, a list of
   what's been tried — into a file in the repository.

That's the whole practice, honestly. The tooling in this repository exists because those four things
get hard to hold onto once several people and several agents are involved — not because they stop
being the point.
