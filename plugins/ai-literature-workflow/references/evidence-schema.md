# Evidence Card Contract

Each included paper receives one JSON file at `corpus/notes/<paper_id>.json`.

Required fields:

- `paper_id`: stable project identifier.
- `title`: exact paper title.
- `year`: integer publication year.
- `venue`: publication venue or preprint server.
- `status`: `preprint`, `peer-reviewed`, `survey`, or `unknown`.
- `problem`: research problem addressed by the paper.
- `method`: core method or model.
- `datasets`: array of datasets.
- `baselines`: array of compared baselines.
- `metrics`: array of evaluation metrics.
- `main_results`: array of evidence-linked result statements.
- `limitations`: array of stated or demonstrated limitations.
- `claims_supported`: array of project claim IDs supported by this paper.
- `quality`: `high`, `medium`, `low`, or `unassessed`.
- `provenance`: object containing `source`, `url`, and `retrieved_at`.

Optional fields include `doi`, `arxiv_id`, `bib_key`, `full_text_status`, `notes`, and `risk_flags`.

The evidence matrix must contain one row per included paper and may duplicate shared fields for downstream tooling. Result statements without a page, section, table, figure, abstract, or full-text source remain provisional.
