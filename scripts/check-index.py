#!/usr/bin/env python3
"""
check-index.py — an index and its shards must agree.

    ./scripts/check-index.py <index-file> <shard-dir> [options]

WHY THIS EXISTS. Splitting one long file into an index plus per-topic shards is
the right move — the index is read every time, a shard only when it is relevant.
It is also a drift generator, because the same facts now live in two places.
They agree on the day they are born and diverge on the day someone tidies a
heading.

This repository already had a drift checker and it was no use to anybody: it is
hardcoded to Grillin's own surfaces. An operator who had just built an
index-plus-shards changelog found it, correctly identified that they had made a
drift generator, and could not point it at their work. What they built instead
was a callout in the index saying the headings were load-bearing — and, in the
same breath, named it as weaker than a check. It is. This is the check.

WHAT IT CHECKS, and the fourth one is theirs:

  1. every path the index links to exists
  2. every shard in the directory is linked from the index — orphans in the
     other direction are how a wave quietly stops being published
  3. the index's name for a shard appears VERBATIM as a heading inside it.
     This is the pair a downstream consumer keys on, and the one most likely to
     be "improved" on one side only.
  4. where the index states a count, the shard holds that many entries

SCOPE. This checks that two surfaces agree. It cannot tell you either of them is
right, and a matching pair of wrong facts passes.

Zero dependencies. Exit 0 = they agree. 1 = they do not. 2 = could not check.
"""
import argparse
import re
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("index", type=Path)
    ap.add_argument("shard_dir", type=Path)
    ap.add_argument("--glob", default="*.md",
                    help="which files in shard_dir are shards (default: *.md)")
    ap.add_argument("--link-re", default=r"\[([^\]]+)\]\(([^)]+)\)",
                    help="over index lines, captures (name, path). Default: a markdown link")
    ap.add_argument("--count-re", default=None,
                    help="over index lines, captures (name, count). Omit to skip check 4")
    ap.add_argument("--entry-re", default=r"^\s*[-*] ",
                    help="what counts as one entry inside a shard (default: a bullet)")
    a = ap.parse_args()

    if not a.index.is_file():
        print(f"check-index: {a.index} is not a file", file=sys.stderr)
        return 2
    if not a.shard_dir.is_dir():
        print(f"check-index: {a.shard_dir} is not a directory", file=sys.stderr)
        return 2

    try:
        link = re.compile(a.link_re)
        count_re = re.compile(a.count_re) if a.count_re else None
        entry = re.compile(a.entry_re, re.M)
    except re.error as e:
        print(f"check-index: bad pattern — {e}", file=sys.stderr)
        return 2

    lines = a.index.read_text(errors="replace").splitlines()
    bad, checked = [], 0

    # name -> (path, line number in the index)
    linked = {}
    for i, line in enumerate(lines, 1):
        for m in link.finditer(line):
            name, rel = m.group(1).strip(), m.group(2).split("#")[0].strip()
            if not rel or "://" in rel:
                continue
            p = (a.index.parent / rel).resolve()
            try:
                inside = p.is_relative_to(a.shard_dir.resolve())
            except AttributeError:                          # python < 3.9
                inside = str(p).startswith(str(a.shard_dir.resolve()))
            if inside:
                linked[name] = (p, i)

    if not linked:
        print(f"check-index: {a.index} links to nothing inside {a.shard_dir} — "
              f"either the wrong pair, or --link-re does not match this index",
              file=sys.stderr)
        return 2

    # ── 1 · every linked shard exists ───────────────────────────────────────
    for name, (p, ln) in sorted(linked.items()):
        if not p.is_file():
            bad.append(f"{a.index}:{ln}  index links {name!r} to {p}, which does not exist")

    # ── 2 · every shard is linked ───────────────────────────────────────────
    # The index may legitimately live inside the shard directory. Reporting it
    # as a shard nobody links is noise, and noise is how a checker gets ignored.
    on_disk = {p.resolve() for p in sorted(a.shard_dir.glob(a.glob))
               if p.resolve() != a.index.resolve()}
    referenced = {p for p, _ in linked.values()}
    for p in sorted(on_disk - referenced):
        bad.append(f"{p}  exists but the index never links it — a shard nobody "
                   f"can reach is a shard nobody reads")

    # ── 3 · the index's name appears verbatim as a heading in the shard ─────
    for name, (p, ln) in sorted(linked.items()):
        if not p.is_file():
            continue
        heads = [h.strip() for h in
                 re.findall(r"^#{1,6}\s+(.+?)\s*$", p.read_text(errors="replace"), re.M)]
        checked += 1
        if name not in heads:
            near = next((h for h in heads if name.lower() in h.lower()
                         or h.lower() in name.lower()), None)
            bad.append(f"{a.index}:{ln}  index calls it {name!r}; "
                       + (f"{p.name} says {near!r}" if near
                          else f"{p.name} has no heading of that name")
                       + ". A consumer keying on the pair breaks on whichever side "
                         "was tidied.")

    # ── 4 · stated counts match ─────────────────────────────────────────────
    if count_re:
        stated = {}
        for i, line in enumerate(lines, 1):
            m = count_re.search(line)
            if m:
                try:
                    stated[m.group(1).strip()] = (int(m.group(2)), i)
                except (IndexError, ValueError):
                    bad.append(f"{a.index}:{i}  --count-re matched but did not capture "
                               f"(name, integer)")
        for name, (n, ln) in sorted(stated.items()):
            if name not in linked:
                bad.append(f"{a.index}:{ln}  a count is stated for {name!r}, which the "
                           f"index links nowhere")
                continue
            p = linked[name][0]
            if not p.is_file():
                continue
            got = len(entry.findall(p.read_text(errors="replace")))
            if got != n:
                bad.append(f"{a.index}:{ln}  index says {name!r} holds {n} entries; "
                           f"{p.name} holds {got}")

    if bad:
        print(f"DRIFT — {a.index} and {a.shard_dir} disagree:\n")
        for b in bad:
            print(f"  · {b}")
        print("\nFix the surface that is wrong, not the check. Two places holding one "
              "fact\nis one fact that will eventually be two different facts.")
        return 1

    print(f"index agrees with its shards — {len(linked)} linked, {checked} heading(s) "
          f"matched verbatim" + (", counts checked" if count_re else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
