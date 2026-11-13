---
name: search-protocol-builder
description: Design and document a reproducible paper-search protocol for an approved AI research scope. Use at G1 to select sources, queries, date limits, and inclusion criteria before searching; do not synthesize papers.
---

# Purpose

Turn the approved research question into an auditable search strategy.

Read [workflow policy](../../references/workflow-policy.md), [gate contract](../../references/gate-contract.md), and [search policy](../../references/search-policy.md).

# Required Artifact

Complete `search/search_protocol.md` with:

- exact queries and synonyms;
- source priority and exclusions;
- date range and justification;
- paper, preprint, venue, and language constraints;
- inclusion and exclusion criteria;
- title, abstract, and full-text screening rules;
- handling of CNKI and Wanfang records;
- expected result budget;
- how duplicate papers and versions are resolved.

Default AI sources are arXiv, OpenAlex, Crossref, Semantic Scholar, OpenReview, and official proceedings. Never treat Google Scholar as the only source.

# Approval

When the user replies `批准`, `同意`, `认可`, or `OK`, append `search_protocol_approval` using the standardized approval record. Do not ask for a separate rationale. Validate G1 with `--write`.

# Boundaries

- Do not run the broad search before approval.
- Do not select papers.
- Do not draft the review.
- If the scope changes, return to `research-scope-builder`.
