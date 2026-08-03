# Phase 9 — Verify the environment this plan assumes ⚑

The method says this phase never scales down, and that in the source session it found four errors
in the plan's own text. Run against this plan.

---

## Verified

| Claim this plan makes | Check | Result |
|---|---|---|
| `~/grillin` exists and contains 7 top-level entries + `templates/` with 7 files | `ls -la`, `find` | **VERIFIED** |
| Every file this plan cites by `file:line` exists | `ls`, direct reads | **VERIFIED** — all 14 read in full |
| The repo has a GitHub remote | `git remote -v` → `git@github.com:A-Pex97/grillin.git` (fetch + push) | **VERIFIED** |
| Branch `main`, `origin/main` present, 11 commits | `git branch -a`, `git log --oneline` | **VERIFIED** |
| `SCALING.json` is valid JSON | `python3 -c "import json; json.load(...)"` | **VERIFIED** |
| Four sources define the scaling model and one disagrees | extracted all four | **VERIFIED** — `03-CONTRADICTIONS.md` C1 |
| 68 placeholders in `templates/` | `grep -ohE '<[a-z][^>]*>' templates/*.template \| wc -l` | **VERIFIED** |
| Zero filled examples | `grep -rilE 'example\|worked'` → one hit, an example *command* in `_HERDR.md.template` | **VERIFIED** |
| 3 broken links inside `templates/` | grep for `](_` targets, checked each against `ls` | **VERIFIED** |
| `git` and `python3` present, so T3's and T7's done-checks are runnable on this box | `which` | **VERIFIED** |
| `~/grillin` is writable by this user | `test -w` | **VERIFIED — and deliberately not used.** I am the method's user, not its author. |

## Corrections this phase made to my own text

**Correction 1 — `01-INVENTORY.md` said "Broken internal links: 0".**
Wrong. The grep behind it globbed `*.md` only and never touched `templates/*.template`, which
contains three. Fixed **at source** in `01-INVENTORY.md`; the row now separates the two globs and
gives the real count. Not logged and left standing — that is the failure the method warns about
(`GRILLING-THE-PLAN.md:406-409`).

The pattern, not the incident: **I wrote a count from a glob I did not check the coverage of.** So
I re-checked every other count in `01-INVENTORY.md` for the same fault. The placeholder count and
the template line counts are per-file and sound. The "0 files named quickstart/tutorial/example"
claim came from `ls` on two directories — sound, because there are only two.

**Correction 2 — I first sized this job XS (~1 hour) on impression, before counting.**
Phase 4's node count came out at 8, which is S. Principle 2: *count before you plan; numbers size
work, impressions don't.* I had committed to "small" from the brief's wording before counting
anything. Corrected at source in `PLAN.md`; the size call now cites the count.

## Not verified — and I will not verify these

| Assumption | Why not |
|---|---|
| **The GitHub repo is actually private.** | Inferred entirely from the task brief's wording. I did not query GitHub. If it is already public, T8 is a no-op and this plan's ending is wrong. **This is the single largest unverified assumption in the plan.** |
| The remote is reachable / the SSH key works | Would require a network call to a third party's host. Out of scope by the constraints I was given. T8 assumes `gh` or the web UI works; the author will find out in one command. |
| `gh` CLI is installed | `which gh` → **not found on this machine.** T8 step 4 names it. The author's machine is presumably not this one, but T8 should say "`gh` or the web UI" — it does. |
| `index.html` renders and behaves correctly | Read, not run. Its data matches `SCALING.json`. Behaviour is **REPORTED**. → T7 step 6. |
| Every pilot number in the repo | Unverifiable in principle from this repo — the pilot project is not here. → `03-CONTRADICTIONS.md` C8. |
| That the author agrees with any of this | Nobody was available. This is the root assumption under T1. |

## Topology

Trivial and worth stating anyway, because the method asks: everything is local, one machine, one
directory, no database, no server, no test harness, no build. The only remote is GitHub and only
T8 touches it.

**The one thing that is genuinely somewhere else is the author's judgement**, and four tasks
depend on it. In a software project phase 9 asks "which machine holds the database?"; here the
equivalent question is "which of these decisions lives outside this repository?" — and the answer
is four of them. That reframing is the only way this phase produced anything, and it is not in the
method.
