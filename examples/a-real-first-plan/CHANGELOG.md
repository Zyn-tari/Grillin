# Changelog — receipts for amendments to this plan

Per `GRILLING-THE-PLAN.md:429`: amend the plan in place, then leave a dated entry saying what
changed and why, referenced both ways. **This file is a receipt, never a substitute for the fix.**

---

## 2026-08-03 — size revised XS → S, before any task was written

`PLAN.md` §"Size call" amended. I had assumed XS (~1 hour) from the brief's framing before
counting anything. Phase 4 produced 8 nodes; `SCALING.json` puts 4–10 at S. The size line now
cites the count rather than the impression.

Reason: principle 2, *count before you plan*. See `09-ENVIRONMENT.md` §"Corrections this phase
made to my own text", Correction 2.

## 2026-08-03 — inventory link count corrected 0 → 3, at source

`01-INVENTORY.md` "Broken internal links" row amended and split in two. The original 0 came from a
grep globbing `*.md` only; `templates/*.template` holds three broken links. The wrong figure was
already cited by `03-CONTRADICTIONS.md` C7 and `tasks/T6/TASK.md` in draft; both now read from the
corrected row.

Reason: phase 9 pointed at my own artefact. See `09-ENVIRONMENT.md` Correction 1, and
`03-CONTRADICTIONS.md` C7.

## 2026-08-03 — phase 5 run at size S despite `SCALING.json` leaving it off

`PLAN.md` §"Size call" now carries an explicit declared deviation. `SCALING.json` gives S
`phasesOn: [0,1,2,3,4,9,10]` — no phase 5 — while phase 5 itself says "one folder per task,
**always**" and the checklist says "no exceptions, whatever the task count". Obeying
`SCALING.json` literally would have produced a diagram and no tasks.

Reason: `03-CONTRADICTIONS.md` C5. Resolving it properly is task **T3** step 4. This entry is the
receipt for having gone around it, not for having fixed it.
