# Case study — where the method came from

Reconstructed from the session that produced it, in order. Not idealised: several steps are
recorded because they went **wrong** and the correction is the lesson.

The project: a live web app web app being redesigned and rebranded, ~24 routed pages,
72 API routes, five prior rounds of defect work behind it.

---

## The arc, in order

### 0 · The ask lands — and nothing starts

> *"I have the new redesign… your job is implementing the new dashboard and deleting the old
> one… acknowledge you understand."*

**What happened:** restated the job in six lines, named the two artefacts still missing, flagged
two things that would shape the plan (an existing gate already enforced the parity requirement;
the 58 UI tests would be invalidated by a redesign), and **stopped**.

**Why it matters:** the acknowledgement is a checkpoint, not a formality. Restating the scope
in your own words is the cheapest place to discover you have understood it differently.

**→ Principle:** *Acknowledge by restating. Flag what shapes the plan. Do not start.*

---

### 1 · Inventory before planning

> *"First fan out a haiku or sonnet read only to count all the data points… put them in a point
> folder."*

**What happened:** seven read-only agents, partitioned **by file ownership** so none overlapped,
each writing one document into a shared folder. Result: 9 files, ~3,800 lines — every route,
page, component, data point and schema column, cited to `file:line`, with counts.

Cheap recon (Haiku) fed the expensive agents later as a briefing, so no Opus agent ever burned
reasoning on inventory.

**→ Principle:** *Count before you plan. Freeze the inventory. Nobody re-derives it later.*

---

### 2 · The first correction — invisible tiering

> *"I told you to fan out with the agent levels not being opus but you did it anyways."*

**What happened:** the tiering had in fact been correct — verified from the live agent
transcripts as 4× Sonnet, 3× Haiku, zero Opus. But the user had **no way to see that**.

The defect was observability, not tiering.

**→ Principle:** *Publish the agent→model table when you fan out. An unverifiable claim is
indistinguishable from a false one. And verify before defending — the answer might not be the
one you expect.*

---

### 3 · Defects surface as a byproduct — triage rather than absorb

> *"write them down if there are product bugs to fix during the restyle"*

**What happened:** the inventory had turned up real defects. They were split three ways:

- **A** — fix during the work (display-only, in files being rewritten anyway)
- **B** — needs a human decision (product or product semantics)
- **C** — real but out of scope (backend, backlog)

Each labelled **VERIFIED** (read live, cited) or **REPORTED** (agent claim, unchecked).

**Why it matters:** without triage, a discovered bug either gets swept into the work — quietly
expanding scope — or gets lost. The three-way split makes scope creep a visible decision.

**→ Principle:** *Triage findings into fix / decide / out-of-scope. Never let a discovery
silently widen the work.*

---

### 4 · Read the source documents against live truth

**What happened:** three planning documents were studied. Checking their claims against the
running system found:

- one document specified **~30 endpoints that did not exist** — a versioned API namespace that
  was never built. Followed literally it would have bound the new frontend to fiction.
- two documents were written against a **stale snapshot**; four of their "this will be built"
  claims had already shipped.
- three documents **disagreed with each other** about a shared configuration constant, and all three disagreed
  with the running configuration.

**Why it matters:** this was the single highest-value hour of the session, and it produced no
plan text at all. It only produced *corrections*.

**→ Principle:** *Documents drift; running systems don't. Declare a precedence ladder, then
check every load-bearing claim against the top of it. Surface contradictions — never resolve
them silently.*

---

### 5 · Diagram before prose

> *"First lets print the diagram necessary for this plan and then write it after I approve."*

**What happened:** a one-screen dependency graph — nodes typed as ASK / BUILD / REFACTOR /
RECONSIDER / LOOP — presented for approval before any task was written.

**Why it matters:** the diagram was rejected-or-approved in one exchange. The prose it authorised
ran to 2,800 lines. Getting shape wrong on a diagram costs a minute.

