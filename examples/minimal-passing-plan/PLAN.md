# Minimal passing plan — the gate's own fixture

This is the smallest plan that passes `validate-plan.py --run-gates` cleanly, and it exists so the
gate can be proven against a known answer before anyone trusts it on their work. Its counterpart,
[`../a-real-first-plan`](../a-real-first-plan), is a real plan that fails with 30+ findings. One of
each is the minimum needed to tell a working validator from a broken one.

**It is a fixture, not a specimen.** Do not copy it as a model plan — it has four tasks that do
nothing, and its whole purpose is to exercise every check exactly once.

## The five shaping answers

| | Question | Answer |
|---|---|---|
| 1 | Does the thing already exist in a form we can inspect? | Yes — this repository. |
| 2 | Will more than one worker act at the same time? | No. Phase 5 skipped. |
| 3 | Are the workers AI agents? | Yes. |
| 4 | Does "done" produce something that runs or deploys? | No. Every gate is a `test -f`. |
| 5 | Is any step hard to undo? | No. |

## Tasks

| ID | Task | Owner | Blocked by |
|---|---|---|---|
| T1 | Write the inventory | worker-a | — |
| T2 | Write the findings | worker-b | T1 |
| T3 | Write the summary | worker-a | T2 |
| T4 | Attack all of it | reviewer | T3 |

T4 is the adversarial pass. Its owner appears nowhere else in this table, which is the point:
an adversary that also produced some of the work is judging itself.
