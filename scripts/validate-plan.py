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
}
VALID_STATUS = {"NOT STARTED", "IN PROGRESS", "BLOCKED", "DONE"}

# Below this many tasks the method itself runs reduced (QUICKSTART §0), and a
# separately-staffed adversary costs more than it returns. At and above it, the
# adversary is not optional.
ADVERSARY_MIN_TASKS = 4
# Sections that constitute a task's contract. Changing any of them after the
# task has been handed out is moving the goalpost, which is why they are hashed.
CONTRACT_SECTIONS = ("what you own", "steps", "done means", "do not")

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
RE_READER = re.compile(r"^\*\*Reader:\*\*\s*([a-z]+)", re.M | re.I)
RE_DELIVERED = re.compile(r"^\*\*Delivered:\*\*\s*(.+)$", re.M | re.I)
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
        # Exit status first, wording second. `shell=True` runs /bin/sh, which is
        # dash on Debian and Ubuntu, and dash says "not found" where bash says
        # "command not found" — so a regex written against bash silently passed
        # a gate that shells out to a binary nobody has installed, and reported
        # it as failing cleanly. 127 and 126 are POSIX and say it without prose.
        blew_up = None
        if r.returncode in (126, 127):
            blew_up = type("M", (), {"group": lambda self, n=0:
                                     f"exit {r.returncode} — not found or not executable"})()
        else:
            blew_up = re.search(
                r"FileNotFoundError|No such file or directory|command not found|"
                r"\bnot found\b|ModuleNotFoundError|ImportError|cannot open|"
                r"Permission denied|unbound variable|syntax error",
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
        mo = RE_OWNER.search(text)
        owners[tid] = mo.group(1).strip().lower() if mo else ""
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
             f"{sorted(adversaries)} staffed as adversarial, owned by nobody else in the plan")


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
        mo = RE_OWNER.search(text)
        if not mo or not re.search(r"\bhuman\b|\byou\b|\brequester\b", mo.group(1), re.I):
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


def _owned_paths(text: str):
    """Specific paths from '## What you own'. Vague ones are ignored on purpose."""
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
                       f"let the other emit a fragment.")
    if not bad:
        f.ok("paths-disjoint", "no two concurrent tasks own the same path")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
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
    check_confirmed_is_exercised(f, plan, cfg)
    check_frozen_human_contracts(f, tasks, cfg)
    check_instrument_fixture(f, plan, tasks, cfg)
    check_rollback_real(f, plan, tasks, cfg)
    check_paths_disjoint(f, tasks, cfg)
    if args.run_gates:
        check_gates_fail_first(f, plan, tasks)

    width = max((len(r[1]) for r in f.rows), default=10)
    for verdict, check, where, msg in f.rows:
        loc = f"  {where}" if where else ""
        print(f"{verdict} — {check.ljust(width)} {msg}{loc}")

    fails = sum(1 for r in f.rows if r[0] == "FAIL")
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
    print("RESULT: PASS — the plan is structurally operable. "
          "That is not the same as correct; it still needs an adversarial pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
