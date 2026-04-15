---
description: Show next action and suggest phase transition
allowed-tools: Read
---

# /next

Show the next action from STATUS.md and suggest the appropriate phase transition.

1. Read `docs/STATUS.md`
2. Display: current phase, next_action, blockers
3. Based on current phase, suggest:
   - Which gate needs approval to proceed
   - Which skill to load for the next phase
   - What artifact should be produced

Phase transition suggestions:

### Client mode

| Current Phase | Next Phase | Gate to Approve | Skill |
|---|---|---|---|
| onboard | discovery | - | client-workflow |
| discovery | requirements | - | client-workflow |
| requirements | scope | - | client-workflow |
| scope | acceptance | - | client-workflow |
| acceptance | handover | - | client-workflow |
| handover | (Dev) | client_ready_for_dev | - |

### Dev mode

| Current Phase | Next Gate | Next Phase | Skill |
|---|---|---|---|
| brainstorm | brainstorm | plan | subagent-dev |
| plan | plan | implement | subagent-dev + tdd |
| implement | - | review | subagent-dev |
| review | review | qa | - |
| qa | qa | security | - |
| security | security | deploy/ship | deploy or ship-and-docs |
| deploy | deploy | ship | ship-and-docs |
| ship | - | docs | ship-and-docs |
| docs | dev_ready_for_client | (Client or done) | - |

If `session_history` or `external_evidence` has 3 entries (the max), suggest
archiving older entries before adding new ones.

If the body `## Session History` section has 10 or more bullet entries,
suggest consolidating or trimming older entries to keep the file concise.

Do not modify any files. Suggest only.
