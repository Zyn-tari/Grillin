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

Zero dependencies (python3 stdlib). Fail-closed: unknown state is a failure.
Exit 0 = operable. Exit 1 = not. Exit 2 = could not run the check itself.

Every finding cites file:line, because a validator that says "something is wrong"
is a worse version of the checklist it replaces.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

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
}
VALID_STATUS = {"NOT STARTED", "IN PROGRESS", "BLOCKED", "DONE"}

RE_STATUS = re.compile(r"^\*\*Status:\*\*\s*([A-Z ]+?)\s*(?:—|$)", re.M)
RE_OWNER = re.compile(r"^\*\*(?:Owner|Agent)\b.*?:\*\*\s*(.+)$", re.M | re.I)
# Both fields commonly share one line: "**Blocked by:** — · **Blocks:** T2, T4".
# Stop at the separator or the next bold field, or every entry in Blocks is read
# as a blocker and the graph check reports a cycle that does not exist.
RE_BLOCKED_BY = re.compile(r"\*\*Blocked by:\*\*\s*([^·\n]*?)(?=\*\*|·|$)", re.M | re.I)
RE_BLOCKS = re.compile(r"\*\*Blocks:\*\*\s*([^·\n]*?)(?=\*\*|·|$)", re.M | re.I)
RE_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)#][^)]*)\)")
RE_FENCE = re.compile(r"```[a-z]*\n(.*?)```", re.S)
RE_TASK_ID = re.compile(r"\b([A-Z]\d{1,3}[a-z]?)\b")


class Findings:
    def __init__(self):
        self.rows = []

    def fail(self, check, where, msg):
        self.rows.append(("FAIL", check, where, msg))

    def ok(self, check, msg):
        self.rows.append(("PASS", check, "", msg))

    @property
    def failed(self):
        return any(r[0] == "FAIL" for r in self.rows)


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
        if cfg.get("require_owner", True) and not RE_OWNER.search(text):
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
        blew_up = re.search(
            r"FileNotFoundError|No such file or directory|command not found|"
            r"ModuleNotFoundError|ImportError|cannot open|Permission denied|"
            r"unbound variable|syntax error",
            (r.stderr or "") + (r.stdout or ""), re.I)
        if blew_up:
            f.fail("gate-fails-first", f"{path}",
                   f"{tid}'s done-command could not run here — it failed on its own "
                   f"inputs, not on the work ({blew_up.group(0)!r}). Its paths are "
                   f"unanchored: an orchestrator running it from anywhere but the "
                   f"author's directory gets an error it may read as a clean fail.")
        elif r.returncode == 0:
            f.fail("gate-fails-first", f"{path}",
                   f"{tid} is {status} but its done-command already exits 0. "
                   f"The gate does not detect the work — an orchestrator would run "
                   f"it, see success, and mark unstarted work complete.")
        else:
            f.ok("gate-fails-first",
                 f"{tid}: gate fails cleanly while {status.lower()}, as a gate should")


def check_references(f: Findings, plan: Path, cfg: dict):
    if not cfg.get("require_refs_resolve", True):
        return
    dangling = 0
    for md in sorted(plan.rglob("*.md")):
        for i, line in enumerate(md.read_text(errors="replace").splitlines(), 1):
            for target in RE_MD_LINK.findall(line):
                t = target.split("#")[0].strip()
                if not t or "://" in t or t.startswith("mailto:"):
                    continue
                if not (md.parent / t).exists():
                    dangling += 1
                    f.fail("references", f"{md}:{i}",
                           f"link target does not resolve: {t!r} "
                           f"(resolved relative to {md.parent})")
    if not dangling:
        f.ok("references", "every relative link in the plan resolves")


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


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan", help="the plan directory")
    ap.add_argument("--run-gates", action="store_true",
                    help="EXECUTE each task's done-command to prove it fails on "
                         "unstarted work. Runs commands the plan author wrote — "
                         "opt-in on purpose.")
    ap.add_argument("--config", default=None, help="JSON file; may only tighten the floors")
    args = ap.parse_args()

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
    if args.run_gates:
        check_gates_fail_first(f, plan, tasks)
    else:
        print("note: --run-gates not given; gates were not executed. "
              "A plan is not proven operable until they are.\n")

    width = max((len(r[1]) for r in f.rows), default=10)
    for verdict, check, where, msg in f.rows:
        loc = f"  {where}" if where else ""
        print(f"{verdict} — {check.ljust(width)} {msg}{loc}")

    fails = sum(1 for r in f.rows if r[0] == "FAIL")
    print()
    if fails:
        print(f"RESULT: FAIL — {fails} finding(s). This plan is not operable as written.")
        return 1
    print("RESULT: PASS — the plan is structurally operable. "
          "That is not the same as correct; it still needs an adversarial pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
