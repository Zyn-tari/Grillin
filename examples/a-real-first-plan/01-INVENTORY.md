# Phase 1 — Inventory (FROZEN 2026-08-03)

**The method says:** fan out read-only workers, partition by file ownership, cite `file:line`,
give counts, label VERIFIED vs REPORTED, end with "what I did not verify", use your cheapest
capable model. Freeze it. Nothing downstream re-derives it.

**What I actually did:** counted it myself, in one pass, in about four minutes. Fanning out
workers to enumerate a fourteen-file repository would have cost more to set up than to do.
`SCALING.json` says S = "2-3 recon workers". I ran zero. Logged as F-05.

**Frozen.** Everything downstream cites this file instead of re-counting.

---

## Repository: `~/grillin` — what exists

| Path | Lines | What it is |
|---|---|---|
| `README.md` | 172 | Front door. Phase table, scaling summary, "the parts most people skip". |
| `GRILLING-THE-PLAN.md` | 513 | The method proper. 11 phases, 16 principles, 25 anti-patterns. |
| `CASE-STUDY.md` | 221 | The origin session, 12 numbered steps. |
| `SCALING.json` | ~880 | The whole method as data. 19 top-level keys. |
| `index.html` | 353 | Interactive phase map, self-contained, data inlined in JS. |
| `LICENSE` | 21 | MIT, © 2026 Zyntari. |
| `.gitignore` | 3 | `.DS_Store`, `node_modules/`, `*.log` — a Node .gitignore in a repo with no code. |
| `templates/` | 7 files, 1,184 lines | see below |

**Total shipped prose: 1,280 lines across 5 documents + 1,184 lines of templates = 2,464 lines.**

## Templates — 7 files

| Template | Lines | Angle-bracket placeholders | Usable by a solo human? |
|---|---|---|---|
| `TASK.md.template` | 80 | **21** | partly |
| `_RULES.md.template` | 186 | 10 | no — agent fleet |
| `_HERDR.md.template` | 229 | 14 | no — requires a specific managed-terminal tool |
| `_WORKTREES.md.template` | 132 | 19 | no — requires git worktrees |
| `_AWARENESS.md.template` | 214 | 0 | no — agent harness hooks |
| `awareness.sh.template` | 242 | 4 | no — shell reporter for an agent fleet |
| `hooks.json.template` | 101 | 0 | no — harness config |

**68 placeholders total.** VERIFIED by `grep -ohE '<[a-z][^>]*>' templates/*.template | wc -l`.

**Templates a non-software, non-fleet user can use: 1 of 7** (`TASK.md.template`, and only after
deleting the branch/worktree/commit sections). VERIFIED by reading all seven.

## Counts that size the work

| Thing | Count | How |
|---|---|---|
| Files a stranger must read before they can start | **5** minimum (README → GRILLING → checklist → 2 templates) | VERIFIED |
| Lines they must read before their first action | **~865** (README 172 + GRILLING 513 + checklist 137, minus overlap) | VERIFIED |
| Files named "quickstart", "getting started", "tutorial", "example" | **0** | VERIFIED — `ls` |
| **Completed, filled-in artefacts anywhere in the repo** | **0** | VERIFIED — grep for "example" hits one file, `_HERDR.md.template`, and it is an example command not an example plan |
| Places the scaling model is defined | **4** (`README.md:81-89`, `GRILLING-THE-PLAN.md:468-474`, `SCALING.json` `scaling[]`, `index.html:234+`) | VERIFIED |
| Of those 4, how many agree on XS | **3** | VERIFIED — see C1 |
| Phases that assume you have code/a repo/commits/a build | **7 of 11** (1, 2, 5, 6, 7, 8, 9) | VERIFIED by reading each phase's Output line and steps |
| Templates that assume an AI agent fleet | **6 of 7** | VERIFIED |
| Broken internal links in the five `.md` documents | **0** | VERIFIED — extracted all 13 link targets, all resolve |
| Broken internal links **inside `templates/`** | **3** | VERIFIED — `_RULES.md.template:74` → `_HERDR.md`, `_AWARENESS.md.template:213` → `_RULES.md`, `_HERDR.md.template:6` → `_RULES.md`; none of those three files exist, they are all `*.md.template`. A fourth, `_WORKTREES.md.template:86`, links to `_AWARENESS.md.template` **with** the suffix — so the templates do not agree with each other on the convention. |
| Git commits | 11 | VERIFIED — `git log --oneline` |
| Git remote | `git@github.com:Zyntari/Grillin.git`, branch `main`, `origin/main` present | VERIFIED |

## What I did not verify

- **Whether the GitHub repo is actually private.** I inferred it from the task brief. I did not
  and will not hit the GitHub API. If it is already public, T8 is a no-op and this plan's ending
  is wrong.
- **Whether `index.html` renders correctly.** I read its source and extracted its data; I did not
  open it in a browser. Its phase/scaling data matches `SCALING.json`. Its *behaviour* is REPORTED,
  not VERIFIED.
- **`SCALING.json` against a JSON Schema.** It declares `$schema: json-schema.org/draft/2020-12`,
  which is the schema-for-schemas, not a schema this document conforms to. It parses as JSON
  (VERIFIED, `python3 -c json.load`). Whether that `$schema` line means anything is REPORTED.
- **The pilot's numbers.** "~30 errors", "29-file plan", "4.9× effective parallelism", "26 task
  folders", "58 tests retired for 16". Every one is unverifiable from this repo — the pilot
  project is not here. They are the method's own evidence and none of it ships with it.
- **Whether the author agrees with any of this.** Nobody was available.
