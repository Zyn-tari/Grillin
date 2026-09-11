# Changelog


## Unreleased — compared against the superpowers skills · 2026-09-11

A research agent compared all fourteen of Anthropic's `superpowers` skills against this method.
Every actionable claim it returned was re-checked before anything was built on it, and the
re-checking changed the result: two of its gaps were overstated, one proposal could not work,
and the finding it scored as its own miss turned out to be the most important thing in the
report. **28 gate checks, up from 26.**

### The integrator was declared, and wired to nothing

Phase 7's output includes "an integrator role", the M band adds one, the roster prices one as
the persona that "merges work it did not write", and every contract says "Do NOT merge". No
check read any of it and the runner never reached it, so a plan could verify every task and
report complete with all of its work still on branches. The agent concluded nothing decides
what happens to branches after a plan verifies. It had missed the integrator *role*; its
conclusion was right anyway, because a role wired to nothing is indistinguishable from no role.

`check_integration`: a plan whose tasks declare a **Branch:** must have a `**Kind:** integration`
task downstream of each — by reachability, not adjacency — whose done-command names each
branch it merges. `Branch` moves from the unparsed list to the parsed one, announced in the
register. Smokin's half refuses `complete` in the same state.

### Placeholders — `check_no_placeholders`, and the owner check

Probed against a clean control before a line was written: `TODO: fill in details.` in Steps,
`implement later` in Steps, and an Owner left as the template's `<agent id, …>` all passed.
The first two are now refused in Steps and Done means — outside code, inline code, quoted
text and comments, because a known-bad fixture's own contract says `no "TBD"` and the first
draft failed it for the mention. The owner check now consults `RE_PLACEHOLDER`, which already
refused that exact string in three other fields and was simply never asked here. The vaguer
half of the writing-plans list ("add appropriate error handling") needs a reader and is
stated as unchecked.

### Haiku takes no effort; a persona file and its task name one model

Haiku 4.5 **rejects** the effort parameter at the API, and the floor demanded one anyway. A
Haiku task now declares no Effort, and one that does is refused — an unappliable pairing
recorded as if applied is the false record this gate exists to stop. And since the runner now
pins a task's subagents from its persona file's `model:` first and its **Model:** second, the
two must agree by family, or the gate fails the plan rather than let the runner pick one.

### Also

- **The fix ladder** (`_RULES` §5): rounds 1–3 the same worker, 4–5 a fresh one with **Model:**
  amended a tier up, then adjudicate. From `subagent-driven-development`, moved from inside a
  session to across dispatches, where the model choice lives.
- **Every finished agent is debriefed** (`_RULES` §1c) — by Haiku, into the task's `debriefs/`,
  in four fixed sections, marked SUSPECTED, grading nothing. Installed from Smokin.
- **Pointers**, not adoptions, in `WORKING-WITH-CLAUDE-CODE.md`: `using-git-worktrees` and
  `finishing-a-development-branch` for work below the method's threshold; and
  `verification-before-completion`, whose principle is this method's and whose use as a
  standing instruction is what Claude 5 retires.
- **Refused:** a check for the brainstorming → writing-plans seam. When writing-plans is used
  instead of Grillin there is no plan directory, so no gate runs; and looking for its output
  means reading the project, which the gate's boundary forbids.
- **`stripped` shipped on 2026-09-07 with a harness CI never ran and no probe** — the shape of
  the check that shipped dead before it, repeated by the same author. Both added; all 37
  probes replayed locally before trusting CI with them, 0 dead.
- A control caught a real defect in the new check before it shipped: the template's own
  `<prefix>/<ID>-<slug>` read as a real branch, because `RE_PLACEHOLDER` only recognises a
  value that is one `<…>` end to end. Any angle brackets now mean unfilled, as for Model.


## Unreleased — a false positive from the field · 2026-09-10

**Reported:** `python3 -m pytest` refused as a missing script. **Two defects were
behind the one report**, and the first hypothesis — read off the code before
reproducing — was the wrong one of the two.

