# Grill checklist — run this against any plan

Print it. Tick it. A plan that fails these is not ready, regardless of how good it reads.

## Before you write anything

- [ ] Precedence ladder declared in writing
- [ ] The ask restated in your own words and confirmed
- [ ] What you still need is named
- [ ] Anything that would change the plan's **shape** is flagged
- [ ] You have not started

## Against the source documents  ⚑ never skip

- [ ] Every load-bearing claim checked against the running system
- [ ] Every "X will exist / has been built" claim verified to exist
- [ ] Every document dated — what shipped since it was written?
- [ ] Documents checked **against each other**, not only against the system
- [ ] Contradictions written down, not silently resolved
- [ ] For each: which source wins, and the ladder rule that says so
- [ ] Claims stated as settled fact in headings treated with **more** suspicion, not less

## Against the inventory

- [ ] Every category has a **number**, not an adjective
- [ ] Every claim cites `file:line`
- [ ] CONFIRMED vs SUSPECTED labelled throughout
- [ ] "What I did not verify" present and specific
- [ ] The inventory is frozen and referenced, not re-derived downstream

## Against the shape

- [ ] A one-screen diagram existed before any task prose
- [ ] It was approved before the prose was written
- [ ] Every node typed (ASK / BUILD / REFACTOR / RECONSIDER / VERIFY / LOOP)
- [ ] At least one node's legitimate output is *"don't build this"*
- [ ] Decision nodes are gates, not notes

## Against the decomposition

- [ ] **One folder per task** — `tasks/<ID>/`, no exceptions, whatever the task count
- [ ] Each task's `TASK.md` is **inside its own folder**, never loose and never shared
- [ ] The folder is what the agent **receives** — a directory, not a pasted prompt
- [ ] Every output the agent writes lands **back in that same folder**
- [ ] Nothing needed to do the task lives outside the folder or the cited inventory
- [ ] One owner per file — no file appears in two tasks' ownership
- [ ] **The contended-file list exists.** Which files do many tasks want?
- [ ] Each contended file has a single owner and a fragment protocol
- [ ] The owner list exists **machine-readably**, not only as prose in a table
- [ ] Every task has a loop **with a cap**, and the loop confirms the **fix**, not just the work
- [ ] Nobody confirms a repair they made themselves
- [ ] Money and authz work gets **two** adversarial passes, the second with fresh context
- [ ] Every "done" is evidence someone else can check
- [ ] Every task has an explicit do-NOT list
- [ ] Onward-delegation policy stated in every prompt
- [ ] Model tier assigned per task, and published

## Against the substrate

- [ ] Tool choice **measured**, not assumed
- [ ] Effective parallelism recorded, not the advertised cap
- [ ] What actually binds identified (compute? memory? latency? admission control?)
- [ ] Every quoted limit checked for **what it governs**
- [ ] The **instrument** was checked, not only the number it produced
- [ ] The rejected alternative written into the plan, with why
- [ ] **Both substrates tried on the same real fan-out** — script-and-collect vs managed session
- [ ] Time-to-detect a **stalled** worker measured on each, not just wall-clock
- [ ] Recovery cost after a context loss measured on each
- [ ] The substrate is **declared once** and not mixed mid-run
- [ ] **Every agent has a role name** — never a fleet of identical kind labels

## Against the environment  ⚑ never skip

- [ ] Every path in the plan resolves — and in the expected repository
- [ ] Every script named is present **and readable** (a failed read ≠ absent — check permissions)
- [ ] Topology verified: which machine holds the data, the server, the tests?
- [ ] Credentials, remotes, quotas verified rather than assumed
- [ ] Things you cannot do yourself listed explicitly as hand-offs

## Against your own plan  ⚑ the one people skip

- [ ] You have re-read your own plan hunting for the errors you warned others about
- [ ] Every path **you** wrote verified on the live system
- [ ] Every number **you** quoted traced to a measurement
- [ ] Every "already exists" **you** asserted checked
- [ ] Errors found in your own text fixed **at source**, not logged elsewhere
- [ ] The same wrong claim searched for everywhere else it might appear

## Before handing it over

- [ ] A single entry point with an explicit read order
- [ ] A paste-ready kickoff prompt
- [ ] Persistent memory updated — a cold start lands here
- [ ] A status surface the requester can read without asking
- [ ] Escalation conditions listed, and they are decisions — not findings

## Will the worker stay oriented?

- [ ] Reminders are **computed from current state**, never static text re-pasted
- [ ] Something fires **before compaction** — the one moment state lands inside the summary
- [ ] That pre-compaction output names **where truth lives**, so the post-summary worker
      re-reads rather than recalls
- [ ] Something fires at a **boundary** — session start, a worker finishing, a wave closing
- [ ] The ambient reminder carries **position only** — no rules
- [ ] No reminder can **block** anything; enforcement lives somewhere else
- [ ] The state reporter **never touches the plan** — its only writes are its own log and
      the published surface — and it exits zero on every path
- [ ] It **degrades out loud** — "no tasks found" beats silence, which reads as fine
- [ ] The requester's surface is **derived from the status writes**, not maintained by hand
- [ ] That surface is **silent to the agent** — acknowledgement turns a record into a performance
- [ ] It separates **claimed** done from **verified** done, and never renders them alike

## Will it survive being forgotten?  ⚑ never skip

- [ ] Every task carries a **status line updated in place** — not tracked in a conversation
- [ ] Every "done" is a **command someone can re-run**, so completion re-derives without memory
- [ ] Deviations amend **the plan itself**; the changelog is a receipt, not a substitute
- [ ] Corrections land in **every** place they belong — plan, rules, skills, durable memory
- [ ] A replaced or re-baselined **gate** got a receipt, with the old and new expected numbers
- [ ] Amendments are **referenced both ways** — plan to reason, record to clause
- [ ] Who may amend the plan is named (the integrator), and task agents report instead
- [ ] The entry point supports a **warm restart**, not only a cold one
- [ ] Orientation steps come **before** work: statuses, changelog, gates, `git log`, working tree
- [ ] A worker that appeared to fail is checked against the tree — **its edits usually landed**
- [ ] **The test:** conversations all end, a new worker clones the repo — can it tell what was
      done, what was in flight, and what changed since the plan was written?

---

**If you tick everything except the last three sections, you have a document.
The last three are what make it a plan.**
