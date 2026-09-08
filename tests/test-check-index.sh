#!/usr/bin/env bash
# check-index.py must fire on each of its four defects and stay silent on a
# correct pair. A checker that only ever passes is a checker nobody can trust.
#
# The fixture is the shape that produced it: a changelog split into an index
# plus per-wave shards, 2,062 lines into 131 + 22 files.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHK="$ROOT/scripts/check-index.py"
LAB="${TMPDIR:-/tmp}/grillin-index.$$"
pass=0; fail=0
ok()  { pass=$((pass+1)); printf '  \033[32mPASS\033[0m  %s\n' "$1"; }
bad() { fail=$((fail+1)); printf '  \033[31mFAIL\033[0m  %s — %s\n' "$1" "$2"; }

build() {
  rm -rf "$LAB"; mkdir -p "$LAB/CHANGELOG"
  cat > "$LAB/CHANGELOG.md" <<'IDX'
# Changelog — index

The wave headings below are load-bearing: the status hook keys on them.

- [W0](CHANGELOG/W0.md) — 2 entries
- [W1](CHANGELOG/W1.md) — 3 entries
IDX
  printf '## W0\n\n- first thing\n- second thing\n' > "$LAB/CHANGELOG/W0.md"
  printf '## W1\n\n- a\n- b\n- c\n' > "$LAB/CHANGELOG/W1.md"
}

run() { python3 "$CHK" "$LAB/CHANGELOG.md" "$LAB/CHANGELOG" \
          --count-re '\[(W[0-9]+)\][^—]*— ([0-9]+) entries' "$@" 2>&1; }

echo "check-index — an index and its shards must agree"
echo

build
out="$(run)"; rc=$?
[ "$rc" -eq 0 ] && ok "a correct pair is silent" || bad "a correct pair is silent" "$out"

build; rm "$LAB/CHANGELOG/W1.md"
out="$(run)"; rc=$?
[ "$rc" -eq 1 ] && ok "1 · a linked shard that does not exist" || bad "1 · missing shard" "rc=$rc"

build; printf '## W2\n\n- orphan\n' > "$LAB/CHANGELOG/W2.md"
out="$(run)"
case "$out" in *"never links it"*) ok "2 · a shard nobody links" ;;
  *) bad "2 · orphan shard" "not reported" ;; esac

build; sed -i 's|^## W1$|## W1 — the interesting one|' "$LAB/CHANGELOG/W1.md"
out="$(run)"
case "$out" in *"index calls it 'W1'"*) ok "3 · a heading tidied on one side only" ;;
  *) bad "3 · heading drift" "not reported: $out" ;; esac

build; printf -- '- d\n' >> "$LAB/CHANGELOG/W1.md"
out="$(run)"
case "$out" in *"holds 3 entries"*|*"holds 4"*) ok "4 · a stated count that no longer holds" ;;
  *) bad "4 · count drift" "not reported: $out" ;; esac

# The heading check is the one their operator asked for, and it must be VERBATIM
# rather than fuzzy — a near-match is exactly the case that breaks a consumer.
build; sed -i 's|^## W0$|## w0|' "$LAB/CHANGELOG/W0.md"
out="$(run)"
case "$out" in *"index calls it 'W0'"*) ok "3b · case is not close enough" ;;
  *) bad "3b · case-only drift" "not reported" ;; esac

# An index that links nothing into the given directory is the wrong pair, or a
# --link-re that does not match this index. Either way it must say so rather
# than report a clean bill on zero comparisons.
build; mkdir -p "$LAB/elsewhere"
out="$(python3 "$CHK" "$LAB/CHANGELOG.md" "$LAB/elsewhere" 2>&1)"; rc=$?
[ "$rc" -eq 2 ] && ok "links nothing into the target dir -> exit 2, not 0" \
                || bad "wrong pair" "rc=$rc"

# The index living inside its own shard directory is legitimate, not an orphan.
build; mv "$LAB/CHANGELOG.md" "$LAB/CHANGELOG/index.md"
sed -i 's|CHANGELOG/W|W|g' "$LAB/CHANGELOG/index.md"
out="$(python3 "$CHK" "$LAB/CHANGELOG/index.md" "$LAB/CHANGELOG" \
        --count-re '\[(W[0-9]+)\][^—]*— ([0-9]+) entries' 2>&1)"; rc=$?
[ "$rc" -eq 0 ] && ok "an index inside its own shard dir is not an orphan" \
                || bad "index-as-orphan" "$out"

# ── the three behaviours added after this tool met a plan-of-plans ─────────
# An index that links tracks as files and shared material as DIRECTORIES, and
# names each shard by the very path it links. All three fixes exist because the
# first real run against such an index reported a correct program as drifted.

build; mkdir -p "$LAB/CHANGELOG/_shared"
printf -- '- [_shared](CHANGELOG/_shared/) — a directory, not a file\n' >> "$LAB/CHANGELOG.md"
out="$(run)"; rc=$?
case "$out" in *"_shared"*"does not exist"*) bad "5 · a linked directory is not missing" "reported present dir as absent" ;;
  *) ok "5 · a linked directory counts as existing" ;; esac

