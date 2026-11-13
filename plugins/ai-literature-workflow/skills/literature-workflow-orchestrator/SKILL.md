---
name: literature-workflow-orchestrator
description: Inspect and route a gated AI literature-research project. Use for project initialization, status checks, gate validation, blocker diagnosis, or choosing the single next workflow step. Do not use for an ordinary one-off paper search.
---

# Purpose

Act as the state reader and scheduler. Do not perform searches, extract evidence, synthesize papers, or draft manuscript prose.

Read `../../AGENTS.md`, [gate contract](../../references/gate-contract.md), and [gates.json](../../references/gates.json).

# State Sources

Prefer, in order:

1. `planning/manifest.json`;
2. canonical artifacts on disk;
3. human decisions in `planning/decisions.jsonl`.

Never trust a reported status when the underlying artifact or human decision is missing.

# Routing

Run:

```powershell
python ../../scripts/validate_gate.py --project <project-root> --next
```

Route exactly one next action:

- G0 missing or failing -> `research-scope-builder`;
- G1 missing or failing -> `research-scope-builder`;
- G2 missing or failing -> `corpus-screener`;
- G3 missing or failing -> `paper-evidence-reader`;
- G4 missing or failing -> `evidence-quality-judge`;
- G5 missing or failing -> `literature-synthesizer`;
- G6 missing or failing -> `related-work-writer`;
- G7 missing or failing -> `citation-and-venue-auditor`;
- G8 missing or failing -> `literature-final-auditor`;
- all gates pass -> packaging may be proposed, but requires explicit user action.

Do not invoke several judgment-bearing stages speculatively.

# Human Decisions

The project manifest is not a substitute for the human ledger. Record a decision only after the user has explicitly supplied the choice and rationale:

```powershell
python ../../scripts/log_decision.py --project <project-root> --type <decision-type> --choice <choice> --rationale <user-rationale> --evidence <path>
```

Never invent or strengthen a rationale.

# Gate Advancement

After a gate genuinely passes, run validation with `--write`:

```powershell
python ../../scripts/validate_gate.py --project <project-root> --gate Gx --write
```

Advance only when the validator returns `PASS`.

# Output

Return:

- profile;
- current gate;
- passed gates;
- blockers;
- missing artifacts;
- exactly one next Skill;
- whether human action is required.

Do not update downstream artifacts merely to make a status look complete.
