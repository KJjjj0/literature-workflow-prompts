---
name: related-work-writer
description: Draft or revise Related Work and Introduction synthesis from an approved literature synthesis and frozen evidence matrix. Use at G6 after G5; do not write unsupported literature claims or add new sources.
---

# Purpose

Draft section prose that remains traceable to the approved evidence base.

Read [gate contract](../../references/gate-contract.md), [writing policy](../../references/writing-policy.md), and [audit contract](../../references/audit-contract.md). Use `scientific-writing` when available.

# Inputs

Read only:

- `synthesis/review_outline.md`;
- `analysis/evidence_matrix.csv`;
- approved evidence cards;
- human claim-scope decisions.

Write `writing/related_work.md` or an explicitly requested section such as `writing/introduction.md`.

# Writing Rules

- Organize by problem, method family, or trade-off.
- Use Pandoc citations such as `[@bib_key]`.
- Distinguish demonstrated results, author claims, and project interpretation.
- State the project position only within the approved claim scope.
- Keep preprint, peer-review, dataset, and compute caveats visible when they affect the claim.
- Do not add a citation during writing.

After the draft exists, validate G6 with `--write`. G6 has no human decision gate.

# Boundaries

- Do not search for new papers.
- Do not overwrite unrelated manuscript sections.
- Do not present a list of summaries as a synthesis.
- If an essential source is missing, stop and reopen the earlier gate.
