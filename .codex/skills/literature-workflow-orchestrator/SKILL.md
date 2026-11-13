---
name: literature-workflow-orchestrator
description: Inspect and route a gated AI literature-research project. Use for project initialization, status checks, gate validation, blocker diagnosis, or choosing the single next workflow step. Do not use for an ordinary one-off paper search.
---

# Purpose

Act as the state reader and scheduler. Do not perform searches, extract evidence, synthesize papers, or draft manuscript prose.

Read [workflow policy](../../references/workflow-policy.md), [gate contract](../../references/gate-contract.md), and [gates.json](../../references/gates.json).

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

The project manifest is not a substitute for the human ledger. An explicit user reply such as `批准`, `同意`, `认可`, or `OK` is sufficient approval. Record it immediately:

```powershell
python ../../scripts/log_decision.py --project <project-root> --type <decision-type> --choice approve --evidence <path> [--rationale <optional-user-note>]
```

The script records a factual standardized approval note when the user gives no explanation. Do not ask the user to repeat an approval merely to obtain free-text rationale.

Ask for a short rationale only when:

- the user rejects or chooses between competing options;
- the user changes an approved scope or claim boundary;
- two alternatives have a material trade-off the user must own.

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
