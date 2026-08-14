# Roster — the fixture's personas

| Persona | Responsible for | Model | Effort | Why |
|---|---|---|---|---|
| `recon` | interpreting what exists — dead? depended on? | `claude-opus-5` | `high` | The dead-modules miss was a reasoning failure, not a thoroughness one. |
| `implementer` | bounded work, decisions already made | `claude-sonnet-5` | `high` | The contract is written; effort buys the reading of it. |
| `adversary` | judging whether the result is true | `claude-opus-5` | `xhigh` | Highest-yield role in the method — 50 defects to the gate's 2. |
| `health` | whether the RULES are being followed, in rounds | `claude-sonnet-5` | `xhigh` | Reads for what is ABSENT across a lot of material, which is the expensive thing to see. Contamination is required here, not disqualifying. |
| `judge` | ruling on whether the plan may advance past a task | `claude-opus-5` | `xhigh` | Owns no task on purpose. A judge that wrote some of the work is certifying its own, so this row exists to be the persona `_RULINGS.toml` can name. |
