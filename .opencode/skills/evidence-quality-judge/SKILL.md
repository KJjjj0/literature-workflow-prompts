---
name: evidence-quality-judge
description: Assess whether included AI papers support specific claims, given methods, baselines, data, statistics, compute, and reproducibility. Use at G4 before synthesis; do not use for manuscript drafting.
---

# Purpose

Judge evidence quality and the boundary of defensible claims.

Read [gate contract](../../references/gate-contract.md), [evidence schema](../../references/evidence-schema.md), and [audit contract](../../references/audit-contract.md). Use `scientific-critical-thinking` when available.

# Checks

For each paper assess:

- task and benchmark fit;
- baseline strength and tuning fairness;
- data leakage and train-test separation;
- metric appropriateness;
- statistical uncertainty and variance;
- ablation sufficiency;
- compute and model-scale differences;
- reproducibility and artifact availability;
- claim language versus reported evidence.

Represent disagreements between papers instead of collapsing them without explanation.

# Quality Report

Write `analysis/quality_report.json`:

```json
{
  "status": "PASS",
  "papers": {
    "paper_id": {
      "quality": "high",
      "supported_claims": ["C1"],
      "unsupported_or_conditional_claims": [],
      "risks": [],
      "rationale": "..."
    }
  }
}
```

`quality` must be `high`, `medium`, or `low`. After the human explicitly approves the claim scope, append `quality_scope_approval`. Validate G4 with `--write`.

# Boundaries

- Do not treat peer review as proof of correctness.
- Do not infer unavailable implementation details.
- Do not approve a universal or causal claim from a single benchmark result.
- Reopen G4 when claim scope changes.