### A flag's value is not a script

`_missing_prereq` took the first argument not starting with `-` as the script an
interpreter runs. That is right for `python3 build.py` and wrong for every flag
that CONSUMES the next word. `python3 -m pytest` looked for a file called
`pytest`; so did `python3 -m unittest`, `python3 -m pip`, `node -e '…'`,
`bash -c '…'`, and `python3 -X dev build.py`, which looked for `dev`.

Split into two cases, because they need different answers. `-m`, `-c`, `-e` and
friends take a module name or inline code, so there is no script and the search
stops. `-X`, `-W` and friends take a value that is neither, so it is stepped over
and the search continues — which is what keeps the check alive rather than
blinded. Same shape as Smokin's `VARIADIC_FLAGS`: a flag that eats the next word
is the thing both tools kept getting wrong.

### A test runner's own "not found" is not a broken gate

Found only by reproducing, and it is the one that actually fired on the reported
command. `\bnot found\b` sat in the unambiguous blow-up list with no
inside-or-outside-the-plan test. `python3 -m pytest tests/` on unstarted work
prints *"ERROR: file or directory not found: tests/"* — and `tests/` is what the
task produces, so that is the gate **working**.

This is the `grep` trap again on a different phrase, with the same cost: the
documented way out of a false "your gate is unanchored" is a weaker gate. The
specific spellings that name a missing binary (`command not found`) stay
unambiguous; the bare phrase moved to the branch that asks *which* file, which
this file has had since the `grep` fix and simply was not wired to it.

`tests/test-gate-fails-first.py` +13 cases, four of them controls proving the
check was not blinded. Two of my own fixtures were wrong before they were right —
one named `python`, which does not exist on this box, so it measured a missing
interpreter and blamed the tool; the other was appended below the summary line,
so the harness printed success before running it.


## Unreleased — parked items · 2026-09-08

### `check-index.py` reads the gating relation — check 5

A plan of plans has edges between its MEMBERS, not just inside them, and nothing
read them. A task-level dependency cycle fails the gate; a plan-level one does not
fail at all — the runner dispatches nothing and looks idle, which is
indistinguishable from work in progress and the most expensive symptom in the file
to diagnose.

Opt-in via `--gates-re`, capturing (name, blockers). It refuses a gating row naming
a shard the index links nowhere (the common defect: a track renamed on one side
only, leaving an edge that points at nothing and silently stops gating), a shard
blocked by itself, and any cycle — printing the path rather than only its
existence. Same reasoning as `check_graph`, one level up, and it lives in the
pointable tool rather than the self-check because it is decidable from an index
file alone and is not specific to Grillin's own surfaces.

Harness 14 → 20 checks. A self-gate briefly produced two findings — the dedicated
message and the cycle walk — and 8d now asserts it produces one.

### Two standing offers, both refused, both recorded

Neither was a defect; both were open because nobody had written down the decision,
which is how the same question gets asked a third time.

**Removing drift block 2b** — refused on evidence from the run that offered it. The
argument was that `--version` now derives its count, so nothing hardcodes it. True
of the script, false of the prose: adding the 26th check left README twice and
WORKING-WITH-CLAUDE-CODE still saying 25, and 2b is what caught all three. A
numeral written into a sentence cannot derive from anything.

**Narrowing the What-you-own harvest** — refused, and the reasoning is now in
`check_paths_disjoint`'s docstring. The error direction is asymmetric (a false
collision is loud, a missed one clobbers at merge time and no later run finds it),
the escape already costs one word, and the pain was never the harvest — it was that
nobody was told about the marker. Both surfaces that could tell them now do.


## Unreleased — Claude 5 · 2026-09-07

Anthropic deleted over 80% of Claude Code's own system prompt for the Claude 5 generation with no
measurable loss on their coding evals, and published the diagnosis: they had been
over-constraining the model. This is Grillin's half of that. **26 gate checks, up from 25.**

