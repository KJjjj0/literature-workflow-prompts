---
name: consistency-auditor
description: Audit paper identity, evidence, bibliography, and draft references for cross-file consistency. Use at G7.5 after citation verification; do not repair by inventing data or silently changing claims.
---

# Purpose

Check that paper identifiers and evidence remain consistent across the frozen corpus, evidence cards, matrix, draft, and bibliography.

Read [audit contract](../../references/audit-contract.md) and [writing policy](../../references/writing-policy.md).

# Audit

Run:

```powershell
python ../../scripts/audit_research.py --project <project-root> --layer consistency --write
```

The audit checks:

- every corpus paper has an evidence card and matrix row;
- paper IDs and bibliography keys agree;
- DOI, arXiv ID, year, venue, and publication status agree;
- cited keys map to the frozen corpus;
- result statements do not conflict across evidence artifacts.

Write `audit/consistency.json`. If it fails, return to the earliest affected gate. Do not weaken the audit to match the draft.

Validate G7.5 with `--write`. This gate has no human decision.
