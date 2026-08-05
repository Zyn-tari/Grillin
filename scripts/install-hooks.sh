#!/usr/bin/env bash
# Point git at the versioned hooks in .githooks/.
#
# .git/hooks is not versioned, so a hook that lives there is a hook only the
# person who wrote it has. core.hooksPath moves the whole directory into the
# repository, where it is reviewable, diffable and shared.
set -euo pipefail

REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"

git config core.hooksPath .githooks
chmod +x .githooks/* 2>/dev/null || true

echo "grillin: hooks installed."
echo "  core.hooksPath = $(git config core.hooksPath)"
echo
echo "Every commit now runs:"
echo "  · the calibration — known-good fixture must pass, known-bad must fail"
echo "  · the full gate on any plan directory the commit touches"
echo
echo "To bypass once, on the record: GRILLIN_SKIP=1 git commit ..."
echo "Skips are appended to .git/grillin-skips.log — a skip nobody can see is"
echo "indistinguishable from a pass."
