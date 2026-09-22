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
import time
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "validate-plan.py"
fails = 0
LAB = Path(tempfile.mkdtemp(prefix="grillin-gff."))
# A GRILLIN_GATE_TIMEOUT exported by the caller would reach every gate this
# harness runs and change what it proves — or, if invalid, fail 43 checks that
# have nothing to do with it. Each check that wants a limit sets its own.
os.environ.pop("GRILLIN_GATE_TIMEOUT", None)


def chk(label, got, want):
    global fails
    if got == want:
        print(f"  \033[32mPASS\033[0m  {label}")
    else:
        fails += 1
        print(f"  \033[31mFAIL\033[0m  {label} — want {want!r}, got {got!r}")


def verdict(done_cmd, status="NOT STARTED", name="p", env=None):
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
                       capture_output=True, text=True, timeout=180,
                       env=dict(os.environ, **(env or {})))
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
# SHORTENED ON PURPOSE, and only here. The claim is that a hanging gate FAILS,
# not how long the limit is, and waiting out the default 60s made this one check
# 60 of the harness's 64 seconds. The default itself is checked right after,
# without running anything for a minute.
_t = time.monotonic()
v, line = verdict("sleep 90", env={"GRILLIN_GATE_TIMEOUT": "2"})
chk("a hanging gate still FAILS on timeout", v, "FAIL")
chk("...and the message names the limit it hit", "after 2s" in line, True)
chk("...which was the 2s asked for, not the default", time.monotonic() - _t < 30, True)

# The default, and the refusals, read straight from the gate module.
import importlib.machinery, importlib.util  # noqa: E401,E402
_spec = importlib.util.spec_from_loader(
    "vp", importlib.machinery.SourceFileLoader("vp", str(GATE)))
VP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(VP)
_saved = os.environ.pop("GRILLIN_GATE_TIMEOUT", None)
chk("with nothing set, the limit is still 60s", VP.gate_timeout(), 60.0)
for bad in ("0", "-5", "61", "600", "soon"):
    os.environ["GRILLIN_GATE_TIMEOUT"] = bad
    try:
        VP.gate_timeout()
        refused = False
    except ValueError:
        refused = True
    chk(f"GRILLIN_GATE_TIMEOUT={bad} is refused", refused, True)
os.environ.pop("GRILLIN_GATE_TIMEOUT", None)
if _saved is not None:
    os.environ["GRILLIN_GATE_TIMEOUT"] = _saved
r = subprocess.run([sys.executable, str(GATE), str(LAB)], capture_output=True, text=True,
                   env=dict(os.environ, GRILLIN_GATE_TIMEOUT="600"))
chk("...and the gate exits 3 on it, before looking at any plan", r.returncode, 3)
chk("...saying why", "may shorten the limit, never lengthen it" in r.stderr, True)

print("\n=== caller mistakes exit 3; INCOMPLETE keeps 2 ===")
# Exit 2 used to cover both "gates were not run" and "you called it wrongly",
# so a CI step reading only the code could not tell them apart (2026-09-17).
def gate_rc(*args):
    return subprocess.run([sys.executable, str(GATE), *args], capture_output=True,
                          text=True, timeout=60).returncode
chk("a plan path that is not a directory exits 3", gate_rc(str(LAB / "no-such-plan")), 3)
chk("an unreadable --config exits 3",
    gate_rc(str(ROOT / "examples" / "minimal-passing-plan"), "--config", str(LAB / "nope.json")), 3)
chk("a missing --contract-hash file exits 3",
    gate_rc(str(LAB), "--contract-hash", str(LAB / "nope.md")), 3)
chk("an unknown option exits 3", gate_rc(str(LAB), "--no-such-option"), 3)
chk("control · a sound plan without --run-gates still exits 2 (INCOMPLETE)",
    gate_rc(str(ROOT / "examples" / "minimal-passing-plan")), 2)
chk("control · the known-bad example still exits 1",
    gate_rc(str(ROOT / "examples" / "a-real-first-plan"), "--run-gates"), 1)

