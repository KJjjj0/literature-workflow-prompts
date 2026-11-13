---
name: research-scope-builder
description: Build and revise the research question and scope for an AI literature project. Use at G0 to define an answerable question, application context, boundaries, date range, and success criteria before search planning.
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

When the user replies `批准`, `同意`, `认可`, or `OK`, append a `scope_approval` decision using the standardized approval record. Do not request a separate free-text reason. Then validate G0 with `--write`.

# Boundaries

- Do not design database queries or run searches. Use `search-protocol-builder` after G0.
- Do not write Related Work.
- Do not create evidence claims.
- Do not infer the user's research priorities.
- Do not hide a trade-off between recency, peer-review status, and coverage.
