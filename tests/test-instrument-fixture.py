#!/usr/bin/env python3
"""Calibrate check_instrument — the check that had never once fired.

WHERE THIS CAME FROM. An 11-track, 180-task XL program — the first real exercise
of the band — reported that `instrument` printed the identical line on all six of
its plans: "no plan-local instrument is load-bearing in any gate". It had never
fired. The cause was two lines: `plan / ref.lstrip("./")` turned an ABSOLUTE
reference into a relative one and joined it onto the plan root, where it never
resolved; and the check never opened the gate it found, so an instrument invoked
one level down was invisible. Meanwhile that program's own face/F4 gate ran a
plan-local measuring script whose bar F5 later demonstrated three ways past.

THE REASON IT COULD HAPPEN AT ALL is the thing this file fixes. Of the gate's 24
checks, `instrument` was the ONLY one with no mutation probe in CI and no
harness here. Without a probe, "my check works" and "my check has never fired"
produce the same output — a clean PASS — and this repository's own first
standard says so in as many words. The check shipped dead for months and was
found by a stranger's program, not by us.

THE MODEL, which the fix also corrects: the script named IN a done-command is
the GATE, and a gate is not an instrument. Scripts the gate CALLS, that live
inside the plan, are the instruments, and each must be run against a fixture
with a known answer.

    python3 tests/test-instrument-fixture.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "validate-plan.py"
LAB = Path(tempfile.mkdtemp(prefix="grillin-instrument."))
fails = 0


def chk(label, got, want):
    global fails
    ok = got == want
    print(f"  \033[32mPASS\033[0m  {label}" if ok
          else f"  \033[31mFAIL\033[0m  {label}\n        got {got!r}, want {want!r}")
    if not ok:
        fails += 1


def build(calibrated: bool, absolute: bool):
    """A plan whose done-command runs a GATE, which calls an INSTRUMENT."""
    plan = LAB / "plan"
    shutil.rmtree(plan, ignore_errors=True)
    shutil.copytree(ROOT / "examples" / "minimal-passing-plan", plan)
    (plan / "tools").mkdir()
    (plan / "fixtures").mkdir()
    (plan / "tools" / "ruler.py").write_text("#!/usr/bin/env python3\nprint('measured')\n")
    (plan / "fixtures" / "known-answer.txt").write_text("measured\n")
    ruler = f"{plan}/tools/ruler.py" if absolute else "tools/ruler.py"
    body = f"#!/usr/bin/env bash\npython3 {ruler}\n"
    if calibrated:
        # Calibration may live in the gate's own body — it does NOT require
        # naming the instrument in a done-command, which would promote it to a
        # gate and exempt it. That escape would make the check unsatisfiable in
        # the only way that matters, so it is asserted here.
        body += f"python3 {ruler} {plan}/fixtures/known-answer.txt\n"
    (plan / "tools" / "gate.sh").write_text(body)
    for f in (plan / "tools").iterdir():
        f.chmod(0o755)
    t2 = plan / "tasks" / "T2" / "TASK.md"
    gate_ref = f"{plan}/tools/gate.sh" if absolute else "tools/gate.sh"
    s = t2.read_text().replace("test -f findings/T2.md", f"bash {gate_ref}")
    t2.write_text(s)
    return plan


def verdict(plan):
    p = subprocess.run([sys.executable, str(GATE), str(plan), "--run-gates"],
                       capture_output=True, text=True)
    for line in (p.stdout + p.stderr).splitlines():
        if line.startswith(("PASS — instrument", "FAIL — instrument")):
            return line.split()[0], line
    return "ABSENT", "the check emitted nothing at all — it did not run"


try:
    # The exact shape that was dead: the gate named by ABSOLUTE path.
    kind, line = verdict(build(calibrated=False, absolute=True))
    chk("probe · absolute gate ref, uncalibrated instrument -> FAIL", kind, "FAIL")
    chk("probe · and it names the instrument, not the gate", "ruler.py" in line, True)

    kind, _ = verdict(build(calibrated=False, absolute=False))
    chk("probe · relative gate ref, uncalibrated instrument -> FAIL", kind, "FAIL")

    # The control. A check that fails everything is as useless as one that
    # passes everything, and this is the half that was never in doubt.
    kind, line = verdict(build(calibrated=True, absolute=True))
    chk("control · calibrated inside the gate body -> PASS", kind, "PASS")
    chk("control · and it says it actually found one", "1 instrument" in line, True)

    kind, _ = verdict(build(calibrated=True, absolute=False))
    chk("control · same, relative ref -> PASS", kind, "PASS")

    # The regression that started all this: a plan with no instrument at all
    # must still say so, rather than the check going silent.
    plain = LAB / "plain"
    shutil.rmtree(plain, ignore_errors=True)
    shutil.copytree(ROOT / "examples" / "minimal-passing-plan", plain)
    kind, line = verdict(plain)
    chk("control · a plan with no instrument passes, and says which", kind, "PASS")
    chk("control · ...with the no-instrument wording, not silence",
        "no plan-local instrument" in line, True)
finally:
    shutil.rmtree(LAB, ignore_errors=True)

print()
print(f"\033[31m{fails} failed\033[0m" if fails
      else "\033[32mall instrument-fixture tests passed\033[0m")
sys.exit(1 if fails else 0)