print("\n=== the strict rule: a missing script is flagged, guarded or not (D12) ===")
# A guard rule was tried on 2026-09-17 and reverted the same day, after three
# adversarial reviews broke it. Every gate below names a script that does not
# exist; each must FAIL — the guarded honest forms because the rule is strict,
# and the rest because sh really does run the missing script.
NL = chr(10)
X = "tasks/T1/run.py"
strict = {
    f"test -f {X} && python3 {X}": "a test -f guard",
    f"[ -f {X} ] && python3 {X}": "a [ -f ] guard",
    f"true || test -f {X} && python3 {X}": "a guard behind ||  (T20)",
    f'echo "x && test -f {X} && y" && python3 {X}': "a guard inside quotes (T20)",
    f"test -f {X} && echo ok{NL}python3 {X}": "a script on the next line (T20)",
    f"echo $(true{NL}test -f {X} && :) && python3 {X}": "a guard inside $( ) (T23)",
    f"echo $((1<<3)){NL}true; python3 {X}": "a shift that looks like a heredoc (T23)",
    f"cat <<END-OF{NL}x{NL}END-OF{NL}python3 {X}": "a heredoc delimiter with a dash (T23)",
    f"cat <<E.O{NL}x{NL}E.O{NL}python3 {X}": "a heredoc delimiter with a dot (T23)",
    f"test -f {X} &>/dev/null && python3 {X}": "&> under dash (T23)",
    f"test -f {X} &&{NL}python3 {X}": "a guard continued on the next line",
}
for cmd, why in strict.items():
    v, _ = verdict(cmd)
    chk(f"{why} FAILS", v, "FAIL")
chk("`python3 - <<'EOF'` reads its program from stdin: no script to find",
    VP._missing_prereq("python3 - <<'EOF'" + NL + "print(1)" + NL + "EOF", LAB), None)
chk("...and a path after `-` is an argv word, not the script it runs",
    VP._missing_prereq("python3 - tasks/T1/nosuch.py", LAB), None)
chk("a redirection is never taken for the script",
    VP._missing_prereq("python3 <in.txt -u >out.txt", LAB), None)
chk("the guard code is gone from the gate",
    any(hasattr(VP, n) for n in ("_sh_segments", "_guarded_path", "_drop_redirections")), False)

print("\n=== `-` is stdin to an interpreter and END OF OPTIONS to a shell (T26) ===")
# `sh - run.sh` RUNS run.sh — POSIX makes a bare `-` the end-of-options marker
# for a shell, not a request to read the program from stdin. Treating every
# interpreter alike let a missing script through under all four shells.
for sh in ("sh", "bash", "dash", "zsh"):
    # At the function, not end to end: `zsh` is not installed here and `bash -`
    # would come back FAIL for the wrong reason ("command not found"), so the
    # end-to-end form is insensitive for two of the four.
    chk(f"`{sh} - <missing script>` names the script",
        "run.py" in (VP._missing_prereq(f"{sh} - {X}", LAB) or ""), True)
for sh in ("sh", "dash"):
    v, _ = verdict(f"{sh} - {X}")
    chk(f"...and `{sh} - <missing script>` is a clean FAIL end to end", v, "FAIL")
for lang in ("python3", "node", "perl", "ruby"):
    chk(f"`{lang} - <path>` still reads its program from stdin",
        VP._missing_prereq(f"{lang} - {X}", LAB), None)

print("\n=== a word in front of the interpreter no longer hides it (T26) ===")
wrapped = {
    f"exec python3 {X}": "exec",
    f"timeout 5 python3 {X}": "timeout with a bare number",
    f"timeout 5s python3 {X}": "timeout with a duration",
    f"env FOO=1 python3 {X}": "env with an assignment",
    f"nohup python3 {X}": "nohup",
    f"stdbuf -o0 python3 {X}": "stdbuf with its own option",
    f"command python3 {X}": "command",
    f"nice -n 5 python3 {X}": "nice with a value-taking flag",
    f"setsid python3 {X}": "setsid",
    f"time python3 {X}": "time",
    f"exec env nohup python3 {X}": "three wrappers at once",
}
for cmd, why in wrapped.items():
    v, _ = verdict(cmd)
    chk(f"a missing script behind {why} FAILS", v, "FAIL")

print("\n=== CONTROL · stripping a wrapper must not invent a missing script ===")
# Non-vacuous: the script IS there, so every one of these must come back None.
(LAB / "tasks" / "T1").mkdir(parents=True, exist_ok=True)
(LAB / X).write_text("print(1)" + NL)
for cmd, why in ((f"exec python3 {X}", "exec"),
                 (f"timeout 5 python3 {X}", "timeout"),
                 (f"env FOO=1 python3 {X}", "env"),
                 (f"nice -n 5 python3 {X}", "nice")):
    chk(f"{why} around a script that exists is clean", VP._missing_prereq(cmd, LAB), None)