The headline is what did NOT change. The guidance says to strip explicit verification
instructions out of prompts because Opus 5 already verifies its own work and instructions to do
it again cause over-verification. Read carelessly that retires the method. It does not: a
done-command is a command a machine runs, an adversary is a different agent judging a result it
did not produce, and Anthropic's most emphasised advice for Claude Code is *give Claude a way to
verify its work*. The rule that separates the two — **cut it if the same agent does the checking,
keep it if a different agent or a machine does** — is now written down in
WORKING-WITH-CLAUDE-CODE.md §6c.

### The converge loop asked for the wrong thing, in the file that matters most

`TASK.md.template` read `do → verify → fix → confirm the fix → re-verify`, which asks the worker
to re-read its own output twice — the documented over-verification trigger. The plan-level copy
in `_RULES.md` §5 always carried the clause this one had dropped, *"by someone who did not make
it"*, so for as long as the two disagreed, **the file the worker actually reads was the one asking
for the behaviour that now costs the most.** Both now name the done-command for those two steps,
which is what they always meant, and the independent-confirm step is untouched.

### `check_stripped_contract` — the 26th check

`TASK.md.template` is over 370 lines and more than half is `<!-- -->` commentary written for the
curator. It has said *"deleted before the file reaches the worker"* since the beginning and
nothing checked, which by this method's own rule made it a preference. The failure mode it
guards is now named by Anthropic: *"If your CLAUDE.md is too long, Claude ignores half of it
because important rules get lost in the noise."*

Fails any shipped `TASK.md` carrying a comment block over 6 lines. **It deliberately does not ban
comments** — a curator's own one-line note to a colleague is legitimate and stays. A short
template fragment left behind therefore passes; that limit is asserted out loud in
`tests/test-stripped-contract.py`, because a check that overstated its own enforcement is the
exact defect the field register was rewritten to stop.

### Phases 0–4 run in plan mode, and the honour system becomes a mechanism

The premise has always said the first phases produce no plan text and are the highest-value
phases. Nothing enforced it. Where the harness has a plan mode the tool layer refuses writes, so
a phase-1 worker cannot "just fix" the thing it was sent to count, and leaving plan mode is the
phase 4 → 5 boundary as an explicit human approval. **Not checkable and never will be** — no
artefact records which mode a phase ran in — so it is registered ADVISORY in
`OPERATING-THE-PLAN.md` §11 with that reason stated.

### Phase 0 interviews instead of guessing

Was *restate and stop*. Restating finds the misunderstandings you can see. Two rounds now, using
a structured question tool where the harness has one, multiple choice rather than open questions:
once before anything is shaped, once after the diagram and before phase 5 writes a task.

### `templates/CLAUDE.md.template` — the calibration file

New, and short on purpose. `TASK.md` is the contract — what to do. `CLAUDE.md` beside it is the
calibration — response length, narration cadence, scope, delegation. Four behaviours that were
free before this generation and are not now, and none of them are about the task. It is named
`CLAUDE.md` because a harness auto-loads that name from its working directory and auto-loads
nothing else; Smokin copies it to the worktree at dispatch, since that is where it gets read.

### `Do NOT spawn sub-agents` is gone from the template, and enforced instead

It sat there for a year as a line nothing could check. Read out of the installed bundle
(`@anthropic-ai/claude-code` 2.1.263), `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` falls back to **20**
and `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` to **3**. The prose is now a paragraph on *whether*
delegating is worth it; *how many* is four entries in Smokin's `runtimes.json`. The prose was
deleted only because the enforcement landed first, which is the order that rule requires.

### Also

- The `--version` check count in `tests/test-check-accounting.py` was the third hardcoded literal
  to break on a new check — `24` when `worktree-disjoint` landed, `25` when this one did. Derived
  now, so it cannot break again.



## v1.2.0 — 2026-08-20

No new gate checks — still 24 — and **no verdict changes**: every finding message on the
known-bad fixture is byte-identical, so a plan that passed v1.1.0 passes this. What changed is
that three surfaces stopped disagreeing with the gate, and CI stopped reporting its own probes
dead.

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
