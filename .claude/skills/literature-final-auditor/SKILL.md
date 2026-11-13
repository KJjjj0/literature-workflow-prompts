---
name: literature-final-auditor
description: Run the final quality-assurance audit for a literature project after citation, consistency, and completeness audits. Use at G8; do not repair by inventing evidence or silently changing claim scope.
---

# Purpose

Perform the independent final quality audit after the two upstream auditors pass.

Read [gate contract](../../references/gate-contract.md), [audit contract](../../references/audit-contract.md), and [writing policy](../../references/writing-policy.md). Use `peer-review` when available for an adversarial manuscript pass.

# Final Quality

Run:

```powershell
python ../../scripts/audit_research.py --project <project-root> --layer final --write
```

The final audit requires `audit/citations.json`, `audit/consistency.json`, and `audit/completeness.json` to pass, then checks anti-fabrication, claim scope, preprint labeling, and submission readiness.

Write `audit/final_audit.json`.

After the user explicitly approves submission scope, append `submission_approval`. Validate G8 with `--write`.

# Packaging

Only after G8 passes and the user explicitly asks:

```powershell
python ../../scripts/build_research_package.py --project <project-root>
```

If an audit fails, return to the earliest affected gate. Do not weaken the audit to match the draft.
