# T7 — Grill the repo against itself before it goes public

**Type:** VERIFY / LOOP
**Status:** NOT STARTED
**Blocked by:** T2, T3, T4, T5, T6 · **Blocks:** T8
**Contended files:** you are the integrator. You apply README edits last, in order
T2 → T3 → T5 → T7, and you are the only one who amends `PLAN.md`.

## Why this exists

This is phase 9 — *verify the environment the plan assumes* — pointed at the artefact itself, plus
"grill your own artefact last and hardest" (`GRILLING-THE-PLAN.md:399`). The method says phase 9
never scales down, and that in the source session it found **four errors in the plan's own text,
written by the author who had spent the session warning about exactly that**
(`GRILLING-THE-PLAN.md:330-331`).

It already happened once on this plan, in miniature: `01-INVENTORY.md` originally recorded "broken
internal links: 0". That count came from a grep over `*.md` only. `templates/*.template` was never
scanned, and it contains **three** broken links. The count was corrected at source rather than
noted somewhere — which is what `GRILLING-THE-PLAN.md:406-409` demands.

Publishing is irreversible in the way that matters: a stranger's first clone is a first
impression.

## What you own

Verification of the whole repository. You do not add features. You correct, and you correct **at
source** — never in a log.

## Steps

1. **Run `templates/GRILL-CHECKLIST.md` against this repository.** All of it. Record which items
   do not apply to a documentation job and *why* — that list is itself a finding for the author,
   because it measures how much of the checklist assumes code.
2. **Every link resolves.** All `.md`, all `.template`, `index.html`, and this time include
   `templates/`. The last count was wrong because the glob was wrong.
3. **Every path named in every file exists**, and in this repository.
4. **Every count re-derived, not trusted.** `01-INVENTORY.md` is frozen; frozen means nobody
   re-derives it *during* the work. Before publishing, re-derive it once — the repo changed under
   T2/T5/T6 and the inventory now describes a repo that no longer exists.
5. **Every number in the repo traced to a source or dropped.** `03-CONTRADICTIONS.md` C8 lists
   them: "~30 errors", "29-file plan", "4.9× effective parallelism", "26 folders", "58 tests
   retired for 16", "1/2 verbatim survival". None is verifiable from the repo. Principle 10 is
   *measure, never quote*. Either mark them plainly as one unpublished pilot's figures, or cut the
   decimal places. **Do not leave a precise number with no traceable instrument in a method whose
   tenth principle forbids exactly that.**
6. **Open `index.html` in a real browser.** It was never verified running — only read. Confirm its
   phase and scaling data still match `SCALING.json` after T3's edits.
7. **Two cold readers.** Neither has seen Grillin'. Each gets only the clone URL and this
   instruction: *"produce a plan for a small real task of your own, and log every point of
   friction."* Keep both logs in this folder. Every question they had to ask a human is a defect —
   file it in `02-TRIAGE.md`, do not answer it in a reply.
8. Amend `PLAN.md` for anything that moved, and add a dated line to `CHANGELOG.md` pointing at the
   clause. The changelog is a receipt, never a substitute for the fix.

## Loop

**Converge, cap 3.** Verify → fix at source → **someone who did not make the fix confirms it** →
re-verify. Exit when both cold readers reach a written plan artefact with zero questions to a
human, and every check in "Done means" passes.

Hitting cap 3 is a **stop-and-report**, not a quiet partial, and it means something structural is
wrong — most likely T4's scope answer. Report it; do not iterate a fourth time.

## Done means

All of these, re-runnable by anyone:

```
# every link target exists, templates included
grep -rohE '\]\([^)#][^)]*\)' --include=*.md --include=*.template --include=*.html . \
  | sed 's/^](//;s/)$//' | sort -u | while read f; do [ -e "$f" ] || echo "BROKEN: $f"; done
# → no output

python3 -c "import json;json.load(open('SCALING.json'))"    # → no error
grep -rc '<[a-z]' examples/ templates/examples/             # → 0
```

plus: **two named cold readers, two friction logs in this folder, two plan artefacts produced,
zero questions escalated to a human.** That last clause is the actual definition of done for the
whole plan and this is the task that evidences it.

## Do NOT

- Do NOT fix a defect and then confirm your own fix. `GRILLING-THE-PLAN.md:501` — that is
  self-certification one level down.
- Do NOT record a correction in a log while leaving the wrong text in place. Fix at source.
- Do NOT skip the two cold readers because the checklist passed. The checklist is the author's
  model of the reader; the readers are the reader.
- Do NOT treat a cold reader's question as a support request. It is a defect report.
- Do NOT proceed to T8 on green checks alone if Q4 is unanswered.

## Outputs

`FINDINGS.md`, `CHANGES.md`, two cold-reader friction logs, `CHANGELOG.md` entries,
the applicability list from step 1.
