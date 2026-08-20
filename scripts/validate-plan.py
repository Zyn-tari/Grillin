#!/usr/bin/env python3
"""
validate-plan.py — read a plan and fail if it is not operable.

    ./scripts/validate-plan.py <plan-dir> [--run-gates]

Grillin's opening argument is "mechanisms over memory". Until this script existed,
Grillin was memory: an 89-item checklist a human ticks and 25 anti-patterns nobody
runs. This is the mechanism.

SCOPE — deliberately narrow. This checks only what a machine can settle:
structure, references, ownership, and whether a stated gate actually gates.
It does NOT judge whether a plan is any good, whether a "done" criterion is
meaningful, or whether a contradiction was resolved correctly. Those need the
adversarial pass, and pretending otherwise would make this a rubber stamp with
a shell script attached.

AND THE CEILING IS LOW — say it out loud. On the first full run measured end to
end, this gate caught 2 defects and the adversarial readers caught 50. The two
layers catch disjoint classes: structural defects here, semantic ones there.
So the most valuable check below is not a structural one at all — it is
`check_adversary`, which does nothing except refuse to pass a plan that has
nobody staffed to attack it. See OPERATING-THE-PLAN.md.

Zero dependencies (python3 stdlib). Fail-closed: unknown state is a failure.
Exit 0 = operable. Exit 1 = not. Exit 2 = could not run the check itself.

Every finding cites file:line, because a validator that says "something is wrong"
is a worse version of the checklist it replaces.
"""

# ── version ─────────────────────────────────────────────────────────────────
# install.sh copies THIS FILE onto your PATH as `grillin`. A copied file has no
# git context, so it cannot work out its own provenance later — the installer
# rewrites INSTALLED_FROM below at install time. Left alone it says so, rather
# than claiming a provenance it does not have.
__version__ = "1.2.0"
INSTALLED_FROM = "source checkout"  # rewritten by install.sh

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

# Derived, never hardcoded: check-drift.py already asserts this set matches
# SCALING.json's gateChecks, so --version cannot claim a count the gate does not
# actually run.
GATE_CHECK_NAMES = sorted(set(re.findall(r'f\.(?:ok|fail)\(\s*"([a-z-]+)"',
                                         Path(__file__).read_text())))

# Why a declared check can stay silent, in that check's own terms. main() prints
# one of these as a SKIP line for every name that said nothing, so the printed
# run adds up to the number --version claims and a reader never has to open this
# file to find out where a missing line went.
#
# Keyed on the EMITTED NAME, not the function: check_owner_status emits two.
# `{floor}` is filled in from ADVERSARY_MIN_TASKS rather than written twice.
# tests/test-check-accounting.py fails when a declared name has no entry here,
# which is the only thing standing between this table and rot.
_ALWAYS = ("this check reports on every run — a SKIP here is a defect in the gate, "
           "not a fact about your plan")
SILENT_BECAUSE = {
    "adversary":           "turned off: the config does not set require_adversary",
    "adversary-context":   "not applicable: under the {floor}-task floor where an adversary "
                           "is staffed, or require_adversary is off",
    "brainstormed":        "not applicable: this plan has no PLAN.md — plan-truth owns that "
                           "failure, and one defect gets one finding",
    "config-integrity":    _ALWAYS,
    "confirmed-exercised": "turned off: the config does not set require_confirmed_is_exercised",
    "done-checkable":      "turned off: the config does not set require_done_command",
    "done-self-reference": "turned off: the config does not set require_done_command",
    "frozen-contract":     "turned off: the config does not set require_frozen_human_contracts",
    "gate-fails-first":    "not run: --run-gates was not given, so no done-command was executed",
    "graph":               "turned off: the config does not set require_graph_consistent",
    "health-checker":      "not applicable: under the {floor}-task floor, or require_adversary "
                           "is off",
    "instrument":          "not applicable: no task has a done-command for a plan-local "
                           "instrument to be load-bearing in, or require_instrument_fixture "
                           "is off",
    "invariants":          "not applicable: this plan declares no _INVARIANTS.toml — the layer "
                           "is opt-in by file and its absence is not a defect",
    "layout":              _ALWAYS,
    "owner":               _ALWAYS,
    "paths-disjoint":      "turned off: the config does not set require_paths_disjoint",
    "persona-model":       "turned off: the config does not set require_persona_model",
    "plan-truth":          "not applicable: this plan has no tasks/<ID>/TASK.md at all — layout "
                           "owns that failure; or require_plan_source_of_truth is off",
    "references":          "turned off: the config does not set require_refs_resolve",
    "research-task":       "not applicable: no task declares itself research, recon or a spike, "
                           "and the contract binds only a task sent to find something out",
    "rollback":            "turned off: the config does not set require_rollback_real",
    "rulings":             "not applicable: this plan declares no _RULINGS.toml — the layer is "
                           "opt-in by file and its absence is not a defect",
    "size-declared":       "not applicable: this plan has no PLAN.md — plan-truth owns that "
                           "failure",
    "status":              _ALWAYS,
}
# A name with no registered reason still gets a line. Silence is the one state
# this gate must never leave a reader to interpret, and an unexplained SKIP at
# least says so out loud instead of vanishing.
UNREGISTERED_SKIP = ("this check reported nothing and no reason is registered for it in "
                     "SILENT_BECAUSE — that is a defect in the gate; please report it")

# ── strictness floors ───────────────────────────────────────────────────────
# The config may only TIGHTEN these. Loosening past a floor is not a config
# change, it is a decision, and it belongs in a changelog entry — not in a
# one-line edit that silently defangs the gate. Lifted from project-base's
# verify_invariants.py, which had this right first.
FLOORS = {
    "require_owner": True,
    "require_status": True,
    "require_done_command": True,
    "require_refs_resolve": True,
    "require_graph_consistent": True,
    "require_layout": True,
    # ── added after the reskin run, where the gate caught 2 defects and the
    # readers caught 50. Four of the five below exist to move work out of the
    # layer with the low ceiling and into the layer that measurably pays.
    "require_plan_source_of_truth": True,
    "require_adversary": True,
    "require_confirmed_is_exercised": True,
    "require_frozen_human_contracts": True,
    "require_instrument_fixture": True,
    # lifted from project-base, which enforced both before Grillin existed
    "require_rollback_real": True,
    "require_paths_disjoint": True,
    "require_persona_model": True,
    "require_research_contract": True,
}
VALID_STATUS = {"NOT STARTED", "IN PROGRESS", "BLOCKED", "DONE"}

# Below this many tasks the method itself runs reduced (QUICKSTART §0), and a
# separately-staffed adversary costs more than it returns. At and above it, the
# adversary is not optional.
ADVERSARY_MIN_TASKS = 4
# Sections that constitute a task's contract. Changing any of them after the
# task has been handed out is moving the goalpost, which is why they are hashed.
# "if it fails" is OPTIONAL in the template and frozen when present. It decides
# "fix it" vs "stop and report", so it grades the work as surely as "Done means"
# does; a gradeable section outside the hash is a goalpost that can be moved after
# delivery, which is the exact failure check_frozen_human_contracts exists to stop.
# Absent sections contribute nothing to section_bodies(), so contracts written
# before this line hash exactly as they did.
CONTRACT_SECTIONS = ("what you own", "steps", "done means", "if it fails", "do not")

RE_STATUS = re.compile(r"^\*\*Status:\*\*\s*([A-Z ]+?)\s*(?:—|$)", re.M)
# TWO SPELLINGS REACHED THIS FIELD AND THEY MEAN DIFFERENT THINGS. `**Owner:**`
# is who is accountable. `**Agent:**` is the PERSONA, and RE_PERSONA owns that.
# The old single alternation matched whichever came FIRST in the file, so a task
# declaring both — which every shipped example does — resolved its owner to
# whichever line the author happened to put higher. In
# examples/minimal-passing-plan/T1 that made the owner
# "`recon` · **Model:** `claude-opus-5` · **Effort:** high", and every check
# downstream compared THAT instead of `worker-a`: adversary uniqueness, human
# ownership, the frozen contract. It was found by a first-time user reading the
# regex, not by any test, because nothing ever asserted what an owner resolves to.
#
# Owner wins wherever it appears. Agent remains a fallback only because
# templates/TASK.md.template shipped for a long time with no Owner line, so
# tasks authored from it have nothing else to name.
RE_OWNER_LINE = re.compile(r"^\*\*Owner\b[^:]*:\*\*\s*([^·\n]+?)\s*(?=\*\*|·|$)", re.M | re.I)
RE_AGENT_LINE = re.compile(r"^\*\*Agent\b[^:]*:\*\*\s*`?([^`·\n]+?)`?\s*(?=\*\*|·|$)", re.M | re.I)


def owner_of(text: str) -> str:
    """Who is accountable for this task. Empty string when nobody is named."""
    m = RE_OWNER_LINE.search(text) or RE_AGENT_LINE.search(text)
    return m.group(1).strip() if m else ""
# Both fields commonly share one line: "**Blocked by:** — · **Blocks:** T2, T4".
# Stop at the separator or the next bold field, or every entry in Blocks is read
# as a blocker and the graph check reports a cycle that does not exist.
RE_BLOCKED_BY = re.compile(r"\*\*Blocked by:\*\*\s*([^·\n]*?)(?=\*\*|·|$)", re.M | re.I)
RE_BLOCKS = re.compile(r"\*\*Blocks:\*\*\s*([^·\n]*?)(?=\*\*|·|$)", re.M | re.I)
RE_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)#][^)]*)\)")
RE_FENCE = re.compile(r"```[a-z]*\n(.*?)```", re.S)
RE_TASK_ID = re.compile(r"\b([A-Z]\d{1,3}[a-z]?)\b")
RE_READER = re.compile(r"^\*\*Reader:\*\*\s*([a-z]+)", re.M | re.I)
RE_DELIVERED = re.compile(r"^\*\*Delivered:\*\*\s*(.+)$", re.M | re.I)
# QUICKSTART §0b question 3 — "Are the workers AI agents?" — is asked once, about
# the whole plan. It had no written form, so the gate could not read the answer
# and applied the agent floors to plans of people. Absent means agents, which is
# what every existing plan means.
RE_WORKERS = re.compile(r"^\*\*Workers:\*\*\s*(.+)$", re.M | re.I)
# NOT anchored to line start: these two share a line, the way Agent/Model/Effort
# do. Anchoring them made the gate demand a Timebox that was already there, six
# characters to the right of where it was looking.
RE_KIND = re.compile(r"\*\*Kind:\*\*\s*([^·\n]+?)\s*(?=\*\*|·|$)", re.M | re.I)
RE_TIMEBOX = re.compile(r"\*\*Timebox:\*\*\s*([^·\n]+?)\s*(?=\*\*|·|$)", re.M | re.I)
RE_SHA = re.compile(r"sha256:([0-9a-f]{8,64})", re.I)
RE_CODE_SPAN = re.compile(r"`([^`\n]+)`")
RE_SCRIPT_REF = re.compile(r"([\w./-]+\.(?:py|sh|js|mjs|ts))")
# An invocation, not a subject. "`image_analyze`" names a thing; "`codewhale
# config get vision_model`" is something that was run. The difference is the
# whole of principle 7, and it is the difference F-2 fell through.
RE_INVOCATION = re.compile(
    r"(\s|--|\(\)|\|)"          # a space, a flag, a call, or a pipe
    r"|^\S+\.(py|sh|js|mjs|ts)\b"
)


class Findings:
    def __init__(self):
        self.rows = []

    def fail(self, check, where, msg):
        self.rows.append(("FAIL", check, where, msg))

    def ok(self, check, msg):
        self.rows.append(("PASS", check, "", msg))

    def skip(self, check, msg):
        # A check that simply says nothing looks exactly like a check that never
        # ran. `--version` claims 24 and a clean run printed 22 named checks; a
        # first-time curator found the gap, could not settle "not applicable"
        # against "did not fire" without reading this source, and was right not
        # to take it on trust. SKIP is a verdict, not a finding: it is never
        # counted in `failed` and never reaches the exit code.
        self.rows.append(("SKIP", check, "", msg))

    @property
    def failed(self):
        return any(r[0] == "FAIL" for r in self.rows)

    @property
    def named(self):
        """Every check that has said anything at all on this run."""
        return {r[1] for r in self.rows}