chk("...and the wrapper's own name is never taken for the script",
    VP._missing_prereq("timeout 5 python3 tasks/T1/gone.py", LAB), 
    VP._missing_prereq("python3 tasks/T1/gone.py", LAB))
chk("a wrapper with nothing after it is not a script run",
    VP._missing_prereq("exec", LAB), None)
(LAB / X).unlink()

print("\n=== a shell's bundled options are options, not a script (T26) ===")
# `sh -ec '<code>'` used to report the whole code string as a missing script,
# and `bash -euo pipefail -c '<code>'` reported one called 'pipefail'. Both
# statements were false about the plan's own files.
for cmd, why in (
    ("sh -ec 'python3 build.py'", "`-ec` bundles inline code"),
    ("bash -ec 'python3 build.py'", "so does bash's"),
    ("bash -euo pipefail -c 'python3 build.py'", "`-euo` ends in -o, which takes a value"),
    ("sh -eu -c 'python3 build.py'", "an unbundled group before -c"),
):
    chk(f"{why}: no script to find", VP._missing_prereq(cmd, LAB), None)
chk("CONTROL · a shell option group with no `c` does not hide the script",
    "run.sh" in (VP._missing_prereq("sh -eu tasks/T1/run.sh", LAB) or ""), True)

print("\n=== a file named on the command line has a ceiling (T26) ===")
# `--config` was stat'd before it was opened; `--contract-hash` was not, and a
# 2 GiB TASK.md gave a MemoryError traceback and exit 1 — FAIL's code.
big = LAB / "huge-task.md"
with open(big, "wb") as fh:
    fh.truncate((1 << 20) + 1)
chk("a --contract-hash file over 1 MiB exits 3, without reading it",
    gate_rc(str(ROOT / "examples" / "minimal-passing-plan"), "--contract-hash", str(big)), 3)
big.unlink()
fifo = LAB / "task-fifo.md"
os.mkfifo(fifo)
chk("a --contract-hash that is a FIFO exits 3 and does not hang",
    gate_rc(str(ROOT / "examples" / "minimal-passing-plan"), "--contract-hash", str(fifo)), 3)
fifo.unlink()
chk("--contract-hash /dev/zero exits 3, without reading it",
    gate_rc(str(ROOT / "examples" / "minimal-passing-plan"), "--contract-hash", "/dev/zero"), 3)
for flag in ("--contract-hash", "--config"):
    chk(f"an empty-string {flag} is a caller mistake, not INCOMPLETE",
        gate_rc(str(ROOT / "examples" / "minimal-passing-plan"), flag, ""), 3)

print("\n=== the rest of the caller mistakes exit 3 (T20) ===")
for n, body in enumerate(("42", "[1]")):
    cfg = LAB / f"cfg-{n}.json"
    cfg.write_text(body)
    chk(f"a --config holding {body} exits 3",
        gate_rc(str(ROOT / "examples" / "minimal-passing-plan"), "--config", str(cfg)), 3)
locked = LAB / "locked-task.md"
locked.write_text("# x\n")
locked.chmod(0)
chk("an unreadable --contract-hash file exits 3", gate_rc(str(LAB), "--contract-hash", str(locked)), 3)
locked.chmod(0o644)
shut = LAB / "shut-plan"
shut.mkdir(exist_ok=True)
shut.chmod(0)
chk("an unreadable plan directory exits 3", gate_rc(str(shut)), 3)
shut.chmod(0o755)

cage = LAB / "cage"
cage.mkdir(exist_ok=True)
(cage / "task.md").write_text("# x\n")
cage.chmod(0)
chk("a --contract-hash file inside a directory the caller cannot enter exits 3",
    gate_rc(str(LAB), "--contract-hash", str(cage / "task.md")), 3)
cage.chmod(0o755)
long = "a" * 5000
chk("an over-long plan path exits 3", gate_rc(long), 3)
chk("an over-long --contract-hash path exits 3", gate_rc(str(LAB), "--contract-hash", long), 3)
loop = LAB / "loop"
if not loop.is_symlink():
    os.symlink(loop, loop)
