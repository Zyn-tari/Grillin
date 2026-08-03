# Status

Derived from the `**Status:**` line in each `tasks/<ID>/TASK.md`. Not maintained by hand.

Regenerate:

```
grep -H '^\*\*Status:' tasks/*/TASK.md
```

As of 2026-08-03, plan authored, nothing executed:

| Task | Status | Blocked by |
|---|---|---|
| T1 Author decisions | NOT STARTED | — (**start here**) |
| T2 QUICKSTART.md | NOT STARTED | T1 |
| T3 Reconcile scaling sources | NOT STARTED | — for most of it (**can start today**) |
| T4 Software-only? | NOT STARTED | T1 |
| T5 Worked example | NOT STARTED | T2, T4 |
| T6 Templates self-sufficient | NOT STARTED | T5 |
| T7 Grill before publishing | NOT STARTED | T2–T6 |
| T8 Publish | NOT STARTED | T7, **T1/Q4 hard block** |

**Claimed done: 0. Verified done: 0.** These are rendered as separate columns on purpose
(`templates/GRILL-CHECKLIST.md:116`).
