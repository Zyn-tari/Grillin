#!/usr/bin/env python3
"""Calibrate check_worktree_disjoint — where git serialises, the plan must order.

WHERE THIS CAME FROM. The first real exercise of the XL band: an 11-track,
180-task program gave each persona one persistent worktree so later tasks landed
where earlier ones did. The runner dispatched the whole ready frontier at once
and one persona held five of them. Five tasks, five branches, ONE worktree.
Nothing failed loudly, both tasks reported success, and one commit contained
another task's staged files. The worker found it before anyone asked:

    "Worktree contention is real: a concurrent task committed my staged files
     into its commit."

A git worktree has exactly one checked-out branch. That is an exclusion git
enforces, not a convention — and git does not report it, it silently interleaves.
`paths-disjoint` already refuses two concurrent tasks that own the same OUTPUT
path; the worktree is a path they both write to on every `git add`, and it was
not covered.

THE CONTROLS MATTER AS MUCH AS THE PROBE. Two tasks sharing a worktree is the
NORMAL, correct design when they are ordered — that is the whole point of a
persistent per-persona worktree, and a check that refused it would push authors
back to one worktree per task and lose the accumulation they built it for.

    python3 tests/test-worktree-disjoint.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "validate-plan.py"
LAB = Path(tempfile.mkdtemp(prefix="grillin-wt."))
fails = 0


def chk(label, got, want):
    global fails
    ok = got == want
    print(f"  \033[32mPASS\033[0m  {label}" if ok
          else f"  \033[31mFAIL\033[0m  {label}\n        got {got!r}, want {want!r}")
    if not ok:
        fails += 1


def verdict(t1_wt, t2_wt, ordered=False):
    """Two tasks, identical but for their worktree and whether one blocks the other."""
    p = LAB / "p"
    shutil.rmtree(p, ignore_errors=True)
    for tid, wt, blocked, blocks in (("T1", t1_wt, "—", "T2" if ordered else "—"),
                                     ("T2", t2_wt, "T1" if ordered else "—", "—")):
        (p / "tasks" / tid).mkdir(parents=True)
        line = f"**Worktree:** {wt}\n" if wt else ""
        (p / "tasks" / tid / "TASK.md").write_text(
            f"# {tid} — fixture\n\n**Status:** NOT STARTED\n**Owner:** human\n"
            f"**Blocked by:** {blocked} · **Blocks:** {blocks}\n{line}\n"
            f"## What you own\n`tasks/{tid}/`\n\n## Done means\n```\ntest -f tasks/{tid}/OUT.md\n```\n")
    (p / "PLAN.md").write_text(
        "# plan\n\n**Size:** XS\n**Workers:** human\n\n"
        "| ID | Task | Blocked by |\n|---|---|---|\n"
        f"| T1 | x | — |\n| T2 | y | {'T1' if ordered else '—'} |\n")
    r = subprocess.run([sys.executable, str(GATE), str(p), "--run-gates"],
                       capture_output=True, text=True, timeout=180)
    line = next((l for l in r.stdout.splitlines() if "worktree-disjoint" in l), "")
    return ("PASS" if line.startswith("PASS") else
            "FAIL" if line.startswith("FAIL") else "NONE"), line


try:
    v, line = verdict("/srv/work/infra", "/srv/work/infra")
    chk("probe · two CONCURRENT tasks in one worktree -> FAIL", v, "FAIL")
    chk("probe · and it names both tasks", "T1 and T2" in line, True)
    chk("probe · and tells the author to put an edge between them",
        "Blocked by" in line, True)

    # The design this check must NOT break.
    v, _ = verdict("/srv/work/infra", "/srv/work/infra", ordered=True)
    chk("control · ORDERED tasks may share a worktree — that is the point", v, "PASS")
    v, _ = verdict("/srv/work/infra", "/srv/work/harness")
    chk("control · concurrent tasks in DIFFERENT worktrees are fine", v, "PASS")
    v, line = verdict(None, None)
    chk("control · a plan that declares no worktree passes", v, "PASS")
    chk("control · ...and says so rather than going silent",
        "no task declares a worktree" in line, True)
    v, _ = verdict("<path>", "<path>")
    chk("control · an unfilled template placeholder is not a declaration", v, "PASS")
    v, line = verdict("/srv/work/infra/", "/srv/work/infra")
    chk("probe · a trailing slash is the same worktree", v, "FAIL")

    # Calibration: the shipped examples declare no worktree, so nothing moves.
    for name, want in (("minimal-passing-plan", 0), ("a-real-first-plan", 1)):
        r = subprocess.run([sys.executable, str(GATE), str(ROOT / "examples" / name),
                            "--run-gates"], capture_output=True, text=True, timeout=300)
        chk(f"calibration · {name} still exits {want}", r.returncode, want)
finally:
    shutil.rmtree(LAB, ignore_errors=True)

print()
print(f"\033[31m{fails} failed\033[0m" if fails
      else "\033[32mall worktree-disjoint tests passed\033[0m")
sys.exit(1 if fails else 0)
