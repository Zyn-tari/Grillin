# T4 — Decide whether Grillin' is software-only, and say so on the front page

**Type:** RECONSIDER
**Status:** NOT STARTED
**Blocked by:** T1 (Q1, Q2) · **Blocks:** T2, T5
**Contended files:** `README.md`, `GRILLING-THE-PLAN.md` — **T3 lands first, you rebase onto it.**

**This is a RECONSIDER node. Its legitimate output is "don't build this."**

## Why this exists

`README.md:32-33` says:

> "Nothing here is tied to the codebase it came from. It is a method, not a framework: no install,
> no dependencies, no lock-in."

Counted against what ships (`01-INVENTORY.md`, VERIFIED):

- **7 of 11 phases assume code, a repo, commits, or a build.** Phase 1 wants `file:line`
  citations. Phase 5 wants file ownership and git branches. Phase 7 wants worktrees. Phase 8 wants
  a fan-out to time and a CPU load figure. Phase 9 wants scripts, permissions and repositories.
  The precedence ladder's rung 2 is literally "live code, live config, live data".
- **6 of 7 templates require an AI agent fleet under a specific harness.**
  `hooks.json.template` is harness config. `awareness.sh.template` is a 242-line shell program.
  `_HERDR.md.template` is 229 lines about one named third-party terminal multiplexer.

That is not "no install, no dependencies". It is a strong, specific, *interesting* opinion about
how work gets run — and a stranger should learn it from the README, not by bouncing off
`_HERDR.md.template` twenty minutes in.

**Evidence this is real, not theoretical:** this plan is a non-code job planned with Grillin'. Its
author had to re-point rung 2 of the precedence ladder at "the artefact as a stranger reads it"
because there was no running system, skipped phase 8 because there was no fan-out to measure, and
logged fourteen friction items, several of them of the form *"this step assumed I had a repo."*

## What you own

The scope claim, wherever it appears. Concretely: `README.md:32-33`, the README's opening framing,
and any phase text in `GRILLING-THE-PLAN.md` that needs a "this assumes you have a codebase" note.

## Steps

1. Read `tasks/T1/DECISIONS.md` Q1 and Q2. This task *applies* that decision; it does not make it.
2. Take one of three positions and write it in one paragraph on the README's front page:
   - **(a) Software-only, fleet expected.** Most likely correct. Amend `README.md:32-33` to say
     what it actually needs. Cost: one paragraph. Deletes work from T2 and T5.
   - **(b) Software-first, degrades to solo/non-code.** Then each of the 7 code-assuming phases
     needs one line saying what it becomes without a codebase, and the README says which templates
     are fleet-only. Cost: real, maybe a day.
   - **(c) General-purpose planning method.** Requires a non-software mode. **Out of scope for
     this plan** — if this is the answer, stop and re-plan at size M.
3. Whatever the answer: add a **"what you need before you start"** block near the top of the
   README. Three or four bullets. A codebase? An agent fleet? A harness with hooks? Say it.
4. Mark the fleet-only templates as fleet-only *in the README's file table*, not only inside the
   templates. `01-INVENTORY.md` has the 6-of-7 breakdown.

## Loop

None. This is a decision applied once. If it turns out to be (c), that is a stop-and-report to the
plan owner, not a loop iteration.

## Done means

`README.md` contains a paragraph naming the assumed context, and a "what you need" block, such
that a reader who does not have a codebase or an agent fleet can tell within 30 seconds whether
this method is for them. Checkable: hand the README to someone planning a non-code job and ask
"is this for you?" — they should answer immediately and correctly.

## Do NOT

- Do NOT hedge to keep the audience wide. A method that claims to fit everything fits nothing, and
  the honest narrow claim is the more useful one.
- Do NOT quietly delete the "no install, no dependencies" sentence. Replace it with what is true.
  Deleting it leaves the same wrong impression with nothing to correct it.
- Do NOT begin before T3 has landed its `GRILLING-THE-PLAN.md` edits.
- Do NOT expand into building a non-software mode. If that is the answer, stop.

## Outputs

`FINDINGS.md`, `CHANGES.md`, and — if the answer is (c) — `QUESTIONS.md` with a re-plan
recommendation.
