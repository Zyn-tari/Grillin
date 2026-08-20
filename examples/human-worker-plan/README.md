# A plan worked by people

Grillin's default assumption is a fleet of agents. This is the other case: a real job, done by
three people with names, planned and gated the same way. It is here because the declaration
that makes it work — `**Workers:** human` — appeared in no shipped plan, and the people who
needed it had to reconstruct it from a test file.

## The trade, in one paragraph

Declaring human workers **buys** you an exemption from the model floor: no task names an
**Agent**, a **Model** or an **Effort**, because a person has none of the three, and you do not
need a `tasks/_ROSTER.md` either — a roster is where a persona's price and the reason for it
are recorded, and a person is not a persona. It **costs** you a freeze: the moment a
human-owned task is handed over, its contract is fixed at a hash, and changing the wording
afterwards fails the gate until you restore it or record an amendment and re-deliver. That is
what stops `human` being the cheap way around the floor — you are not exempted from being
pinned down, you are pinned down somewhere else.

| | Agents | People |
|---|---|---|
| `**Agent:** / **Model:** / **Effort:**` on every task | required, effort at or above `high` | **absent** — nobody has a model |
| `tasks/_ROSTER.md` | needed, and the task must match it | **not needed** |
| Contract may be edited after hand-over | yes, the agent re-reads the directory | **no — frozen at a hash** |
| Owner, status, dependency graph, links | required | required, unchanged |
| Done-command that is real and fails first | required | required, unchanged |

## Where the declaration goes — and why you write it twice

**In [`PLAN.md`](PLAN.md), at the top:**

```
**Workers:** human — three named people. Nobody in this plan has a model or an effort.
```

That line is shaping question 3 written where the gate can read it. It stands the model floor
down for the whole plan, which is what you want when your workers have job titles rather than
the literal word "human" in their names.

**And in each task's owner line:**

```
**Owner:** Priya (human, incident commander on the night)
```

Both, deliberately. The plan-level line lifts the floor; the freeze and the runner's "never
dispatch this to a model" behaviour key off the *task's* owner containing the word `human`
(`is_human_owned` in [`../../scripts/validate-plan.py`](../../scripts/validate-plan.py)). Write
only the plan-level line and you take the discount without the bill: the models stop being
checked and nothing ever freezes. Keep the person's name in the same line — the gate reads the
whole owner string, so `Priya (human, incident commander)` is both a real person and a legible
declaration.

## What a human task file looks like

Open [`tasks/T2/TASK.md`](tasks/T2/TASK.md). The header is four lines and there is no agent
row:

```
**Status:** NOT STARTED
**Owner:** Dan (human, on-call for payments that week)
**Blocked by:** T1 · **Blocks:** T3
```

Everything below it — What you own, Steps, Done means, Do NOT — is the same contract an agent
would get. The briefing model is the only thing that changes: an agent receives a directory,
a person receives this file in a message and never opens the directory again.

## The frozen contract, in practice

[`tasks/T1/TASK.md`](tasks/T1/TASK.md) is the one that has been handed over, so this plan ships
mid-flight on purpose — T1 is `IN PROGRESS`, and its header carries:

```
**Delivered:** 2026-08-19 09:40, in the incident channel · contract `sha256:<12 hex>`
```

The hash covers **What you own**, **Steps**, **Done means**, **If it fails** and **Do NOT** —
the five sections that grade the work. It does not cover the title, the status, or this
paragraph, so a task can move to DONE without breaking its own freeze.

Compute it with the validator, never by hand:

```bash
./scripts/validate-plan.py examples/human-worker-plan \
  --contract-hash examples/human-worker-plan/tasks/T1/TASK.md
```

(The plan argument is required by the parser and ignored by this flag.)

Then try it. Change one word inside T1's **Steps** — say six rows to five — and run the gate:

```bash
./scripts/validate-plan.py examples/human-worker-plan --run-gates
```

It fails with `frozen-contract`, naming the recorded hash and the current one. That is the
entire mechanism, and it exists because on a real run a capture method was rewritten two and a
half hours after the person had already satisfied the original, and the delivery was then
scored against the rewrite. A person cannot re-read the directory to notice. A hash can.

Restoring the word makes it green again. Genuinely needing the change is fine too — edit,
re-run `--contract-hash`, write the new hash in, and tell the person it was re-delivered. The
freeze does not forbid amendments; it forbids silent ones.

## Done-commands for work a machine cannot do

Not executable is not the same as not checkable. None of the three gates here runs the review —
they grade the document the review produces:

- **T1** must state `Time to detect:` and `Time to mitigate:` and hold at least six timestamped
  rows. `test -s` would be satisfied by an empty-ish file with a title.
- **T2** requires every factor row to carry `CONFIRMED` or `SUSPECTED`, at least two of them,
  and rejects the phrase "human error" outright.
- **T3** requires a verdict, at least one action item, a date on every action item, and no
  action owned by "the team".

Two things worth stealing from them:

1. **Grade content, not existence.** Every clause above is false on a file somebody created and
   did not fill in.
2. **Never open with a negation.** `! grep -q PHRASE file.md` succeeds when the file does not
   exist, so a chain that starts with one is green before the work begins. Put a clause that
   must be true first; the chain then fails on the missing file, which the gate reads as a
   clean fail because the file is inside the plan.

## What has not changed

The gate still checks the owner, the status, that `PLAN.md` and `tasks/` name the same tasks
and the same edges, that every link resolves, that the declared size matches the task count,
and that each done-command fails before the work. Below four tasks the adversary and health
roles are not enforced — T3 keeps the spirit of the first one by hand, because the person
signing off wrote neither of the documents they are judging.

Run it:

```bash
./scripts/validate-plan.py examples/human-worker-plan --run-gates
```

It exits 0 with T1 in flight and its contract frozen.

---

**See also:** [`../../QUICKSTART.md`](../../QUICKSTART.md) §0b question 3 (where the question is
asked), [`../../OPERATING-THE-PLAN.md`](../../OPERATING-THE-PLAN.md) §10b (a task a person owns
is parked, never dispatched), [`../../tests/test-human-workers.sh`](../../tests/test-human-workers.sh)
(the harness that asserts both halves of the trade), and
[`../research-first-plan/PLAN.md`](../research-first-plan/PLAN.md) for the same size of plan
worked by agents.
