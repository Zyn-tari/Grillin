#!/usr/bin/env python3
"""Three defects reported from the outside, and the ruling on one of them.

D2 · THE PHASE-5 CONTRADICTION, which turned out to be a sentence and not a
     bug. SCALING.json gives size S `phase5Form: "reduced — ... no persona,
     skills or fragments"` while `check_persona_model` demands a Model and an
     Effort at every size, and two rounds of first-time users read that as the
     document and the gate disagreeing. They do not: the reduced form drops a
     PERSONA, and the check has never required one. `taskContract.required`
     lists model and effort with no size qualifier at all. What is asserted
     here is the ruling — that the floor is size-blind on purpose, and that a
     task with no persona at all still passes — so a later "let's make it
     size-aware" has to argue with a test instead of with a comment.

D3 · A LINK TO A FILE THE PLAN WILL PRODUCE was graded as a dangling link, so
     the research-first shape the method recommends could not link
     `tasks/T1/FINDINGS.md` from T2. A target now counts as real when a task's
     own contract promises it; a typo, a link into a task that does not exist,
     and anything outside `tasks/` still fail.

D4 · A CITED PATH WAS HARVESTED AS OWNERSHIP. A curator took a FAIL on two
     tasks that only named the same file, one of them read-only. RE_DISCLAIMS
     had closed the negated wording; RE_CITES closes the positive one.

Every fix below is asserted in BOTH directions. A test that only proves the new
leniency would pass just as well if the check had been deleted, and a check
that fires on everything is discarded within a week — which costs more than the
false FAIL it was fixing.
"""
import importlib.util
import json
import pathlib
import shutil
import sys
import tempfile

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


def fails(check_name, fn, *args):
    """Run one check in isolation; True when it reported at least one FAIL."""
    f = vp.Findings()
    fn(f, *args)
    return any(r[0] == "FAIL" and r[1] == check_name for r in f.rows)


AGENT_ROW = "**Agent:** `implementer` · **Model:** `claude-sonnet-5` · **Effort:** high\n"


def build(tmp, size, tasks):
    """A plan directory. `tasks` is {id: TASK.md body}."""
    plan = pathlib.Path(tmp)
    (plan / "PLAN.md").write_text(f"# probe plan\n\n**Size:** {size}\n")
    for tid, body in tasks.items():
        d = plan / "tasks" / tid
        d.mkdir(parents=True)
        (d / "TASK.md").write_text(body)
    return plan, vp.find_tasks(plan)


# ── D2 · the ruling: the model floor is size-blind, and that is deliberate ──
print("D2 — the reduced form drops a persona, not a model")

spec_json = json.loads((ROOT / "SCALING.json").read_text())
required = spec_json["taskContract"]["required"]
chk("SCALING.json requires a model of every task contract", "model" in required, True)
chk("...and an effort", "effort" in required, True)
# If a band ever DOES declare a task contract of its own, this ruling has to be
# re-argued rather than silently outvoted by a new key.
chk("no size band overrides the task contract",
    [b["size"] for b in spec_json["scaling"] if "taskContract" in b], [])
chk("the reduced form is still declared at S",
    "reduced" in spec_json["scaling"][1].get("phase5Form", ""), True)

REDUCED = ("# T1\n\n**Status:** NOT STARTED\n**Owner:** worker-a\n"
           "**Model:** `claude-sonnet-5` · **Effort:** high\n\n"
           "## What you own\n\n`src/a/`\n")
with tempfile.TemporaryDirectory() as tmp:
    plan, tasks = build(tmp, "S", {"T1": REDUCED})
    chk("a task with NO persona at all passes — the reduced form is honoured",
        fails("persona-model", vp.check_persona_model, plan, tasks, {}), False)

