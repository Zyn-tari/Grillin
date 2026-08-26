#!/usr/bin/env python3
"""Calibrate check-drift's ninth block — a citation that names a heading resolves.

WHERE THIS CAME FROM. The build-brief extraction moved every shared rule into one
home in GRILLING-THE-PLAN.md and left pointers behind — `GRILLING-THE-PLAN.md §
"Title"` — so a rule would live in exactly one place. That trade buys
single-sourcing and sells a new drift: rename a heading and every pointer to it
breaks in silence, because nothing read them. The counts have been mirrored across
four surfaces since check-drift.py existed, for precisely this reason; the
citations were a fifth surface nobody was watching, and they were created by the
same pass that argued a fact published in four places becomes four different facts.

THE CONTROL MATTERS AS MUCH AS THE PROBE. A citation checker that finds nothing
and a citation checker that has quietly stopped matching look identical from the
outside: both print "surfaces agree". So this asserts both directions — that the
repository as it stands is silent, and that breaking one heading is loud — and it
restores every file it touched byte-for-byte, verified, whether it passes or not.

    python3 tests/test-citation-mirroring.py
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRIFT = ROOT / "scripts" / "check-drift.py"
fails = 0


def chk(label, got, want):
    global fails
    ok = got == want
    print(f"  \033[32mPASS\033[0m  {label}" if ok
          else f"  \033[31mFAIL\033[0m  {label}\n        got {got!r}, want {want!r}")
    if not ok:
        fails += 1


def drift():
    """Exit code and stdout of a real check-drift run against the real tree."""
    p = subprocess.run([sys.executable, str(DRIFT)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# ── the control, taken FIRST: if the tree is already dirty every probe below is
#    measuring something other than its own mutation, and says so instead.
rc, out = drift()
chk("control · the repository as it stands has no citation drift", rc, 0)
if rc != 0:
    print("\n  \033[31mABORT\033[0m  the tree was already failing check-drift; "
          "no mutation below would be attributable.\n")
    print(out)
    sys.exit(1)

# ── find a citation that actually exists, rather than assuming one does. A probe
#    whose mutation misses reports its own check dead — this repo has shipped that
#    failure twice in CI (see .github/workflows/gate.yml on model-is-tier-word).
CITE = re.compile(r'GRILLING-THE-PLAN\.md[`)\]]*\s*§\s*"([^"]{1,200})"')
target, citing_file = None, None
for f in sorted(ROOT.rglob("*.template")) + sorted(ROOT.rglob("*.md")):
    if ".git" in f.parts:
        continue
    m = CITE.search(f.read_text(errors="replace"))
    if m:
        target, citing_file = re.sub(r"\s+", " ", m.group(1)).strip(), f
        break
chk("a quoted section citation exists to mutate", target is not None, True)
if target is None:
    sys.exit(1)
print(f"        mutating: {target!r}, cited by {citing_file.relative_to(ROOT)}")

GTP = ROOT / "GRILLING-THE-PLAN.md"
BRIEF = ROOT / "templates" / "BRIEF.md.template"
gtp_before, brief_before = GTP.read_bytes(), BRIEF.read_bytes()

try:
    # ── probe 1 · the cited heading is renamed. Every pointer to it must be named.
    src = GTP.read_text()
    heading = next(ln for ln in src.splitlines()
                   if re.match(r"^#+\s+", ln)
                   and re.sub(r"\s+", " ", ln.split(" ", 1)[1]).strip() == target)
    GTP.write_text(src.replace(heading, heading + " RENAMED", 1))
    rc, out = drift()
    chk("probe · renaming a cited heading fails check-drift", rc, 1)
    chk("probe · and the failure names the missing heading", target in out, True)
    chk("probe · and names the file and line that cites it",
        str(citing_file.relative_to(ROOT)) in out, True)
    GTP.write_bytes(gtp_before)

    # ── probe 2 · a numbered citation pointing at a section that does not exist.
    BRIEF.write_text(BRIEF.read_text()
                     + "\n<!-- OPERATING-THE-PLAN.md §77 does not exist. -->\n")
    rc, out = drift()
    chk("probe · a citation of a section number that does not exist fails", rc, 1)
    chk("probe · and says which number it could not find", "§77" in out, True)
    BRIEF.write_bytes(brief_before)

    # ── the silent control, taken again AFTER the mutations. A check that fires on
    #    a mutation and also fires on a clean tree fails everything, which is the
    #    same as checking nothing.
    rc, out = drift()
    chk("control · silent again once the mutations are reverted", rc, 0)
finally:
    GTP.write_bytes(gtp_before)
    BRIEF.write_bytes(brief_before)

chk("every mutated file was restored byte-for-byte",
    (GTP.read_bytes(), BRIEF.read_bytes()) == (gtp_before, brief_before), True)

print()
print(f"\033[31m{fails} failed\033[0m" if fails
      else "\033[32mall citation-mirroring tests passed\033[0m")
sys.exit(1 if fails else 0)
