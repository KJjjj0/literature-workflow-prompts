---
name: literature-final-auditor
description: Run the final consistency, claim, citation, and submission-readiness audit for a literature project. Use at G8 after citation verification; do not repair by inventing evidence or silently changing claim scope.
---

# Purpose

Perform the independent final audit and decide whether the research package may be assembled.

Read [gate contract](../../references/gate-contract.md), [audit contract](../../references/audit-contract.md), and [writing policy](../../references/writing-policy.md). Use `peer-review` when available for an adversarial manuscript pass.

# Audit Layers

## Consistency

Compare corpus, evidence cards, evidence matrix, synthesis, draft, and bibliography for:

- paper identity, year, venue, DOI, arXiv ID, and status;
- result values and comparisons;
- claim scope;
- paper IDs and bibliography keys;
- stale artifacts after a scope change.

Write `audit/consistency.json` with `status: PASS` only when no blocking issue remains.

## Final Quality

Check:

- citation audit is PASS;
- no citation outside the frozen corpus;
- every research gap follows from evidence;
- no unsupported novelty or superiority claim;
- preprints are labeled correctly;
- venue requirements are satisfied;
- no placeholders remain.

Write `audit/final_audit.json`.

After the user explicitly approves submission scope, append `submission_approval`. Validate G8 with `--write`.

# Packaging

Only after G8 passes and the user explicitly asks:

```powershell
python ../../scripts/build_research_package.py --project <project-root>
```

If an audit fails, return to the earliest affected gate. Do not weaken the audit to match the draft.
