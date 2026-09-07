#!/usr/bin/env python3
"""Calibrate check_stripped_contract — the worker must not read the curator's notes.

WHY THIS CHECK EXISTS. templates/TASK.md.template is over 370 lines and well
over half of it is `<!-- -->` commentary: which failure bought each field, what
breaks if it is dropped, which of them the gate actually parses. That is written
for the person AUTHORING a task and it is noise to the agent DOING it. The
template has said "deleted before the file reaches the worker" since the
beginning and nothing checked — which by OPERATING-THE-PLAN.md §11 made it a
preference, and preferences are the first thing dropped under time pressure.

WHAT MADE IT URGENT. Anthropic's guidance for the Claude 5 generation names this
exact failure — "If your CLAUDE.md is too long, Claude ignores half of it
because important rules get lost in the noise" — and their own remedy was to
delete over 80% of Claude Code's system prompt with no measurable loss on their
coding evals. A contract that ships 200 lines of history is not thorough. Its
real instructions are competing with an essay.

THE CONTROLS CARRY THE ARGUMENT. A short hand-written note is a legitimate thing
for one human to leave another in a task file, and a check that refused them
would teach curators that the gate objects to writing anything down. So the
probe is a template-sized block and the control is a curator-sized note, and the
test asserts they land on opposite sides. It also asserts, out loud, the case
this check deliberately MISSES: a short fragment left behind passes. That is the
safe direction for this check and the opposite of the one paths-disjoint chose,
because what is being protected here is attention rather than a file.

    python3 tests/test-stripped-contract.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "validate-plan.py"
TEMPLATE = ROOT / "templates" / "TASK.md.template"
LAB = Path(tempfile.mkdtemp(prefix="grillin-strip."))
fails = 0


def chk(label, got, want):
    global fails
    ok = got == want
    print(f"  \033[32mPASS\033[0m  {label}" if ok
          else f"  \033[31mFAIL\033[0m  {label}\n        got {got!r}, want {want!r}")
    if not ok:
        fails += 1


# A structurally sound plan run WITHOUT --run-gates exits 2, not 0: the gate
# refuses to call a plan operable when nothing has proved a done-command fails
# on unstarted work. So 2 is this fixture's "passed", and asserting 0 would be
# asserting the wrong success.
OK, BAD = 2, 1


def run(body, cfg=None):
    """One task carrying `body` between its header and its done-command."""
    p = LAB / "p"
    shutil.rmtree(p, ignore_errors=True)
    (p / "tasks" / "T1").mkdir(parents=True)
    (p / "tasks" / "T1" / "TASK.md").write_text(
        "# T1 — fixture\n\n**Status:** NOT STARTED\n**Owner:** human\n"
        "**Blocked by:** — · **Blocks:** —\n\n"
        f"{body}\n"
        "## What you own\n`tasks/T1/`\n\n## Done means\n```\ntest -f tasks/T1/OUT.md\n```\n")
    (p / "PLAN.md").write_text("# Fixture\n\n**Size:** XS\n\n| Task | Owner |\n|---|---|\n| T1 | human |\n")
    argv = [sys.executable, str(GATE), str(p)]
    if cfg is not None:
        (LAB / "cfg.json").write_text(cfg)
        argv += ["--config", str(LAB / "cfg.json")]
    r = subprocess.run(argv, capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if "stripped" in l]
    return r.returncode, "\n".join(lines)


BIG = "<!-- " + "\n".join(f"     line {i} of curator commentary" for i in range(12)) + " -->"
SMALL = "<!-- TODO: confirm this path with the platform team -->"
EDGE6 = "<!-- " + "\n".join(f"     line {i}" for i in range(6)) + " -->"   # exactly 6 lines
EDGE7 = "<!-- " + "\n".join(f"     line {i}" for i in range(7)) + " -->"   # exactly 7

print("\n=== 1 · PROBE · a template-sized block fails the plan ===")
rc, out = run(BIG)
chk("a 12-line comment block fails", rc, BAD)
chk("...and the finding is a FAIL on `stripped`", out.startswith("FAIL"), True)
chk("...and it says how many lines it found", "12-line" in out, True)
chk("...and it quotes the block so the deletion is visible", "curator commentary" in out
    or "<!--" in out, True)

print("\n=== 2 · CONTROL · a curator's own short note is untouched ===")
rc, out = run(SMALL)
chk("a one-line note passes", rc, OK)
chk("...and `stripped` reports PASS rather than staying silent", out.startswith("PASS"), True)

print("\n=== 3 · CONTROL · a contract with no comments at all ===")
rc, out = run("")
chk("no comments passes", rc, OK)
chk("...and still reports, so a clean plan is distinguishable from a skipped check",
    out.startswith("PASS"), True)

print("\n=== 4 · the threshold is where the docstring says it is ===")
rc, _ = run(EDGE6)
chk("exactly 6 lines passes — MAX_COMMENT_LINES is inclusive", rc, OK)
rc, _ = run(EDGE7)
chk("7 lines fails", rc, BAD)

print("\n=== 5 · the check can be turned off, and says so when it is ===")
rc, out = run(BIG, cfg='{"require_stripped_contract": false}')
chk("the block no longer fails the plan", rc, OK)
chk("...and the SKIP names the config key rather than going silent",
    "require_stripped_contract" in out, True)

print("\n=== 6 · the real template would be caught ===")
# The point of the whole check: a curator who copies the template verbatim and
# fills in the fields, without deleting the notes, must not pass. Read the real
# file rather than a fixture of it, so this assertion cannot rot away from it.
tpl = TEMPLATE.read_text()
rc, out = run(tpl.split("# <ID>", 1)[1] if "# <ID>" in tpl else tpl)
chk("shipping templates/TASK.md.template as a contract fails", rc, BAD)
chk("...on `stripped`", out.startswith("FAIL"), True)

print("\n=== 7 · STATED LIMIT · a short leftover fragment is NOT caught ===")
# Asserted deliberately. This is the documented blind spot, and a test that
# claimed otherwise would be the check overstating its own enforcement — the
# exact defect TASK.md.template's field register was rewritten to stop.
rc, _ = run("<!-- (no RESEARCH value on purpose — see the two axes above.) -->")
chk("a 1-line template fragment passes, as documented", rc, OK)

shutil.rmtree(LAB, ignore_errors=True)
print(f"\n\033[31m{fails} failed\033[0m" if fails else "\n\033[32mall passed\033[0m")
sys.exit(1 if fails else 0)
