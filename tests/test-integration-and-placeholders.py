#!/usr/bin/env python3
"""Calibrate the checks bought on 2026-09-11 by comparing Grillin to superpowers.

Four defects, each found by a probe against a clean control rather than argued:

  placeholders    `TODO: fill in details.` and `implement later` in Steps passed
                  every check — an unmade decision delivered as an instruction
  owner           an Owner left as the template's `<agent id, …>` passed as owned
  integration     the integrator was declared in the roster, phase 7 and every
                  "Do NOT merge", and wired to nothing — a plan could verify every
                  task and report complete with every branch unmerged
  persona-model   Haiku 4.5 REJECTS the effort parameter at the API, and the floor
                  demanded one anyway; and a persona file and its task could name
                  two different models, leaving the runner to pin whichever it read

Every probe has a control, because each of these checks has an obvious way to be
wrong in the other direction — a TODO inside a done-command that greps for one, a
quoted "TBD" that is a mention and not a placeholder, a branch whose integrator is
two hops downstream. The controls are where the argument is.

    python3 tests/test-integration-and-placeholders.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "validate-plan.py"
LAB = Path(tempfile.mkdtemp(prefix="grillin-intph."))
fails = 0


def chk(label, got, want):
    global fails
    ok = got == want
    print(f"  \033[32mPASS\033[0m  {label}" if ok
          else f"  \033[31mFAIL\033[0m  {label}\n        got {got!r}, want {want!r}")
    if not ok:
        fails += 1


def task(tid, *, owner="**Owner:** human", extra="", steps="1. Do the thing.", done=None,
         blocked="—", why="It matters."):
    done = done or f"test -f tasks/{tid}/OUT.md"
    return (f"# {tid} — fixture\n\n**Status:** NOT STARTED\n{owner}\n"
            f"**Blocked by:** {blocked} · **Blocks:** —\n{extra}\n"
            f"## Why this exists\n\n{why}\n\n"
            f"## What you own\n`tasks/{tid}/`\n\n## Steps\n\n{steps}\n\n"
            f"## Done means\n```\n{done}\n```\n")


def verdict(check, tasks, cfg=None, files=None):
    """Build a plan from {tid: TASK.md text}; return the named check's line."""
    p = LAB / "p"
    shutil.rmtree(p, ignore_errors=True)
    for tid, text in tasks.items():
        (p / "tasks" / tid).mkdir(parents=True)
        (p / "tasks" / tid / "TASK.md").write_text(text)
    rows = "\n".join(f"| {t} | x |" for t in tasks)
    (p / "PLAN.md").write_text(f"# plan\n\n**Size:** XS\n\n| ID | Task |\n|---|---|\n{rows}\n")
    for rel, body in (files or {}).items():
        (p / rel).parent.mkdir(parents=True, exist_ok=True)
        (p / rel).write_text(body)
    argv = [sys.executable, str(GATE), str(p)]
    if cfg:
        (LAB / "cfg.json").write_text(cfg)
        argv += ["--config", str(LAB / "cfg.json")]
    r = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    lines = [l for l in r.stdout.splitlines() if f"— {check} " in l or l.endswith(f"— {check}")]
    line = lines[0] if lines else ""
    return ("PASS" if line.startswith("PASS") else "FAIL" if line.startswith("FAIL")
            else "SKIP" if line.startswith("SKIP") else "NONE"), "\n".join(lines)


H = "**Owner:** human"

print("\n=== 1 · placeholders — PROBES ===")
v, line = verdict("placeholders", {"T1": task("T1", steps="1. TODO: fill in details.")})
chk("`TODO: fill in details.` in Steps FAILS", v, "FAIL")
chk("...and quotes the offending line", "fill in details" in line, True)
v, _ = verdict("placeholders", {"T1": task("T1", steps="1. Add error handling — implement later.")})
chk("'implement later' in Steps FAILS", v, "FAIL")

print("\n=== 1b · placeholders — CONTROLS: a mention is not a placeholder ===")
v, _ = verdict("placeholders", {"T1": task("T1", done="! grep -rn TODO src/")})
chk("a done-command that greps for TODO (fenced) passes", v, "PASS")
v, _ = verdict("placeholders", {"T1": task("T1", steps="1. Remove every `TODO` marker from src/.")})
chk("`TODO` in inline code passes", v, "PASS")
v, _ = verdict("placeholders", {"T1": task("T1", steps='1. Leave four decisions, no "TBD".')})
chk('a quoted "TBD" — the known-bad fixture\'s own wording — passes', v, "PASS")
v, _ = verdict("placeholders", {"T1": task("T1", why="TODO: explain this later.")})
chk("a TODO in Why is out of scope, as documented", v, "PASS")
v, _ = verdict("placeholders", {"T1": task("T1")})
chk("a clean contract reports PASS, not silence", v, "PASS")
v, line = verdict("placeholders", {"T1": task("T1", steps="1. TODO")},
                  cfg='{"require_no_placeholders": false}')
chk("turned off, it SKIPs and names the key", (v, "require_no_placeholders" in line),
    ("SKIP", True))

