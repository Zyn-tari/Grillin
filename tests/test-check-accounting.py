#!/usr/bin/env python3
"""Calibrate the gate's own arithmetic — every declared check accounts for itself.

WHERE THIS CAME FROM. `--version` says `gate: 24 checks`. A clean run printed 22
named checks, and the two missing ones — `rulings` and `invariants` — were silent
because the plan had declared neither `_RULINGS.toml` nor `_INVARIANTS.toml`. A
first-time curator counted the lines, could not settle "did not apply" against
"did not fire", and had to read the source to find out. That is the one question a
gate must never leave to interpretation: a check that says nothing is
indistinguishable from a check that has quietly stopped running, and a tool that
cannot account for its own checks is asking to be trusted on faith.

So silence is now a printed verdict. SKIP names the check and says why it did not
apply, `reported + skipped` equals what `--version` claims, and SKIP is not a
finding — it must not read as one and must not move an exit code.

AND THE SECOND HALF. The PASS block used to print "On the run measured end to end
this gate caught 2 defects and the readers caught 50" under the result of YOUR
plan, on every run, phrased as a live reading. It is one job, one operator, one
domain, in August 2026. The fact stays — it is the most useful thing this tool
says about its own ceiling — but it now reads as history and names its source,
and the two numbers are held here against SCALING.json's `measurement` block so
the gate cannot drift away from the record it is citing.

    python3 tests/test-check-accounting.py
"""
import importlib.machinery
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "validate-plan.py"
spec = importlib.util.spec_from_loader(
    "gate", importlib.machinery.SourceFileLoader("gate", str(GATE)))
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)

fails = 0
LAB = Path(tempfile.mkdtemp(prefix="grillin-accounting."))


def chk(label, got, want):
    global fails
    if got == want:
        print(f"  \033[32mPASS\033[0m  {label}")
    else:
        fails += 1
        print(f"  \033[31mFAIL\033[0m  {label} — want {want!r}, got {got!r}")


def has(label, got, needle):
    chk(label, needle in (got or ""), True)


