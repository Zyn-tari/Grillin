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

echo
echo "  $pass passed, $fail failed"
rm -rf "$LAB"
[ "$fail" -eq 0 ]
