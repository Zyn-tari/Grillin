# Contributing

One person maintains this. That shapes everything below, so it is said first rather than
discovered.

**Issues get read in batches, roughly weekly. There is no SLA and I am not going to pretend
otherwise.** If something is broken and you need it fixed today, fork it — the licence lets
you, and a fork you control beats a maintainer who is asleep.

---

## The one rule that matters

**Every rule in this method traces to a defect that actually happened.** Not a defect that
could happen. One that did, on a real run, with a date and an artefact you could point at.

That is the whole reason this is worth reading instead of the hundred other planning
documents. It is also the first thing that erodes under contribution pressure, because
"wouldn't it be sensible if…" is always easier to write than "here is what went wrong."

So: **a pull request that adds a rule, a phase, a check or an anti-pattern must name the
incident it came from.** What was being built, what went wrong, how it was noticed, what it
cost. If it happened to you, that is perfect. If you cannot name one, the change is a
preference, and preferences do not go in.

This applies to me too, and there are places in the history where I broke it and had to
take something back out.

## What is genuinely wanted

**Reports that the method failed you.** Far and away the most valuable thing. Not "I think
phase 6 is redundant" — *"I ran this on a real job and here is where it fell over."* Several
of the sharpest rules in here came from first-time users doing exactly that, including one
who found a live defect by reading the source and never running it.

**Defects in the gate.** A check that fires when it should not, or stays quiet when it should
not. Include the plan that reproduces it; a task file is usually enough.

**Examples.** A plan directory from a real job, scrubbed, that shows a shape the existing
examples do not. Small ones are more useful than large ones.

**Prose that is wrong.** A claim that overstates, a number that no longer holds, an
instruction that cannot be followed as written. These are defects and they are graded as
defects.

## What will be declined, and why

**Rules with no incident.** See above.

**Anything that crosses the boundary.** Grillin owns what a plan **declares**. Smokin owns
what actually **happens**. Grillin does not run plans; Smokin does not author them. This
separation is the most load-bearing structural decision in either repository and it is under
constant, entirely reasonable-sounding pressure. It is not negotiable. `tests/test-config-contract.py`
exists to catch the two drifting apart.

**Dependencies.** The gate is python3, stdlib, no packages, and it stays that way. Somebody
has to run this on a server they do not control at two in the morning.

**Anything that makes the gate part of a product's build.** Grillin runs *on* a plan, from
outside it. The project you are planning changes to must build, test and ship with Grillin
uninstalled. If a change would break that, it is the wrong change.

**Style refactors.** The code is plain on purpose and the comments are long on purpose —
they carry the incidents. A tidier version that drops the reasoning is a worse version.

## If you touch a check

Two things, both of which the CI enforces:

1. **A mutation probe.** Break the thing your check exists to catch, and prove the check
   fires. `.github/workflows/gate.yml` has thirty of them; add yours beside the others.
2. **A control.** Prove the check is *silent* when nothing is wrong. Without this, "my check
   works" and "my check fails everything" look identical — and a check that fires on
   everything gets ignored within a week, which is worse than not having it.

Run before you open anything:

```bash
./scripts/validate-plan.py examples/minimal-passing-plan --run-gates   # must exit 0
./scripts/validate-plan.py examples/a-real-first-plan  --run-gates   # must exit 1
./scripts/check-drift.py                                             # surfaces must agree
python3 tests/test-owner-and-ownership.py
bash    tests/test-human-workers.sh
```

The known-good fixture passing and the known-bad example failing is the calibration. A gate
that has not been proven against a known answer authorises every measurement downstream of
it, so if you change a check, run both.

**Four surfaces publish the same facts** — the markdown, `SCALING.json`, `index.html` and the
README counts. `check-drift.py` fails when they disagree. It has caught real drift more than
once; if it complains, fix the surface that is wrong rather than the check.

## Licence

The tools are **PolyForm Noncommercial 1.0.0**; the method and documents are **CC BY 4.0**.
See [`LICENSE`](LICENSE) and [`LICENSE-DOCS`](LICENSE-DOCS), and the README for the plain
answer to "is my use commercial?" (short version: if you are one person, it's free).

By opening a pull request you agree your contribution ships under those same terms. If that
is a problem for you, say so in the issue before writing code rather than after.

## Tone

Findings are welcome, blunt is fine, and being wrong in public is normal here — the case
study documents the author's own mistakes at some length because they were the most
instructive part. What is not welcome is certainty without evidence, in either direction.
