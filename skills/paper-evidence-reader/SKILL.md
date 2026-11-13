---
name: paper-evidence-reader
description: Read included papers and extract structured, provenance-linked evidence cards for an AI literature project. Use at G3 after the corpus is frozen; do not use to synthesize whole literatures.
---

# Purpose

Produce one evidence card per included paper and synchronize the evidence matrix.

Read [gate contract](../../references/gate-contract.md), [evidence schema](../../references/evidence-schema.md), and [writing policy](../../references/writing-policy.md).

# Reading

Use `nature-reader` when available for detailed Chinese-English reading, aligned equations, figures, and tables. Use `liteparse` for local PDF layout extraction. Use `open-notebook` only when a persistent multi-document notebook is useful. If these adapters are absent, use the available local PDF-reading tools without inventing inaccessible content.

Read full text when extracting experimental details. If only the abstract was available, record `full_text_status: "abstract-only"` and mark result details as provisional.

# Evidence Cards

Write `corpus/notes/<paper_id>.json` using the required evidence schema. Include:

- problem, method, datasets, baselines, and metrics;
- result statements grounded in a section, table, figure, page, or abstract;
- limitations;
- project claim IDs supported by the paper;
- source URL and retrieval date;
- preprint or peer-review status.

Do not convert benchmark gains into general superiority claims. Do not invent missing baselines or metrics.

# Evidence Matrix

Maintain one row per included paper in `analysis/evidence_matrix.csv`. Keep `paper_id` and `bib_key` aligned with `corpus/index.csv`.

When every included paper has a complete card and matrix row, validate G3 with `--write`. G3 has no human decision gate.

# Boundaries

- Do not write thematic synthesis.
- Do not add papers.
- Do not resolve conflicts by majority vote.
- Do not cite a paper that lacks a frozen corpus row.
