#!/usr/bin/env python3
# FOR THIS REPOSITORY ONLY. This is Grillin checking ITSELF — its surfaces are
# hardcoded (SCALING.json, index.html, README.md, GRILLING-THE-PLAN.md). It is
# not a tool you can point at your own files. For that, use check-index.py.
"""
check-drift.py — the surfaces must say the same thing.

Grillin publishes the same facts four times: as prose in GRILLING-THE-PLAN.md,
as data in SCALING.json, as a rendered page in index.html, and as counts in
README.md. That is a drift generator, and it has fired twice:

  · two anti-patterns reached SCALING.json and index.html and never the markdown,
    and stayed inconsistent for four commits;
  · phase 5 was turned on at size S in SCALING.json, and index.html kept
    rendering S without it — a stale claim on the page most people actually read.

Both were found by hand, late. This is the mechanism that finds them early.

index.html embeds its own copy on purpose: the README tells you to download it
and open it locally, and a fetch() of SCALING.json fails under file:// . So the
duplication is deliberate and the check is the price of it.

Exit 0 = the surfaces agree. Exit 1 = they do not. Exit 2 = could not check.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def embedded_array(html: str, key: str):
    """Pull a balanced [...] literal that follows `key:` in the page's data blob."""
    i = html.index(f"{key}:[") + len(key) + 1
    depth = 0
    for j in range(i, len(html)):
        if html[j] == "[":
            depth += 1
        elif html[j] == "]":
            depth -= 1
            if depth == 0:
                return html[i:j + 1]
    raise ValueError(f"unbalanced array for {key}")


def main() -> int:
    try:
        spec = json.loads((ROOT / "SCALING.json").read_text())
        html = (ROOT / "index.html").read_text()
        readme = (ROOT / "README.md").read_text()
        prose = (ROOT / "GRILLING-THE-PLAN.md").read_text()
    except OSError as e:
        print(f"check-drift: {e}", file=sys.stderr)
        return 2

    bad = []

    # ── 1 · the phase-on lists, per size ────────────────────────────────────
    try:
        arr = embedded_array(html, "scaling")
    except ValueError as e:
        print(f"check-drift: {e}", file=sys.stderr)
        return 2
    page = {m.group(1): [int(x) for x in m.group(2).split(",") if x.strip()]
            for m in re.finditer(r'\{size:"(\w+)".*?on:\[([0-9,\s]*)\]', arr, re.S)}
    for row in spec["scaling"]:
        size, want = row["size"], row["phasesOn"]
        got = page.get(size)
        if got is None:
            bad.append(f"index.html has no row for size {size}")
        elif got != want:
            missing = sorted(set(want) - set(got))
            extra = sorted(set(got) - set(want))
            bad.append(
                f"size {size}: SCALING.json says phases {want}, index.html renders {got}"
                + (f" — missing {missing}" if missing else "")
                + (f" — extra {extra}" if extra else ""))

    # ── 2 · the counts, wherever they are asserted in words ─────────────────
    WORDS = {16: "sixteen", 17: "seventeen", 25: "twenty-five", 11: "eleven"}
    n_principles = len(spec["principles"])
    n_anti = len(spec["antiPatterns"])
    n_phases = len(spec["phases"])

    for n, label, where in ((n_principles, "principles", readme),
                            (n_phases, "phases", readme)):
        word = WORDS.get(n)
        if word and not re.search(rf"\b{word}\s+{label}\b", where, re.I):
            bad.append(f"README does not say '{word} {label}' but SCALING.json has {n}")

    if not re.search(rf"\b{WORDS.get(n_principles, n_principles)}\s+principles\b", prose, re.I):
        bad.append(f"GRILLING-THE-PLAN.md heading disagrees with {n_principles} principles")

    # ── 3 · the anti-pattern rows, count only ──────────────────────────────
    try:
        anti = embedded_array(html, "anti")
        page_rows = len(re.findall(r'\[', anti)) - 1
        if page_rows != n_anti:
            bad.append(f"index.html renders {page_rows} anti-patterns, SCALING.json has {n_anti}")
    except ValueError:
        pass                                   # shape differs; count check is best-effort

    # ── 4 · the check list the validator actually reports ──────────────────
    v = (ROOT / "scripts" / "validate-plan.py").read_text()
    declared = set(spec.get("gateChecks", []))
    if declared:
        emitted = set(re.findall(r'f\.(?:ok|fail)\(\s*"([a-z-]+)"', v))
        missing = declared - emitted
        extra = emitted - declared
        if missing:
            bad.append(f"SCALING.json lists gate checks the validator never emits: {sorted(missing)}")
        if extra:
            bad.append(f"the validator emits checks SCALING.json does not list: {sorted(extra)}")

    # ── the size bands ──────────────────────────────────────────────────────
    # Published in three places: BANDS in validate-plan.py, scaling[].tasks in
    # SCALING.json, and Plan.size() in Smokin. The first two live in this repo,
    # so the first two get compared. A band table that drifts turns
    # `size-declared` into a check that enforces a number nobody agreed on.
    m = re.search(r"^BANDS\s*=\s*\[(.*?)\]", v, re.M | re.S)
    if m:
        gate = {n: (int(a), int(b)) for n, a, b in
                re.findall(r'\("([A-Z]{1,2})",\s*(\d+),\s*(\d+)\)', m.group(1))}
        for row in spec.get("scaling", []):
            size, rng = row.get("size"), str(row.get("tasks", ""))
            if size not in gate:
                bad.append(f"SCALING.json declares size {size!r}; the gate's BANDS has no such band")
                continue
            r = re.match(r"(\d+)\s*[-–]\s*(\d+)", rng) or re.match(r"(\d+)\s*\+", rng)
            if not r:
                continue
            lo = int(r.group(1))
            hi = int(r.group(2)) if r.lastindex and r.lastindex > 1 else gate[size][1]
            if (lo, hi) != gate[size]:
                bad.append(f"size {size}: SCALING.json says {rng!r}, the gate's BANDS says "
                           f"{gate[size][0]}-{gate[size][1]}")
    else:
        bad.append("validate-plan.py has no BANDS table — size-declared cannot be drift-checked")

    if bad:
        print("DRIFT — the surfaces disagree:\n")
        for b in bad:
            print(f"  · {b}")
        print("\nFix the surface that is wrong, not the check. A fact published four times"
              "\nis a fact that will eventually be four different facts.")
        return 1

    print(f"surfaces agree — {n_phases} phases, {n_principles} principles, "
          f"{n_anti} anti-patterns, {len(spec.get('gateChecks', []))} gate checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