# THE MUTATION PROBE. Drop the model from a task at the smallest band, which is
# where the reported contradiction lives. If a future size-aware rewrite exempts
# XS or S, this goes quiet and the floor is gone for 1-10 tasks — most plans.
NO_MODEL = REDUCED.replace("**Model:** `claude-sonnet-5` · ", "")
NO_EFFORT = REDUCED.replace(" · **Effort:** high", "")
LOW_EFFORT = REDUCED.replace("**Effort:** high", "**Effort:** low")
for size in ("XS", "S"):
    with tempfile.TemporaryDirectory() as tmp:
        plan, tasks = build(tmp, size, {"T1": NO_MODEL})
        chk(f"at {size}, a task naming no model still FAILS",
            fails("persona-model", vp.check_persona_model, plan, tasks, {}), True)
    with tempfile.TemporaryDirectory() as tmp:
        plan, tasks = build(tmp, size, {"T1": NO_EFFORT})
        chk(f"at {size}, a task naming no effort still FAILS",
            fails("persona-model", vp.check_persona_model, plan, tasks, {}), True)
    with tempfile.TemporaryDirectory() as tmp:
        plan, tasks = build(tmp, size, {"T1": LOW_EFFORT})
        chk(f"at {size}, an effort below high still FAILS",
            fails("persona-model", vp.check_persona_model, plan, tasks, {}), True)
    # THE CONTROL for the probes above.
    with tempfile.TemporaryDirectory() as tmp:
        plan, tasks = build(tmp, size, {"T1": REDUCED})
        chk(f"at {size}, a reduced task that names both is SILENT",
            fails("persona-model", vp.check_persona_model, plan, tasks, {}), False)


# ── D3 · a promised output is not a dangling link ───────────────────────────
print("\nD3 — a link to a file the plan produces")

PRODUCER = ("# T1\n\n**Status:** NOT STARTED\n**Owner:** worker-a\n" + AGENT_ROW +
            "**Blocked by:** — · **Blocks:** T2\n\n"
            "## What you own\n\n`tasks/T1/`\n\n"
            "## Done means\n\n```\ntest -s tasks/T1/FINDINGS.md\n```\n")


def consumer(link):
    return ("# T2\n\n**Status:** NOT STARTED\n**Owner:** worker-b\n" + AGENT_ROW +
            "**Blocked by:** T1 · **Blocks:** —\n\n"
            "## What you own\n\n`tasks/T2/`\n\n"
            f"## Steps\n\n1. Read [what T1 found]({link}) first.\n")


def refs_fail(link):
    with tempfile.TemporaryDirectory() as tmp:
        plan, _ = build(tmp, "XS", {"T1": PRODUCER, "T2": consumer(link)})
        return fails("references", vp.check_references, plan, {})


# THE CONTROL, and the defect itself: this is the shape the method recommends.
chk("a link to the FINDINGS.md T1's done-command promises is SILENT",
    refs_fail("../T1/FINDINGS.md"), False)
chk("a link to the task's own folder is SILENT",
    refs_fail("../T1/"), False)

# THE MUTATION PROBES. Each of these is a genuinely missing file and each must
# still fail, or the fix has simply switched the check off under `tasks/`.
chk("a typo in the filename still FAILS — nobody promised FINDNGS.md",
    refs_fail("../T1/FINDNGS.md"), True)
chk("a link into a task the plan does not hold still FAILS",
    refs_fail("../T9/FINDINGS.md"), True)
chk("a doc nobody wrote, outside tasks/, still FAILS",
    refs_fail("../../docs/architecture.md"), True)
chk("a promised NAME under the wrong task still FAILS — T2 promised nothing",
    refs_fail("FINDINGS.md"), True)

# And against the shipped fixture, which is the shape this defect was reported
# on, rather than a synthetic.
src = ROOT / "examples" / "research-first-plan"
with tempfile.TemporaryDirectory() as tmp:
    live = pathlib.Path(tmp) / "p"
    shutil.copytree(src, live)
    t2 = live / "tasks" / "T2" / "TASK.md"
    t2.write_text(t2.read_text().replace(
        "Read `tasks/T1/FINDINGS.md` first.",
        "Read [T1's findings](../T1/FINDINGS.md) first."))
    chk("examples/research-first-plan may link T1's findings from T2",
        fails("references", vp.check_references, live, {}), False)


