# T6 — Make the templates usable without asking the author

**Type:** BUILD
**Status:** NOT STARTED
**Blocked by:** T5 · **Blocks:** T7
**Contended files:** none exclusively — you own all of `templates/`, `.gitignore`, and
`SCALING.json:2` (coordinate the `SCALING.json` touch with T3, who owns that file's content).

## Why this exists

68 angle-bracket placeholders across 7 templates, and no filled counterpart to any of them
(`01-INVENTORY.md`, VERIFIED). Some placeholders are self-evident (`<ID>`, `<path>`). Several are
not:

| Placeholder | File | Why it stalls a first-timer |
|---|---|---|
| `<the specific trap for this task>` | `TASK.md.template:70` | Requires already knowing the project's scar tissue and the method's theory of do-NOT lists |
| `<the pattern that looks helpful and is not>` | `TASK.md.template:71` | Same, worse — it is a riddle |
| `<the scar tissue it holds>` | `_RULES.md.template:45` | "Scar tissue" is defined in phase 6, three files away |
| `<project-specific wrong-source-of-truth trap>` | `_RULES.md.template:99` | Every project has one; nothing tells you how to find yours |
| `<build → promote → restart → run ALL gates>` | `_RULES.md.template:126` | An example pretending to be a placeholder — is it a default or a prompt? |
| `<universal do-NOT list>` | `TASK.md.template:73` | Cross-references a section number that does not exist yet |

Plus three broken links **inside `templates/`** (`03-CONTRADICTIONS.md` C7) and two conventions in
use for the same thing.

## What you own

All of `templates/`, `.gitignore`, `SCALING.json:2`.

## Steps

1. **Ship a filled sibling for every template**, sourced from T5's worked example — not invented.
   `templates/TASK.md.template` gets `templates/examples/TASK.md` beside it, filled, zero
   placeholders. A placeholder next to a filled example is self-explanatory; alone it is a quiz.
   This is one change that fixes most of the table above without editing a single placeholder.
2. For the six placeholders in the table that a filled example does not fix, add a one-line
   HTML comment above each saying **what kind of thing goes there** and pointing at the phase that
   explains it. Example: `<!-- the trap: a plausible-looking wrong move specific to THIS task.
   See phase 5, "an explicit do-NOT list". -->`
3. Fix C7. `_RULES.md.template:74`, `_AWARENESS.md.template:213`, `_HERDR.md.template:6` link to
   `_HERDR.md` / `_RULES.md`, which do not exist — every file in that directory carries a
   `.template` suffix. `_WORKTREES.md.template:86` and `GRILLING-THE-PLAN.md:228` use the *other*
   convention. Pick one, apply it everywhere, and if the intent is "these resolve after you copy
   them into your project and drop the suffix" then **write that sentence in a
   `templates/README.md`**, because nothing anywhere says it and a stranger browsing GitHub clicks
   a 404.
4. Add `templates/README.md`: which templates you need at which size, which require an AI agent
   fleet (6 of 7 — get the breakdown from `01-INVENTORY.md`), and the suffix convention.
5. Fix `SCALING.json:2` — `"$schema": "https://json-schema.org/draft/2020-12/schema"` declares the
   file *is* a JSON Schema. It is data. Either write a real schema and point at it, or drop the
   line. Anything that tries to validate it today fails.
6. Fix `.gitignore` — it ignores `node_modules/` and `*.log` in a repository containing no code.
   Harmless, but it is an early signal that implies a build that does not exist.

## Loop

**Converge, cap 2.** Fill → a cold reader instantiates `TASK.md.template` for a task of their own
→ count remaining placeholders in their output → fix what they left blank → they confirm. Exit
when a cold reader leaves zero placeholders unfilled and asks zero questions.

## Done means

Three re-runnable checks:

```
grep -rn ']([^)]*\.md)' templates/ | grep -v '\.template)'   # → empty, or every hit explained
                                                              #   in templates/README.md
grep -rc '<[a-z]' templates/examples/                         # → 0
python3 -c "import json;json.load(open('SCALING.json'))"      # → no error, and $schema is honest
```

## Do NOT

- Do NOT delete the placeholders and inline the example. The template must stay a template.
- Do NOT invent example content. Source it from T5 so the example and the template describe the
  same real job — two different fictions is worse than none.
- Do NOT rewrite `_HERDR.md.template`'s substance. It is fleet-specific by design; T4 decides how
  it is framed, you only fix its links and label it.

## Outputs

`templates/examples/**`, `templates/README.md`, `FINDINGS.md`, `CHANGES.md`
