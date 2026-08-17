# Phase 2 — Triaged defect register

Recon always finds defects. Sort them, never absorb them. Buckets per
`GRILLING-THE-PLAN.md:86-90`.

Evidence labels: this file uses **VERIFIED / REPORTED** per `GRILLING-THE-PLAN.md:71`, which means
it fails `templates/GRILL-CHECKLIST.md:26` ("CONFIRMED vs SUSPECTED labelled throughout"). See
`03-CONTRADICTIONS.md` C2.

---

## A — fix during the work

In files being edited anyway; no change to what the method *means*.

| # | Defect | Evidence | Task |
|---|---|---|---|
| A1 | `GRILLING-THE-PLAN.md:470` XS row omits phase 10 | VERIFIED — C1 | T3 |
| A2 | CONFIRMED/SUSPECTED vs VERIFIED/REPORTED split across 6 files | VERIFIED — C2 | T3 |
| A3 | `CASE-STUDY.md` step numbers off by one from phase numbers after step 2; `:213` cites the wrong three | VERIFIED — C3 | T3 |
| A4 | 3 broken links inside `templates/`; 2 conventions in use | VERIFIED — C7 | T6 |
| A5 | `SCALING.json:2` `$schema` points at the meta-schema | VERIFIED — C9 | T6 |
| A6 | `.gitignore` ignores `node_modules/` in a repo with no code | VERIFIED — C9 | T6 |
| A7 | No `QUICKSTART`; 865 lines to read before the first action | VERIFIED — `01-INVENTORY.md` | T2 |
| A8 | 68 placeholders, 0 filled examples anywhere | VERIFIED — `01-INVENTORY.md` | T5, T6 |

## B — needs a human decision. **These block the plan.**

Product/framing semantics. I do not decide these. All four are for the repo author.

| # | Question | Why I cannot answer it | Blocks |
|---|---|---|---|
| **Q1** | **Is Grillin' software-only?** Yes → one sentence in the README and the job is small. No → a non-software mode has to be designed, and this plan is the wrong size. | 7 of 11 phases assume code; the README claims none of that. Only the author knows which was intended. | T4 → T2, T5 |
| **Q2** | **Is the agent fleet mandatory, recommended, or optional?** 6 of 7 templates need one. A solo human planner can use the eleven phases and one template. | Changes what "a stranger can follow it" even means. | T4 → T2 |
| **Q3** | **At XS, which parts of phase 10 survive?** Phase 10 is on; its "status surface" output is explicitly off. The other four are unstated. | C6 — unresolvable from the text. | T3 |
| **Q4** | **May the pilot's project details be published?** `CASE-STUDY.md` describes a live web app, its route counts, its unbuilt endpoints, a constant disagreement, an unreadable root-owned deploy script. Public repo publishes all of it. | Third-party disclosure. Not mine to clear. | **T8 — hard block on publishing** |

## C — real, out of scope, recorded not scheduled

| # | Finding | Why out of scope |
|---|---|---|
| C-1 | No CONTRIBUTING, no issue templates, no code of conduct | Publishing ≠ running a community. Add when someone files an issue. |
| C-2 | No versioning/changelog discipline for the method itself; `SCALING.json` says `1.0.0`, nothing else carries a version | Worth doing eventually. Not needed for a stranger to produce a plan. |
| C-3 | `index.html` is not verified in a browser | REPORTED. Cheap for the author to check, pointless for me to plan around. |
| C-4 | The method has been run **once**, by its author. Two of its phases (7, 8) rest entirely on that one run. | Not fixable by documentation. Fixable only by other people running it — which is what publishing is for. This plan's own friction log is the second data point in existence. |
| C-5 | The eleven-phase method is a *description of one session* generalised into a *prescription*. `README.md:146` says so: "The phases are **descriptive, not invented**". | That is a strength for honesty and a risk for generality. Out of scope; flagged for the author. |

---

**Scope creep this triage prevented:** C-2 and C-1 both felt like "obviously you'd do that before
publishing", and both would have added tasks. Neither is required by the definition of done in
`PLAN.md`. They are recorded, not scheduled. That is the phase working.
