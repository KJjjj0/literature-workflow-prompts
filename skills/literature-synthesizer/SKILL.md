---
name: literature-synthesizer
description: Synthesize a frozen, quality-judged AI literature corpus into method families, evidence trends, disagreements, and research gaps. Use at G5 before drafting; do not create citations that are absent from the corpus.
---

# Purpose

Turn the evidence matrix into an approved synthesis and review outline.

Read [gate contract](../../references/gate-contract.md), [writing policy](../../references/writing-policy.md), and [audit contract](../../references/audit-contract.md). Use `literature-review` for systematic review structure when it fits.

# Synthesis

Build the smallest useful taxonomy around:

- research problems and assumptions;
- method families and trade-offs;
- datasets and evaluation protocols;
- evidence strength and conflicting findings;
- open problems that follow concretely from the included evidence.

Do not list papers one by one. Do not claim a consensus that the evidence matrix does not support.

# Artifacts

Write:

- `analysis/gap_map.md`: evidence-backed gaps, why they remain open, and the evidence required to address them;
- `synthesis/review_outline.md`: section order, claims per section, and paper IDs supporting each claim.

Every outline claim must reference evidence-card claim IDs or paper IDs.

After the user explicitly approves the synthesis and gap scope, append `synthesis_approval`. Validate G5 with `--write`.

# Boundaries

- Do not draft polished prose yet.
- Do not introduce new papers.
- Do not turn speculation into a research gap.
- Return to G2 or G4 when evidence is insufficient.
