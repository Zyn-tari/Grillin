#!/usr/bin/env python3
"""Calibrate check-drift block 7b — the size table's third column is a real copy.

WHERE THIS CAME FROM. Block 7 was added because the prose size table's NUMBERS
had drifted into overlapping bands and nothing read them. It checked the numbers
and stopped. The third column is a second copy of SCALING.json's `turnOn` arrays,
and it had ALREADY drifted by the time anyone looked: SCALING.json said size M
turns on `substrate measurement` — the phase-8 obligation — and the prose row for
M did not mention it, so the surface most people actually read omitted a whole
phase's worth of work. Third copy, third silent drift, same as 3b and 7.

WHAT IT DOES NOT CHECK, AND WHY. Only `turnOn`, and only in one direction: every
phrase the data says a band turns on must appear in that band's prose row.
`leaveOff` is left alone on purpose — asserting a phrase is ABSENT from prose is
unreliable in exactly the way a drift checker must not be, since "no skills"
contains "skills". Dash and case normalisation is a spelling allowance between
two house styles, not a fuzzy match; nothing else is forgiven.

    python3 tests/test-size-table-mirroring.py
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRIFT = ROOT / "scripts" / "check-drift.py"
GTP = ROOT / "GRILLING-THE-PLAN.md"
fails = 0


def chk(label, got, want):
    global fails
    ok = got == want
    print(f"  \033[32mPASS\033[0m  {label}" if ok
          else f"  \033[31mFAIL\033[0m  {label}\n        got {got!r}, want {want!r}")
    if not ok:
        fails += 1


def drift():
    p = subprocess.run([sys.executable, str(DRIFT)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


rc, out = drift()
chk("control · the size table and SCALING.json agree as they stand", rc, 0)
if rc != 0:
    print("\n  \033[31mABORT\033[0m  already drifting; no mutation below is attributable.\n")
    print(out)
    sys.exit(1)

before = GTP.read_bytes()
try:
    # ── probe 1 · the exact drift this block was written for: a turnOn phrase
    #    present in the data and missing from the prose row.
    src = GTP.read_text()
    mutated = src.replace(" + substrate measurement (Phase 8),", "", 1)
    chk("probe 1 · the mutation applied (a probe that misses reports itself dead)",
        mutated != src, True)
    GTP.write_text(mutated)
    rc, out = drift()
    chk("probe 1 · dropping a turnOn phrase from the prose row fails drift", rc, 1)
    chk("probe 1 · and the failure names the phrase", "substrate measurement" in out, True)
    chk("probe 1 · and names the band", re.search(r"size M turns on", out) is not None, True)
    GTP.write_bytes(before)

    # ── probe 2 · a phrase reworded rather than removed. The surfaces disagree
    #    just as much, and this is the likelier real-world shape.
    src = GTP.read_text()
    mutated = src.replace("+ waves with merge gates,", "+ waves,", 1)
    chk("probe 2 · the mutation applied", mutated != src, True)
    GTP.write_text(mutated)
    rc, out = drift()
    chk("probe 2 · rewording a turnOn phrase fails drift", rc, 1)
    chk("probe 2 · and quotes what the data said", "waves with merge gates" in out, True)
    GTP.write_bytes(before)

    rc, out = drift()
    chk("control · silent again once reverted", rc, 0)
finally:
    GTP.write_bytes(before)

chk("the mutated file was restored byte-for-byte", GTP.read_bytes() == before, True)

print()
print(f"\033[31m{fails} failed\033[0m" if fails
      else "\033[32mall size-table mirroring tests passed\033[0m")
sys.exit(1 if fails else 0)