chk("a plan path that is a symlink loop exits 3", gate_rc(str(loop)), 3)
deep = LAB / "deep.json"
deep.write_text("[" * 100000)
chk("a --config nested too deeply exits 3",
    gate_rc(str(ROOT / "examples" / "minimal-passing-plan"), "--config", str(deep)), 3)
chk("--config /dev/zero exits 3, without reading it",
    gate_rc(str(ROOT / "examples" / "minimal-passing-plan"), "--config", "/dev/zero"), 3)
fifo = LAB / "cfg.fifo"
if not fifo.exists():
    os.mkfifo(fifo)
try:
    rc = gate_rc(str(ROOT / "examples" / "minimal-passing-plan"), "--config", str(fifo))
except subprocess.TimeoutExpired:
    rc = "hung"
chk("a --config that is a FIFO exits 3 and does not hang", rc, 3)
big = LAB / "big.json"
big.write_text("{" + '"k": 1,' * 200000 + '"z": 1}')
chk("a --config over 1 MiB exits 3",
    gate_rc(str(ROOT / "examples" / "minimal-passing-plan"), "--config", str(big)), 3)
r = subprocess.run([sys.executable, str(GATE), "--help"], capture_output=True, text=True)
chk("--help states exit 3", "3 = the command itself was wrong" in r.stdout, True)

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
print("\n=== 8 · a flag's VALUE is not a script — reported from the field ===")
# `python3 -m pytest` was refused because no file named `pytest` exists. The old
# search took the first argument not starting with `-`, which is right for
# `python3 build.py` and wrong for every flag that CONSUMES the next word. Two
# defects were behind the one report and both are exercised here: this one, and
# the runner's own "file or directory not found" being read as a broken gate
# (section 9). Same shape as Smokin's VARIADIC_FLAGS.
v, line = verdict("python3 -m pytest tests/")
chk("`python3 -m pytest tests/` is a CLEAN FAIL", v, "PASS")
chk("...and nothing claims a script called 'pytest' is missing",
    "'pytest'" in line, False)
v, _ = verdict("python3 -m unittest discover")
# NOT `python`. This box has only python3, so the first version of this case was
# measuring a missing interpreter (exit 127) and reporting the tool wrong for
# catching it. The harness found it, which is the whole reason a control exists.
chk("`python3 -m unittest discover` is clean", v, "PASS")
v, _ = verdict("node -e \"process.exit(1)\"")
chk("`node -e` runs code, not a file called 'process.exit(1)'", v, "PASS")
v, _ = verdict("bash -c 'exit 1'")
chk("`bash -c` likewise", v, "PASS")

print("\n=== 8b · CONTROL · a real missing script is still caught ===")
# The whole value of section 8 is that it did not blind the check. A flag that
# takes a value must be STEPPED OVER, not treated as an exit from the search.
v, line = verdict("python3 /nonexistent/checker.py")
chk("a script that is really absent still FAILS", v, "FAIL")
chk("...and the message names it", "/nonexistent/checker.py" in line, True)
v, line = verdict("python3 -X dev /nonexistent/checker.py")
chk("...and a value-taking flag before it does not hide it", v, "FAIL")
chk("...naming the script, not the flag's value 'dev'", "'dev'" in line, False)

print("\n=== 9 · a test runner's own 'not found' is not a broken gate ===")
# `\bnot found\b` sat in the unambiguous list with no inside-or-outside-the-plan
# test, so a runner reporting that the directory it was told to collect does not
# exist yet failed the plan. tests/ is what the task PRODUCES: that is the gate
# working. Same defect as the `grep` trap in section 1, on a different phrase.
v, line = verdict("python3 -m pytest tasks/T1/tests/")
chk("a runner pointed at a directory the task will create is clean", v, "PASS")
chk("...and no 'could not run here' verdict", "could not run here" in line, False)

print("\n=== 9b · CONTROL · 'command not found' still means what it said ===")
# The specific spelling names a missing BINARY and stays unambiguous. Only the
# bare phrase moved.
v, line = verdict("sh -c 'definitely-not-a-real-binary'")
chk("a missing binary inside a subshell still FAILS", v, "FAIL")

if fails:
    print(f"\033[31m{fails} failed\033[0m")
else:
    print("\033[32mall gate-fails-first checks passed\033[0m")
shutil.rmtree(LAB, ignore_errors=True)
sys.exit(1 if fails else 0)