def line_of(path: Path, needle: str) -> int:
    try:
        for i, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
            if needle in line:
                return i
    except OSError:
        pass
    return 0


def self_check(f: Findings, cfg: dict):
    """A gate that can be turned off by editing one line is not a gate."""
    for key, floor in FLOORS.items():
        if cfg.get(key, floor) is not True and floor is True:
            f.fail("config-integrity", "config",
                   f"{key} is disabled, but the hardcoded floor requires it. "
                   f"Loosening this is a decision, not a config edit — record it "
                   f"in the changelog and change the floor deliberately.")
    if not f.failed:
        f.ok("config-integrity", "config is within the hardcoded strictness floors")


def find_tasks(plan: Path):
    """One folder per task, TASK.md inside it. Returns {id: path}."""
    tasks = {}
    tdir = plan / "tasks"
    if tdir.is_dir():
        for d in sorted(tdir.iterdir()):
            if d.is_dir() and (d / "TASK.md").is_file():
                tasks[d.name] = d / "TASK.md"
    return tasks


def check_layout(f: Findings, plan: Path, tasks: dict):
    if not tasks:
        f.fail("layout", str(plan),
               "no tasks/<ID>/TASK.md found — a plan with no locatable tasks "
               "cannot be dispatched or resumed")
        return
    # A task file living anywhere but its own folder breaks containment, the
    # output contract and the status glob at the same time.
    loose = [p for p in plan.rglob("TASK.md")
             if p.parent.parent.name != "tasks"]
    for p in loose:
        f.fail("layout", str(p), "TASK.md outside tasks/<ID>/ — see phase 5")
    stray = [p for p in plan.glob("*.md")
             if re.match(r"^(T\d|task[-_])", p.name, re.I)]
    for p in stray:
        f.fail("layout", str(p),
               "task-shaped file loose at the plan root; tasks born mid-run "
               "still get a folder before their first artefact")
    if not loose and not stray:
        f.ok("layout", f"{len(tasks)} tasks, each in its own folder")


def check_owner_status(f: Findings, tasks: dict, cfg: dict):
    missing_owner, bad_status = [], []
    for tid, path in tasks.items():
        text = path.read_text(errors="replace")
        if cfg.get("require_owner", True) and not owner_of(text):
            missing_owner.append(tid)
            f.fail("owner", f"{path}:1",
                   f"{tid} names no owner — an orchestrator cannot dispatch it")
        if cfg.get("require_status", True):
            m = RE_STATUS.search(text)
            if not m:
                bad_status.append(tid)
                f.fail("status", f"{path}:1",
                       f"{tid} has no **Status:** line — progress is unrecoverable "
                       f"after a context loss")
            elif m.group(1).strip() not in VALID_STATUS:
                bad_status.append(tid)
                f.fail("status", f"{path}:{line_of(path, m.group(0))}",
                       f"{tid} status {m.group(1).strip()!r} is not one of "
                       f"{sorted(VALID_STATUS)}")
    if not missing_owner:
        f.ok("owner", "every task names an owner")
    if not bad_status:
        f.ok("status", "every task carries a valid status line")


def done_command(path: Path):
    """
    The fenced command under a Done heading, if there is one.

    Scanned line by line rather than by regex because a shell comment inside the
    fence ("# all four sources agree") looks exactly like a markdown heading, and
    a regex that stops at the next '#' truncates mid-fence and reports a perfectly
    good command as prose. A validator that cries wolf gets ignored.
    """
    lines = path.read_text(errors="replace").splitlines()
    body, in_section, in_fence = [], False, False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_section:
                body.append(line)
            in_fence = not in_fence
            continue
        if not in_fence and re.match(r"^#+\s", line):
            if in_section:
                break
            in_section = bool(re.match(r"^#+\s*Done\b", line, re.I))
            continue
        if in_section:
            body.append(line)
    fence = RE_FENCE.search("\n".join(body) + "\n")
    if not fence:
        return None
    cmd = "\n".join(l for l in fence.group(1).splitlines()
                    if l.strip() and not l.strip().startswith("#")).strip()
    return cmd or None


def check_done_is_command(f: Findings, tasks: dict, cfg: dict):
    if not cfg.get("require_done_command", True):
        return
    missing = []
    for tid, path in tasks.items():
        if not done_command(path):
            missing.append(tid)
            f.fail("done-checkable", f"{path}:1",
                   f"{tid}'s done criterion is prose, not a runnable command — "
                   f"nobody can re-derive completion without asking someone")
    if not missing:
        f.ok("done-checkable", "every task's done criterion is a runnable command")


# The shapes a shell actually uses to say a file is missing. Kept small and
# literal on purpose: a clever parser that guesses wrong here re-creates the
# defect it exists to fix, and the fallback (look at the command itself) covers
# whatever these miss.
_MISSING_PATTERNS = (
    r"(?:^|\n)[^\n:]*: ([^\n:]+): No such file or directory",   # grep: f: No such…
    r"No such file or directory: '([^']+)'",                      # FileNotFoundError
    r"can't open file '([^']+)'",                                 # python3 foo.py
    r"cannot open '?([^'\n:]+)'?",                                # various
)


def _missing_path(err: str, cmd: str):
    """Which file did the shell say was missing? None when it did not say."""
    for pat in _MISSING_PATTERNS:
        m = re.search(pat, err, re.I)
        if m:
            return m.group(1).strip()
    # THE FALLBACK, and it is the honest one. If the diagnostic named no path,
    # look at what the command itself reads: a done-command that mentions a file
    # under the plan and got a missing-file error is overwhelmingly failing on
    # that file. Returning None here would put the plan back in the old
    # behaviour, which is the outcome this whole change exists to avoid.
    for tok in re.findall(r"[\w./-]+\.[\w]+", cmd):
        if not tok.startswith(("/", "~")) and ".." not in tok:
            return tok
    return None


def _inside(rel: str, plan: Path) -> bool:
    """Is this path inside the plan directory — i.e. something the plan makes?"""
    if rel.startswith("~"):
        return False
    try:
        target = (plan / rel).resolve() if not rel.startswith("/") else Path(rel).resolve()
        target.relative_to(plan.resolve())
        return True
    except (ValueError, OSError):
        return False


