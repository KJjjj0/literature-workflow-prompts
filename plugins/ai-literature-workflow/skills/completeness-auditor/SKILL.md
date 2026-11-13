---
name: completeness-auditor
description: Audit whether the active literature workflow profile contains all required evidence, synthesis, citation, and writing artifacts. Use at G7.8 after consistency auditing; do not judge prose style.
---

# Purpose

Check semantic and workflow completeness before final quality assurance.

Read [gate contract](../../references/gate-contract.md) and [audit contract](../../references/audit-contract.md).

# Audit

Run:

```powershell
python ../../scripts/audit_research.py --project <project-root> --layer completeness --write
```

The audit verifies:

- all completed-gate artifacts still exist;
- every included paper has evidence and a claim mapping;
- synthesis cites evidence rather than paper counts alone;
- the draft does not contain unresolved placeholders;
- the bibliography and citation audit are current.

Write `audit/completeness.json`.

Validate G7.8 with `--write`. This gate has no human decision.

# Boundaries

- Do not assess literary quality here.
- Do not add missing evidence from model memory.
- Report missing artifacts as blocking.
