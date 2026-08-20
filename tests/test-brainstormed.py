#!/usr/bin/env python3
"""Calibrate `check_brainstormed` — the shape was argued before the files existed.

WHAT THIS GUARDS. Every other check in this gate reads structure, and a plan can
be structurally perfect and about the wrong problem. The five questions in
QUICKSTART 0b were the first answer and they are necessary; they are not
sufficient, because a curator can answer all five inside their own head in the
same two minutes they decided what to build. So a plan big enough to be worth
arguing about must record that the argument happened, and with whom it landed.

AND IT IS SIZE-AWARE, WHICH IS THE HALF MOST LIKELY TO ROT. `check_persona_model`
is size-BLIND while SCALING.json declares per-band behaviour, and two independent
rounds of first-time users found the contradiction. A new scaling check that
hardcoded its own bands would become the third place a band is written down and
the second place it is wrong — so the requirement is READ from SCALING.json, and
the checks below prove that by moving the data rather than by reading the source.

    python3 tests/test-brainstormed.py
"""
import importlib.machinery
import importlib.util
import json
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
LAB = Path(tempfile.mkdtemp(prefix="grillin-shapechk."))


def chk(label, got, want):
    global fails
    if got == want:
        print(f"  \033[32mPASS\033[0m  {label}")
    else:
        fails += 1
        print(f"  \033[31mFAIL\033[0m  {label} — want {want!r}, got {got!r}")


def has(label, got, needle):
    chk(label, needle in (got or ""), True)


def mkplan(name, n_tasks, header_extra="", root=None):
    """n tasks, each trivially valid, so the ONLY variable is the header."""
    p = (root or LAB) / name
    shutil.rmtree(p, ignore_errors=True)
    rows = []
    for i in range(1, n_tasks + 1):
        tid = f"T{i}"
        (p / "tasks" / tid).mkdir(parents=True)
        # A UNIQUE OWNER PER TASK. The adversary must own work nobody else owns
        # or it is judging its own; `**Workers:** human` in PLAN.md is what
        # carries the model-floor exemption, so the owner strings stay distinct.
        L = [f"# {tid} — fixture", "", "**Status:** NOT STARTED",
             f"**Owner:** person-{tid}"]
        # ABOVE THE 4-TASK FLOOR THE GATE STAFFS READERS, and it is right to.
        # A fixture that ignored that would fail for reasons this file is not
        # about, and every check here would read the wrong verdict.
        if n_tasks >= 4 and i == n_tasks - 1:
            L += ["**Reader:** adversary",
                  "**Context:** fresh — not a subagent of the orchestrator, "
                  "not a continued session"]
        if n_tasks >= 4 and i == n_tasks:
            L.append("**Reader:** health")
        L += ["**Blocked by:** — · **Blocks:** —",
              "", "## What you own", f"`tasks/{tid}/`",
              "", "## Done means", "```", f"test -s tasks/{tid}/OUT.md", "```", ""]
        (p / "tasks" / tid / "TASK.md").write_text("\n".join(L))
        rows.append(f"| {tid} | x | — |")
    band = G.band_of(n_tasks)
    (p / "PLAN.md").write_text(
        f"# plan\n\n**Size:** {band}\n**Workers:** human\n{header_extra}\n\n"
        "| ID | Task | Blocked by |\n|---|---|---|\n" + "\n".join(rows) + "\n")
    return p


def gate(plan, cwd=None):
    # --run-gates ALWAYS. Without it the gate exits 2 (INCOMPLETE) by design and
    # never reports success, so a helper that omitted it would test nothing and
    # every check below would read 2 instead of the verdict it was asking for.
    r = subprocess.run([sys.executable, str(GATE), str(plan), "--run-gates"],
                       capture_output=True, text=True, timeout=180, cwd=cwd)
    line = next((l for l in (r.stdout + r.stderr).splitlines()
                 if "brainstormed" in l), "")
    return r.returncode, line


print("\n=== 1 · the band comes from SCALING.json, not from this checker ===")
spec_json = json.loads((ROOT / "SCALING.json").read_text())
declared = {b["size"]: b.get("brainstormed") for b in spec_json["scaling"]}
chk("SCALING.json declares the rule for every band",
    sorted(declared), ["L", "M", "S", "XL", "XS"])
chk("XS is advisory", declared["XS"], "advisory")
chk("S and above are required",
    {declared[k] for k in ("S", "M", "L", "XL")}, {"required"})
for size, n in (("XS", 2), ("S", 5), ("M", 12)):
    chk(f"{n} tasks is band {size}", G.band_of(n), size)
chk("band_rule reads the declaration for S", G.band_rule("brainstormed", "S"), "required")
chk("...and for XS", G.band_rule("brainstormed", "XS"), "advisory")
# A missing key must not invent strictness — a checker that fails closed on an
# absent declaration would fail every plan the day someone adds a band.
chk("an unknown band yields the default, not a requirement",
    G.band_rule("brainstormed", "XXL", "advisory"), "advisory")
