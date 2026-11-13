# Search Policy

## Default AI Sources

1. arXiv for preprints and recent work.
2. OpenAlex and Crossref for metadata, DOI, venues, and citation relationships.
3. Semantic Scholar for related-paper and citation-graph discovery.
4. OpenReview and official conference proceedings for peer-reviewed AI work.
5. Exa or general web retrieval for project pages, code, and conference information.

## Chinese-Language Sources

CNKI and Wanfang are not covered by the bundled search adapter. Import their records manually into `search/raw_results.csv` and preserve the retrieval date and source URL or accession number.

## Query Logging

Every query records:

- query text;
- source;
- date range;
- filters;
- retrieval date;
- number of results returned;
- whether results were opened or only inspected as metadata.

## Deduplication

Use this order:

1. normalized DOI;
2. normalized arXiv ID;
3. normalized title plus year.

Keep all source provenance when merging duplicate records.

## Screening

Title and abstract screening records one of `include`, `exclude`, or `maybe`, with a concrete reason. Full-text screening follows the approved inclusion and exclusion criteria. Human approval is required before freezing the corpus.
