# Phase 3 — Contradictions register ⚑

**The method calls this the highest-value phase and says it produces no plan text. It was right.**
This register produced no plan text and six of the eight tasks.

**What "the running system" is here.** The method's ladder says rung 2 is "live code, live config,
live data — beats every document". There is none. I re-pointed rung 2 at *the artefact as a
stranger reads it, plus the observed friction of running it*. That substitution is itself a
finding — see `FRICTION.md` F-02.

Nothing below is resolved silently. Each says which source wins and why.

---

## C1 — Four sources define the scaling model. Three agree. One does not. **BLOCKING**

`GRILLING-THE-PLAN.md:470`:

> `| **XS** | 1–3 | Phases 0, 3, 9. No fan-out, no skills, no isolation. ~1 hour of planning. |`

`README.md:81-83`:

> "**Small change — 1–3 tasks, ~1 hour:** run phases **0, 3, 9, 10**. Declare precedence, grill
> the spec against the running system, verify the environment, ship an entry point. Skip the rest."

`SCALING.json`, `scaling[0]`: `"phasesOn": [0, 3, 9, 10]`
`index.html:235`: `{size:"XS",tasks:"1–3",effort:"~1 hour",on:[0,3,9,10], ...}`

**Which wins:** the three-way majority (0, 3, 9, 10), and independently the method's own
anti-pattern table settles it: `GRILLING-THE-PLAN.md:513` — *"Ship a plan with no entry point |
nobody can start it"*. A scaling row that omits phase 10 instructs you to commit the last
anti-pattern in the list.

**Why it matters more than a typo:** the first thing a new user does is pick a size, and
`GRILLING-THE-PLAN.md` is the file the README calls "the method". A first-timer reading the method
file top to bottom is told to ship a plan nobody can start. → **T3**

---

## C2 — Two different vocabularies for the same evidence label. **BLOCKING**

`GRILLING-THE-PLAN.md:71` — "Label **VERIFIED** (read it) vs **REPORTED** (inferred)."
`GRILLING-THE-PLAN.md:92` — "Label each **VERIFIED** or **REPORTED**."
`CASE-STUDY.md:70` — "Each labelled **VERIFIED** ... or **REPORTED**".

versus

`templates/GRILL-CHECKLIST.md:26` — "CONFIRMED vs SUSPECTED labelled throughout"
`templates/_RULES.md.template:107` — "cite `file:line`; **CONFIRMED** vs **SUSPECTED**"
`SCALING.json`, `taskContract.outputs.FINDINGS.md` — "CONFIRMED vs SUSPECTED"

**Which wins:** no rule in the method decides this, because both sources sit at the same rung. It
is a genuine fork, not drift.

The method *is* consistent about the split: the prose files use VERIFIED/REPORTED, the operational
files (checklist, rules template, machine-readable contract) use CONFIRMED/SUSPECTED. That could
be deliberate — but nothing says so, and the checklist's line "CONFIRMED vs SUSPECTED labelled
throughout" is a checklist item that will fail against every artefact the method's own prose tells
you to write. This document uses VERIFIED/REPORTED and therefore fails
`GRILL-CHECKLIST.md:26`. I could not tell whether I had done it right. → **T3**

---

## C3 — `CASE-STUDY.md` numbers twelve steps for eleven phases, and cross-references the wrong ones

`CASE-STUDY.md` runs steps 0–11. The method has phases 0–10. The extra is step 2, "The first
correction — invisible tiering", which is a story beat, not a phase. Everything after it is
**off by one** from the phase it corresponds to.

Then `CASE-STUDY.md:213`:

> "Three of the eleven steps produced **no plan text at all** — steps 4, 9 and 10"

while `README.md:63,68,69` flags phases **3, 8, 9**. Both are correct in their own numbering and a
reader moving between the two files lands on the wrong phase three times out of three. Case-study
step 10 ("Verify the environment") is method phase 9; case-study step 9 ("Choose the substrate")
is method phase 8.

**Which wins:** `GRILLING-THE-PLAN.md`'s numbering — it is the method. The case study should
either drop its own numbers or annotate each step with the phase it became. → **T3**

---

## C4 — "No install, no dependencies, no lock-in" is not true of the templates. **BLOCKING**

`README.md:32-33`:

> "Nothing here is tied to the codebase it came from. It is a method, not a framework: no install,
> no dependencies, no lock-in."

Checked against what ships:

- `templates/hooks.json.template` is configuration for a specific AI coding harness's hook system.
  That is an install.
- `templates/awareness.sh.template` (242 lines) is a shell program with modes, wired to that hook
  config.
- `templates/_HERDR.md.template` (229 lines) is 100% about driving one named third-party terminal
  multiplexer. `README.md:48` even describes it as "the **secondary** substrate". That is a
  dependency and a named vendor.
- `templates/_WORKTREES.md.template` requires git worktrees.
- `templates/_RULES.md.template` requires an agent fleet with model tiers.