print("\n=== 2 · owner — a template placeholder is not an owner ===")
v, _ = verdict("owner", {"T1": task("T1", owner="**Owner:** <agent id, a person's name, or `human`>")})
chk("Owner left as the template's <...> FAILS", v, "FAIL")
v, _ = verdict("owner", {"T1": task("T1", owner="**Agent:** `<persona — must appear in ../_ROSTER.md>`")})
chk("...and so does an Agent-only placeholder, through the owner fallback", v, "FAIL")
v, _ = verdict("owner", {"T1": task("T1")})
chk("CONTROL · `human` is an owner", v, "PASS")
v, _ = verdict("owner", {"T1": task("T1", owner="**Owner:** worker-a")})
chk("CONTROL · a name is an owner", v, "PASS")

print("\n=== 3 · persona-model — Haiku takes no effort ===")
AG = lambda m, e="": f"**Owner:** impl\n**Agent:** `impl` · **Model:** `{m}`" + (f" · **Effort:** {e}" if e else "")
v, _ = verdict("persona-model", {"T1": task("T1", owner=AG("claude-haiku-4-5"))})
chk("Haiku with no Effort PASSES — none is owed", v, "PASS")
v, line = verdict("persona-model", {"T1": task("T1", owner=AG("claude-haiku-4-5", "high"))})
chk("Haiku WITH an Effort FAILS", v, "FAIL")
chk("...saying the model rejects the parameter", "rejects the effort" in line, True)
v, _ = verdict("persona-model", {"T1": task("T1", owner=AG("claude-sonnet-5"))})
chk("CONTROL · Sonnet with no Effort still FAILS — the floor is unchanged", v, "FAIL")
v, _ = verdict("persona-model", {"T1": task("T1", owner=AG("claude-sonnet-5", "high"))})
chk("CONTROL · Sonnet with high still PASSES", v, "PASS")

print("\n=== 4 · persona-model — the persona file and the task name one model ===")
T = {"T1": task("T1", owner=AG("claude-opus-5", "high"))}
v, line = verdict("persona-model", T, files={"_personas/impl.md": "---\nmodel: haiku\n---\nYou are impl.\n"})
chk("persona file says haiku, task says opus: FAILS", v, "FAIL")
chk("...naming the file", "_personas/impl.md" in line, True)
v, _ = verdict("persona-model", T, files={"_personas/impl.md": "---\nmodel: opus\n---\n"})
chk("CONTROL · alias `opus` agrees with `claude-opus-5`", v, "PASS")
v, _ = verdict("persona-model", T, files={"_personas/impl.md": "---\nmodel: inherit\n---\n"})
chk("CONTROL · `inherit` pins nothing and agrees with anything", v, "PASS")
v, _ = verdict("persona-model", T, files={"_personas/impl.md": "You are impl. No frontmatter.\n"})
chk("CONTROL · a persona file with no frontmatter is not a mismatch", v, "PASS")

print("\n=== 5 · integration — every branch is merged downstream, by name ===")
BR = "**Branch:** `feat/a`"
MERGE = "git merge-base --is-ancestor feat/a main"
v, line = verdict("integration", {"T1": task("T1")})
chk("no branch declared: SKIP, with a reason", (v, "nothing to merge" in line), ("SKIP", True))
v, line = verdict("integration", {"T1": task("T1", extra=BR)})
chk("a branch and no integration task FAILS", v, "FAIL")
chk("...naming the branch", "feat/a" in line, True)
v, _ = verdict("integration", {"T1": task("T1", extra=BR),
                               "T2": task("T2", extra="**Kind:** integration", blocked="T1", done=MERGE)})
chk("CONTROL · a downstream integrator naming the branch PASSES", v, "PASS")
v, line = verdict("integration", {"T1": task("T1", extra=BR),
                                  "T2": task("T2", extra="**Kind:** integration", done=MERGE)})
chk("an integrator NOT downstream of the branch FAILS", v, "FAIL")
chk("...saying it could run concurrently", "still being written" in line, True)
v, line = verdict("integration", {"T1": task("T1", extra=BR),
                                  "T2": task("T2", extra="**Kind:** integration", blocked="T1",
                                             done="git branch --merged main | grep -c .")})
chk("an integrator whose done-command never names the branch FAILS", v, "FAIL")
v, _ = verdict("integration", {"T1": task("T1", extra=BR),
                               "T2": task("T2", blocked="T1"),
                               "T3": task("T3", extra="**Kind:** integration", blocked="T2", done=MERGE)})
chk("CONTROL · an integrator two hops downstream PASSES — reachability, not adjacency", v, "PASS")
v, _ = verdict("integration", {"T1": task("T1", extra="**Branch:** `<prefix>/<ID>-<slug>`")})
chk("CONTROL · an unfilled Branch placeholder is not a branch", v, "SKIP")
v, line = verdict("integration", {"T1": task("T1", extra=BR)}, cfg='{"require_integration": false}')
chk("turned off, it SKIPs", v, "SKIP")

shutil.rmtree(LAB, ignore_errors=True)
print(f"\n\033[31m{fails} failed\033[0m" if fails else "\n\033[32mall passed\033[0m")
sys.exit(1 if fails else 0)
