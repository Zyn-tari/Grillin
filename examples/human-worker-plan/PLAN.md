# INC-2231 — the incident review, written by the people who were in it

**Size:** XS
**Workers:** human — three named people. Nobody in this plan has a model or an effort.

Checkout returned 502 for forty-one minutes on 18 August. A customer found it before the
monitoring did. Three people write the review: the incident commander who ran the night, the
on-call engineer whose service it was, and a staff engineer who was on neither rotation and
signs it off.

**Why these workers are people, and not a fleet.** What Priya believed at 02:14, and why she
tried the rollback before the cache flush, is not in the repository — it is in her head and in
a channel nobody exported. The sign-off is an accountability act: A1 and A2 land on a named
person who agreed to them out loud. No amount of model tier substitutes for either.

**This is the plan that shows what declaring people costs and buys.** Read
[`README.md`](README.md) beside this file before you copy it — the trade is the whole point,
and it is one paragraph long.

## What the declaration changes

The `**Workers:** human` line above is answer 3 of the five shaping questions, written down
where the gate can read it. Because of it, no task file here names an **Agent**, a **Model**
or an **Effort**, and there is no `tasks/_ROSTER.md`. A roster prices personas; a person is
not a persona and has no price to record.

In exchange, every task whose owner is a person **freezes its contract when it is handed
over**. T1 was handed to Priya on 19 August and carries the hash of its own contract. Edit
T1's Steps, its Done means, or its If it fails today and the gate fails until the hash is
restored or the amendment is re-delivered. That is deliberate: on the run this rule came from,
a capture method was rewritten two and a half hours after the person had already satisfied the
original, and the delivery was then scored against the rewrite.

## Tasks

| ID | Task | Owner | Blocked by |
|---|---|---|---|
| T1 | The timeline: what happened, minute by minute | Priya — incident commander | — |
| T2 | The contributing factors, labelled by how well we know them | Dan — on-call, payments | T1 |
| T3 | The review and the sign-off | Alex — staff engineer, neither rotation | T2 |

Three tasks, so Grillin runs reduced: no separately-staffed adversary, no collision step. T3
is still owned by somebody who wrote neither of the other two — that is principle 8 kept by
hand at a size where nothing enforces it, and it costs nothing to keep.

## The five shaping answers

| | Question | Answer |
|---|---|---|
| 1 | Does the thing already exist in a form we can inspect? | Partly. The logs do; what people believed at the time does not, which is why T1 is first and why a person writes it. |
| 2 | Will more than one worker act at the same time? | No — T1, then T2, then T3. Ownership is declared anyway, for resuming. |
| 3 | Are the workers AI agents? | **No. They are three named people.** That answer is the `**Workers:**` line at the top. |
| 4 | Does "done" produce something that runs or deploys? | No. It produces three documents, and every gate greps them for content. |
| 5 | Is any step hard to undo? | No. Nothing here deploys, and a review can be reissued. |

## What the gate still asks of a plan of people

Everything except the model floor. Each task names an owner and a status; each done-command is
a real command that fails while the work is unfinished and grades what the document says, not
that a file exists; `PLAN.md` and `tasks/` agree on the same three tasks and the same two
edges; every link resolves. A plan of people is not a plan with the checking taken out.
