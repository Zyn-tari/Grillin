# T3 — Reconcile the four scaling sources and the two evidence vocabularies

**Type:** REFACTOR
**Status:** NOT STARTED
**Blocked by:** T1 for Q3 only — **the rest can start today** · **Blocks:** T7
**Contended files:** `GRILLING-THE-PLAN.md` (shared with T4 — **you land first, T4 rebases**),
`SCALING.json` + `index.html` (**single owner: you**; they must change together or the
interactive map lies), `README.md`, `CASE-STUDY.md`, `templates/GRILL-CHECKLIST.md`,
`templates/_RULES.md.template`.

## Why this exists

Four files define the scaling model and one of them disagrees. `GRILLING-THE-PLAN.md:470` tells an
XS user to run phases 0, 3, 9 — omitting phase 10 — while `README.md:81`, `SCALING.json` and
`index.html` all say 0, 3, 9, **10**. The method's own last anti-pattern is *"Ship a plan with no
entry point | nobody can start it."* The file the README calls "the method" currently instructs
its smallest users to commit it.

Separately, the repo uses **two vocabularies for the same evidence label** — VERIFIED/REPORTED in
the prose, CONFIRMED/SUSPECTED in the checklist, rules template and `SCALING.json`. A first-time
user picks one and fails the checklist. I did exactly that; this plan's registers use
VERIFIED/REPORTED and fail `templates/GRILL-CHECKLIST.md:26`.

This is the method's phase 3 pointed at the method. `03-CONTRADICTIONS.md` is the register.

## What you own

Every file listed under Contended files. You own the *scaling model* and the *evidence
vocabulary* across the whole repo. You do NOT own the templates' link conventions (T6) or the
software-only framing (T4).

## Steps

1. Read `03-CONTRADICTIONS.md` C1, C2, C3, C5, C6.
2. **C1:** fix `GRILLING-THE-PLAN.md:470` to `0, 3, 9, 10`. Then grep the whole repo for every
   other place the XS phase set appears and confirm all four now agree. *A bad fact is usually
   written down more than once* (`GRILLING-THE-PLAN.md:409`).
3. **C2:** pick one vocabulary. Change every occurrence of the loser. Six files carry it:
   `GRILLING-THE-PLAN.md`, `CASE-STUDY.md`, `templates/GRILL-CHECKLIST.md`,
   `templates/_RULES.md.template`, `SCALING.json` (`taskContract.outputs`), `TASK.md.template`.
   If the split is deliberate — prose one way, operational files the other — then **say so in one
   line in the checklist** rather than leaving a reader to infer it.
4. **C5:** decide where the tasks of an S-sized project get written down. `SCALING.json` leaves
   phase 5 off at S while phase 5 says "one folder per task, **always**, regardless of how many
   tasks there are" and the checklist says "no exceptions, whatever the task count". Either turn
   phase 5 on at S in reduced form, or soften the "always". Both are defensible; leaving both
   absolutes standing is not.
5. **C3:** in `CASE-STUDY.md`, annotate each numbered step with the phase it became, or drop the
   step numbers. Fix `CASE-STUDY.md:213` — it cites "steps 4, 9 and 10" where the README flags
   phases 3, 8, 9. Both are right in their own numbering and a cross-referencing reader lands
   wrong three times out of three.
6. **C6/Q3:** once `tasks/T1/DECISIONS.md` answers Q3, state in `SCALING.json` and in phase 10's
   text which of phase 10's five outputs survive at XS.
7. Regenerate nothing by hand that can be checked mechanically: after editing, re-extract the
   phase sets from all four sources and diff them.

## Loop

**Converge, cap 3.** Edit → re-extract all four scaling sources and diff → fix → have someone who
did not make the edit re-run the diff → re-verify. Exit when the four sources produce byte-identical
phase sets for all five sizes and one grep finds one vocabulary. Cap hit = stop and report which
source keeps drifting; that is a structural problem, not an editing problem.

## Done means

Both of these commands produce the stated result, re-runnable by anyone:

```
# all four sources agree on every size
python3 - <<'EOF'
import json,re
j=[s['phasesOn'] for s in json.load(open('SCALING.json'))['scaling']]
h=[eval(m) for m in re.findall(r'on:(\[[\d,]*\])', open('index.html').read())]
print('json ==  html:', j==h)
EOF
# → True, and the README + GRILLING tables read the same by eye

grep -rn 'REPORTED\|SUSPECTED' --include=*.md --include=*.json --include=*.template .
# → one vocabulary only, or a documented split with the documenting line in the output
```

## Do NOT

- Do NOT fix `GRILLING-THE-PLAN.md` and leave `SCALING.json` and `index.html` — they are one
  artefact in three encodings and the map is the thing users trust.
- Do NOT resolve C5 by quietly deleting the word "always". That is a real design decision; write a
  line saying which way it went and why.
- Do NOT touch the software-only framing. T4 owns it.
- Do NOT start step 6 before `tasks/T1/DECISIONS.md` exists.

## Outputs

`FINDINGS.md`, `CHANGES.md`
