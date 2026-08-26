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
import subprocess
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

    # ── 3b · ...and the markdown table, which is the one that actually drifted ──
    # Check 3 compares SCALING.json against index.html and stops. The incident in
    # this file's own docstring is anti-patterns that reached those two and never
    # GRILLING-THE-PLAN.md — the surface the check did not read. Found by an
    # adversarial reader, not by this script, which is the point.
    # The section is last in the file today, so the terminator must also accept EOF —
    # anchoring it to '---' alone made this check fail closed on the real file.
    m = re.search(r"^## Anti-patterns\s*$(.*?)(?=^---\s*$|^## |\Z)", prose, re.M | re.S)
    if m is None:
        bad.append("GRILLING-THE-PLAN.md has no '## Anti-patterns' section to count")
    else:
        # Data rows only: a table row starts with '| ' and the separator does not.
        prose_rows = [ln for ln in m.group(1).splitlines()
                      if ln.startswith("| ") and not ln.startswith("| Don't")]
        if len(prose_rows) != n_anti:
            bad.append(f"GRILLING-THE-PLAN.md lists {len(prose_rows)} anti-patterns, "
                       f"SCALING.json has {n_anti}")

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

    # ── 6 · the known-bad example's finding count, published in three places ──
    # THE INCIDENT THIS IS FOR. The stored gate report said 26 findings, both
    # prose surfaces said "30+", and a fresh run produced 51. The report was
    # generated once and never regenerated, so every check added since had
    # silently invalidated it — including the one added the day this was found.
    # The report is a MEASUREMENT of the gate, so it rots every time the gate
    # gains a check, which makes it exactly the kind of fact that has to be
    # derived rather than remembered.
    report = ROOT / "examples" / "a-real-first-plan-GATE-REPORT.txt"
    plan = ROOT / "examples" / "a-real-first-plan"
    if report.is_file() and plan.is_dir():
        txt = report.read_text(errors="replace")
        m = re.search(r"RESULT: FAIL — (\d+) finding", txt)
        stored = int(m.group(1)) if m else None
        counted = len(re.findall(r"^FAIL", txt, re.M))
        if stored is None:
            bad.append(f"{report.name} has no RESULT line — it cannot be checked "
                       f"against the gate it claims to record")
        elif stored != counted:
            bad.append(f"{report.name} says {stored} findings and lists {counted}")
        else:
            r = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate-plan.py"),
                                str(plan), "--run-gates"],
                               capture_output=True, text=True)
            live = re.search(r"RESULT: FAIL — (\d+) finding", r.stdout)
            if live is None:
                bad.append(f"the gate no longer reports FAIL on {plan.name} — it is this "
                           f"repo's known-bad fixture and a gate that passes it catches "
                           f"nothing")
            elif int(live.group(1)) != stored:
                bad.append(f"{report.name} records {stored} findings, the gate now "
                           f"produces {int(live.group(1))}. Regenerate it: "
                           f"./scripts/validate-plan.py examples/a-real-first-plan "
                           f"--run-gates > {report.name} (then rewrite the absolute paths "
                           f"to ~/grillin)")
            else:
                # EVERY surface, and the root README was the one missed the
                # first time this was fixed — a first-time reader of the map
                # found it hours later, still saying 26. A drift check that
                # covers most of the surfaces is a drift check that will be
                # trusted and wrong.
                for surface in (ROOT / "README.md",
                                ROOT / "examples" / "README.md",
                                ROOT / "examples" / "minimal-passing-plan" / "PLAN.md"):
                    if not surface.is_file():
                        continue
                    t = surface.read_text(errors="replace")
                    said = set(int(x) for x in re.findall(r"(?:with|fails with)\s+(\d+)\s+findings", t))
                    wrong = said - {stored}
                    if wrong:
                        bad.append(f"{surface.relative_to(ROOT)} says "
                                   f"{sorted(wrong)} findings, the gate produces {stored}")

    # ── 7 · the size table in the prose, which nothing was reading ──────────
    # check 5 compares SCALING.json's ranges to the gate's BANDS and stops. The
    # markdown table is a THIRD copy, and it said M 10-25, L 25-60, XL 60+ —
    # overlapping bands, so a 25-task plan was two sizes at once. It survived
    # because this file never read it, which is the same reason the anti-pattern
    # table drifted in check 3b.
    m = re.search(r"^\|\s*\*\*XS\*\*.*?(?=^\s*$|\Z)", prose, re.M | re.S)
    if m is None:
        bad.append("GRILLING-THE-PLAN.md has no size table to check against BANDS")
    else:
        for row in m.group(0).splitlines():
            r = re.match(r"\|\s*\*\*(XS|S|M|L|XL)\*\*\s*\|\s*([0-9]+)[–-]?([0-9]*)\+?\s*\|", row)
            if not r:
                continue
            size, lo, hi = r.group(1), int(r.group(2)), r.group(3)
            want = gate.get(size)
            if not want:
                continue
            if lo != want[0] or (hi and int(hi) != want[1]):
                bad.append(f"GRILLING-THE-PLAN.md's size table says {size} is "
                           f"{lo}-{hi or '+'}, the gate's BANDS says "
                           f"{want[0]}-{want[1]}")

    # ── 7b · ...and the third column, which nothing was reading either ──────
    # Block 7 checks the size table's NUMBERS and stops there. The description
    # column is a second copy of SCALING.json's `turnOn` arrays, and it had
    # already drifted when this was written: SCALING.json said M turns on
    # `substrate measurement` and the prose row for M did not mention it, so the
    # phase-8 obligation was invisible on the surface most people read. Same
    # failure as 3b and 7, third surface.
    #
    # Strict containment, one direction: every phrase SCALING.json says a band
    # turns on must appear in that band's prose row. Dashes and case are
    # normalised because the two surfaces spell them differently by house style
    # (en dash in prose, hyphen in JSON) — that is a spelling normalisation, not
    # a fuzzy match, and nothing else is forgiven. leaveOff is deliberately NOT
    # checked: asserting a phrase is ABSENT from prose is unreliable in exactly
    # the way this file must not be ("no skills" contains "skills").
    def _norm(t):
        return re.sub(r"\s+", " ", t.replace("–", "-").replace("—", "-")).strip().lower()

    m = re.search(r"^\|\s*\*\*XS\*\*.*?(?=^\s*$|\Z)", prose, re.M | re.S)
    if m:
        prose_rows = {}
        for row in m.group(0).splitlines():
            r = re.match(r"\|\s*\*\*(XS|S|M|L|XL)\*\*\s*\|[^|]*\|(.*)\|\s*$", row)
            if r:
                prose_rows[r.group(1)] = _norm(r.group(2))
        for band in spec.get("scaling", []):
            size, row = band.get("size"), prose_rows.get(band.get("size"))
            if row is None:
                continue
            for phrase in band.get("turnOn", []):
                if _norm(phrase) not in row:
                    bad.append(f"SCALING.json says size {size} turns on "
                               f"{phrase!r}; GRILLING-THE-PLAN.md's size table row "
                               f"for {size} does not say so")

    # ── 8 · the headline number has to be the sum of its parts ──────────────
    # "the readers caught 50" is printed by the gate on every run. Its parts are
    # health 20 and adversary 44 (30 blocking, 14 non-blocking), which sum to 64.
    # A reader tried to add it up, could not, and nothing in the repo explained
    # the gap. 50 is health + the adversary's BLOCKING findings; that reading is
    # now recorded, and this asserts it stays true.
    meas = spec.get("measurement", {})
    head = re.search(r"readers caught (\d+)", meas.get("headline", ""))
    adv = re.search(r"(\d+)\s+blocking", (spec.get("readers", {})
                                           .get("adversary", {}).get("found", "")))
    if head and adv:
        want = meas.get("healthChecker", 0) + int(adv.group(1))
        if int(head.group(1)) != want:
            bad.append(f"SCALING.json's headline says the readers caught "
                       f"{head.group(1)}, but healthChecker {meas.get('healthChecker')} "
                       f"+ adversary {adv.group(1)} blocking = {want}")
        if "headlineDecomposition" not in meas:
            bad.append("SCALING.json's headline number has no stated decomposition — "
                       "a number the gate prints on every run must be addable")

    # ── 9 · cross-file section citations resolve to a real heading ─────────
    # The build-brief extraction moved every shared rule into one home and left
    # pointers of the form `GRILLING-THE-PLAN.md § "Title"` behind. That trade
    # buys single-sourcing and sells a new drift: rename a heading and every
    # pointer to it breaks in silence, because until now nothing read them. It
    # is the same failure the count mirroring above exists to catch, arriving on
    # a surface nobody was watching. Numbered citations (§7, §10b) go through
    # the same door — they were already load-bearing and already unchecked.
    heads = {}
    for name in ("GRILLING-THE-PLAN.md", "OPERATING-THE-PLAN.md", "QUICKSTART.md"):
        try:
            src = (ROOT / name).read_text()
        except OSError:
            continue
        titles, numbers = set(), set()
        for ln in src.splitlines():
            m = re.match(r"^#+\s+(.+?)\s*$", ln)
            if not m:
                continue
            t = re.sub(r"\s+", " ", m.group(1)).strip()
            titles.add(t)
            n = re.match(r"^(\d+[a-z]?)\s*·", t)
            if n:
                numbers.add(n.group(1))
        heads[name] = (titles, numbers)

    # A quoted title may wrap across lines in the source that cites it, so the
    # match spans newlines and both sides are whitespace-normalised before they
    # are compared. Bounded at 200 chars: an unterminated quote elsewhere in a
    # file must not swallow the rest of it and report a heading nobody wrote.
    cite = re.compile(
        r"(GRILLING-THE-PLAN|OPERATING-THE-PLAN|QUICKSTART)\.md[`)\]]*\s*"
        r"§\s*(?:\"([^\"]{1,200})\"|(\d+[a-z]?))")
    for src_file in sorted(ROOT.rglob("*.md")) + sorted(ROOT.rglob("*.template")):
        if ".git" in src_file.parts or src_file.name == "CHANGELOG.md":
            continue                  # the changelog is a record, not a surface
        body = src_file.read_text(errors="replace")
        for m in cite.finditer(body):
            fname = f"{m.group(1)}.md"
            if fname not in heads:
                continue
            titles, numbers = heads[fname]
            where = f"{src_file.relative_to(ROOT)}:{body.count(chr(10), 0, m.start()) + 1}"
            if m.group(2):
                want = re.sub(r"\s+", " ", m.group(2)).strip()
                if want not in titles:
                    bad.append(f"{where} cites {fname} § \"{want}\" — "
                               f"that file has no heading by that name")
            elif m.group(3) and m.group(3) not in numbers:
                bad.append(f"{where} cites {fname} §{m.group(3)} — "
                           f"that file has no section numbered {m.group(3)}")

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
