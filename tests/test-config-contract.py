#!/usr/bin/env python3
"""
The two validators must not drift.

Grillin's `check_rulings` and `check_invariants` re-state limits that live in
Smokin's loaders. Copies drift, and the standard shape of that failure is well
known outside this repo: two validators with similar names, where the authoring
one permits what the runtime one refuses, discovered when something breaks in
production. The authoring side is not the authority — the runtime is, because
the runtime decides what actually executes. The mitigation is not "be careful";
it is an assertion that fails the moment the two disagree.

This is that assertion. It builds a plan, drops known-bad configs into it, and
requires BOTH tools to refuse each one.

THREE SETS, and the third is the point:

  SHARED     both must refuse. A defect Grillin passes and Smokin halts on is a
             plan that got handed over and died at tick 1.
  GRILLIN    Grillin refuses, Smokin accepts — on purpose, and named here so a
             divergence is a decision somebody wrote down rather than a bug.
  POSITIVE   both must ACCEPT. Without this the whole file passes vacuously if a
             validator starts refusing everything, which is the failure mode
             OPERATING-THE-PLAN.md §5 exists to stop. An instrument gets proven
             against a known answer before the measurements it authorises.

If Smokin is not installed beside this repo the cross-tool half cannot run. It
says so LOUDLY and exits non-zero on the Grillin half alone, because a skip
nobody can see is indistinguishable from a pass.
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATE = ROOT / "scripts" / "validate-plan.py"
GOOD_PLAN = ROOT / "examples" / "minimal-passing-plan"
SMOKIN = Path(os.environ.get("SMOKIN_HOME", Path.home() / "smokin"))

passed = failed = 0


def ok(msg):
    global passed
    passed += 1
    print(f"  \033[32mPASS\033[0m  {msg}")


def bad(msg, detail=""):
    global failed
    failed += 1
    print(f"  \033[31mFAIL\033[0m  {msg}" + (f" — {detail}" if detail else ""))


# ── the fixtures ────────────────────────────────────────────────────────────
GOOD_INV = """
[[invariant]]
name = "the neighbour still answers"
run = "printf 200"
because = "this plan adds a vhost to a server that already serves two sites"
"""

SHARED_INV = {
    "no entries":        '[policy]\nbudget_s = 30\n',
    "unparseable":       '[[invariant]\nname = ',
    "unknown key":       GOOD_INV + '\n[[invariant]]\nname = "b"\nrun = "true"\n'
                                    'because = "x"\nmode = "strict"\n',
    "no because":        '[[invariant]]\nname = "a"\nrun = "printf 200"\n',
    "no run":            '[[invariant]]\nname = "a"\nbecause = "x"\n',
    "equals AND matches": '[[invariant]]\nname = "a"\nrun = "true"\nbecause = "x"\n'
                          'equals = "1"\nmatches = "1"\n',
    "agent binary":      '[[invariant]]\nname = "a"\nrun = "claude -p check"\nbecause = "x"\n',
    "budget zero":       '[[invariant]]\nname = "a"\nrun = "true"\nbecause = "x"\nbudget_s = 0\n',
    "duplicate name":    '[[invariant]]\nname = "a"\nrun = "true"\nbecause = "x"\n'
                         '[[invariant]]\nname = "a"\nrun = "false"\nbecause = "y"\n',
}

GOOD_RUL = """
[[ruling]]
class = "receipt-trust"
when = "verdict.passed"
persona = "judge"
evidence = ["receipt"]
outcomes = ["accept", "reject", "insufficient-evidence"]
default = "halt"
"""

SHARED_RUL = {
    "no entries":  '[policy]\nuncovered = "halt"\n',
    "unparseable": '[[ruling]\nclass = ',
}


def run_grillin(plan: Path, check: str) -> bool:
    """True if the gate FAILED on `check`."""
    r = subprocess.run([sys.executable, str(VALIDATE), str(plan)],
                       capture_output=True, text=True)
    return any(l.startswith(f"FAIL — {check}") for l in r.stdout.splitlines())


def load_smokin(mod_name: str, plan: Path):
    """Smokin's own loader. Returns its .error, or None if it accepted."""
    spec = importlib.util.spec_from_file_location(
        mod_name, SMOKIN / "bin" / f"{mod_name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.load(plan).error


def case(label, filename, body, check, mod, want_grillin, want_smokin, cross):
    plan = Path(tempfile.mkdtemp()) / "plan"
    shutil.copytree(GOOD_PLAN, plan)
    (plan / filename).write_text(body)
    try:
        g = run_grillin(plan, check)
        if g == want_grillin:
            ok(f"{label} — grillin {'refuses' if want_grillin else 'accepts'}")
        else:
            bad(f"{label} — grillin",
                f"expected {'refuse' if want_grillin else 'accept'}, got the opposite")
        if cross:
            s = load_smokin(mod, plan) is not None
            if s == want_smokin:
                ok(f"{label} — smokin {'refuses' if want_smokin else 'accepts'}")
            else:
                bad(f"{label} — smokin",
                    f"expected {'refuse' if want_smokin else 'accept'}, got the opposite")
    finally:
        shutil.rmtree(plan.parent, ignore_errors=True)


def main():
    cross = (SMOKIN / "bin" / "smokin_invariants.py").is_file()
    print("the two validators agree" + ("" if cross else "  [SMOKIN NOT FOUND]"))
    print()

    if not cross:
        print(f"  \033[31mNOT RUN\033[0m  the cross-tool half — no smokin at {SMOKIN}")
        print("           Set SMOKIN_HOME, or accept that nothing here proves the")
        print("           authoring gate and the runtime loader still agree.")
        print()

    print("  _INVARIANTS.toml")
    for label, body in SHARED_INV.items():
        case(label, "_INVARIANTS.toml", body, "invariants",
             "smokin_invariants", True, True, cross)
    case("valid set", "_INVARIANTS.toml", GOOD_INV, "invariants",
         "smokin_invariants", False, False, cross)

    print("  _RULINGS.toml")
    for label, body in SHARED_RUL.items():
        case(label, "_RULINGS.toml", body, "rulings",
             "smokin_rulings", True, True, cross)
    case("valid set", "_RULINGS.toml", GOOD_RUL, "rulings",
         "smokin_rulings", False, False, cross)

    # ── the documented divergence ───────────────────────────────────────────
    # Grillin refuses this and Smokin does not, because only the authoring side
    # can see that the command was copied out of a task contract. Asserted so it
    # stays a decision instead of becoming a surprise.
    print("  divergence, on purpose")
    dc = (GOOD_PLAN / "tasks" / "T2" / "TASK.md").read_text()
    import re
    m = re.search(r"## Done means.*?```(?:\w*)\n(.*?)```", dc, re.S)
    if not m:
        bad("could not read T2's done-command out of the fixture")
    else:
        cmd = m.group(1).strip().splitlines()[0].strip()
        body = (f'[[invariant]]\nname = "a"\nrun = "{cmd}"\n'
                f'because = "copied out of T2, which is the error"\n')
        case("an invariant that is really a done-command", "_INVARIANTS.toml", body,
             "invariants", "smokin_invariants", True, False, cross)

    print()
    print(f"  {passed} passed, {failed} failed")
    return 1 if failed or not cross else 0


if __name__ == "__main__":
    sys.exit(main())