# ── D4 · citing a path is not claiming it ───────────────────────────────────
print("\nD4 — a read-only citation is not an ownership claim")

chk("'read-only' on the line is not a claim",
    sorted(vp._owned_paths("## What you own\n`src/a/`\n`db/schema.sql` — read-only.\n")),
    ["src/a"])
chk("'read only' unhyphenated is not a claim",
    sorted(vp._owned_paths("## What you own\n`src/a/`\n`db/schema.sql`, read only.\n")),
    ["src/a"])
chk("'for reference' is not a claim",
    sorted(vp._owned_paths("## What you own\n`src/a/`\n`db/schema.sql` for reference.\n")),
    ["src/a"])
chk("'reference only' is not a claim",
    sorted(vp._owned_paths("## What you own\n`src/a/`\n`db/schema.sql` — reference only.\n")),
    ["src/a"])
chk("'context only' is not a claim",
    sorted(vp._owned_paths("## What you own\n`src/a/`\n`api/v1.yaml` — context only.\n")),
    ["src/a"])

# THE CONTROL. Naming somebody else as the owner is NOT a citation marker on its
# own, because "owned by this task" is written the same way, and a claim lost is
# a collision missed.
chk("naming another owner, with no read-only marker, is STILL a claim",
    sorted(vp._owned_paths("## What you own\n`src/a/`\n`db/schema.sql` — T3 owns it.\n")),
    ["db/schema.sql", "src/a"]),
chk("two plain claims are both still owned — the harvester is not disabled",
    sorted(vp._owned_paths("## What you own\n`src/a/`\n`db/schema.sql`\n")),
    ["db/schema.sql", "src/a"])
chk("a path is not swallowed because 'reference' appears in another sense",
    sorted(vp._owned_paths("## What you own\n`src/a/` — the reference implementation\n")),
    ["src/a"])

print("\nD4 — end to end, through check_paths_disjoint")


def owner_task(tid, blocks, own_block):
    return (f"# {tid}\n\n**Status:** NOT STARTED\n**Owner:** worker-{tid}\n" + AGENT_ROW +
            f"**Blocked by:** {blocks} · **Blocks:** —\n\n"
            f"## What you own\n\n{own_block}\n")


def disjoint_fails(a_block, b_block, b_blocked_by="—"):
    with tempfile.TemporaryDirectory() as tmp:
        _, tasks = build(tmp, "XS", {
            "T1": owner_task("T1", "—", a_block),
            "T2": owner_task("T2", b_blocked_by, b_block)})
        return fails("paths-disjoint", vp.check_paths_disjoint, tasks, {})


# THE MUTATION PROBE — genuine double ownership, which must keep failing. This
# is the whole reason the check exists and the thing a lenient fix would kill.
chk("two concurrent tasks plainly claiming one path still FAIL",
    disjoint_fails("`db/schema.sql`", "`db/schema.sql`"), True)
chk("...and still fail when one of them buries it in a longer list",
    disjoint_fails("`src/a/`\n`db/schema.sql`", "`db/schema.sql`\n`src/b/`"), True)
# THE CONTROL — the curator's real plan.
chk("one owner and one read-only citation is SILENT",
    disjoint_fails("`db/schema.sql`", "`db/schema.sql` — read-only, T1 owns it"), False)
chk("both citing it read-only is SILENT",
    disjoint_fails("`db/schema.sql` — read-only", "`db/schema.sql` — read-only"), False)
# Ordering was already the exemption and stays it.
chk("sequenced tasks sharing a path are exempt, as before",
    disjoint_fails("`db/schema.sql`", "`db/schema.sql`", "T1"), False)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
