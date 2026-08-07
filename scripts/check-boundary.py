#!/usr/bin/env python3
"""Does the scoping boundary reach every surface a reader can enter through?

Whitespace-normalised, so a statement wrapped across lines still counts — the
first version of this check grepped line-by-line for one exact phrasing and
reported two correctly-fixed files as missing. A checker that only matches the
wording its author happened to use is a search, not a check.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Each surface must carry at least one of these ideas, however phrased.
SIGNALS = [
    r"ship with Grillin uninstalled",
    r"break(s|ing)? .{0,20}build",
    r"runs \*?\*?on\*?\*? a plan, from outside",
    r"notOutput",
    r"never sees",
    r"must never be the same",
]

SURFACES = {
    "README.md":              "the front door",
    "QUICKSTART.md":          "where a reader first places tasks/",
    "OPERATING-THE-PLAN.md":  "where the committed hook is celebrated",
    "install-hooks.sh":       "the artefact that reaches into a project",
    "install.sh":             "the other installer",
    "SCALING.json":           "what gets handed to an agent",
    "templates/GRILL-CHECKLIST.md": "the artefact most easily read as a to-do list",
}

bad = 0
for name, why in SURFACES.items():
    text = (ROOT / name).read_text(encoding="utf-8")
    flat = re.sub(r"\s+", " ", text)
    hits = [s for s in SIGNALS if re.search(s, flat, re.I)]
    if hits:
        print(f"  scoped   {name:24} {len(hits)} signal(s)   — {why}")
    else:
        bad += 1
        print(f"  MISSING  {name:24} —— {why}")

print()
if bad:
    print(f"{bad} surface(s) carry no scoping statement.")
    sys.exit(1)
print("every entry surface carries the boundary.")
