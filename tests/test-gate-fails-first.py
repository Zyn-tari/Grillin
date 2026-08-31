#!/usr/bin/env python3
"""Calibrate `check_gates_fail_first` — which failures are the gate working.

THE DEFECT THIS FILE EXISTS FOR, and it was open from v1.0.0.

A done-command that grades CONTENT — `grep -q DONE tasks/T1/OUT.md` — reports
"No such file or directory" while the work is unstarted, because the artefact it
grades does not exist yet. That is the gate WORKING. This check read it as a
broken gate and told the author *"Its paths are unanchored"*, which was not true:
the path was anchored, `grep` simply exits 2 on stderr where `test -s` exits 1
silently.

The wasted cycle was not the cost. The cost was that the documented way out is a
bare `test -s`, which is satisfied by writing ANY file at all — so the refusal
pushed authors off a gate that reads content and onto one that gates paperwork.
One curator put it exactly that way, unprompted. And QUICKSTART §0b question 4
recommended the failing form the entire time.

Four first-time users reached it independently, plus one field report of the
mirror defect: a check that PASSED while printing the words "cannot open" in its
own message was reported as broken, because the scan read stdout as diagnosis.

THE RULE NOW. Exit 126/127 and a shell that names a missing tool, module,
permission or syntax error are broken gates. A missing FILE is ambiguous, so the
question is which file: one inside the plan directory is an artefact the plan has
not produced yet and the fail is clean; one outside it is a gate that cannot run
here. Diagnosis is read from stderr only — stdout is the gate's output, not its
opinion of itself.

    python3 tests/test-gate-fails-first.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "validate-plan.py"
fails = 0
LAB = Path(tempfile.mkdtemp(prefix="grillin-gff."))


def chk(label, got, want):
    global fails
    if got == want:
        print(f"  \033[32mPASS\033[0m  {label}")
    else:
        fails += 1
        print(f"  \033[31mFAIL\033[0m  {label} — want {want!r}, got {got!r}")


def verdict(done_cmd, status="NOT STARTED", name="p"):
    """Build a one-task plan around `done_cmd` and return (verdict, message).

    Everything except the done-command is held constant, so the ONLY thing any
    check below can be responding to is the command itself.
    """
    p = LAB / name
    shutil.rmtree(p, ignore_errors=True)
    (p / "tasks" / "T1").mkdir(parents=True)
    (p / "tasks" / "T1" / "TASK.md").write_text(
        f"# T1 — fixture\n\n**Status:** {status}\n**Owner:** human\n"
        f"**Blocked by:** — · **Blocks:** —\n\n## What you own\n`tasks/T1/`\n\n"
        f"## Done means\n```\n{done_cmd}\n```\n")
    (p / "PLAN.md").write_text(
        "# plan\n\n**Size:** XS\n**Workers:** human\n\n"
        "| ID | Task | Blocked by |\n|---|---|---|\n| T1 | x | — |\n")
    r = subprocess.run([sys.executable, str(GATE), str(p), "--run-gates"],
                       capture_output=True, text=True, timeout=180)
    line = next((l for l in r.stdout.splitlines() if "gate-fails-first" in l), "")
    return ("PASS" if line.startswith("PASS") else
            "FAIL" if line.startswith("FAIL") else "NONE"), line


print("\n=== 1 · the trap itself — a gate that reads content ===")
v, line = verdict("grep -q FOUND tasks/T1/OUT.md")
chk("the form QUICKSTART recommends is a CLEAN FAIL", v, "PASS")
chk("...and nothing calls the author's paths unanchored",
    "unanchored" in line, False)
v, _ = verdict("test -s tasks/T1/OUT.md && grep -q FOUND tasks/T1/OUT.md")
chk("the guarded form is unchanged", v, "PASS")
v, _ = verdict("[ \"$(cat tasks/T1/COUNT 2>/dev/null)\" = 7 ]")
chk("a count against a file that does not exist yet is clean", v, "PASS")
v, _ = verdict("python3 -c \"import sys,pathlib;"
               "sys.exit(0 if pathlib.Path('tasks/T1/OUT.md').read_text() else 1)\"")
chk("a python FileNotFoundError on a plan file is clean too", v, "PASS")

print("\n=== 2 · a genuinely broken gate still fails ===")
v, line = verdict("definitely-not-a-real-binary --check")
chk("a missing tool FAILS", v, "FAIL")
chk("...by exit status, not by wording (dash and bash word it differently)",
    "127" in line, True)
v, line = verdict("grep -q X /etc/no-such-file-anywhere")
chk("a file OUTSIDE the plan FAILS", v, "FAIL")
chk("...and the message names it", "/etc/no-such-file-anywhere" in line, True)
v, _ = verdict("python3 -c \"import no_such_module_at_all\"")
chk("a missing module FAILS", v, "FAIL")
v, _ = verdict("if then fi")
chk("a shell syntax error FAILS", v, "FAIL")
v, line = verdict("true")
chk("a gate that already passes on unstarted work FAILS", v, "FAIL")
chk("...for the right reason", "already exits 0" in line, True)

print("\n=== 3 · stdout is the gate's output, not its diagnosis ===")
# THE FIELD DEFECT. A passing check whose own message contained "cannot open"
# was reported as a broken gate — a string match on prose.
v, _ = verdict('echo "the fence in the page cannot open a fence in the proposal"; exit 1')
chk("prose containing 'cannot open' on stdout is NOT a broken gate", v, "PASS")
v, _ = verdict('echo "No such file or directory"; exit 1')
chk("...nor is the shell's own wording quoted on stdout", v, "PASS")
# ...but the same words on STDERR, about a file outside the plan, still count.
v, _ = verdict('echo "grep: /etc/passwd-nope: No such file or directory" >&2; exit 2')
chk("the same words on stderr about an outside path DO count", v, "FAIL")

print("\n=== 4 · silent controls — the parts that must not have moved ===")
v, _ = verdict("test -s tasks/T1/OUT.md", status="DONE")
chk("a DONE task is skipped entirely", v, "NONE")
v, _ = verdict("sleep 90")
chk("a hanging gate still FAILS on timeout", v, "FAIL")

print("\n=== 5 · the shipped fixtures ===")
print("\n=== 5 · a command's own PREREQUISITES are not deliverables ===")
# Found by the first real XL-band run: ten done-commands ran a script that did
# not exist yet. Which way the gate read that depended on the INTERPRETER —
# `bash missing.sh` exits 127 and was caught; `python3 missing.py` exits 2 with
# "No such file or directory", which the missing-file rule reads as a data
# artefact the plan has not produced, and passed. The reporting program was
# Python-heavy, so it saw the failing half.
v, line = verdict("python3 tools/check.py")
chk("a python script that does not exist FAILS", v, "FAIL")
chk("...and the message says it is the script, not the work",
    "the script it runs" in line, True)
v, _ = verdict("bash tools/run_done_command.sh")
chk("...and so does a shell script, as it always did", v, "FAIL")
v, _ = verdict("node tools/verify.js")
chk("...and any other interpreter", v, "FAIL")

# THE CONTROL THAT KEEPS THIS FROM SWALLOWING EVERY PLAN. A gate that grades a
# file the task will WRITE is the shape QUICKSTART recommends and must stay a
# clean fail. Only the script the gate EXECUTES is a prerequisite.
v, _ = verdict("test -f tasks/T1/OUT.md")
chk("control · a data artefact the task produces is still a clean fail", v, "PASS")
v, _ = verdict("grep -q FOUND tasks/T1/OUT.md")
chk("control · so is grepping one", v, "PASS")

print("\n=== 6 · the working directory, with the plan/no-plan line intact ===")
v, line = verdict("cd /srv/no-such-service && bash run.sh")
chk("cd into a directory OUTSIDE the plan FAILS", v, "FAIL")
chk("...and names the directory", "/srv/no-such-service" in line, True)
# `cd` short-circuits `&&`, so the command exits 1 — indistinguishable from a
# clean fail by exit status alone. That is why this is decided statically.
v, _ = verdict("cd dist && test -f app.js")
chk("control · cd into a directory the task BUILDS is a clean fail", v, "PASS")
v, _ = verdict("cd tasks && test -f T1/OUT.md")
chk("control · cd into one that exists is a clean fail", v, "PASS")

print("\n=== 7 · a task in flight is neither of this check's two states ===")
# The rule is "work that is not done must fail its gate". It holds at NOT
# STARTED and retires at DONE; in between, a done-command SHOULD start passing
# part way through. Reported from a 232-task plan where the cost was concrete:
# this gate is also the commit hook, so every commit taken during a long run was
# refused for a transient condition, and the way out is GRILLIN_SKIP — the habit
# the hook exists to prevent.
v, line = verdict("true", status="IN PROGRESS")
chk("a running task whose gate already passes is NOT a finding", v, "PASS")
chk("...and the line says no ruling was made, not that it passed",
    "no ruling is made" in line, True)
v, _ = verdict("false", status="IN PROGRESS")
chk("...and a running task whose gate fails is equally unruled", v, "PASS")

# THE CONTROLS. This check exists to catch a gate that is green before the work
# starts; making it blind to IN PROGRESS must not make it blind at NOT STARTED,
# which is where the defect it was written for actually lives.
v, _ = verdict("true", status="NOT STARTED")
chk("control · NOT STARTED and already passing is still the original defect", v, "FAIL")
v, _ = verdict("test -f tasks/T1/OUT.md", status="NOT STARTED")
chk("control · NOT STARTED and failing cleanly is still fine", v, "PASS")
v, _ = verdict("true", status="BLOCKED")
chk("control · BLOCKED is not in flight — still ruled on", v, "FAIL")

r = subprocess.run([sys.executable, str(GATE),
                    str(ROOT / "examples" / "minimal-passing-plan"), "--run-gates"],
                   capture_output=True, text=True, timeout=300)
chk("known-good still exits 0", r.returncode, 0)
r = subprocess.run([sys.executable, str(GATE),
                    str(ROOT / "examples" / "a-real-first-plan"), "--run-gates"],
                   capture_output=True, text=True, timeout=300)
chk("known-bad still exits 1", r.returncode, 1)
# The fix did not merely silence findings on the known-bad plan — it re-diagnosed
# one. T3's real defect is that its gate passes on unstarted work, which the
# missing-file misreading had been hiding behind the wrong message.
chk("...and T3 is now reported as the more serious defect it actually has",
    any("T3 is NOT STARTED but its done-command already exits 0" in l
        for l in r.stdout.splitlines()), True)

print()
if fails:
    print(f"\033[31m{fails} failed\033[0m")
else:
    print("\033[32mall gate-fails-first checks passed\033[0m")
shutil.rmtree(LAB, ignore_errors=True)
sys.exit(1 if fails else 0)
