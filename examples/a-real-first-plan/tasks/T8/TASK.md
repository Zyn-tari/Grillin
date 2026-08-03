# T8 — Flip it public and cut a release

**Type:** BUILD
**Status:** NOT STARTED — **HARD BLOCKED on T1/Q4**
**Blocked by:** T7 (all checks), T1 Q4 (disclosure clearance) · **Blocks:** —
**Owner:** the repo author. **Hand-off — I have no credentials for this and would not use them.**

## Why this exists

Everything upstream makes the repo followable. This makes it reachable. Separating them is
deliberate: publishing is the only irreversible step in the plan, and it is the one where the
non-technical blocker lives.

## Steps

1. Confirm `tasks/T1/DECISIONS.md` Q4 is answered **and permissive**. `CASE-STUDY.md` publishes a
   third party's live web app app: ~24 routed pages, 72 API routes, ~30 endpoints specified
   and never built, three documents disagreeing about a shared configuration constant, a root-owned unreadable
   deploy script, five prior rounds of defect work. If Q4 is not cleared, **stop here** — the fix
   is to anonymise `CASE-STUDY.md`, which is a new task, not an adjustment to this one.
2. Confirm every check in `tasks/T7/TASK.md` "Done means" passed, including the two cold readers.
3. Scan the git *history*, not just the working tree, for anything the working tree no longer
   shows. Eleven commits; this is a five-minute read. A public repo publishes every commit.
4. `gh repo edit --visibility public` (or the web UI).
5. Tag `v1.1.0` and write release notes as a **diff against the private version**: quickstart
   added, worked example added, scaling sources reconciled, evidence vocabulary unified, scope
   claim corrected. Someone who saw the private version should be able to tell what changed.
6. Verify from outside: log out, open the URL in a private window, click every link in the
   rendered README on github.com. Relative markdown links behave differently rendered than they
   do locally — this is the phase-9 check applied to the published artefact.
7. Set the repo description and topics. The description is the second thing a stranger reads,
   after the name, and neither of them explains what Grillin' is.

## Loop

None. One irreversible action, gated on evidence gathered elsewhere.

## Done means

A logged-out browser, from a machine that has never authenticated to this account, loads the repo,
follows `QUICKSTART.md`, and reaches the worked example without a 404. Evidence: a screenshot or a
transcript in this folder, taken while logged out.

## Do NOT

- Do NOT publish before Q4 is answered. Public is not reversible — forks and caches persist.
- Do NOT publish on green checks alone if either cold reader stalled. `_RULES.md.template:130` —
  "Never ship on green gates alone."
- Do NOT announce anywhere. That was not in the ask and is not in this plan. If it should be, it
  is a new task (`02-TRIAGE.md`, "what I still need").

## Outputs

`CHANGES.md`, release notes, the logged-out verification transcript.
