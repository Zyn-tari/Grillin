# Changelog


## Unreleased

### The shape gets argued before the files exist — 2026-08-20

Every other check in this gate reads structure, and a plan can be structurally perfect and
about the wrong problem. QUICKSTART §0b was the first answer to that and it is necessary, not
sufficient: a curator can answer all five questions inside their own head in the same two
minutes they decided what to build.

- **New check `brainstormed`** (gate: 23 → 24). A plan of **4 tasks or more** must record that
  its shape was agreed with a person before the files were written:
  `**Brainstormed:** architectural · approved 2026-08-19`.
- **It is size-aware, and the band is read from `SCALING.json`** rather than written into the
  checker. That is deliberate: `check_persona_model` is size-BLIND while SCALING.json declares
  per-band behaviour, and two independent rounds of first-time users found the contradiction.
  A new scaling check with its own hardcoded bands would be the third place a band is written
  down and the second place it is wrong. `band_rule()` is the shared reader; a mutation to
  size-blindness fails 8 checks in `tests/test-brainstormed.py`.
- **The value is checked, not just its presence.** `spike` and `bounded` are defined as
  producing no plan document, so a five-task plan declaring itself bounded is a plan whose own
  header says it should not exist. The message says re-classify rather than relabel — the
  ratchet is one-way.
- **Approval is required, in those words** (`approved`, `agreed`, `signed off`). Presenting a
  design and starting in the same breath is the failure being recorded.
- **Claude Code's `brainstorming` skill is named as the mechanism**, with the seam stated:
  on its architectural path it ends by invoking its own `writing-plans` skill, and it must not
  — Grillin *is* the plan-writing method, and running both yields two plans in two formats.
  QUICKSTART §0 maps its three paths onto this method's size rows; the detail is in
  `WORKING-WITH-CLAUDE-CODE.md` §6b, and `OPERATING-THE-PLAN.md` §11 records it as ENFORCED.
- **Calibration held, and got more honest.** `examples/minimal-passing-plan` records the field
  and still exits 0. `examples/a-real-first-plan` still exits 1 — and it is a genuine specimen
  of this exact failure: its own `04-SHAPE.md` says *"This diagram has not been approved… I
  wrote the task contracts anyway."*

`tests/test-brainstormed.py` — 44 checks.

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
