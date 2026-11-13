---
name: research-scope-builder
description: Build and revise the research question and search protocol for an AI literature project. Use at G0 or G1 to define an answerable question, scope, date range, sources, queries, and inclusion criteria before searching.
---

# Purpose

Create the human-owned research frame and the reproducible search plan.

Read [workflow policy](../../references/workflow-policy.md), [gate contract](../../references/gate-contract.md), [search policy](../../references/search-policy.md), and [writing policy](../../references/writing-policy.md).

# G0 Scope

Complete `planning/question_card.md` with:

- answerable research question;
- AI task and application context;
- methods and systems in scope;
- adjacent topics out of scope;
- publication-date range;
- evidence-backed success criteria;
- required output form.

Use `hypothesis-generation` when available to make claims and expected evidence testable.

After the user explicitly approves the question and scope, append a `scope_approval` decision. Then validate G0 with `--write`.

# G1 Search Protocol

Complete `search/search_protocol.md` with:

- exact queries and synonyms;
- arXiv, OpenAlex, Crossref, Semantic Scholar, OpenReview, official proceedings, and optional web sources;
- date range;
- inclusion and exclusion criteria;
- title, abstract, and full-text screening method;
- handling of CNKI and Wanfang manual imports.

Do not run a broad search before the protocol is approved. Avoid treating Google Scholar as the only source.

After the user explicitly approves the protocol, append `search_protocol_approval`. Validate G1 with `--write`.

# Boundaries

- Do not write Related Work.
- Do not create evidence claims.
- Do not infer the user's research priorities.
- Do not hide a trade-off between recency, peer-review status, and coverage.
