#!/usr/bin/env bash
# The pre-commit hook must gate a plan that sits at the REPOSITORY ROOT.
#
# Reported 2026-08-13 by an agent setting up `fred-plans`. The hook walked up
# from each changed file looking for a directory containing tasks/*/TASK.md,
# and the walk was written:
#
#     while [ "$d" != "$REPO" ] && [ "$d" != "/" ]; do
#
# so it stopped BEFORE testing $REPO itself. For a plan whose directory IS the
# repository root, `plans` stayed empty, `[ -n "$plans" ] || exit 0` returned 0,
# and the commit was accepted. Running the gate by hand on the same tree
# reported 6 findings and RESULT: FAIL.
#
# This is the exact failure this method exists to prevent — a gate that is
# installed, reports success, and checks nothing. It is worse than an
# uninstalled gate, because the green is load-bearing.
#
# The existing suite could not have caught it: every fixture nests the plan
# below the root, which is the one arrangement the walk covered.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAB="${TMPDIR:-/tmp}/grillin-hook.$$"
pass=0; fail=0
ok()  { pass=$((pass+1)); printf '  \033[32mPASS\033[0m  %s\n' "$1"; }
bad() { fail=$((fail+1)); printf '  \033[31mFAIL\033[0m  %s — %s\n' "$1" "$2"; }

# A global hooksPath change would follow the developer out of this test and into
# their real work. It has happened once. Assert it does not happen again.
GLOBAL_BEFORE="$(git config --global --get core.hooksPath 2>/dev/null || echo NONE)"

newrepo() { # $1 = repo dir, $2 = where the plan lives, relative ("" = the root)
  rm -rf "$1"; mkdir -p "$1"; ( cd "$1" && git init -q && git config user.email t@t && git config user.name t )
  local p="$1${2:+/$2}"
  mkdir -p "$p/tasks/T1"
  # Knowingly malformed: no Owner, no Status, and a done-criterion that is prose.
  { echo "# T1 — a task nobody can dispatch"; echo
    echo "## What you own"; echo "everything"; echo
    echo "## Done means"; echo "it feels finished"; echo
    echo "## Do NOT"; echo "- Do NOT stray."
  } > "$p/tasks/T1/TASK.md"
  printf '# plan\n\n**Size:** XS\n' > "$p/PLAN.md"
}

echo "Grillin — the hook gates a plan wherever it sits"
echo

for where in "" "plans/probe"; do
  label="${where:-the repository root}"
  P="$LAB/$(echo "${where:-root}" | tr / -)"
  newrepo "$P" "$where"
  ( cd "$P" && GRILLIN_BIN="$ROOT/scripts/validate-plan.py" \
      bash "$ROOT/install-hooks.sh" >/dev/null 2>&1 )

  # The gate, run by hand, must reject this tree — otherwise the fixture is
  # wrong and the test below would pass for the wrong reason.
  "$ROOT/scripts/validate-plan.py" "$P${where:+/$where}" --run-gates >/dev/null 2>&1
  [ "$?" -ne 0 ] && ok "by hand: the gate rejects the malformed plan at $label" \
                 || bad "by hand: the gate rejects the malformed plan at $label" "it passed"

  out="$( cd "$P" && git add -A && git commit -m "malformed" 2>&1 )"; rc=$?
  if [ "$rc" -ne 0 ]; then
    ok "commit REFUSED at $label"
  else
    bad "commit accepted at $label" "the hook checked nothing and exited 0"
  fi
  case "$out" in
    *"grillin: gating"*) ok "...and the hook said which plan it gated" ;;
    *) bad "...the hook named no plan at $label" "it never found one" ;;
  esac
done

GLOBAL_AFTER="$(git config --global --get core.hooksPath 2>/dev/null || echo NONE)"
[ "$GLOBAL_BEFORE" = "$GLOBAL_AFTER" ] \
  && ok "global core.hooksPath untouched" \
  || bad "global core.hooksPath changed" "$GLOBAL_BEFORE -> $GLOBAL_AFTER"

echo
echo "  $pass passed, $fail failed"
rm -rf "$LAB"
[ "$fail" -eq 0 ]