chk("an unknown KEY yields the default too",
    G.band_rule("no-such-rule", "S", None), None)

print("\n=== 2 · required at S, advisory at XS ===")
rc, line = gate(mkplan("xs-silent", 3))
chk("an XS plan with no declaration passes", rc, 0)
has("...and says the size is why", line, "advisory at this size")
rc, line = gate(mkplan("s-missing", 5))
chk("an S plan with no declaration FAILS", rc, 1)
has("...naming the size and the count", line, "5 tasks (S)")
has("...and saying what to write", line, "**Brainstormed:** architectural")
has("...and where the rule lives", line, "SCALING.json")
has("...and pointing at the skill that does the job", line, "brainstorming")

rc, line = gate(mkplan("s-ok", 5,
                       "**Brainstormed:** architectural · approved 2026-08-19"))
chk("an S plan that records it passes", rc, 0)
has("...saying which path and that it was approved", line, "architectural")

print("\n=== 3 · the VALUE is checked, not merely its presence ===")
# Two of the three paths are DEFINED as producing no plan document, so a plan
# declaring one is a plan whose own header says it should not exist. That
# contradiction is worth more than a non-empty field.
for path in ("spike", "bounded"):
    rc, line = gate(mkplan(f"s-{path}", 5,
                           f"**Brainstormed:** {path} · approved 2026-08-19"))
    chk(f"an S plan declaring the {path!r} path FAILS", rc, 1)
    has(f"...because {path} produces no plan document", line, "NO plan document")
    has("...and it says to re-classify, not to relabel", line, "Re-classify")

rc, line = gate(mkplan("s-nopath", 5, "**Brainstormed:** yes, we talked about it"))
chk("a declaration naming no path FAILS", rc, 1)
has("...listing the three it accepts", line, "spike")

rc, line = gate(mkplan("s-noapproval", 5, "**Brainstormed:** architectural · 2026-08-19"))
chk("a path with no approval FAILS", rc, 1)
has("...and names the failure it is for", line, "same breath")
# The synonyms a person actually writes, since refusing them would teach people
# to write the magic word rather than the truth.
for word in ("approved", "agreed", "signed off", "signed-off"):
    rc, _ = gate(mkplan("s-syn", 5, f"**Brainstormed:** architectural · {word} 2026-08-19"))
    chk(f"...but {word!r} is accepted", rc, 0)

print("\n=== 4 · it does not fire where it has no business ===")
# SILENT CONTROLS. A new check's real risk is the plans it was never meant to see.
rc, line = gate(mkplan("xs-declared", 3,
                       "**Brainstormed:** architectural · approved 2026-08-19"))
chk("an XS plan that declares it anyway still passes", rc, 0)
has("...and the gate notices it was declared", line, "declared anyway")
p = mkplan("noplan", 5, "**Brainstormed:** architectural · approved 2026-08-19")
(p / "PLAN.md").unlink()
rc, line = gate(p)
# It still does not REPORT here — check_plan_source_of_truth owns a missing
# PLAN.md and one defect gets one finding. What changed is that the silence is
# now PRINTED: since the gate began accounting for every declared check, a check
# with nothing to say emits a SKIP rather than nothing at all. Asserting on the
# empty string was asserting that this check leaves no trace, which was never
# the property being defended.
chk("a plan with no PLAN.md is not reported by THIS check",
    line.split(" —")[0], "SKIP")
has("...and the SKIP names who owns that failure instead", line,
    "plan-truth owns that failure")

print("\n=== 5 · the shipped fixtures stay calibrated ===")
# 0 for known-good and 1 for known-bad is the repo's own instrument calibration,
# and a new check is exactly the kind of change that breaks it.
rc, _ = gate(ROOT / "examples" / "minimal-passing-plan")
chk("known-good still exits 0", rc, 0)
rc, line = gate(ROOT / "examples" / "a-real-first-plan")
chk("known-bad still exits 1", rc, 1)
# It is a genuine specimen of this failure — its own 04-SHAPE.md says the shape
# was never approved and the task prose was written anyway.
has("...and check_brainstormed is one of the reasons why", line, "brainstormed")
shape = (ROOT / "examples" / "a-real-first-plan" / "04-SHAPE.md").read_text()
has("...which that example states in its own words", shape, "has not been approved")

print("\n=== 6 · the surfaces agree about the count ===")
chk("the emitted name is registered", "brainstormed" in G.GATE_CHECK_NAMES, True)
chk("SCALING.json lists it among the gate checks",
    "brainstormed" in spec_json["gateChecks"], True)
chk("...and the two sets are the same size",
    len(G.GATE_CHECK_NAMES), len(spec_json["gateChecks"]))
r = subprocess.run([sys.executable, str(GATE), "--version"],
                   capture_output=True, text=True, timeout=60)
has("--version reports the new count", r.stdout, "24 checks")

print()
if fails:
    print(f"\033[31m{fails} failed\033[0m")
else:
    print("\033[32mall brainstormed checks passed\033[0m")
shutil.rmtree(LAB, ignore_errors=True)
sys.exit(1 if fails else 0)
