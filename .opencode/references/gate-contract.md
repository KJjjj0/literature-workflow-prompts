# Gate Contract

## State Model

The project manifest is the machine-readable state source. Human approvals are stored in an append-only JSONL ledger. A gate passes only when its required artifacts exist, contain no unresolved placeholders, and the required human decision is present.

| Gate | Status | Required artifacts | Required human decision |
|---|---|---|---|
| G0 | `RESEARCH_SCOPE_FROZEN` | `planning/question_card.md` | `scope_approval` |
| G1 | `SEARCH_PROTOCOL_APPROVED` | `search/search_protocol.md` | `search_protocol_approval` |
| G2 | `CORPUS_FROZEN` | `search/raw_results.csv`, `search/screening.csv`, `corpus/index.csv` | `corpus_freeze` |
| G2.5 | `CORPUS_RISK_SCREENED` | `analysis/corpus_risk_report.json` | none |
| G3 | `EVIDENCE_EXTRACTED` | Evidence card for every included paper, `analysis/evidence_matrix.csv` | none |
| G4 | `QUALITY_JUDGED` | `analysis/quality_report.json` | `quality_scope_approval` |
| G5 | `SYNTHESIS_APPROVED` | `analysis/gap_map.md`, `synthesis/review_outline.md` | `synthesis_approval` |
| G6 | `DRAFT_READY` | `writing/related_work.md` | none |
| G7 | `CITATIONS_VERIFIED` | `references/references.bib`, `audit/citations.json` | none |
| G7.5 | `CONSISTENCY_AUDITED` | `audit/consistency.json` | none |
| G7.8 | `COMPLETENESS_AUDITED` | `audit/completeness.json` | none |
| G8 | `FINAL_AUDIT_PASSED` | `audit/consistency.json`, `audit/completeness.json`, `audit/final_audit.json` | `submission_approval` |

## Allowed Actions After a Passed Gate

- After G0: design the search protocol.
- After G1: run searches and screen candidates.
- After G2: read included papers and extract evidence.
- After G2.5: read included papers and extract evidence.
- After G3: judge evidence quality and claim support.
- After G4: synthesize themes and research gaps.
- After G5: draft sections from the approved synthesis and evidence matrix.
- After G6: generate and audit citations and venue formatting.
- After G7: run final consistency and quality audits.
- After G7.5: run completeness audit.
- After G7.8: run final quality audit.
- After G8: package the approved research artifacts.

## Invalid Transitions

- Do not draft Related Work before G5.
- Do not add a new paper after G2 without reopening screening and affected evidence.
- Do not change a supported claim without reopening G4 through G8.
- Do not package a submission when any audit is missing or stale.
