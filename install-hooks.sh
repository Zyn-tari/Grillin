#!/usr/bin/env sh
# Make the gate run on every commit, in ANY repository that holds plans.
#
#   curl -fsSL https://raw.githubusercontent.com/A-Pex97/grillin/main/install-hooks.sh | sh
#
# A gate nobody runs is documentation with an exit code. This is what turns
# "enforceable" into "enforced", and the difference is the whole distinction
# between a mechanism and a preference.
#
# ── WHICH REPO ─────────────────────────────────────────────────────────────
# Run it from inside the repo that HOLDS YOUR PLANS. That is usually not the
# repo you are planning changes to, and it must never be the same one.
#
#   Grillin runs ON a plan, from outside it. Put the gate on your PATH; never
#   put it in the build, the CI, or the commit path of the project you are
#   planning changes to — that project must be able to build, test and ship
#   with Grillin uninstalled.
#
# The test is one line: if removing Grillin breaks someone's build, it was
# installed in the wrong place.
#
# This warning exists because an earlier version of this file said "it works in
# Grillin's own repo and in yours", and further down told you to commit
# .githooks/ so everyone gets it. A competent agent read both, correctly
# declined to run this script because core.hooksPath would have clobbered the
# project's existing pre-commit hook, and then hand-built the same integration
# safely — a plan gate in the application's commit path. It was not misreading
# anything. Every caveat in this repository pointed at the prose; the one
# artefact that can reach into a user's project carried none.
set -eu

say() { printf '%s\n' "$*"; }
die() { printf 'grillin: %s\n' "$*" >&2; exit 1; }

command -v git >/dev/null 2>&1 || die "git not found"
REPO=$(git rev-parse --show-toplevel 2>/dev/null) || die "not inside a git repository"
cd "$REPO"

GATE="${GRILLIN_BIN:-}"
if [ -z "$GATE" ]; then
  if [ -x "$REPO/scripts/validate-plan.py" ]; then GATE="$REPO/scripts/validate-plan.py"
  elif command -v grillin >/dev/null 2>&1; then GATE="$(command -v grillin)"
  else
    die "no gate found. Install it first:
    curl -fsSL https://raw.githubusercontent.com/A-Pex97/grillin/main/install.sh | sh"
  fi
fi

mkdir -p .githooks

# If this repo ships its own hook — Grillin does — do not overwrite it.
if [ -f .githooks/pre-commit ] && grep -q "Grillin pre-commit gate" .githooks/pre-commit 2>/dev/null; then
  say "grillin: this repo already ships .githooks/pre-commit — keeping it"
else
  cat > .githooks/pre-commit <<HOOK
#!/usr/bin/env bash
# Installed by grillin install-hooks.sh. Gates every plan directory this commit
# touches. A plan directory is one containing tasks/<ID>/TASK.md.
#
# Skip once, on the record:  GRILLIN_SKIP=1 git commit ...
set -uo pipefail
REPO="\$(git rev-parse --show-toplevel)"
GATE="\${GRILLIN_BIN:-$GATE}"

if [ "\${GRILLIN_SKIP:-}" = "1" ]; then
  echo "grillin: GATE SKIPPED by GRILLIN_SKIP=1 — this commit was not validated." >&2
  printf '%s  gate skipped\n' "\$(date -u +%FT%TZ)" >> "\$REPO/.git/grillin-skips.log"
  exit 0
fi
command -v "\$GATE" >/dev/null 2>&1 || [ -x "\$GATE" ] || {
  echo "grillin: gate not found at \$GATE — refusing to pass silently" >&2; exit 1; }

plans=""
while IFS= read -r f; do
  d="\$REPO/\$f"
  while [ "\$d" != "\$REPO" ] && [ "\$d" != "/" ]; do
    if compgen -G "\$d/tasks/*/TASK.md" > /dev/null 2>&1; then
      case " \$plans " in *" \$d "*) ;; *) plans="\$plans \$d" ;; esac
      break
    fi
    d="\$(dirname "\$d")"
  done
done < <(git diff --cached --name-only --diff-filter=ACMR)

[ -n "\$plans" ] || exit 0

fail=0
for p in \$plans; do
  echo "grillin: gating \${p#\$REPO/}"
  "\$GATE" "\$p" --run-gates || fail=1
done

if [ "\$fail" -ne 0 ]; then
  cat >&2 <<'MSG'

grillin: commit refused. A green gate means the plan is OPERABLE, not correct —
so this is the low bar and it was not cleared.

  To commit anyway, deliberately and on the record:
      GRILLIN_SKIP=1 git commit ...
MSG
  exit 1
fi
exit 0
HOOK
  say "grillin: wrote .githooks/pre-commit"
fi

chmod +x .githooks/* 2>/dev/null || true
git config core.hooksPath .githooks

say ""
say "grillin: hooks installed in $(basename "$REPO")"
say "  core.hooksPath = $(git config core.hooksPath)"
say "  gate           = $GATE"
say ""
say "  .git/hooks is not versioned, so core.hooksPath is what makes this shared"
say "  rather than personal. Commit .githooks/ if this repo holds plans."
say ""
say "  BUT NOT IF THIS IS THE PROJECT YOU ARE PLANNING CHANGES TO. Grillin runs"
say "  ON a plan, from outside it. A product repo must build, test and ship with"
say "  Grillin uninstalled — so its commit path, CI and build must never depend"
say "  on this. If removing Grillin would break someone's build, it is in the"
say "  wrong repository. Move the plans out and run the gate from there."
say ""
say "  Bypass once: GRILLIN_SKIP=1 git commit ...   (appended to .git/grillin-skips.log —"
say "  a skip nobody can see is indistinguishable from a pass.)"
