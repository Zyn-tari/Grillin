#!/usr/bin/env sh
# Grillin installer.
#
#   curl -fsSL https://raw.githubusercontent.com/Zyn-tari/Grillin/main/install.sh | sh
#
# Installs `grillin` — the gate — onto your PATH, and nothing else. The method
# is prose you read in a browser; the only thing worth installing is the part
# that runs.
#
# POSIX sh on purpose: this is the one file that must work before anything is
# installed, on a machine you have not seen. No bashisms, no dependencies
# beyond curl-or-wget, and python3 which the gate itself needs anyway.
set -eu

REPO="${GRILLIN_REPO:-Zyn-tari/Grillin}"
REF="${GRILLIN_REF:-main}"
RAW="https://raw.githubusercontent.com/$REPO/$REF"
PREFIX="${GRILLIN_PREFIX:-$HOME/.local/bin}"

say()  { printf '%s\n' "$*"; }
die()  { printf 'grillin: %s\n' "$*" >&2; exit 1; }

fetch() { # url -> stdout
  if command -v curl >/dev/null 2>&1; then curl -fsSL "$1"
  elif command -v wget >/dev/null 2>&1; then wget -qO- "$1"
  else die "need curl or wget"; fi
}

# ── preflight ───────────────────────────────────────────────────────────────
command -v python3 >/dev/null 2>&1 || die "python3 is required (stdlib only, no packages)"
PYV=$(python3 -c 'import sys;print("%d.%d"%sys.version_info[:2])' 2>/dev/null || echo 0.0)
case "$PYV" in
  3.*) ;;
  *) die "python3 not usable (reported version '$PYV')" ;;
esac

mkdir -p "$PREFIX" || die "cannot create $PREFIX"

# ── install ─────────────────────────────────────────────────────────────────
TMP=$(mktemp -d 2>/dev/null || mktemp -d -t grillin)
trap 'rm -rf "$TMP"' EXIT INT HUP TERM

say "grillin: fetching the gate from $REPO@$REF"
fetch "$RAW/scripts/validate-plan.py" > "$TMP/grillin" || die "download failed"
# check-drift.py is NOT installed. Its own header says "FOR THIS REPOSITORY
# ONLY" — its surfaces are hardcoded to Grillin's own files, so on your machine
# it can only ever mislead you. check-index.py is the one that works on your
# files, and it lives in the repo for you to copy deliberately.

# Prove it runs BEFORE it is on the PATH. An installer that puts a broken file
# somewhere permanent and reports success is the exact failure this project is
# about — and a truncated download is a real thing, not a hypothetical.
python3 -c "import ast,sys;ast.parse(open(sys.argv[1]).read())" "$TMP/grillin" \
  || die "the downloaded gate does not parse — refusing to install a broken file"

# Stamp what was actually fetched. A copied file has no git context, so without
# this `grillin --version` can only say "source checkout" — and a user who
# cannot tell you which ref they are on is a bug report you cannot act on.
STAMP="$REF"
[ "$REF" = "main" ] && STAMP="main, $(date -u +%Y-%m-%d)"
sed -i.bak "s|^INSTALLED_FROM = .*|INSTALLED_FROM = \"$STAMP\"  # stamped by install.sh|" "$TMP/grillin" 2>/dev/null \
  || sed "s|^INSTALLED_FROM = .*|INSTALLED_FROM = \"$STAMP\"  # stamped by install.sh|" "$TMP/grillin" > "$TMP/g2" && mv "$TMP/g2" "$TMP/grillin"
rm -f "$TMP/grillin.bak"

chmod +x "$TMP/grillin"
"$TMP/grillin" --help >/dev/null 2>&1 || die "the downloaded gate will not run"

mv "$TMP/grillin" "$PREFIX/grillin"

# ── verify, then say so ─────────────────────────────────────────────────────
VER_OK=no
if "$PREFIX/grillin" --help 2>&1 | grep -q "run-gates"; then VER_OK=yes; fi
[ "$VER_OK" = yes ] || die "installed, but it does not behave like the gate — remove $PREFIX/grillin"

say ""
say "grillin installed -> $PREFIX/grillin"

case ":${PATH}:" in
  *":$PREFIX:"*) ;;
  *)
    say ""
    say "  $PREFIX is NOT on your PATH. Add it:"
    say "      echo 'export PATH=\"$PREFIX:\$PATH\"' >> ~/.profile && . ~/.profile"
    ;;
esac

cat <<'EOF'

Use it:

    grillin <plan-dir> --run-gates

  Exit 0 = the plan is operable.  1 = it is not.  2 = INCOMPLETE, because
  without --run-gates nothing proved a single gate would fail on unstarted work.

  A green gate means OPERABLE, not correct. On the one job measured end to end
  the gate caught 2 defects and the readers caught 50 — so run it, and then
  have somebody who did not write the plan try to break it.

Run it on every commit, in THE REPO THAT HOLDS YOUR PLANS:

    curl -fsSL https://raw.githubusercontent.com/Zyn-tari/Grillin/main/install-hooks.sh \
      -o grillin-hooks.sh && sh grillin-hooks.sh

  Not the project you are planning changes to. Grillin runs ON a plan, from
  outside it — that project must build, test and ship with Grillin uninstalled.
  If removing Grillin would break someone's build, it is in the wrong repo.

The method itself is prose and needs nothing installed:

    https://github.com/Zyn-tari/Grillin
EOF