build; rm -rf "$LAB/CHANGELOG/_shared"
printf -- '- [CHANGELOG/nope/](CHANGELOG/nope/) — absent directory\n' >> "$LAB/CHANGELOG.md"
out="$(run)"
case "$out" in *"does not exist"*) ok "5b · ...but an ABSENT directory still fires" ;;
  *) bad "5b · absent directory" "not reported — the fix went too far" ;; esac

# 6 · a name that IS the path cannot drift from a heading, so check 3 must not
#     fire on it. The control below proves check 3 is still alive for labels.
build; sed -i 's|^- \[W1\](CHANGELOG/W1.md)|- [CHANGELOG/W1.md](CHANGELOG/W1.md)|' "$LAB/CHANGELOG.md"
sed -i 's|^## W1$|## W1 — retitled freely|' "$LAB/CHANGELOG/W1.md"
out="$(run --count-re 'ZZZ_NO_MATCH_ZZZ')"
case "$out" in *"index calls it"*) bad "6 · a path-name skips the heading check" "still fired" ;;
  *) ok "6 · a path-name skips the heading check" ;; esac

build; sed -i 's|^## W1$|## W1 — retitled freely|' "$LAB/CHANGELOG/W1.md"
out="$(run)"
case "$out" in *"index calls it 'W1'"*) ok "6b · control · a LABEL still gets the heading check" ;;
  *) bad "6b · label heading check" "check 3 is now dead" ;; esac

# 7 · a wrong --entry-re yields a precise, plausible, wrong number. It cannot be
#     detected, so the finding must show what it counted.
build
out="$(run --entry-re '^#')"
case "$out" in *"--entry-re matched"*) ok "7 · a count mismatch shows what it counted" ;;
  *) bad "7 · count diagnostics" "no sample in the message" ;; esac

build
out="$(run --entry-re 'ZZZ_NEVER_MATCHES')"
case "$out" in *"Zero matches usually means the wrong --entry-re"*) ok "7b · zero matches names the likely cause" ;;
  *) bad "7b · zero-match hint" "not shown" ;; esac

# 8 · the gating relation. A plan of plans has edges between its MEMBERS, and a
#     cycle there does not fail — the runner dispatches nothing and looks idle,
#     which is indistinguishable from work in progress. Same check as the gate's
#     `check_graph`, one level up.
GATES='^- \[(W[0-9]+)\][^|]*\| blocked by: ([^|]*)\|'
gplan() {   # $1 = W0's blockers, $2 = W1's
  rm -rf "$LAB"; mkdir -p "$LAB/CHANGELOG"
  {
    echo "# Program"; echo
    echo "- [W0](CHANGELOG/W0.md) — 2 entries | blocked by: $1 |"
    echo "- [W1](CHANGELOG/W1.md) — 3 entries | blocked by: $2 |"
  } > "$LAB/CHANGELOG.md"
  printf '## W0\n\n- first thing\n- second thing\n' > "$LAB/CHANGELOG/W0.md"
  printf '## W1\n\n- a\n- b\n- c\n' > "$LAB/CHANGELOG/W1.md"
}

gplan "—" "W0"; out="$(run --gates-re "$GATES")"; rc=$?
case "$rc$out" in 0*) ok "8 · CONTROL · a well-formed gating relation passes" ;;
  *) bad "8 · clean gating" "rc=$rc :: $out" ;; esac

gplan "—" "W9"; out="$(run --gates-re "$GATES")"
case "$out" in *"links nowhere"*) ok "8b · a blocker naming no shard is caught" ;;
  *) bad "8b · dangling blocker" "not reported — the edge would silently stop gating" ;; esac

gplan "W0" "—"; out="$(run --gates-re "$GATES")"
n=$(printf '%s' "$out" | grep -c '^  ·')
case "$out" in *"blocked by itself"*) ok "8c · a self-gate is caught" ;;
  *) bad "8c · self-gate" "not reported" ;; esac
case "$n" in 1) ok "8d · ...and yields ONE finding, not a self-gate plus a cycle" ;;
  *) bad "8d · one defect one finding" "got $n findings" ;; esac

gplan "W1" "W0"; out="$(run --gates-re "$GATES")"
case "$out" in *"gating cycle: "*"→"*) ok "8e · a cycle is caught and its PATH is printed" ;;
  *) bad "8e · cycle path" "no path in the message" ;; esac

# 8f · CONTROL · the whole check is opt-in. Without --gates-re nothing about
#      gating is read, so an index that states no relation cannot fail on one.
gplan "W1" "W0"; out="$(run)"; rc=$?
case "$out" in *"gating"*) bad "8f · gating is opt-in" "fired without --gates-re" ;;
  *) ok "8f · CONTROL · no --gates-re, no gating findings" ;; esac

echo
echo "  $pass passed, $fail failed"
rm -rf "$LAB"
[ "$fail" -eq 0 ]
