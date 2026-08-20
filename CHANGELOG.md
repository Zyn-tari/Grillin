# Changelog



## Unreleased

### The CI was failing, and it was failing honestly — 2026-08-20

Two probes in `.github/workflows/gate.yml` reported their own checks dead on every run. That
is the failure mail, and both were the exact defect class the probes exist to catch: **a
mutation that does not apply.**

- `model-is-tier-word` sed'd `claude-sonnet-5` while the fixture says `claude-opus-5`, so the
  plan stayed unmutated and green.
- `done-self-ref` used `|` as its `s///` delimiter over a replacement containing a pipe, so
  sed died with ``unknown option to `s'``.

All 31 probes now fire. **Five harnesses had no CI step at all** — `brainstormed`,
`gate-fails-first`, `citations-and-promises`, `check-accounting`, and the human-worker example
— and a check with no CI step only runs when somebody remembers, which is what the two dead
probes look like from the inside.

### Two numbers that did not add up

- **The size table overlapped the gate.** `GRILLING-THE-PLAN.md` said M `10–25`, L `25–60`,
  XL `60+` while `BANDS` says `11–25`, `26–60`, `61+` — so a 25-task plan was two sizes. It
  survived because `check-drift.py` compared `BANDS` to `SCALING.json` and never to the prose.
- **"the readers caught 50" could not be added up.** Health found ~20, the adversary 44 (30
  blocking + 14 non-blocking), plus 1 fixture defect — which sums to 64, not 50. The headline
  counts health plus the adversary's *blocking* findings, and nothing said so. Now recorded in
  `measurement.headlineDecomposition`, and the gate prints this number on every run, so it had
  better be addable.

**Both are now drift checks** (7 and 8), each mutation-proven, because the reason each survived
is that nothing was reading that surface.

### Asking and owning are two things

`OPERATING-THE-PLAN.md` §10a names them apart. **ASKING** — the work is an agent's, only the
decision is yours: `QUESTIONS.md` → `ANSWER.md`, and the plan does not stop while it waits.
**OWNING** — the work itself is a person's. Reach for asking unless the *work* is human, not
just the decision.

The template said *"record it in `QUESTIONS.md` and stop"*, which is now the opposite of what
the tools do: the worker stops its own branch, never the plan. And the `**Workers:** human`
exemption hole is recorded as a stated limit rather than left implicit — the plan-level line
lifts the model floor for every task while the freeze reads each task's Owner, so write both.

## v1.1.0 — 2026-08-20

**Read this before you re-run the gate on a plan that was green.** This release changes
verdicts in BOTH directions, which no previous release has done:

- Plans of **4 tasks or more that were passing will now FAIL** until they add a
  `**Brainstormed:**` line. That is a new obligation, not a bug fix.
- Plans that were **failing on `gate-fails-first` may now PASS**, because a done-command that
  grades content is no longer misread as a broken gate. If a plan of yours goes green here,
  it was green all along and the gate was wrong.

The gate is **24 checks**, up from the 23 that v1.0.0 shipped. `--version` reported "1.0.0"
alongside "gate: 24 checks" for a few hours today — the same version string describing two
different gates, which is the exact class of defect this repo exists to catch.

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

### The `grep` trap — 2026-08-20

**Open since v1.0.0, recommended by our own QUICKSTART, and reached independently by four
first-time users.** A done-command that grades CONTENT — `grep -q DONE tasks/T1/OUT.md` —
says "No such file or directory" while the work is unstarted, because the artefact it grades
does not exist yet. That is the gate working. `check_gates_fail_first` called it a broken
gate and told the author *"Its paths are unanchored"*, which was false: the path was
anchored; `grep` exits 2 on stderr where `test -s` exits 1 silently.

The wasted cycle was never the cost. **The documented way out is a bare `test -s`, which is
satisfied by writing any file at all** — so the refusal pushed authors off a gate that reads
content and onto one that gates paperwork. A curator said exactly that, unprompted.

- **A missing FILE is now ambiguous and gets resolved.** Inside the plan directory → an
  artefact the plan has not produced yet → clean fail. Outside it → a gate that cannot run
  here → still refused, and the message now names the file instead of blaming the author's
  paths. Exit `126`/`127` and a shell naming a missing tool, module, permission or syntax
  error remain blow-ups, by exit status where possible because dash and bash word them
  differently.
- **Diagnosis is read from stderr only.** This fixes the mirror defect reported from the
  field: a check that PASSED while printing the words *"cannot open"* in its own message was
  reported as broken — a string match on prose. stdout is the gate's output, not its opinion
  of itself.
- **`QUICKSTART.md` §0b question 4 no longer recommends the failing form**, and now says why
  the content check is the one worth writing.
- **The known-bad fixture got a better diagnosis, not just fewer findings** (51 → 49): T3's
  real defect is that its gate passes on unstarted work, which the missing-file misreading
  had been hiding behind the wrong message.

`tests/test-gate-fails-first.py` — 21 checks. Mutation-proven: reverting to the v1.0.0
behaviour fails 11 of them while every broken-gate control still passes, so the file is not
merely asserting that everything fails.

### The known-bad example was telling three different stories — 2026-08-20

`examples/a-real-first-plan` is this repo's known-bad calibration fixture, and the record of
what the gate says about it had rotted in three places at once:

| Surface | Said | Reality |
|---|---|---|
| `a-real-first-plan-GATE-REPORT.txt` | 26 findings | 51 |
| `examples/README.md` (twice) | "30+", then 26 | 51 |
| `examples/minimal-passing-plan/PLAN.md` | "30+" | 51 |

The report was generated once, on 17 August, and never regenerated — so every check added
since had silently invalidated it, `brainstormed` included. All four surfaces now say 51.

**And the rot is now checkable, which is the actual fix.** `check-drift.py` gained a sixth
check: the stored report must agree with its own FAIL lines, with a live gate run, and with
every prose surface that states a count. A stored measurement of the gate rots every time the
gate gains a check, which makes it exactly the class of fact this repo says must be derived
rather than remembered — and it was the one such fact nothing was deriving. Mutation-proven
both ways: a stale report and stale prose each fail it with the surface named.

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
