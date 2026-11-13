---
name: corpus-screener
description: Execute and document literature searches, deduplicate candidates, and produce a frozen included-paper corpus. Use at G2 after an approved search protocol; do not use for prose synthesis.
---

# Purpose

Convert the approved search plan into a reproducible candidate set and frozen corpus.

Read `../../AGENTS.md`, [gate contract](../../references/gate-contract.md), [search policy](../../references/search-policy.md), and [evidence schema](../../references/evidence-schema.md).

# Search

Use `paper-lookup` as the primary scholarly search adapter when available. Use `exa-search` or `parallel-web` for OpenReview, official conference pages, project pages, and current web evidence when appropriate. If a search adapter is unavailable, work only from user-provided exports and other verified tools; never recreate search results from model memory.

For every query, append to `search/queries.jsonl`:

```json
{
  "query": "...",
  "source": "arXiv",
  "date_range": "2022-2026",
  "filters": "...",
  "retrieved_at": "ISO-8601",
  "result_count": 42,
  "metadata_opened": false
}
```

Store returned records in `search/raw_results.csv` without deleting raw observations.

# Deduplication

Run:

```powershell
python ../../scripts/normalize_and_dedupe.py --input <project>/search/raw_results.csv --output <project>/search/deduped.csv
```

Do not merge two genuinely different papers merely because titles are similar. Preserve source provenance when duplicates are merged.

# Screening

Record title and abstract decisions in `search/screening.csv` with `include`, `exclude`, or `maybe`, plus a concrete reason. Apply the approved criteria consistently.

Build `corpus/index.csv` only from included papers. Each row requires a stable `paper_id` and planned `bib_key`.

After full-text screening is complete and the user explicitly approves the included set, append `corpus_freeze`. Validate G2 with `--write`.

# Boundaries

- Do not draft.
- Do not use citation counts as a substitute for relevance.
- Do not silently add papers after the corpus is frozen.
- Reopen G2 when a new essential paper is introduced.