**→ Principle:** *Shape first, at a size that can be rejected cheaply.*

---

### 6 · Decompose into owned tasks

**What happened:** one folder per task. Each carrying: persona · exactly the files it owns ·
steps · a **loop with an explicit exit condition and an iteration cap** · done-means-**evidence**
· an explicit do-NOT list · an output contract.

Ownership was assigned **by file, not by task** — when several jobs touch one file, that file
gets one owner who receives all of them.

**→ Principle:** *A task is a contract, not a description. Own by file. Every loop has a cap,
and hitting it is a stop-and-report.*

---

### 7 · Extract tacit knowledge into skills

> *"remember that LLMs are finetuned by their starting context and skills are a key component."*

**What happened:** the project's scar tissue — the bugs that had actually shipped, the
conventions, the traps — was pulled out of the task files into **seven reusable skills**, grouped
by *category of work* rather than by task. Each task then declared which to load **before its
first tool call**.

**Why it matters:** the same warning was being restated in eleven task files. One skill, eleven
references, one place to fix when it changes.

**→ Principle:** *Recurring context belongs in a skill, loaded first. Context read after work
begins has already missed the decisions it existed to inform.*

---

### 8 · Design the isolation — and find the collision

> *"make sure that agent work is contained to its specific job and nothing else… proper working
> trees."*

**What happened:** designing worktree isolation exposed a flaw in the already-written plan:
**five tasks all appended to one gate script, three to one schema file.** Five branches editing
one file is five conflicts resolved by whoever merges last — the collision merely relocated to
merge time.

Fixed by making contended files **single-owner**: task agents emit *fragments* into their own
folders, and one dedicated integrator applies them in merge order.

**→ Principle:** *Isolation is not just separate directories. Find the files many tasks want,
give each one owner, and have everyone else emit a fragment.*

---

### 9 · Choose the execution substrate by measurement

> *"can we do this with headless agents? or will a workflow be best?"*

**What happened:** the user's premise — that the concurrency cap applied only to writing agents
— was wrong, and saying so mattered. Measured on the box: one orchestration tool capped at **2**
concurrent regardless of read/write (1.78× effective); the other sustained **4.9×**. Load peaked
at 0.35, so CPU was never the constraint.

Then a follow-up: *would an 8-core machine be better?* More cores would raise one tool's cap and
change almost nothing else — and the work had to happen where the database, the web server and
the gates were.

**→ Principle:** *Measure the constraint; never quote it. And name what it governs before it
shapes a plan — a real number scoped to the wrong thing looks authoritative and silently shrinks
the work.*

---

### 10 · Verify the environment the plan assumes

**What happened:** a check of the plan's own assumptions found, in the plan's own text:

- three references to a schema file **in the wrong repository**
- two deploy scripts assumed present; one was in fact **root-owned and unreadable** (reported
  "missing" on a failed read — a second, separate error), the other genuinely on a different
  machine
- an assumption of outbound network access that **did not exist**

Every one was in a document written by the same author who had spent the session warning about
exactly this failure mode.

**→ Principle:** *Grill your own artefact last and hardest. A plan is a document, and documents
drift — including the one you just wrote.*

---

### 11 · Write the entry point, not just the plan

**What happened:** a single `PLAN.md` with a read order; a paste-ready kickoff prompt; and the
project's persistent memory updated so a cold session lands on the plan rather than on last
month's work.

**→ Principle:** *A plan nobody can enter is not a plan. Ship the door with the building.*

---

## What the arc shows

Three of the eleven steps produced **no plan text at all** — steps 4, 9 and 10 only produced
corrections. Between them they caught roughly thirty errors, several of which would have
invalidated whole tracks of work.

Two of the eleven were **the author's own mistakes**, caught by the same discipline applied
inward.

**The grilling is not a review stage at the end. It is the load-bearing activity, applied
continuously — most valuably to your own work.**
