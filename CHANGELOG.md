# Changelog

## The policy, before the entries

**A new version can add checks, and a plan that passed before may fail after.**

That is not a regression. A check exists because a defect was found, so a plan that
starts failing has been failing all along — the gate has only just learned to see it.
The count went 21 → 23 in two days for exactly that reason.

If you need a plan to keep its answer across a job, **pin the version**:

```bash
GRILLIN_REF=v1.0.0 sh grillin-install.sh
```

Then update deliberately, between jobs, and read the entry below before you do.

Checks are only ever **added or tightened**, never quietly loosened. `self_check`
enforces that at runtime: the hardcoded floors cannot be lowered by a config file,
because a gate you can switch off with one line is not a gate.

---

## v1.0.0 — 2026-08-18

First public release. Everything below already existed; this is the point it got a
number so you can pin it.

**The method** — eleven phases, sixteen principles, twenty-seven anti-patterns, the
scaling model, and [`OPERATING-THE-PLAN.md`](OPERATING-THE-PLAN.md) for being inside a
plan after it turns out to be wrong.

**The gate** — 23 checks, python3 stdlib only. Calibrated in CI against a known-good
fixture that must pass and a known-bad example that must fail, and every check has a
mutation probe proving it fires on its own defect.

**Task types** — `Kind: research` for a timeboxed task graded on the findings it writes
rather than on what it found. Five first-time users each invented this independently
before it existed.

**Human-owned plans** — `**Workers:** human` in `PLAN.md` stands the model floor down.
A person has no model and no effort; their contracts freeze on delivery instead.

**Templates** — including `BRIEF.md.template` for one delegated task with no plan
directory around it.

### Known limits, stated rather than discovered

- `_owned_paths` reads disclaimers line by line. A "you do not own X" split across two
  lines still contributes X to the owned set — over-claiming is a loud false collision,
  which is the safe direction to be wrong in.
- `check-drift.py` and `check-boundary.py` are hardcoded to this repository's own files.
  They are not installed and they will not work on yours. `check-index.py` will.
- The gate proves a plan is **operable**, never that it is correct. On the one job
  measured end to end it caught 2 defects and the readers caught 50.
