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

- [ ] One owner per file — no file appears in two tasks' ownership
- [ ] **The contended-file list exists.** Which files do many tasks want?
- [ ] Each contended file has a single owner and a fragment protocol
- [ ] Every task has a loop **with a cap**
- [ ] Every "done" is evidence someone else can check
- [ ] Every task has an explicit do-NOT list
- [ ] Onward-delegation policy stated in every prompt
- [ ] Model tier assigned per task, and published

## Against the substrate

- [ ] Tool choice **measured**, not assumed
- [ ] Effective parallelism recorded, not the advertised cap
- [ ] What actually binds identified (compute? memory? latency? admission control?)
- [ ] Every quoted limit checked for **what it governs**
- [ ] The rejected alternative written into the plan, with why

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

---

**If you tick everything except the last two sections, you have a document.
The last two are what make it a plan.**