**6 of 7 templates are unusable without an AI agent fleet running under a specific harness**
(`01-INVENTORY.md`). The eleven-phase *method* is genuinely portable. The templates — which is
what the README's own "Start here" table sends you to — are not.

**Which wins:** the artefact. The claim is the thing that is wrong, not the templates.
→ **T4** decides the framing, **T2** and **T7** apply it.

---

## C5 — Phase 5's "always" is switched off at the size where it first applies

`GRILLING-THE-PLAN.md:141`:

> "**One folder per task. Always, and regardless of how many tasks there are.** Three tasks or
> forty, the structure does not change"

`templates/GRILL-CHECKLIST.md:41`:

> "**One folder per task** — `tasks/<ID>/`, no exceptions, whatever the task count"

But `SCALING.json` gives S (`4-10 tasks`) `phasesOn: [0,1,2,3,4,9,10]`. **Phase 5 is off.** So at
4–10 tasks the method both mandates one folder per task "no exceptions" and does not run the phase
that creates them. Nothing in the method says where the tasks of an S-sized project are written
down. XS has the same hole with 1–3 tasks.

**Which wins:** the "always" — it is stated twice, absolutely, and the checklist enforces it. I
therefore ran phase 5 in reduced form at size S and recorded the deviation in `PLAN.md`. But I
guessed, and a first-time user who obeys `SCALING.json` literally produces a diagram and no tasks.
→ **T3**

---

## C6 — Phase 10 is "on" at XS but half its outputs are "off" at XS

`SCALING.json` XS: `phasesOn: [...10]` and `leaveOff: [..., "status surface"]`.
Phase 10 (`GRILLING-THE-PLAN.md:337-351`) lists five required outputs, one of which is "**A status
surface** the requester can read without asking". So phase 10 is on and one fifth of it is off.

Nothing tells you which of the other four also drop out at XS. Is "persistent memory updated"
required on a one-hour job? I could not tell. **Which wins:** unresolvable from the text; needs
the author. → bucket B, `02-TRIAGE.md` Q3.

---

## C7 — Three broken links inside `templates/`, and the templates disagree on the convention

`templates/_RULES.md.template:74` → `[_HERDR.md](_HERDR.md)` — no such file; it is
`_HERDR.md.template`.
`templates/_AWARENESS.md.template:213` → `[_RULES.md](_RULES.md)` — same.
`templates/_HERDR.md.template:6` → `[_RULES.md](_RULES.md)` — same.

But `templates/_WORKTREES.md.template:86` → `[_AWARENESS.md](_AWARENESS.md.template)` — link text
without the suffix, target *with* it. And `GRILLING-THE-PLAN.md:228` does the same.

So the repo uses two conventions and the more common one is broken on GitHub. Defensible
intent — after you copy a template into your project you drop `.template`, so the links come
right — but nothing anywhere says that, and a stranger browsing the repo clicks a 404. → **T6**

---

## C8 — Every number the method uses to justify itself is unverifiable from the repo

"roughly **30 errors**" (`README.md:29`), "a 29-file executable plan" (`README.md:29`), "capped at
**2** concurrent (1.78× effective); the other sustained **4.9×**" (`CASE-STUDY.md:170-172`), "all
twenty-six *planned* folders survived intact" (`GRILLING-THE-PLAN.md:155`), "a 58-test suite
retired for a 16-test smoke suite" (`GRILLING-THE-PLAN.md:446`), "verbatim survival into the
summary measured 1/2; the post-boundary register measured 3/3"
(`templates/GRILL-CHECKLIST.md:105-106`).

The method's own principle 10 is "**Measure constraints; never quote them — then check the
instrument, and label the conditions.**" A reader of this repo can only quote. The pilot is not
here; no measurement, no instrument, no conditions ship with it.

**This is not a defect to fix — you cannot publish someone else's live product.** It is a
framing decision: say plainly that the numbers come from one unpublished pilot, or drop the
precision. It also interacts with FLAG 3 — the case study already publishes a lot about that
system. → bucket B, `02-TRIAGE.md` Q4.

---

## C9 — Small, non-blocking

- `.gitignore` ignores `node_modules/` and `*.log` in a repository containing no code. Harmless,
  but it is the first file a curious stranger opens after README and it implies a build.
- `SCALING.json:2` declares `"$schema": "https://json-schema.org/draft/2020-12/schema"` — that is
  the meta-schema, i.e. the file is claiming to *be* a JSON Schema. It is not; it is data. Anything
  that actually validates it will fail. → **T6**
- `README.md:172` — "Derived from one planning session, 2026-07-31." Honest and easy to miss. It
  is the single most useful sentence for calibrating trust and it is in `<sub>` tags at the bottom.

---

## What this register did to the work

Phase 3 promises: "Expect it to resize the work."

Before running it I expected roughly three tasks: write a quickstart, tidy the README, flip the
repo public. After it: **eight**, four of them existing only because of C1, C2, C4 and C5 — and
one of them (T1) existing because four of these contradictions cannot be resolved by anyone
except the author.

The phase paid for itself. It is also the only phase in the method that did.