def run(plan, *extra):
    r = subprocess.run([sys.executable, str(GATE), str(plan), *extra],
                       capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


def verdicts(out):
    """{name: verdict} for every check line the run printed."""
    d = {}
    for line in out.splitlines():
        m = re.match(r"^(PASS|FAIL|SKIP) — (\S+)\s", line)
        if m:
            d.setdefault(m.group(2), set()).add(m.group(1))
    return d


def tally(out):
    m = re.search(r"^checks: (\d+) declared — (\d+) reported above, (\d+) skipped",
                  out, re.M)
    return tuple(int(x) for x in m.groups()) if m else None


GOOD = ROOT / "examples" / "minimal-passing-plan"
BAD = ROOT / "examples" / "a-real-first-plan"

print("\n=== 1 · the count is auditable from the printed run alone ===")
rc, out = run(GOOD, "--run-gates")
chk("the known-good fixture still exits 0", rc, 0)
n_declared, n_reported, n_skipped = tally(out)
chk("the tally line declares what --version declares",
    n_declared, len(G.GATE_CHECK_NAMES))
chk("...and reported + skipped accounts for all of them",
    n_reported + n_skipped, n_declared)
v = verdicts(out)
chk("...and the distinct names printed equal the declared set",
    sorted(v), sorted(G.GATE_CHECK_NAMES))
r = subprocess.run([sys.executable, str(GATE), "--version"],
                   capture_output=True, text=True, timeout=60)
has("--version still claims 24 checks", r.stdout, "24 checks")
chk("...the same number the run accounts for",
    f"gate: {n_declared} checks" in r.stdout, True)

print("\n=== 2 · the two checks that started this now say why they are quiet ===")
# Opt-in by file. Absence is not a defect, and the old output made it look like
# one thing or the other and let the reader guess which.
chk("`invariants` is SKIPped, not absent", v.get("invariants"), {"SKIP"})
chk("`research-task` is SKIPped, not absent", v.get("research-task"), {"SKIP"})
has("...and the invariants line names the file that would turn it on",
    out, "_INVARIANTS.toml")
has("...and says the absence is not a defect", out, "absence is not a defect")
has("...and the research-task line says which kind of task it binds",
    out, "sent to find something out")
# This fixture DOES declare _RULINGS.toml, so that one has to report for real —
# a SKIP here would mean the check had stopped running, which is the failure
# mode this whole file exists to make visible.
chk("`rulings` reports for real on a plan that declares it", v.get("rulings"), {"PASS"})

print("\n=== 3 · MUTATION PROBE · make a check go silent, prove it is accounted for ===")
# Drop the opt-in file and the check that read it must appear as a SKIP with a
# reason, not vanish from the output.
mut = LAB / "no-rulings"
shutil.copytree(GOOD, mut)
(mut / "_RULINGS.toml").unlink()
# The fixture's PLAN.md links to its sibling example, and check_references is
# right to resolve that relative to wherever the plan actually sits. Give the
# copy the sibling it expects, or this probe reports a broken link and calls it
# a result about SKIP.
(LAB / "a-real-first-plan").mkdir(exist_ok=True)
rc, mout = run(mut, "--run-gates")
mv = verdicts(mout)
chk("removing _RULINGS.toml exits 0 — it is opt-in, not required", rc, 0)
chk("...and `rulings` flips from PASS to SKIP", mv.get("rulings"), {"SKIP"})
has("...naming the file that would turn it back on", mout, "_RULINGS.toml")
chk("...and the run still accounts for every declared check",
    sum(tally(mout)[1:]), n_declared)
chk("...one more skipped than before", tally(mout)[2], n_skipped + 1)

# The other way a check goes quiet: it is switched off. The floors make that a
# config-integrity FAIL, and the SKIP has to say so rather than leaving a hole.
off = LAB / "refs-off.json"
off.write_text(json.dumps({"require_refs_resolve": False}))
rc, cout = run(GOOD, "--run-gates", "--config", str(off))
cv = verdicts(cout)
chk("a disabled check fails config-integrity, as it always did", rc, 1)
chk("...and `references` is SKIPped rather than silently missing",
    cv.get("references"), {"SKIP"})
has("...saying which switch turned it off", cout, "require_refs_resolve")
chk("...and the arithmetic still closes", sum(tally(cout)[1:]), n_declared)

# And the third: a check that cannot run because the run was cheap.
rc, iout = run(GOOD)
chk("without --run-gates the exit code is still 2", rc, 2)
chk("...and `gate-fails-first` says it did not run", verdicts(iout).get("gate-fails-first"),
    {"SKIP"})
has("...and says what would have run it", iout, "--run-gates was not given")

print("\n=== 4 · CONTROL · SKIP is not a failure and moves nothing ===")
# Without this, "the gate accounts for itself" and "the gate now fails plans it
# used to pass" look identical from the outside.
chk("the known-good fixture is unaffected: exit 0", run(GOOD, "--run-gates")[0], 0)
has("...and still reports PASS", out, "RESULT: PASS")
chk("no SKIP line is counted as a finding", "RESULT: FAIL" in out, False)
chk("every SKIPped name is a declared check, never an invented one",
    [k for k, s in v.items() if s == {"SKIP"} and k not in G.GATE_CHECK_NAMES], [])
chk("no check both reports and skips on one run",
    [k for k, s in v.items() if len(s) > 1 and "SKIP" in s], [])

rc, bout = run(BAD, "--run-gates")
chk("the known-bad fixture still exits 1", rc, 1)
m = re.search(r"RESULT: FAIL — (\d+) finding", bout)
chk("...and its finding count is FAIL lines only, unchanged by the SKIPs",
    int(m.group(1)), len(re.findall(r"^FAIL — ", bout, re.M)))
chk("...with the same arithmetic closing there too",
    sum(tally(bout)[1:]), n_declared)
# The shipped small plans, which take the other RESULT branch entirely.
for name, want in (("one-task-plan", 0), ("research-first-plan", 0)):
    rc, sout = run(ROOT / "examples" / name, "--run-gates")
    chk(f"{name} still exits {want}", rc, want)
    chk(f"...and accounts for every check", sum(tally(sout)[1:]), n_declared)

print("\n=== 5 · no declared check can go quiet without a registered reason ===")
# The table is the only thing that makes a SKIP line worth reading. Nothing else
# in the repo would notice a check added tomorrow with no reason written for it.
missing = [n for n in G.GATE_CHECK_NAMES if n not in G.SILENT_BECAUSE]
chk("every declared check has a reason registered", missing, [])
stale = [n for n in G.SILENT_BECAUSE if n not in G.GATE_CHECK_NAMES]
chk("...and no reason names a check that no longer exists", stale, [])
chk("an unregistered name still gets a line rather than vanishing",
    G.SILENT_BECAUSE.get("no-such-check", G.UNREGISTERED_SKIP), G.UNREGISTERED_SKIP)
has("...which says out loud that the gate is at fault, not the plan",
    G.UNREGISTERED_SKIP, "defect in the gate")
chk("the floor in the reason text is filled in, not left as a placeholder",
    "{floor}" in out, False)
has("...from ADVERSARY_MIN_TASKS", run(ROOT / "examples" / "one-task-plan")[1],
    f"{G.ADVERSARY_MIN_TASKS}-task floor")

print("\n=== 6 · the historical measurement reads as history ===")
scaling = json.loads((ROOT / "SCALING.json").read_text())
meas = scaling["measurement"]
line = next((l for l in out.splitlines() if "the readers" in l), "")
has("the PASS block dates the run it is quoting", line, "5 Aug 2026")
has("...names the source it came from", line, "SCALING.json")
has("...says it is not a reading of this plan", line, "rather than anything measured here")
has("...and carries SCALING.json's own caveat", line, "one job, one operator, one domain")
# The sentence it replaced, which read as a live measurement of the plan just run.
chk("the bare live-sounding phrasing is gone",
    "On the run measured end to end this gate caught" in out, False)
has("...but the fact itself is still printed", line, "the readers 50")

# THE NUMBERS AGAINST THE RECORD. A remembered measurement is one edit away from
# citing a source that no longer says it.
m = re.search(r"the gate caught (\d+) defects, the readers (\d+)", line)
chk("the printed numbers parse", bool(m), True)
gate_n, readers_n = (int(m.group(1)), int(m.group(2))) if m else (None, None)
chk("the gate's number is SCALING.json's measurement.gate", gate_n, meas["gate"])
headline = int(re.search(r"readers caught (\d+)", meas["headline"]).group(1))
chk("the readers' number is SCALING.json's headline", readers_n, headline)

# MUTATION PROBE for the two checks above: doctor the record and prove the
# comparison notices. Testing the comparator, because a comparator that cannot
# fail is a comment.
doctored = dict(meas, gate=meas["gate"] + 1)
chk("a moved measurement.gate would be caught", gate_n == doctored["gate"], False)
doctored_headline = meas["headline"].replace(f"caught {headline}", f"caught {headline + 1}")
chk("...and a moved headline too",
    readers_n == int(re.search(r"readers caught (\d+)", doctored_headline).group(1)), False)

print("\n=== 7 · CONTROL · the small-plan branch is untouched ===")
# Below the adversary floor the PASS block never printed the measurement and
# still must not: a plan with no reader staffed has no reader result to caveat.
rc, small = run(ROOT / "examples" / "one-task-plan", "--run-gates")
chk("a below-floor plan still exits 0", rc, 0)
chk("...and does not print the historical measurement at all",
    "the readers 50" in small, False)
has("...it prints the branch it always printed", small, "you are the reader")

# ── AN OPEN SURFACE DISAGREEMENT, RECORDED RATHER THAN RESOLVED ─────────────
# Not asserted, because nothing here can tell which surface is wrong, and a test
# that picks one would be inventing the answer. SCALING.json records the health
# checker at ~20 and the adversary at 44 (30 blocking + 14 non-blocking) but
# headlines the readers at 50. 20 + 44 = 64. 20 + 30 = 50, which is the only
# reading that lands — the headline appears to count the adversary's BLOCKING
# findings only, and nothing on any surface says so. Whoever owns SCALING.json
# should either write the composition down or restate the headline.
hc = re.search(r"(\d+)", scaling["readers"]["healthChecker"]["found"]).group(1)
adv = scaling["measurement"]["adversary"]
print(f"\n  \033[33mNOTE\033[0m  surface disagreement, NOT fixed here: SCALING.json has "
      f"healthChecker ~{hc} and adversary {adv}, which sum to {int(hc) + adv}, "
      f"but headlines the readers at {headline}. The composition of {headline} is "
      f"written down nowhere. Reported, not resolved — SCALING.json is not this "
      f"change's to edit.")

print()
if fails:
    print(f"\033[31m{fails} failed\033[0m")
else:
    print("\033[32mall check-accounting tests passed\033[0m")
shutil.rmtree(LAB, ignore_errors=True)
sys.exit(1 if fails else 0)
