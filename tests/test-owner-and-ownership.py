#!/usr/bin/env python3
"""Two defects a first-time user found by reading the source, not by running it.

1 · OWNER RESOLUTION. `**Owner:**` and `**Agent:**` both matched one alternation
    and the first line in the file won. Every shipped example declares both, so
    the owner resolved to whichever the author put higher. In
    examples/minimal-passing-plan/T1 the owner was the persona line itself.

2 · DISCLAIMED PATHS. `_owned_paths` harvested every path in "## What you own",
    including ones the text said the worker does NOT own — so writing down the
    neighbours, which BRIEF.md.template tells authors to do, manufactured a
    collision that was not real.

Both directions are asserted. A test that only proves the new behaviour would
pass just as well if the check had been deleted.
"""
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("vp", ROOT / "scripts" / "validate-plan.py")
vp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vp)

passed = failed = 0


def chk(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  \033[32mPASS\033[0m  {label}")
    else:
        failed += 1
        print(f"  \033[31mFAIL\033[0m  {label} — want {want!r}, got {got!r}")


print("owner resolution")
AGENT_FIRST = ("**Agent:** `recon` · **Model:** `claude-opus-5` · **Effort:** high\n"
               "**Owner:** worker-a\n")
OWNER_FIRST = ("**Owner:** worker-a\n"
               "**Agent:** `recon` · **Model:** `claude-opus-5` · **Effort:** high\n")
chk("Owner wins when it comes second", vp.owner_of(AGENT_FIRST), "worker-a")
chk("Owner wins when it comes first", vp.owner_of(OWNER_FIRST), "worker-a")
chk("Agent is the fallback when no Owner line exists",
    vp.owner_of("**Agent:** `recon` · **Model:** `claude-opus-5`\n"), "recon")
chk("nobody named is empty, not a crash", vp.owner_of("**Status:** DONE\n"), "")

# The regression itself, against the shipped fixture rather than a synthetic.
t1 = (ROOT / "examples/minimal-passing-plan/tasks/T1/TASK.md").read_text()
chk("the known-good fixture's T1 owner is worker-a, not its persona line",
    vp.owner_of(t1), "worker-a")

print("\ndisclaimed paths")
chk("a plain claim is owned",
    sorted(vp._owned_paths("## What you own\n`src/api/`\n")), ["src/api"])
chk("'do NOT own' is not ownership",
    sorted(vp._owned_paths("## What you own\n`src/api/`\nYou do NOT own `frontend/`.\n")),
    ["src/api"])
chk("'are not yours' is not ownership",
    sorted(vp._owned_paths("## What you own\n`a/b/`\n`c/d/` and `e/f/` are not yours.\n")),
    ["a/b"])
chk("'Do NOT touch' is not ownership",
    sorted(vp._owned_paths("## What you own\n`a/b/`\nDo NOT touch `c/d/`.\n")), ["a/b"])
chk("'must not modify' is not ownership",
    sorted(vp._owned_paths("## What you own\n`a/b/`\nYou must not modify `s/x.sql`.\n")),
    ["a/b"])

# THE CONTROL. If the fix had simply stopped collecting paths, every assertion
# above would still pass and the collision check would be dead.
chk("two plain claims are BOTH still owned — the check is not disabled",
    sorted(vp._owned_paths("## What you own\n`a/b/`\n`c/d/`\n")), ["a/b", "c/d"])
chk("a path is not swallowed just because 'not' appears elsewhere",
    sorted(vp._owned_paths("## What you own\n`a/b/` — this is not optional\n")), ["a/b"])

print("\nhuman ownership, which the two fixes above interact with")
AGENT_ROW = "**Agent:** `recon` · **Model:** `claude-opus-5` · **Effort:** high\n"
chk("explicit `human` outranks a declared model",
    vp.is_human_owned("**Owner:** human\n" + AGENT_ROW), True)
chk("`you` beside a declared model is NOT a person doing the work",
    vp.is_human_owned("**Owner:** you\n" + AGENT_ROW), False)
chk("`you` with no model IS a person",
    vp.is_human_owned("**Owner:** you\n"), True)
chk("an ordinary agent owner is not human", vp.is_human_owned("**Owner:** worker-a\n"), False)

print()
print(f"  {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
