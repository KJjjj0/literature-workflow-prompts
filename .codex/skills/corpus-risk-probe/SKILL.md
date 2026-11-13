---
name: corpus-risk-probe
description: Audit a frozen paper corpus for source diversity, metadata completeness, recency, screening consistency, and coverage risk before evidence reading. Use at G2.5; do not extract paper evidence.
---

# Purpose

Run a time-bounded coverage and data-quality probe after the corpus is frozen.

Read [gate contract](../../references/gate-contract.md), [search policy](../../references/search-policy.md), and [evidence schema](../../references/evidence-schema.md).

# Probe

Run:

```powershell
python ../../scripts/audit_corpus_coverage.py --project <project-root> --write
```

Review `analysis/corpus_risk_report.json` for:

- raw, deduplicated, screened, and included counts;
- source and venue diversity;
- publication-year coverage;
- DOI or arXiv identifier coverage;
- preprint and peer-review distribution;
- unresolved screening records;
- duplicate and missing-metadata risks;
- profile-specific minimum coverage.

`PASS` and `CONDITIONAL` are acceptable for G2.5. A `FAIL` blocks evidence reading and requires reopening corpus screening.

Validate G2.5 with `--write`. This gate has no human decision.

# Boundaries

- Do not add papers to hide a coverage warning.
- Do not rewrite screening decisions to pass the probe.
- Report genuine coverage limitations instead of producing a synthetic corpus.
