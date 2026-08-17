#!/usr/bin/env bash
# A plan of PEOPLE must pass the gate.
#
# QUICKSTART §0b question 3 says that when the workers are not agents you ignore
# templates/ and "everything else still works". Everything else did not still
# work: the model floor failed every task twice, --config could not lower it
# (self_check refuses), and three first-time users hit it independently. Two of
# them stopped running the gate at all — which is the expensive failure, because
# a gate that is wrong about a case people really have gets discarded whole.
#
# Both directions are asserted. A test that only proves the exemption works
# would still pass if the floor had simply been deleted.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
V="$ROOT/scripts/validate-plan.py"
LAB="${TMPDIR:-/tmp}/grillin-human.$$"
pass=0; fail=0
ok()  { pass=$((pass+1)); printf '  \033[32mPASS\033[0m  %s\n' "$1"; }
bad() { fail=$((fail+1)); printf '  \033[31mFAIL\033[0m  %s — %s\n' "$1" "$2"; }

# A plan of people: no Model, no Effort, no roster — and it says so at the top.
mkhuman() {
  # mkdir -p the PARENT, not the target: a missing lab directory made cp fail
  # silently and the first assertion passed on a plan that did not exist. A
  # green check on an absent subject is the failure this whole file is about.
  rm -rf "$1"; mkdir -p "$(dirname "$1")"
  cp -r "$ROOT/examples/minimal-passing-plan" "$1"
  rm -f "$1/tasks/_ROSTER.md"
  sed -i '/^\*\*Agent:\*\*/d;/^\*\*Model:\*\*/d;/^\*\*Effort:\*\*/d' "$1"/tasks/*/TASK.md
  sed -i 's|\[`../a-real-first-plan`\](../a-real-first-plan)|the failing example|' "$1/PLAN.md"
}

echo "a plan of people"
echo

# ── 1 · declared human: the floor does not apply ────────────────────────────
P="$LAB/declared"; mkhuman "$P"
sed -i '0,/^$/s//\n**Workers:** human\n/' "$P/PLAN.md"
out="$("$V" "$P" 2>&1)"
if grep -q "^FAIL — persona-model" <<<"$out"; then
  bad "a declared human plan does not fail the model floor" "it still fired"
else ok "a declared human plan does not fail the model floor"; fi
grep -q "^PASS — persona-model.*human workers" <<<"$out" \
  && ok "...and says why, rather than staying silent" \
  || bad "...and says why" "no explanatory PASS line"

# ── 2 · the control: undeclared, the floor still bites ──────────────────────
# Without this the exemption could be "the check was deleted" and §1 would not
# notice. OPERATING-THE-PLAN §5: prove the instrument against a known answer.
P="$LAB/undeclared"; mkhuman "$P"
# Capture first, then grep. Under `set -o pipefail` the validator's own exit 1
# becomes the pipeline's status even when grep matched, so `if validate | grep`
# reads the wrong answer and reports a live check as dead.
out="$("$V" "$P" 2>&1)"
if grep -q "^FAIL — persona-model" <<<"$out"; then
  ok "an UNdeclared plan missing models still fails — the floor is intact"
else
  bad "an undeclared plan still fails" "the floor is gone, not exempted"
fi

# ── 3 · the trade, not a loophole ───────────────────────────────────────────
# Declaring human buys an exemption and costs an obligation. If the frozen
# contract check stopped applying too, "human" would be the cheap way out.
P="$LAB/handed"; mkhuman "$P"
sed -i '0,/^$/s//\n**Workers:** human\n/' "$P/PLAN.md"
sed -i 's/^\*\*Status:\*\* NOT STARTED/**Status:** IN PROGRESS/' "$P/tasks/T1/TASK.md"
sed -i 's/^\*\*Owner:\*\* .*/**Owner:** human/' "$P/tasks/T1/TASK.md"
out="$("$V" "$P" 2>&1)"
if grep -q "^FAIL — frozen-contract" <<<"$out"; then
  ok "a handed-out human task still owes a frozen contract"
else
  bad "a handed-out human task still owes a frozen contract" "the obligation vanished too"
fi

# ── 3b · "Owner: you" is not a person when an agent is named ────────────────
# The shipped examples say `**Owner:** you` and also name a persona and a model:
# it means "you are driving this plan", not "a person executes this task". The
# first version of the exemption matched on the owner wording alone, so those
# examples went exempt and their models stopped being checked — the gate printed
# PASS for the right check for the wrong reason. Caught by reading the hook's
# own output on the way to a commit, not by any assertion here at the time.
P="$LAB/youbutagent"; mkhuman "$P"
sed -i "0,/^\*\*Status:/s//**Agent:** \`implementer\` · **Model:** \`claude-sonnet-5\` · **Effort:** high\n**Status:/" "$P/tasks/T1/TASK.md"
sed -i 's/^\*\*Owner:\*\* .*/**Owner:** you/' "$P/tasks/T1/TASK.md"
out="$("$V" "$P" 2>&1)"
if grep -q "human-owned task(s) exempt" <<<"$out"; then
  bad "'Owner: you' plus a named agent is NOT an exemption" "it was exempted anyway"
else
  ok "'Owner: you' plus a named agent is NOT an exemption"
fi

# ── 4 · an agent plan is untouched ──────────────────────────────────────────
if "$V" "$ROOT/examples/minimal-passing-plan" --run-gates >/dev/null 2>&1; then
  ok "the agent-fleet fixture is unaffected"
else
  bad "the agent-fleet fixture is unaffected" "it regressed"
fi

echo
echo "  $pass passed, $fail failed"
rm -rf "$LAB"
[ "$fail" -eq 0 ]