def check_gates_fail_first(f: Findings, plan: Path, tasks: dict):
    """
    The check that would have caught the worst defect in the pilot plan.

    A done-gate on work that has NOT been done must FAIL. A gate that is green
    before the task starts is not a gate — an orchestrator runs it, sees zero,
    and marks untouched work complete. Equally, a gate that cannot pass under
    any circumstance burns its loop cap and blocks everything downstream.
    """
    for tid, path in sorted(tasks.items()):
        text = path.read_text(errors="replace")
        m = RE_STATUS.search(text)
        status = m.group(1).strip() if m else "NOT STARTED"
        if status == "DONE":
            continue
        cmd = done_command(path)
        if not cmd:
            continue
        try:
            r = subprocess.run(cmd, shell=True, cwd=plan, timeout=60,
                               capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            f.fail("gate-fails-first", f"{path}",
                   f"{tid}'s done-command timed out after 60s — an orchestrator "
                   f"would hang on it")
            continue
        except OSError as e:
            f.fail("gate-fails-first", f"{path}", f"{tid}'s done-command could not run: {e}")
            continue
        # THREE outcomes, not two. A gate that fails because it cannot find its
        # own inputs is not a working gate — it is an unanchored one, and reading
        # its non-zero exit as "correctly fails" is false reassurance on exactly
        # the plans that are broken.
        # Exit status first, wording second. `shell=True` runs /bin/sh, which is
        # dash on Debian and Ubuntu, and dash says "not found" where bash says
        # "command not found" — so a regex written against bash silently passed
        # a gate that shells out to a binary nobody has installed, and reported
        # it as failing cleanly. 127 and 126 are POSIX and say it without prose.
        # STDERR ONLY. This used to scan stdout as well, and a task whose gate
        # PASSED while printing the words "cannot open" in its own message was
        # reported as a broken gate — a string match on prose, found in the
        # field. Under `sh`, a missing binary, a traceback and an unreadable file
        # all report on stderr; 126/127 below covers the rest by exit status. So
        # stdout is the gate's OUTPUT and is no longer read as its diagnosis.
        err = r.stderr or ""
        blew_up = None
        if r.returncode in (126, 127):
            blew_up = f"exit {r.returncode} — not found or not executable"
        else:
            m2 = re.search(
                r"command not found|\bnot found\b|ModuleNotFoundError|ImportError|"
                r"Permission denied|unbound variable|syntax error", err, re.I)
            if m2:
                blew_up = m2.group(0)
        # THE MISSING FILE IS AMBIGUOUS, AND READING IT ONE WAY WAS THE DEFECT.
        # `grep -q DONE tasks/T1/OUT.md` on unstarted work says "No such file or
        # directory" and exits 2 — which is the gate WORKING: the artefact it
        # grades does not exist yet. This check called that a broken gate, and
        # told the author "your paths are unanchored" when they were not. The
        # cost was not the wasted cycle. It was that the documented way out is a
        # bare `test -s`, which is satisfied by writing any file at all — so the
        # refusal pushed authors from a gate that reads content to one that reads
        # paperwork. Confirmed by four first-time users independently, and
        # QUICKSTART 0b recommended the failing form the whole time.
        #
        # So the question is WHICH file is missing. One the plan will produce is
        # a clean fail. One outside the plan is a gate that cannot run here.
        if blew_up is None:
            missing = re.search(
                r"FileNotFoundError|No such file or directory|cannot open|"
                r"can't open file", err, re.I)
            if missing:
                where = _missing_path(err, cmd)
                if where is None or not _inside(where, plan):
                    blew_up = (f"{missing.group(0)}: "
                               f"{where or 'and the gate does not say which file'}")
        if blew_up:
            f.fail("gate-fails-first", f"{path}",
                   f"{tid}'s done-command could not run here — it failed on its own "
                   f"inputs, not on the work ({blew_up!r}). Whatever it needs is not "
                   f"inside the plan directory, so an orchestrator running it from "
                   f"anywhere but the author's machine gets an error it may read as a "
                   f"clean fail.")
        elif r.returncode == 0:
            f.fail("gate-fails-first", f"{path}",
                   f"{tid} is {status} but its done-command already exits 0. "
                   f"The gate does not detect the work — an orchestrator would run "
                   f"it, see success, and mark unstarted work complete.")
        else:
            f.ok("gate-fails-first",
                 f"{tid}: gate fails cleanly while {status.lower()}, as a gate should")


# A LINK TO A FILE THE PLAN HAS NOT WRITTEN YET IS NOT A DANGLING LINK. This
# check resolved every relative link against the disk, so the shape the method
# recommends failed the method's own gate: a research-first plan grades T1 on
# `tasks/T1/FINDINGS.md` and tells T2 to read it before doing anything, and the
# moment T2 wrote that as a markdown link instead of a code span the gate called
# it broken. examples/research-first-plan is exactly that shape and only passes
# today because its cross-reference happens to be a backtick. The check was
# teaching authors to stop linking, which is the reverse of what it is for.
#
# WHERE THE LINE IS DRAWN, and it is not "anything under tasks/". Existing on
# disk is one way for a target to be real; being PROMISED is the other, and a
# promise counts only when it is written down. So a missing target is forgiven
# when both hold: it sits inside `tasks/<ID>/` for a task this plan actually
# holds, AND that task's own contract names the file — in its done-command, its
# Outputs section, anywhere in its TASK.md. That is the plan declaring what it
# produces, which is the only kind of evidence Grillin ever reads.
#
# What still fails, and has to: a typo (`tasks/T1/FINDNGS.md` is named by
# nobody), a link into a task folder that does not exist, and every link outside
# `tasks/` — a doc nobody wrote does not become real by being linked to.
def _promised_output(plan: Path, tasks: dict, md: Path, target: str):
    """Which task's contract promises `target`. None means no task's does."""
    rel = os.path.relpath(os.path.normpath(str(md.parent / target)), str(plan))
    parts = Path(rel).parts
    if len(parts) < 3 or parts[0] != "tasks" or parts[1] not in tasks:
        return None
    # LINKS ARE STRIPPED BEFORE THE PROMISE IS LOOKED FOR, and this was found by
    # this fix's own probe rather than by reading it. A task linking
    # `[notes](TYPO.md)` inside its OWN folder put the string "TYPO.md" into its
    # own contract, so the link stood as its own promise and every typo a task
    # made about itself passed. A link is a reference; only a declaration
    # promises — a done-command, an Outputs line, a sentence.
    text = RE_MD_LINK.sub("", tasks[parts[1]].read_text(errors="replace"))
    # The bare filename is enough: a done-command reading `test -s
    # tasks/T1/FINDINGS.md` and an Outputs line reading `FINDINGS.md` are the
    # same promise written at two levels of detail.
    if parts[-1] in text or "/".join(parts) in text:
        return parts[1]
    return None


def check_references(f: Findings, plan: Path, cfg: dict):
    if not cfg.get("require_refs_resolve", True):
        return
    tasks = find_tasks(plan)
    dangling = promised = 0
    for md in sorted(plan.rglob("*.md")):
        for i, line in enumerate(md.read_text(errors="replace").splitlines(), 1):
            for target in RE_MD_LINK.findall(line):
                t = target.split("#")[0].strip()
                if not t or "://" in t or t.startswith("mailto:"):
                    continue
                if (md.parent / t).exists():
                    continue
                if _promised_output(plan, tasks, md, t):
                    promised += 1
                    continue      # not written yet; declared, and that is real
                dangling += 1
                f.fail("references", f"{md}:{i}",
                       f"link target does not resolve: {t!r} "
                       f"(resolved relative to {md.parent})")
    if not dangling:
        f.ok("references", "every relative link in the plan resolves"
             + (f"; {promised} of them to a file a task's contract promises"
                if promised else ""))


def check_graph(f: Findings, tasks: dict, cfg: dict):
    if not cfg.get("require_graph_consistent", True):
        return
    blocked_by, blocks = {}, {}
    for tid, path in tasks.items():
        text = path.read_text(errors="replace")
        mb = RE_BLOCKED_BY.search(text)
        mk = RE_BLOCKS.search(text)
        blocked_by[tid] = set(RE_TASK_ID.findall(mb.group(1))) if mb else set()
        blocks[tid] = set(RE_TASK_ID.findall(mk.group(1))) if mk else set()

    bad = 0
    for tid in tasks:
        for dep in blocked_by[tid]:
            if dep not in tasks:
                bad += 1
                f.fail("graph", f"{tasks[tid]}",
                       f"{tid} is blocked by {dep}, which is not a task in this plan — "
                       f"an orchestrator cannot resolve or dispatch it")
            elif tid not in blocks.get(dep, set()):
                bad += 1
                f.fail("graph", f"{tasks[tid]}",
                       f"{tid} says it is blocked by {dep}, but {dep} does not list "
                       f"{tid} in Blocks — the graph disagrees with itself")
    # cycles
    seen, stack = set(), set()

    def walk(n):
        nonlocal bad
        if n in stack:
            bad += 1
            f.fail("graph", "", f"dependency cycle through {n}")
            return
        if n in seen:
            return
        seen.add(n); stack.add(n)
        for d in blocked_by.get(n, ()):
            if d in tasks:
                walk(d)
        stack.discard(n)

    for t in tasks:
        walk(t)
    if not bad:
        f.ok("graph", "dependency graph is consistent and acyclic")


# ── the execution-time checks ───────────────────────────────────────────────
# Everything above this line checks a plan as written. Everything below checks
# a plan as OPERATED — the state it is in once something has already gone
# wrong, which is where a plan spends most of its life and where Grillin had
# nothing to say until the reskin run made the gap impossible to miss.


def lines_outside_fences(path: Path):
    """(lineno, text) for every line that is not inside a code fence."""
    out, in_fence = [], False
    for i, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append((i, line))
    return out


def section_bodies(path: Path, wanted):
    """Text under each '## <wanted>' heading, in file order."""
    body, current, out = [], None, []
    for line in path.read_text(errors="replace").splitlines():
        m = re.match(r"^#+\s*(.+?)\s*$", line)
        if m:
            if current is not None:
                out.append("\n".join(body))
            head = re.sub(r"[^a-z ]", "", m.group(1).lower()).strip()
            current = head if any(head.startswith(w) for w in wanted) else None
            body = []
            continue
        if current is not None:
            body.append(line.rstrip())
    if current is not None:
        out.append("\n".join(body))
    return out


def contract_hash(path: Path) -> str:
    import hashlib
    chunks = section_bodies(path, CONTRACT_SECTIONS)
    norm = "\n".join(l for c in chunks for l in c.splitlines() if l.strip())
    return hashlib.sha256(norm.encode()).hexdigest()


def md_tables(path: Path):
    """Yield (header_cells, [row_cells...]) for each pipe table in the file."""
    rows, header = [], None
    for _, line in lines_outside_fences(path):
        if line.lstrip().startswith("|") and line.count("|") >= 2:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue                      # the ---|--- separator row
            if header is None:
                header = cells
            else:
                rows.append(cells)
        else:
            if header is not None:
                yield header, rows
            header, rows = None, []
    if header is not None:
        yield header, rows


def check_plan_source_of_truth(f: Findings, plan: Path, tasks: dict, cfg: dict):
    """
    tasks/ and PLAN.md must agree.

    check_graph validates TASK.md files against each other and nothing else, so
    a silently rewritten dependency edge is invisible to it: both sides of the
    edge get rewritten together and stay self-consistent. In the reskin run that
    concealed a DONE task depending on a BLOCKED prerequisite for three review
    rounds. A plan whose own source of truth is unchecked against its tasks has
    a blind spot exactly where re-planning happens.
    """
    if not cfg.get("require_plan_source_of_truth", True) or not tasks:
        return
    src = plan / "PLAN.md"
    if not src.is_file():
        f.fail("plan-truth", str(plan / "PLAN.md"),
               "no PLAN.md — tasks/ has nothing to be checked against. The task "
               "files can then drift as a set while staying self-consistent, "
               "which is invisible to every other check here.")
        return

    named, edges, saw_graph_table = set(), {}, False
    for _, line in lines_outside_fences(src):
        named |= set(RE_TASK_ID.findall(line))
    for header, rows in md_tables(src):
        idx = next((i for i, h in enumerate(header)
                    if re.search(r"blocked\s*by|depends", h, re.I)), None)
        if idx is None:
            continue
        saw_graph_table = True
        for cells in rows:
            if not cells or idx >= len(cells):
                continue
            ids = RE_TASK_ID.findall(cells[0])
            if len(ids) != 1:
                continue
            edges[ids[0]] = set(RE_TASK_ID.findall(cells[idx]))

    # A plan's task-ID namespace is defined by its own folders. Question ids
    # (Q1), rule ids (R2b) and contradiction ids (C1) are the same SHAPE as a
    # task id and are not task ids — flagging them is how a gate becomes
    # wallpaper. Only ids sharing a prefix with a real task folder are in scope.
    prefixes = {m.group(1) for m in
                (re.match(r"^([A-Z]+)", t) for t in tasks) if m}
    bad = 0
    for tid in sorted(named - set(tasks)):
        m = re.match(r"^([A-Z]+)", tid)
        if not m or m.group(1) not in prefixes:
            continue
        bad += 1
        f.fail("plan-truth", f"{src}:{line_of(src, tid)}",
               f"PLAN.md names {tid} but tasks/{tid}/TASK.md does not exist")
    for tid in sorted(set(tasks) - named):
        bad += 1
        f.fail("plan-truth", f"{tasks[tid]}:1",
               f"tasks/{tid}/ exists but PLAN.md never names it — the plan's "
               f"source of truth does not know this task is in the run")

    for tid, declared in sorted(edges.items()):
        if tid not in tasks:
            continue
        text = tasks[tid].read_text(errors="replace")
        mb = RE_BLOCKED_BY.search(text)
        actual = set(RE_TASK_ID.findall(mb.group(1))) if mb else set()
        if declared != actual:
            bad += 1
            f.fail("plan-truth", f"{tasks[tid]}:1",
                   f"{tid} is blocked by {sorted(actual) or '—'} in its TASK.md but "
                   f"{sorted(declared) or '—'} in PLAN.md. One of them was edited "
                   f"and the other was not; the gate cannot tell you which is right, "
                   f"only that the plan no longer describes the work.")

    if not saw_graph_table and len(tasks) >= ADVERSARY_MIN_TASKS:
        bad += 1
        f.fail("plan-truth", f"{src}:1",
               "PLAN.md declares no dependency table, so its graph cannot be "
               "cross-checked against tasks/. Give it a table with a 'Blocked by' "
               "column — one row per task — or the edges live in exactly one place "
               "and drift there unobserved.")
    if not bad:
        f.ok("plan-truth", "PLAN.md and tasks/ name the same tasks and the same edges")


def check_adversary(f: Findings, tasks: dict, cfg: dict):
    """
    Someone must be staffed to attack the work, and they must be clean.

    Principle 8 already says never certify your own work. It has never had a
    mechanism, a staffing model or a check, and it is the highest-yield rule in
    the framework: on the reskin run the readers found 50 of the 52 defects and
    the gate found 2. A reader that has read the plan's reasoning is excellent
    at process enforcement and disqualified from judging the result — those are
    two roles, not one, and the disqualification is what this check enforces.
    """
    if not cfg.get("require_adversary", True):
        return
    if len(tasks) < ADVERSARY_MIN_TASKS:
        f.ok("adversary", f"{len(tasks)} tasks — below the {ADVERSARY_MIN_TASKS}-task "
                          f"floor where a separately-staffed adversary earns its cost")
        return

    owners, readers = {}, {}
    for tid, path in tasks.items():
        text = path.read_text(errors="replace")
        owners[tid] = owner_of(text).lower()
        mr = RE_READER.search(text)
        if mr:
            readers[tid] = mr.group(1).strip().lower()

    adversaries = [t for t, r in readers.items() if r == "adversary"]
    if not adversaries:
        f.fail("adversary", f"{sorted(tasks)[0]}",
               "no task declares '**Reader:** adversary'. The plan has nobody "
               "staffed to attack it. A green gate means operable, not correct — "
               "and the correctness layer is the one that finds almost everything.")
        return

    bad = 0
    for adv in adversaries:
        who = owners.get(adv, "")
        if not who:
            bad += 1
            f.fail("adversary", f"{tasks[adv]}:1",
                   f"{adv} is the adversarial pass but names no owner — the one "
                   f"task that must be staffed deliberately is unstaffed")
            continue
        clash = sorted(t for t, o in owners.items() if t != adv and o == who)
        if clash:
            bad += 1
            f.fail("adversary", f"{tasks[adv]}:1",
                   f"{adv}'s owner ({who!r}) also owns {clash}. The adversary is "
                   f"contaminated: it would be judging work it produced. Give this "
                   f"task an owner that appears nowhere else in the plan.")
    if not bad:
        f.ok("adversary",
             f"{sorted(adversaries)} is declared adversarial and its owner is named on no "
             f"other task. This checks the DECLARATION only \u2014 nothing here can tell who "
             f"actually RAN it, and in a one-agent setup the separation is fictional. "
             f"`smokin verify` says so out loud; `smokin tick` enforces it where it can.")


RE_CONTEXT = re.compile(r"^\*\*Context:\*\*\s*(.+)$", re.M | re.I)


def check_health_checker(f: Findings, tasks: dict, cfg: dict):
    """
    The OTHER reader. There are two, and only one of them was ever enforced.

    A **health checker** runs continuously, in rounds, asking *are the rules
    being followed?* — it has read everyone's reasoning, which is exactly what
    makes it good at this and disqualifies it from judging the result.
    An **adversary** runs once, at the end, asking *is the result true?* — where
    that same contamination is disqualifying.

    Opposite contamination rules, so they cannot be the same person, and this
    check deliberately does NOT require a clean owner: for the health role,
    contamination is the qualification.

    On the reference run the health checker caught roughly 20 defects. An agent
    briefing an orchestrator from QUICKSTART alone staffed the adversary and left
    this role out entirely, because nothing asked for it and the document that
    describes it was unreachable from the entry path.
    """
    if not cfg.get("require_adversary", True):
        return
    if len(tasks) < ADVERSARY_MIN_TASKS:
        return                          # check_adversary already reported the floor
    for tid, path in sorted(tasks.items()):
        m = RE_READER.search(path.read_text(errors="replace"))
        if m and m.group(1).strip().lower() == "health":
            f.ok("health-checker",
                 f"{tid} declares '**Reader:** health' — the rules-following pass, "
                 f"run in rounds. Its contamination is required, not disqualifying, "
                 f"so it is not checked for a clean owner.")
            return
    f.fail("health-checker", f"{sorted(tasks)[0]}",
           "no task declares '**Reader:** health'. There are TWO reader roles and this "
           "plan staffs one. The health checker runs in rounds asking whether the RULES "
           "are being followed — it caught ~20 defects on the reference run, and it is "
           "the role most often left out because the adversary is the famous one. "
           "See OPERATING-THE-PLAN.md §7.")


def check_adversary_context(f: Findings, tasks: dict, cfg: dict):
    """
    The adversary must not be a subagent of the orchestrator.

    §7: fresh context — "Not a subagent of the orchestrator, not a continued
    session." An agent briefing an orchestrator instructed the exact arrangement
    the method forbids, because the rule lived in a document the entry path never
    mentioned.

    THIS CHECK SURFACES THE RULE; IT DOES NOT ENFORCE IT. Nothing readable from
    files can establish how a task was actually instantiated. What it does is put
    the sentence in front of whoever writes the adversary's contract, which is
    where the mistake was made.
    """
    if not cfg.get("require_adversary", True) or len(tasks) < ADVERSARY_MIN_TASKS:
        return
    bad = 0
    for tid, path in sorted(tasks.items()):
        text = path.read_text(errors="replace")
        m = RE_READER.search(text)
        if not m or m.group(1).strip().lower() != "adversary":
            continue
        mc = RE_CONTEXT.search(text)
        if not mc:
            bad += 1
            f.fail("adversary-context", f"{path}:1",
                   f"{tid} is the adversarial pass and declares no '**Context:**'. §7 "
                   f"requires fresh context — NOT a subagent of the orchestrator, NOT a "
                   f"continued session. Add: '**Context:** fresh — not a subagent of the "
                   f"orchestrator, not a continued session'. This line is a declaration, "
                   f"not a proof: nothing here can see how the task was really started.")
        elif "fresh" not in mc.group(1).lower():
            bad += 1
            f.fail("adversary-context", f"{path}:{line_of(path, mc.group(0))}",
                   f"{tid}'s **Context:** says {mc.group(1).strip()!r}. §7 requires fresh "
                   f"context; a subagent or a continued session is reviewing its own "
                   f"reasoning.")
    if not bad:
        f.ok("adversary-context",
             "the adversarial pass declares fresh context (a declaration, not a proof)")


def check_confirmed_is_exercised(f: Findings, plan: Path, cfg: dict):
    """
    CONFIRMED means you ran something.

    Principle 7 already says evidence is execution, not inspection. The LABEL
    did not carry the principle: QUICKSTART defined CONFIRMED as "you checked it
    yourself", and reading a capability out of a compiled binary satisfies that
    wording exactly. It was also false. A finding that claims CONFIRMED has to
    quote the invocation that produced it, not the subject it is about.
    """
    if not cfg.get("require_confirmed_is_exercised", True):
        return
    bad, seen = 0, 0
    for md in sorted(plan.rglob("*.md")):
        for i, line in lines_outside_fences(md):
            if not re.search(r"\bCONFIRMED\b", line):
                continue
            # A finding lives in a table row and carries CONFIRMED as its own
            # cell. Prose that DISCUSSES the label — a legend, a retrospective,
            # this paragraph — is not a finding, and flagging it would train
            # everyone to ignore the check.
            if not line.lstrip().startswith("|"):
                continue
            cells = [re.sub(r"[*~_`\s]", "", c) for c in line.strip().strip("|").split("|")]
            if not any(c.upper().startswith("CONFIRMED") for c in cells):
                continue
            if re.search(r"\bSUSPECTED\b", line):
                continue                      # a legend row, not a finding row
            seen += 1
            spans = RE_CODE_SPAN.findall(line)
            if any(RE_INVOCATION.search(s) for s in spans) or re.search(r"HTTP\s+\d{3}", line):
                continue
            bad += 1
            f.fail("confirmed-exercised", f"{md}:{i}",
                   "a CONFIRMED finding here quotes no invocation. Cite the command "
                   "or call that produced it — naming the subject is inspection, and "
                   "principle 7 says inspection is not evidence. If you only inferred "
                   "it, the honest label is SUSPECTED.")
    if seen and not bad:
        f.ok("confirmed-exercised", f"all {seen} CONFIRMED findings cite an invocation")
    elif not seen:
        f.ok("confirmed-exercised", "no CONFIRMED findings to check")


def is_human_owned(text: str) -> bool:
    """Is this task owned by a person rather than an agent?

    ONE definition, used by two checks that pull in opposite directions, which is
    the point. `check_frozen_human_contracts` ADDS an obligation to a human-owned
    task (its contract freezes on delivery, hash and all). `check_persona_model`
    REMOVES one (a person has no model and no effort). Declaring `human` is
    therefore a trade, not an exemption — which is what stops it being the cheap
    way around the floor.

    Two definitions of "human" would eventually disagree, and the failure would
    be a task that is exempt from the model floor and also exempt from the freeze
    — invisible, because each check would be behaving correctly on its own.
    """
    # A task that names an Agent or a Model is run by one, whatever the Owner
    # line says. `**Owner:** you` is the idiom in the shipped examples and it
    # means "you are driving this plan", not "a person executes this task" —
    # those examples also name a persona and a model. Without this clause the
    # owner wording alone exempted them and their models silently stopped being
    # checked: the gate printed PASS for the right check for the wrong reason,
    # which is worse than printing FAIL.
    own = owner_of(text)
    if not own:
        return False
    # `human` is an EXPLICIT declaration and outranks everything, including a
    # model line. An earlier version of this guard checked the persona/model
    # lines FIRST, which suppressed the explicit case too — a task owned by
    # `human` and carrying the template's Agent row stopped counting as human,
    # and check_frozen_human_contracts went quiet on exactly the tasks it exists
    # for. Its mutation probe caught it; nothing else did.
    if re.search(r"\bhuman\b", own, re.I):
        return True
    # `you` and `requester` are idiom, not declaration. The shipped examples say
    # `**Owner:** you` while naming a persona and a model, and there they mean
    # "you are driving this plan", not "a person executes this task".
    if RE_PERSONA.search(text) or RE_MODEL.search(text):
        return False
    return bool(re.search(r"\byou\b|\brequester\b", own, re.I))


def human_worked_plan(plan: Path) -> bool:
    """Does PLAN.md declare that the workers are people?

    The per-task test above only fires on the literal words human/you/requester.
    Real plans of people do not write that — they write "Writer A", "the DBA",
    "a reviewer who wrote neither T5 nor T6". Two of the five trial plans failed
    the model floor on exactly those owners, and no regex over job titles is ever
    going to close that. So the answer is declared once, where the question is
    actually asked, and the gate reads the declaration instead of guessing at the
    owner string.
    """
    p = plan / "PLAN.md"
    if not p.is_file():
        return False
    mw = RE_WORKERS.search(p.read_text(errors="replace"))
    return bool(mw and re.search(r"\bhumans?\b|\bpeople\b|\bpersons?\b",
                                 mw.group(1), re.I))


def check_frozen_human_contracts(f: Findings, tasks: dict, cfg: dict):
    """
    A human-owned task's contract freezes the moment it is handed out.

    Grillin's briefing model is 'every agent receives a directory, not a prompt'.
    A human does not read the directory. On the reskin run the capture method was
    rewritten two and a half hours AFTER the human had already satisfied the
    original, and the run then scored them against the rewrite. That is not a
    deviation by the human; it is a retroactively moved goalpost, and it is the
    one failure mode a hash can settle outright.
    """
    if not cfg.get("require_frozen_human_contracts", True):
        return
    bad, seen = 0, 0
    for tid, path in sorted(tasks.items()):
        text = path.read_text(errors="replace")
        if not is_human_owned(text):
            continue
        ms = RE_STATUS.search(text)
        status = ms.group(1).strip() if ms else "NOT STARTED"
        if status == "NOT STARTED":
            continue
        seen += 1
        md = RE_DELIVERED.search(text)
        if not md:
            bad += 1
            f.fail("frozen-contract", f"{path}:1",
                   f"{tid} is human-owned and {status.lower()}, but has no "
                   f"'**Delivered:**' line. Nothing records that the contract ever "
                   f"reached the person who has to satisfy it, or what it said when "
                   f"it did.")
            continue
        msha = RE_SHA.search(md.group(1))
        if not msha:
            bad += 1
            f.fail("frozen-contract", f"{path}:{line_of(path, md.group(0))}",
                   f"{tid}'s Delivered line carries no 'sha256:<hash>' of the "
                   f"contract as handed over — so the contract can still be edited "
                   f"underneath the person doing the work")
            continue
        recorded = msha.group(1).lower()
        actual = contract_hash(path)
        if not actual.startswith(recorded):
            bad += 1
            f.fail("frozen-contract", f"{path}:{line_of(path, md.group(0))}",
                   f"{tid}'s contract has changed since it was handed to its human "
                   f"owner (recorded {recorded[:12]}, now {actual[:12]}). Judging the "
                   f"delivery against the new wording is moving the goalpost. Either "
                   f"restore it, or record the amendment and re-deliver.")
    if seen and not bad:
        f.ok("frozen-contract", f"{seen} human-owned task(s) delivered against a frozen contract")
    elif not seen:
        f.ok("frozen-contract", "no human-owned task has been handed out yet")


def check_instrument_fixture(f: Findings, plan: Path, tasks: dict, cfg: dict):
    """
    Validate the ruler separately from the measurements it authorises.

    Grillin's whole model is 'check the claim against the thing'. It has nothing
    to say about the INSTRUMENT being wrong. On the reskin run a measuring script
    shattered a gradient into 24 near-identical near-blacks and reported no accent
    detectable — every individual number true, the conclusion worthless. What
    caught it was a fixture with a known answer, and nothing in the method asked
    for one.
    """
    if not cfg.get("require_instrument_fixture", True):
        return
    cmds = [c for c in (done_command(p) for p in tasks.values()) if c]
    if not cmds:
        return
    scripts = set()
    for c in cmds:
        for ref in RE_SCRIPT_REF.findall(c):
            if (plan / ref.lstrip("./")).is_file():
                scripts.add(ref.lstrip("./"))
    if not scripts:
        f.ok("instrument", "no plan-local instrument is load-bearing in any gate")
        return
    bad = 0
    for s in sorted(scripts):
        stem = Path(s).name
        proven = any(stem in c and re.search(r"fixture|golden|known", c, re.I)
                     for c in cmds)
        if not proven:
            bad += 1
            f.fail("instrument", f"{plan / s}",
                   f"{s} produces evidence a gate depends on, but no done-command "
                   f"runs it against a fixture with a known answer. An instrument "
                   f"nobody calibrated authorises every measurement downstream of it.")
    if not bad:
        f.ok("instrument", f"{len(scripts)} instrument(s), each proven against a known answer")


RE_REVERSIBLE = re.compile(r"\*\*Reversible:\*\*\s*([^·\n]*?)(?=\*\*|·|$)", re.M | re.I)
RE_ROLLBACK = re.compile(r"\*\*Rollback:\*\*\s*(.+?)$", re.M | re.I)
RE_PLACEHOLDER = re.compile(r"^\s*(TODO|TBD|N/?A|none|—|-|\?+|<[^>]*>)\s*$", re.I)
RE_OWNED_PATH = re.compile(r"`([^`\n]+)`")
RE_MODEL = re.compile(r"\*\*Model:\*\*\s*`?([^`·\n]+?)`?\s*(?=\*\*|·|$)", re.M | re.I)
RE_EFFORT = re.compile(r"\*\*Effort:\*\*\s*([a-z]+)", re.M | re.I)
RE_PERSONA = re.compile(r"\*\*(?:Agent|Persona):\*\*\s*`?([^`·\n]+?)`?\s*(?=\*\*|·|$)", re.M | re.I)
# Effort is never below `high`. The misses that cost most in this method's
# history were on work priced as routine — a recon pass that called 34 live
# re-export shims dead modules, and a CONFIRMED read out of a binary's strings.
# Neither was a knowledge failure; both were attention failures.
VALID_EFFORT = {"high", "xhigh", "max"}
TIER_WORDS = {"cheap", "mid", "top", "low", "medium", "default", "fast", "smart"}


def check_rollback_real(f: Findings, plan: Path, tasks: dict, cfg: dict):
    """
    An irreversible task must name a real way back.

    Lifted from project-base's plan_validate.sh, which has enforced it since
    June: "rollback is real, not a stub — no revert path = an un-undoable
    change." Grillin asks shaping question 5 (*is any step hard to undo?*) and
    then never checked that anything answered it. Asking a question whose
    answer nothing verifies is how a plan acquires a reassuring paragraph and
    no revert path.
    """
    if not cfg.get("require_rollback_real", True):
        return
    bad, seen = 0, 0
    for tid, path in sorted(tasks.items()):
        text = path.read_text(errors="replace")
        m = RE_REVERSIBLE.search(text)
        irreversible = bool(m and m.group(1).strip().lower().startswith(("no", "false")))
        rb = RE_ROLLBACK.search(text)
        if not irreversible and not rb:
            continue
        seen += 1
        if irreversible and not rb:
            bad += 1
            f.fail("rollback", f"{path}:1",
                   f"{tid} declares itself irreversible and names no **Rollback:**. "
                   f"An un-undoable change with no revert path is the one shape a "
                   f"plan cannot recover from.")
            continue
        val = rb.group(1).strip() if rb else ""
        if RE_PLACEHOLDER.match(val):
            bad += 1
            f.fail("rollback", f"{path}:{line_of(path, rb.group(0))}",
                   f"{tid}'s rollback is a placeholder ({val!r}). A stub revert path "
                   f"reads as covered and is not.")
        # "just undo it" is three words and passes any is-this-a-sentence test,
        # which is exactly why an earlier version of this check let it through.
        # The rule is the same one Done means uses: write it as inline code, or
        # it is not something another person can run.
        elif not RE_OWNED_PATH.search(val) and not re.search(r"[/$]|--", val):
            bad += 1
            f.fail("rollback", f"{path}:{line_of(path, rb.group(0))}",
                   f"{tid}'s rollback is prose, not something anyone can run. "
                   f"Same rule as Done means: if nobody else can execute it, it is "
                   f"a hope rather than a revert path.")

    # The plan says an irreversible step exists; no task owns one.
    src = plan / "PLAN.md"
    if src.is_file():
        for line in src.read_text(errors="replace").splitlines():
            if not re.search(r"hard to undo|irreversible", line, re.I):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and re.match(r"\**\s*yes", cells[2], re.I):
                if not any(RE_REVERSIBLE.search(p.read_text(errors="replace"))
                           for p in tasks.values()):
                    bad += 1
                    f.fail("rollback", f"{src}:{line_of(src, line[:40])}",
                           "the shaping answers say a step is hard to undo, but no task "
                           "declares '**Reversible:** no'. The risk was named at phase 0 "
                           "and then belongs to nobody.")
                break
    if seen and not bad:
        f.ok("rollback", f"{seen} task(s) with a revert path, each runnable")
    elif not seen and not bad:
        f.ok("rollback", "no task declares itself irreversible")


# A line that DISCLAIMS a path rather than claiming one. Naming what a worker
# must not touch is good practice — templates/BRIEF.md.template instructs authors
# to do exactly that — and until this existed, every such line was harvested as
# OWNERSHIP. "You do NOT own `frontend/`" put `frontend/` in the owned set, so
# the task collided with whoever legitimately owned it. A first-time user hit
# this on their own plan and reworded four tasks to escape a collision that was
# not real.
#
# Line-level, deliberately. A disclaimer split across two lines still leaks its
# paths, and that is the safe direction to be wrong in: over-claiming ownership
# produces a loud false collision, while under-claiming produces a silent missed
# one, and a missed collision is the failure this check exists to prevent.
RE_DISCLAIMS = re.compile(
    r"\b(?:do\s*n[o']?t|does\s*n[o']?t|never|must\s+not|may\s+not|cannot)\s+"
    r"(?:own|touch|modify|edit|write|change)\b"
    r"|\bnot\s+(?:yours|owned|your\s+\w+)\b"
    r"|\bis\s+not\s+yours\b", re.I)


# CITING A PATH IS NOT CLAIMING IT. RE_DISCLAIMS closed the negated case; this
# is the positive one, and a curator took a real FAIL on it: two tasks listed
# the same schema file under "## What you own" — one because it owns it, one
# because it is the thing that must not break — and the gate failed BOTH, then
# named the two innocent tasks as a collision. The advice that follows a false
# collision is "stop writing the neighbours down", which deletes the sentence
# that made the boundary reviewable in the first place. That is the same cost
# RE_DISCLAIMS was added to stop, arriving through the other door.
#
# A MARKER, NOT A GUESS. The author has to say it — `read-only`, `reference
# only`, `for reference`, `context only` — and saying it is one word. Naming
# somebody else as the owner ("T3 owns it") is deliberately NOT enough on its
# own, because "owned by this task" is a claim written the same shape, and
# under-claiming is the silent failure: a false collision is loud and gets
# argued with, a missed one ships and clobbers at merge time.
#
# Line-level, for the same reason and with the same trade as RE_DISCLAIMS: a
# citation split across two lines still leaks its paths, and over-claiming is
# the safe direction to be wrong in.
RE_CITES = re.compile(
    r"\bread[\s-]?only\b"
    r"|\b(?:reference|context)\s+only\b"
    r"|\bfor\s+(?:reference|context)\b", re.I)


def _owned_paths(text: str):
    """Specific paths from '## What you own'. Vague ones are ignored on purpose,
    and so are paths on a line that says the worker does NOT own them, or that
    marks them read-only — a task may need to name what it must not break."""
    body, in_section, in_fence = [], False, False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and re.match(r"^#+\s", line):
            if in_section:
                break
            in_section = bool(re.match(r"^#+\s*What you own\b", line, re.I))
            continue
        if in_section:
            if RE_DISCLAIMS.search(line) or RE_CITES.search(line):
                continue          # a disclaimer or a read-only citation, not a
                                  # claim — see RE_DISCLAIMS and RE_CITES
            body.append(line)
    out = set()
    for span in RE_OWNED_PATH.findall("\n".join(body)):
        s = span.strip().rstrip("/")
        # Only paths specific enough to collide: a directory or a file with a
        # suffix. A bare word is a description, and treating it as a path is
        # how this check would start crying wolf.
        if "/" in s or re.search(r"\.\w{1,5}$", s):
            out.add(s)
    return out


def check_paths_disjoint(f: Findings, tasks: dict, cfg: dict):
    """
    Two tasks that can run at the same time may not own the same path.

    Grillin has said this in prose since phase 7 — separate worktrees are the
    easy half, the contended-file list is the hard half — and never checked it.
    project-base has: "file overlap between slices -> two parallel Executors
    editing one file race + clobber". Same-file collision is the most-reported
    failure in every multi-agent post-mortem in the prior art.

    Concurrent means: neither task can reach the other through the dependency
    graph. Ordering is what makes shared ownership safe, so tasks in sequence
    are exempt.
    """
    if not cfg.get("require_paths_disjoint", True):
        return
    blocked_by, owns = {}, {}
    for tid, path in tasks.items():
        text = path.read_text(errors="replace")
        mb = RE_BLOCKED_BY.search(text)
        blocked_by[tid] = {d for d in (RE_TASK_ID.findall(mb.group(1)) if mb else []) if d in tasks}
        owns[tid] = _owned_paths(text)

    def reaches(a, b, seen=None):
        seen = seen or set()
        if a in seen:
            return False
        seen.add(a)
        return b in blocked_by[a] or any(reaches(d, b, seen) for d in blocked_by[a])

    ids = sorted(tasks)
    bad = 0
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if reaches(a, b) or reaches(b, a):
                continue                      # ordered — sharing is safe
            shared = owns[a] & owns[b]
            for p in sorted(shared):
                bad += 1
                f.fail("paths-disjoint", f"{tasks[a]}:1",
                       f"{a} and {b} can run at the same time and both own {p!r}. "
                       f"Two workers editing one path is one conflict, relocated to "
                       f"merge time where it is most expensive. Give it one owner and "
                       f"let the other emit a fragment. If one of them only READS it, "
                       f"say so on that line — 'read-only' — and it stops counting as "
                       f"a claim; naming the path is worth keeping.")
    if not bad:
        f.ok("paths-disjoint", "no two concurrent tasks own the same path")


def check_persona_model(f: Findings, plan: Path, tasks: dict, cfg: dict):
    """
    Every task names a real model, an effort at or above `high`, and a persona
    the roster knows.

    A persona is a description of what someone is responsible for. It is not a
    capability, and writing one does not confer one — the model and the effort
    are what the persona is actually made of. Leaving them as tier words means
    the pairing was never decided, only gestured at, and an orchestrator cannot
    dispatch `mid`.

    SIZE-BLIND, AND THAT IS THE RULING — NOT AN OVERSIGHT. Two rounds of
    first-time users reported this check as contradicting SCALING.json, which
    gives size S `phase5Form: "reduced — folder, owner, status, done-command; no
    persona, skills or fragments"` while the check demands a Model and an Effort
    at every size. examples/a-real-first-plan/tasks/T1 is a user writing exactly
    that down — "Reduced contract: size S, phase 5 run in reduced form. No
    persona, no skills" — and taking two findings for it.

    It reads like a contradiction and it is not one. The reduced form drops a
    PERSONA. A model and an effort are not a persona; they are what a persona
    would have been made of, and they survive it. Three things say so:

      · SCALING.json `taskContract.required` lists "model" and "effort" with no
        size qualifier anywhere in the file. The band rows carry a phase5Form,
        never a task contract.
      · that reduced string is a restatement of `taskContract.layout.
        minimumAtEverySize` — the same four items, in the same order. It is the
        FLOOR of what a task folder must carry, not the ceiling of what it may.
      · this check already implements the reduced form as written: it never
        REQUIRES a persona. `mp` is validated only `if mp and roster`. What the
        document switches off is the one field the gate does not ask for.

    So the defect is in the sentence, not here, and the repair belongs in
    SCALING.json: say plainly that the reduced form still names a model and an
    effort. Making this check size-aware via band_rule was the other candidate
    and it was rejected on purpose — XS and S are 1-10 tasks, which is most
    plans, and a plan that may skip declaring its model is a plan whose price
    nobody can read. `high` stays the floor at every size. band_rule's own
    docstring cites this check as the reason it exists; it stays the right tool
    for a rule SCALING.json actually declares per band, and this is not one.
    """
    if not cfg.get("require_persona_model", True):
        return

    roster, roster_path = set(), None
    for cand in (plan / "tasks" / "_ROSTER.md", plan / "_ROSTER.md"):
        if cand.is_file():
            roster_path = cand
            for line in cand.read_text(errors="replace").splitlines():
                if line.lstrip().startswith("|"):
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    if cells:
                        roster |= set(RE_CODE_SPAN.findall(cells[0]))
            break

    if human_worked_plan(plan):
        f.ok("persona-model",
             "PLAN.md declares human workers, so no task names a model or an effort — "
             "a person has neither. Their contracts freeze on delivery instead.")
        return

    bad, humans = 0, 0
    for tid, path in sorted(tasks.items()):
        text = path.read_text(errors="replace")

        # A person has no model and no effort, and QUICKSTART §0b question 3 says
        # so outright: when the workers are not agents, "ignore templates/
        # entirely — everything else still works". Everything else did not still
        # work. This floor failed a legitimate human-owned plan twice per task
        # and `--config` could not rescue it, because self_check refuses to let a
        # floor be lowered. Three first-time users hit it independently; two of
        # them stopped running the gate at all, which is the expensive outcome —
        # a gate that is wrong about a case people actually have gets discarded
        # whole, taking the twenty checks that were right with it.
        #
        # The exemption is not free: see is_human_owned. A task that claims it
        # picks up the frozen-contract obligation in exchange.
        if is_human_owned(text):
            humans += 1
            continue

        mm = RE_MODEL.search(text)
        if not mm:
            bad += 1
            f.fail("persona-model", f"{path}:1",
                   f"{tid} names no **Model:** — the requester cannot see a subagent's "
                   f"tier and must not have to ask for it")
        else:
            model = mm.group(1).strip()
            if model.lower() in TIER_WORDS:
                bad += 1
                f.fail("persona-model", f"{path}:{line_of(path, mm.group(0))}",
                       f"{tid}'s model is the tier word {model!r}, not an identifier. "
                       f"An orchestrator cannot dispatch a tier — name the model, e.g. "
                       f"`claude-opus-5`.")
            elif "<" in model or ">" in model:
                bad += 1
                f.fail("persona-model", f"{path}:{line_of(path, mm.group(0))}",
                       f"{tid}'s model is still the template placeholder")

        me = RE_EFFORT.search(text)
        if not me:
            bad += 1
            f.fail("persona-model", f"{path}:1", f"{tid} names no **Effort:**")
        else:
            eff = me.group(1).strip().lower()
            if eff not in VALID_EFFORT:
                bad += 1
                f.fail("persona-model", f"{path}:{line_of(path, me.group(0))}",
                       f"{tid}'s effort is {eff!r}; allowed: {sorted(VALID_EFFORT)}. "
                       f"The saving looks free on routine work and that is exactly where "
                       f"it has cost most — see _ROSTER.md §0.")

        mp = RE_PERSONA.search(text)
        if mp and roster:
            persona = mp.group(1).strip()
            if "<" not in persona and persona not in roster:
                bad += 1
                f.fail("persona-model", f"{path}:{line_of(path, mp.group(0))}",
                       f"{tid} names persona {persona!r}, which is not in "
                       f"{roster_path.name}. A persona invented in a task file is one "
                       f"nobody priced — add it to the roster with its reason first.")

    # ── the same persona is the same pairing, everywhere ────────────────────
    # A persona is a role, and a role has one price. Two tasks naming `recon`
    # at different models are not one role — they are two roles sharing a name,
    # and the roster stops describing the fleet the moment that is true. This is
    # also how a tier silently drifts downward: one task gets lowered "just for
    # this one", nothing rejects it, and the next author copies that task.
    seen: dict = {}
    for tid, path in sorted(tasks.items()):
        text = path.read_text(errors="replace")
        mp, mm, me = (RE_PERSONA.search(text), RE_MODEL.search(text),
                      RE_EFFORT.search(text))
        if not (mp and mm and me):
            continue
        persona = mp.group(1).strip()
        if "<" in persona:
            continue
        pairing = (mm.group(1).strip(), me.group(1).strip().lower())
        if persona in seen and seen[persona][0] != pairing:
            other, otherp = seen[persona][1], seen[persona][0]
            bad += 1
            f.fail("persona-model", f"{path}:1",
                   f"persona {persona!r} runs as {pairing[0]}/{pairing[1]} in {tid} but "
                   f"{otherp[0]}/{otherp[1]} in {other}. One persona is one pairing — "
                   f"two prices for one role means the roster no longer describes the "
                   f"fleet, and it is how a tier drifts down one task at a time.")
        seen.setdefault(persona, (pairing, tid))

    # And what the roster says is what the tasks must do.
    if roster_path:
        declared = {}
        for line in roster_path.read_text(errors="replace").splitlines():
            if not line.lstrip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 4:
                continue
            names = RE_CODE_SPAN.findall(cells[0])
            models = [c for c in RE_CODE_SPAN.findall(cells[-3] if len(cells) > 4 else cells[2])
                      if c.startswith("claude-")]
            efforts = [c.lower() for c in
                       RE_CODE_SPAN.findall(cells[-2]) + [cells[-2].strip()]
                       if c.lower() in VALID_EFFORT]
            if names and models and efforts:
                for n in names:
                    declared[n] = (models[0], efforts[0])
        for persona, (pairing, tid) in sorted(seen.items()):
            want = declared.get(persona)
            if want and want != pairing:
                bad += 1
                f.fail("persona-model", f"{tasks[tid]}:1",
                       f"{tid} runs {persona!r} as {pairing[0]}/{pairing[1]}; the roster "
                       f"says {want[0]}/{want[1]}. The roster wins — it is where the "
                       f"reason for the pairing is written.")

    if not bad:
        f.ok("persona-model",
             (f"every agent-owned task names a real model and an effort at or above high"
              if humans else
              f"every task names a real model and an effort at or above high")
             + (f"; {len(seen)} persona(s) consistent with the roster" if seen else "")
             + (f"; {humans} human-owned task(s) exempt, and frozen on delivery instead"
                if humans else ""))


RE_SIZE = re.compile(r"^\*\*Size:\*\*\s*([A-Za-z]{1,2})\b", re.M)
# Published in three places now — here, SCALING.json's scaling[].tasks, and
# Smokin's Plan.size(). check-drift.py compares the first two, because a number
# published three times is a number that eventually disagrees with itself.
BANDS = [("XS", 1, 3), ("S", 4, 10), ("M", 11, 25), ("L", 26, 60), ("XL", 61, 999999)]

RE_BRAINSTORMED = re.compile(r"^\*\*Brainstormed:\*\*\s*(.+)$", re.M | re.I)
# The three paths the brainstorming skill classifies a request into. Two of them
# do not produce a plan document at all, which is exactly why the value matters
# rather than merely being present.
BRAINSTORM_PATHS = ("spike", "bounded", "architectural")


def band_of(n: int) -> str:
    for name, lo, hi in BANDS:
        if lo <= n <= hi:
            return name
    return BANDS[-1][0]


def band_rule(key: str, size: str, default=None):
    """Read a per-band rule from SCALING.json rather than hardcoding the bands.

    THE REASON THIS EXISTS. `check_persona_model` is size-BLIND while
    SCALING.json declares per-band behaviour, and the contradiction has been
    found independently by two rounds of first-time users: the document says one
    thing at XS and the gate demands another. Any new check that scales must
    read the same file the documents are generated from, or it becomes the third
    place a band is written down and the second place it is wrong.
    """
    try:
        spec = json.loads((Path(__file__).resolve().parent.parent
                           / "SCALING.json").read_text())
    except (OSError, ValueError):
        return default          # a missing spec must not invent strictness
    for b in spec.get("scaling", []):
        if b.get("size") == size:
            return b.get(key, default)
    return default


def check_size_declared(f: Findings, plan: Path, tasks: dict, cfg: dict):
    """A size band nobody enforces is advice.

    Found in a watched trial: the user told his agent "this is a small job,
    1-3 tasks, use the short path" and got five tasks with rollback commands and
    a baseline-snapshot task. The bands live in prose a reader sees and the
    plan-WRITING agent is never obliged to obey. So the plan declares its band,
    and the count has to match it.

    This is itself a declaration check — an agent can write `**Size:** M` and
    produce twenty tasks legitimately. It closes the drift observed (a stated
    band silently exceeded), not the deeper problem of a plan being the wrong
    size to begin with.
    """
    p = plan / "PLAN.md"
    if not p.is_file():
        return          # check_plan_source_of_truth owns that failure; two
                        # checks reporting one defect is noise
    m = RE_SIZE.search(p.read_text(errors="replace"))
    n = len(tasks)
    if not m:
        f.fail("size-declared", f"{p}:1",
               "PLAN.md declares no **Size:**. A plan that never says how big it is cannot "
               "be held to it, and the bands stay advice until it does. Add one of "
               f"{[b[0] for b in BANDS]}.")
        return
    want = m.group(1).upper()
    band = next((b for b in BANDS if b[0] == want), None)
    if band is None:
        f.fail("size-declared", f"{p}:{line_of(p, m.group(0))}",
               f"Size {want!r} is not one of {[b[0] for b in BANDS]}")
        return
    _, lo, hi = band
    if not (lo <= n <= hi):
        shown = f"{lo}-{hi}" if hi < 999999 else f"{lo}+"
        f.fail("size-declared", f"{p}:{line_of(p, m.group(0))}",
               f"PLAN.md declares Size: {want} ({shown} tasks); this plan has {n}. Either it "
               f"grew past what you scoped — say so and re-scope — or the declaration is "
               f"stale. A band nobody enforces is advice, and this is the drift that turned "
               f"a stated \"1-3 tasks, short path\" into 5 with rollback plans.")
        return
    f.ok("size-declared", f"declared {want} and holds {n} task(s), inside the band")


RE_CMP = re.compile(r"\b(diff|cmp|sha\d*sum|md5sum|git\s+diff|comm)\b")
RE_PATHISH = re.compile(r"[\w./~-]*/[\w./-]+")


def check_done_self_reference(f: Findings, plan: Path, tasks: dict, cfg: dict):
    """
    A task must not be graded against a fixture it produced itself.

    Found by a first-time user, on her own plan, an hour after reading about the
    method. Her refactor task's done-command was:

        python3 summarize.py sample.log | diff -u tasks/T2/baseline.txt -

    which is a good instinct — freeze the behaviour, then prove the refactor did
    not change it. But the baseline lives inside the task's OWN folder and the
    task is what produces it. So the check asserts equivalence to a snapshot the
    task took of itself, and it passes whether or not the refactor ever happened.
    Revert the work, re-run the gate, still green.

    `check_gates_fail_first` cannot catch this. It skips DONE tasks, and while the
    task is unstarted the baseline does not exist yet, so the command fails for
    the wrong reason and looks correct. The hole only opens once the work is done
    — which is precisely when principle 14 says a fresh session must be able to
    reconstruct the truth from the repository.

    This is principle 8 one level down: never certify your own work, where "your
    own work" includes the ruler you measured it with.
    """
    if not cfg.get("require_done_command", True):
        return
    bad = 0
    for tid, path in sorted(tasks.items()):
        cmd = done_command(path)
        if not cmd or not RE_CMP.search(cmd):
            continue
        own = f"tasks/{tid}/"
        hits = [p for p in RE_PATHISH.findall(cmd) if own in p.replace("./", "")]
        if not hits:
            continue
        bad += 1
        f.fail("done-self-reference", f"{path}:1",
               f"{tid}'s done-command compares against {hits[0]!r}, a fixture inside "
               f"{tid}'s own folder — so {tid} is graded against a snapshot it took of "
               f"itself, and passes whether or not the work happened. Revert the change "
               f"and it is still green. Add a clause that is FALSE before the work (assert "
               f"the new function, file or flag exists), or move the fixture out of this "
               f"task's ownership and say who produced it.")
    if not bad:
        f.ok("done-self-reference",
             "no task is graded against a fixture it produces itself")


def check_brainstormed(f: Findings, plan: Path, tasks: dict, cfg: dict):
    """Was the shape argued out with a person before the files were written?

    THE FAILURE THIS IS FOR. A curator with a capable agent goes from a one-line
    ask straight to a directory of task files. The plan is then structurally
    perfect and about the wrong problem — and every check in this gate passes,
    because structure is all they can see. The five questions in QUICKSTART 0b
    were the first answer to that and they are necessary; they are not
    sufficient, because a curator can answer all five inside their own head in
    the same two minutes they decided what to build.

    So on a plan big enough to be worth arguing about, the plan must record that
    the argument happened: which path the work was classified as, and that the
    design was approved BEFORE the files existed. Claude Code ships the
    mechanism as its `brainstorming` skill; this check does not care which
    mechanism was used, only that the plan says a shape was agreed and by when.

    SIZE-AWARE, AND THE BAND COMES FROM SCALING.json. At XS this is advisory:
    a one-to-three task plan is the case QUICKSTART already tells people not to
    ceremonialise. Reading the requirement from the spec rather than hardcoding
    it is deliberate — see `band_rule`.

    THE PATH VALUE IS CHECKED, not just its presence. Two of the three paths
    (`spike`, `bounded`) are defined as producing NO plan document. A four-task
    plan declaring itself bounded is a plan whose own header says it should not
    exist, and that contradiction is worth more than the field being non-empty.
    """
    p = plan / "PLAN.md"
    if not p.is_file():
        return          # check_plan_source_of_truth owns that failure
    size = band_of(len(tasks))
    rule = (band_rule("brainstormed", size) or "advisory").lower()
    m = RE_BRAINSTORMED.search(p.read_text(errors="replace"))
    if rule != "required":
        f.ok("brainstormed",
             f"{size} — the shape is advisory at this size; "
             f"{'declared anyway' if m else 'not declared'}")
        return
    if not m:
        f.fail("brainstormed", f"{p}:1",
               f"This plan holds {len(tasks)} tasks ({size}), and SCALING.json requires a "
               f"plan this size to record that its shape was agreed with a person before "
               f"the files were written. Nothing in this gate can tell a plan that is "
               f"structurally perfect from one that is about the wrong problem. Add a line "
               f"to PLAN.md: `**Brainstormed:** architectural · approved <date>`. Using "
               f"Claude Code, that is the `brainstorming` skill, run BEFORE step 1 — and it "
               f"hands over to this method instead of its own writing-plans skill.")
        return
    val = m.group(1).strip()
    path = next((w for w in BRAINSTORM_PATHS if re.search(rf"\b{w}\b", val, re.I)), None)
    if path is None:
        f.fail("brainstormed", f"{p}:1",
               f"**Brainstormed:** says {val!r}, which names none of {list(BRAINSTORM_PATHS)}. "
               f"The path taken is the half that carries information — it is what says how "
               f"much argument the shape got.")
        return
    if path != "architectural":
        f.fail("brainstormed", f"{p}:1",
               f"**Brainstormed:** declares the {path!r} path, but a {path} classification "
               f"is defined as producing NO plan document — and this is a plan of "
               f"{len(tasks)} tasks. Either the classification was wrong and this is "
               f"architectural work, or the plan should not exist. Re-classify rather than "
               f"editing the label: the ratchet is one-way, hidden complexity upgrades the "
               f"path and nothing downgrades it.")
        return
    if not re.search(r"\bapproved\b|\bagreed\b|\bsigned[- ]off\b", val, re.I):
        f.fail("brainstormed", f"{p}:1",
               f"**Brainstormed:** says {val!r} but never says the design was APPROVED. "
               f"Presenting a design and starting in the same breath is the whole failure "
               f"this records; the gate is the approval, not the design's length.")
        return
    f.ok("brainstormed", f"{size} — shape agreed on the {path} path, and approved")


def check_research_task(f: Findings, plan: Path, tasks: dict, cfg: dict):
    """
    A task that goes and finds something out is graded on its findings, never on
    the finding.

    WHERE THIS CAME FROM. Five first-time users were each handed a different job
    and asked to plan it with Grillin. Every one of them hit the same wall — the
    facts the plan needed did not exist yet — and every one of them invented the
    same answer independently: make the first task go and get them. All five then
    said some version of *"the method never says this is fine, it just doesn't
    say it isn't."* The method had no research step, and five out of five people
    built one anyway.

    WHY IT IS A TASK AND NOT A PHASE. The phases produce prose that nothing
    reads. A task has an owner, a folder and a done-command, which is the entire
    surface this gate can see. And research is the one activity whose natural
    done-command — "I understand it now" — is exactly the unfalsifiable claim the
    rest of the method exists to refuse.

    So the contract is borrowed from the practice that solved this long ago: a
    spike is timeboxed, answers ONE question, and its deliverable is a written
    finding, not working code. A spike without a timebox is research with no exit
    condition. Two things are checkable and both are checked:

      1 · it declares a **Timebox:**
      2 · its done-command tests for its own findings artefact

    NOT checkable, and stated rather than pretended: whether the findings are any
    good, and whether "what I could not establish" was answered honestly. Those
    are the reader's, and on a plan below the four-task floor there is no reader
    but you.

    ON THE INTERACTION WITH check_done_self_reference: that check forbids grading
    a task against a fixture in its own folder, and this one requires exactly
    that. They do not collide, and the reason is worth writing down — the other
    check only fires on a COMPARISON (`diff`, `cmp`), because comparing yourself
    to your own snapshot passes whether or not the work happened. Testing that
    you produced a non-empty artefact is false before the work and true after,
    which is the property a done-command needs.
    """
    if not cfg.get("require_research_contract", True):
        return
    n, bad = 0, 0
    for tid, path in sorted(tasks.items()):
        text = path.read_text(errors="replace")
        mk = RE_KIND.search(text)
        if not mk or not re.search(r"\bresearch\b|\brecon\b|\bspike\b", mk.group(1), re.I):
            continue
        n += 1

        if not RE_TIMEBOX.search(text):
            bad += 1
            f.fail("research-task", f"{path}:1",
                   f"{tid} is a research task and declares no **Timebox:**. Research with no "
                   f"exit condition does not end — it gets abandoned, which is the same thing "
                   f"arriving later and less honestly. Name the budget, and say in Steps that "
                   f"reaching it without an answer is a REPORTABLE RESULT, not a failure.")

        cmd = done_command(path) or ""
        own = f"tasks/{tid}/"
        if not cmd:
            continue                          # check_done_is_command owns that failure
        if not any(own in p.replace("./", "") for p in RE_PATHISH.findall(cmd)):
            bad += 1
            f.fail("research-task", f"{path}:1",
                   f"{tid}'s done-command does not test for anything in {own} — so it is "
                   f"graded on the thing it was sent to find out, which nobody can check, "
                   f"rather than on the findings it was sent to write. Point it at the "
                   f"artefact: `test -s {own}FINDINGS.md`. That is false before the work and "
                   f"true after, and it stays true when the answer is 'could not establish'.")

    # Only when nothing failed. An earlier version emitted the PASS line beside its
    # own FAIL lines for the same check, which reads as "fixed" at a glance.
    if n and not bad:
        f.ok("research-task",
             f"{n} research task(s), each timeboxed and graded on the findings it writes")


def check_rulings(f: Findings, plan: Path, tasks: dict, cfg: dict):
    """
    If the plan opts into Smokin's delegation node, its `_RULINGS.toml` declares
    who may be asked to judge, and what they may answer.

    SCOPE, and the boundary matters. Smokin's own loader is authoritative for
    evaluation semantics — the `when` grammar, the evidence resolver, what
    happens at run time. This checks only what a PLAN validator can settle
    without running anything: that the judges are people the roster priced, that
    no judge is being asked to certify its own work, and that the two settings
    which can silently disable the whole layer are not set that way. The
    duplication is deliberate and bounded; a plan should not have to be executed
    before somebody can tell it is not operable.
    """
    cfgf = plan / "_RULINGS.toml"
    if not cfgf.is_file():
        return                                    # opt-in by file; absence is not a defect
    try:
        import tomllib
    except ModuleNotFoundError:
        f.fail("rulings", f"{cfgf}:1",
               "this plan declares _RULINGS.toml but python is older than 3.11, so nothing "
               "here can read it. A config nobody can parse is a config nobody is applying.")
        return
    try:
        raw = tomllib.loads(cfgf.read_text(errors="replace"))
    except (OSError, tomllib.TOMLDecodeError) as e:
        f.fail("rulings", f"{cfgf}:1",
               f"_RULINGS.toml does not parse ({e}). Smokin refuses to make ANY ruling in a "
               f"plan whose config is broken, so this silently turns the judgement layer off.")
        return

    roster = {}
    for cand in (plan / "tasks" / "_ROSTER.md", plan / "_ROSTER.md"):
        if cand.is_file():
            for line in cand.read_text(errors="replace").splitlines():
                if line.lstrip().startswith("|"):
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    for n in RE_CODE_SPAN.findall(cells[0] if cells else ""):
                        roster[n] = cand.name
            break

    # Which persona OWNS each task — a judge must not be asked to rule on work
    # its own persona did. Principle 8, one level up from the adversary check.
    owners = {}
    for tid, path in tasks.items():
        mp = RE_PERSONA.search(path.read_text(errors="replace"))
        if mp and "<" not in mp.group(1):
            owners.setdefault(mp.group(1).strip(), []).append(tid)

    bad, declared = 0, raw.get("ruling")
    if not isinstance(declared, list) or not declared:
        f.fail("rulings", f"{cfgf}:1",
               "_RULINGS.toml exists and declares no [[ruling]]. Smokin treats that as a "
               "load error and halts. Either declare a class or delete the file.")
        return

    pol = str((raw.get("policy") or {}).get("uncovered", "halt")).lower()
    if pol not in ("halt", "accept"):
        bad += 1
        f.fail("rulings", f"{cfgf}:1",
               f"policy.uncovered is {pol!r}; it must be 'halt' or 'accept'.")

    for i, r in enumerate(declared):
        if not isinstance(r, dict):
            bad += 1
            f.fail("rulings", f"{cfgf}:1", f"ruling[{i}] is not a table")
            continue
        cls = (r.get("class") or f"[{i}]").strip()
        persona = (r.get("persona") or "").strip()
        if not persona:
            bad += 1
            f.fail("rulings", f"{cfgf}:1", f"ruling {cls!r} names no persona")
        elif roster and persona not in roster:
            bad += 1
            f.fail("rulings", f"{cfgf}:1",
                   f"ruling {cls!r} names judge persona {persona!r}, which is not in "
                   f"{next(iter(roster.values()))}. Its model and effort come from the "
                   f"roster, so an unrostered judge is a judge running at nothing.")
        elif persona in owners:
            bad += 1
            f.fail("rulings", f"{cfgf}:1",
                   f"ruling {cls!r} asks {persona!r} to judge, and {persona!r} owns "
                   f"{', '.join(sorted(owners[persona]))}. Never certify your own work — "
                   f"give the ruling to a persona that wrote none of it.")

        default = str(r.get("default", "halt")).lower()
        if default != "halt":
            bad += 1
            f.fail("rulings", f"{cfgf}:1",
                   f"ruling {cls!r} sets default = {default!r}. It must be 'halt'. A judge "
                   f"that cannot be reached, resolving to anything else, certifies work "
                   f"nobody read — and it does it silently.")

        outs = r.get("outcomes")
        if not isinstance(outs, list) or not outs:
            bad += 1
            f.fail("rulings", f"{cfgf}:1", f"ruling {cls!r} declares no outcomes")
        elif "insufficient-evidence" not in [str(o).strip() for o in outs]:
            bad += 1
            f.fail("rulings", f"{cfgf}:1",
                   f"ruling {cls!r} gives the judge no way to say 'I cannot tell'. Add "
                   f"'insufficient-evidence' — a judge without it will answer something else.")

        ev = r.get("evidence")
        if not isinstance(ev, list) or not ev:
            bad += 1
            f.fail("rulings", f"{cfgf}:1",
                   f"ruling {cls!r} declares no evidence. A judge handed nothing rules on nothing.")

    if not bad:
        f.ok("rulings", f"{len(declared)} judgement class(es) declared; every judge is "
                        f"rostered, wrote none of the work, and halts when unreachable")


# Smokin's loader is the AUTHORITY on this file. These are copies of its limits,
# and copies drift — the standard failure is two validators with similar names
# where the authoring one permits what the runtime one refuses, discovered in
# production. `tests/test-config-contract.sh` is the assertion that they have not
# drifted: it feeds the same fixtures to both and requires both to refuse. Change
# a number here and that test fails until Smokin agrees.
INVARIANT_KEYS = {"name", "run", "equals", "matches", "because", "budget_s"}
MAX_INVARIANTS = 32
AGENT_BINARIES = {"claude", "codex", "codewhale", "opencode", "aider", "herdr",
                  "gemini", "smokin", "smokin-run", "smokin-emit"}


def check_invariants(f: Findings, plan: Path, tasks: dict, cfg: dict):
    """
    If the plan opts into Smokin's plan-level invariants, its `_INVARIANTS.toml`
    declares the readings that must not move while the plan runs.

    SCOPE, and the boundary matters — the same boundary check_rulings draws.
    Smokin's loader owns evaluation semantics: when a reading is taken, how a
    baseline is compared, what halts. This checks only what a PLAN validator can
    settle without running anything, and it is deliberately limited to the
    defects that make the layer LOAD-FAIL — because Smokin refuses to tick a plan
    whose invariant file is broken, and finding that out at tick 1 means the
    author already handed the plan over.

    One check here is NOT a copy of Smokin's, and it is the reason this function
    earns its place: an invariant whose command is a task's own done-command.
    That reads as diligence and is the exact conceptual error the feature exists
    to prevent. A done-command answers "did this task achieve its thing"; an
    invariant answers "what did this task break on the way". A done-command
    promoted to an invariant is FALSE at baseline (the work has not happened
    yet), so it either refuses the capture or bakes the unfinished state in as
    normal — and the blast radius stays unmeasured, behind a file that looks like
    it is measuring it. Smokin cannot see this: at run time it has no view of
    which readings were copied out of which contract.
    """
    cfgf = plan / "_INVARIANTS.toml"
    if not cfgf.is_file():
        return                                    # opt-in by file; absence is not a defect
    try:
        import tomllib
    except ModuleNotFoundError:
        f.fail("invariants", f"{cfgf}:1",
               "this plan declares _INVARIANTS.toml but python is older than 3.11, so nothing "
               "here can read it. Smokin will refuse to tick rather than run unguarded.")
        return
    try:
        raw = tomllib.loads(cfgf.read_text(errors="replace"))
    except (OSError, tomllib.TOMLDecodeError) as e:
        f.fail("invariants", f"{cfgf}:1",
               f"_INVARIANTS.toml does not parse ({e}). Smokin halts the plan rather than "
               f"running half an invariant set, so this stops the plan at tick 1.")
        return

    declared = raw.get("invariant")
    if not isinstance(declared, list) or not declared:
        f.fail("invariants", f"{cfgf}:1",
               "_INVARIANTS.toml exists and declares no [[invariant]]. Smokin treats that as a "
               "load error and halts. Either declare a reading or delete the file.")
        return
    if len(declared) > MAX_INVARIANTS:
        f.fail("invariants", f"{cfgf}:1",
               f"{len(declared)} invariants declared, ceiling is {MAX_INVARIANTS} — every one "
               f"of them re-runs at every tick boundary.")
        return

    # The done-commands, normalised, so an invariant that is really a completion
    # check can be named against the task it was copied from.
    done = {}
    for tid, path in tasks.items():
        c = (done_command(path) or "").strip()
        if c:
            done[" ".join(c.split())] = tid

    bad, seen = 0, set()
    for i, d in enumerate(declared):
        tag = f"invariant[{i}]"
        if not isinstance(d, dict):
            bad += 1
            f.fail("invariants", f"{cfgf}:1", f"{tag} is not a table")
            continue
        name = str(d.get("name") or "").strip()
        if not name:
            bad += 1
            f.fail("invariants", f"{cfgf}:1",
                   f"{tag} has no name. The name is a key in the baseline and a heading in the "
                   f"halt message; without it nobody can tell which reading moved.")
            continue
        tag = f"invariant {name!r}"
        if name in seen:
            bad += 1
            f.fail("invariants", f"{cfgf}:1",
                   f"{tag} is declared twice — an invariant is one reading or it is none.")
            continue
        seen.add(name)

        unknown = sorted(set(d) - INVARIANT_KEYS)
        if unknown:
            bad += 1
            f.fail("invariants", f"{cfgf}:1",
                   f"{tag} has unknown key(s): {', '.join(unknown)}. Known: "
                   f"{', '.join(sorted(INVARIANT_KEYS))}. Smokin refuses the whole file.")
            continue

        cmd = str(d.get("run") or "").strip()
        if not cmd:
            bad += 1
            f.fail("invariants", f"{cfgf}:1",
                   f"{tag} has no run — an invariant with no command measures nothing.")
            continue
        try:
            tokens = shlex.split(cmd)
        except ValueError as e:
            bad += 1
            f.fail("invariants", f"{cfgf}:1", f"{tag}: run is not a parseable command ({e}).")
            continue
        banned = sorted({Path(t).name for t in tokens} & AGENT_BINARIES)
        if banned:
            bad += 1
            f.fail("invariants", f"{cfgf}:1",
                   f"{tag}: run invokes {', '.join(banned)}. It re-runs at every tick boundary, "
                   f"so it would measure whether the tool is installed, forever.")
            continue

        if not str(d.get("because") or "").strip():
            bad += 1
            f.fail("invariants", f"{cfgf}:1",
                   f"{tag} has no because. The person who reads the halt is not the person who "
                   f"wrote the command, and a halt they cannot act on is an outage.")
            continue

        if "equals" in d and "matches" in d:
            bad += 1
            f.fail("invariants", f"{cfgf}:1",
                   f"{tag} declares both equals and matches — one reading, one test.")
            continue

        try:
            budget = int(d.get("budget_s", 30))
        except (TypeError, ValueError):
            bad += 1
            f.fail("invariants", f"{cfgf}:1", f"{tag}: budget_s is not a number.")
            continue
        if budget <= 0:
            bad += 1
            f.fail("invariants", f"{cfgf}:1", f"{tag}: budget_s must be positive, not {budget}.")
            continue

        # ── the check Smokin cannot make ───────────────────────────────────
        owner = done.get(" ".join(cmd.split()))
        if owner:
            bad += 1
            f.fail("invariants", f"{cfgf}:1",
                   f"{tag} runs {owner}'s own done-command. That is a completion check, not an "
                   f"invariant: it is FALSE at baseline because {owner} has not run yet, so it "
                   f"either refuses the capture or records the unfinished state as normal. An "
                   f"invariant is a reading about something this plan is NOT supposed to "
                   f"change — the neighbours, the other endpoint, the row count.")

    if not bad:
        f.ok("invariants", f"{len(declared)} plan-level invariant(s) declared; each names a "
                           f"reading, a reason, and a command that is not a task's own gate")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version",
                    version=f"grillin {__version__} ({INSTALLED_FROM})\n"
                            f"gate: {len(GATE_CHECK_NAMES)} checks")
    ap.add_argument("plan", help="the plan directory")
    ap.add_argument("--run-gates", action="store_true",
                    help="EXECUTE each task's done-command to prove it fails on "
                         "unstarted work. Runs commands the plan author wrote — "
                         "opt-in on purpose.")
    ap.add_argument("--config", default=None, help="JSON file; may only tighten the floors")
    ap.add_argument("--contract-hash", metavar="TASK.md", default=None,
                    help="print the contract hash for one TASK.md and exit. This is what goes "
                         "in its **Delivered:** line when a human-owned task is handed over.")
    args = ap.parse_args()

    if args.contract_hash:
        p = Path(args.contract_hash)
        if not p.is_file():
            print(f"validate-plan: {p} is not a file", file=sys.stderr)
            return 2
        print(f"sha256:{contract_hash(p)[:12]}")
        return 0

    plan = Path(args.plan).resolve()
    if not plan.is_dir():
        print(f"validate-plan: {plan} is not a directory", file=sys.stderr)
        return 2

    cfg = dict(FLOORS)
    if args.config:
        try:
            cfg.update(json.loads(Path(args.config).read_text()))
        except (OSError, ValueError) as e:
            print(f"validate-plan: unreadable config: {e}", file=sys.stderr)
            return 2

    f = Findings()
    self_check(f, cfg)
    tasks = find_tasks(plan)
    check_layout(f, plan, tasks)
    check_owner_status(f, tasks, cfg)
    check_done_is_command(f, tasks, cfg)
    check_references(f, plan, cfg)
    check_graph(f, tasks, cfg)
    check_plan_source_of_truth(f, plan, tasks, cfg)
    check_adversary(f, tasks, cfg)
    check_health_checker(f, tasks, cfg)
    check_adversary_context(f, tasks, cfg)
    check_confirmed_is_exercised(f, plan, cfg)
    check_frozen_human_contracts(f, tasks, cfg)
    check_instrument_fixture(f, plan, tasks, cfg)
    check_rollback_real(f, plan, tasks, cfg)
    check_paths_disjoint(f, tasks, cfg)
    check_persona_model(f, plan, tasks, cfg)
    check_size_declared(f, plan, tasks, cfg)
    check_done_self_reference(f, plan, tasks, cfg)
    check_research_task(f, plan, tasks, cfg)
    check_brainstormed(f, plan, tasks, cfg)
    check_rulings(f, plan, tasks, cfg)
    check_invariants(f, plan, tasks, cfg)
    if args.run_gates:
        check_gates_fail_first(f, plan, tasks)

    # ── every declared check accounts for itself ────────────────────────────
    # The two that started this were `rulings` and `invariants`, both opt-in by
    # file and both silent when the file is absent — indistinguishable, in the
    # printed output, from two checks that had quietly stopped running. A gate
    # that cannot account for its own checks is asking to be trusted on faith.
    reported = f.named
    for name in GATE_CHECK_NAMES:
        if name not in reported:
            f.skip(name, SILENT_BECAUSE.get(name, UNREGISTERED_SKIP)
                                       .format(floor=ADVERSARY_MIN_TASKS))

    width = max((len(r[1]) for r in f.rows), default=10)
    for verdict, check, where, msg in f.rows:
        loc = f"  {where}" if where else ""
        print(f"{verdict} — {check.ljust(width)} {msg}{loc}")

    fails = sum(1 for r in f.rows if r[0] == "FAIL")
    skipped = sum(1 for r in f.rows if r[0] == "SKIP")
    print()
    # The arithmetic a reader could not do before: reported + skipped is exactly
    # what --version claims, so nothing declared can go missing unnoticed.
    print(f"checks: {len(GATE_CHECK_NAMES)} declared — "
          f"{len(GATE_CHECK_NAMES) - skipped} reported above, {skipped} skipped. "
          f"A SKIP is not a finding and does not reach the exit code.")
    print()
    # ── the RESULT line is a PARSED INTERFACE, not just prose ───────────────
    # External tooling reads it. A learning cache on this machine matches
    # `RESULT: FAIL — <n> finding(s)` to recover the remaining-defect count, so a
    # descending 30 -> 4 -> 0 reads as a repair curve rather than a binary
    # pass/fail. Reword these three lines and that degrades silently: nothing
    # here fails, the count stops parsing, and the consumer quietly falls back to
    # the exit code.
    #
    # Grillin takes no dependency on any of that and should not. But the wording
    # is a contract someone else relies on, and an undeclared contract is the
    # drift class this whole file exists to catch. If you change it, say so.
    if fails:
        print(f"RESULT: FAIL — {fails} finding(s). This plan is not operable as written.")
        return 1
    if not args.run_gates:
        # Previously this printed a note and exited 0, which meant the cheap
        # half of the check could be mistaken for the whole of it — by a human
        # skimming, and by any CI step that reads only the exit code. A run
        # that did not execute the gates has not settled operability, and
        # "could not settle" is exit 2, not success.
        print("RESULT: INCOMPLETE — structure is sound, but --run-gates was not "
              "given, so no done-command was executed. Nothing here proves a "
              "single gate would fail on unstarted work. Re-run with --run-gates.")
        return 2
    # Name what is still unchecked FOR THIS PLAN, rather than printing one
    # unconditional caveat. The old line said "operable, not correct" on every
    # single run, and an operator later described reading it as boilerplate —
    # correctly, because a sentence that never changes carries no information.
    # A line that names this plan's readers changes when the plan does.
    readers = {}
    for tid, path in sorted(tasks.items()):
        m = RE_READER.search(path.read_text(errors="replace"))
        if m:
            readers.setdefault(m.group(1).strip().lower(), []).append(tid)
    print("RESULT: PASS — the plan is structurally operable.")
    if len(tasks) < ADVERSARY_MIN_TASKS:
        print(f"        Not checked: whether it is CORRECT. At {len(tasks)} task(s) this "
              f"plan is below the {ADVERSARY_MIN_TASKS}-task floor, so no reader is "
              f"required — you are the reader.")
    else:
        who = " · ".join(f"{r}: {', '.join(t)}" for r, t in sorted(readers.items())) or "none"
        print("        Not checked: whether it is CORRECT. Nothing above is a reading "
              "of this plan's correctness.")
        print(f"        This plan staffs — {who} — and NEITHER HAS REPORTED YET.")
        # THE NUMBERS BELOW ARE HISTORY AND HAVE TO READ AS HISTORY. They used to
        # be printed bare, under the result of YOUR plan, phrased as though the
        # gate had just measured it — one run, in August 2026, reported as if it
        # were a live reading. The fact stays because it is the most useful thing
        # this tool says about its own ceiling; the framing is what was wrong.
        # tests/test-check-accounting.py holds these two numbers to
        # SCALING.json's `measurement` block so they cannot drift apart.
        print("        For scale, and this is the historical record rather than anything "
              "measured here — SCALING.json's one end-to-end run (5 Aug 2026; one job, "
              "one operator, one domain): the gate caught 2 defects, the readers 50.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
