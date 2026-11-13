---
name: citation-and-venue-auditor
description: Verify citations, BibTeX, identifiers, and venue formatting for an approved literature draft. Use at G7 after drafting; do not use to invent missing metadata or finalize unsupported claims.
---

# Purpose

Make the draft bibliographically traceable and venue-ready.

Read [gate contract](../../references/gate-contract.md), [writing policy](../../references/writing-policy.md), and [audit contract](../../references/audit-contract.md). Use `citation-management` when available for DOI metadata and BibTeX. Use `pyzotero` only when a Zotero library is explicitly in scope. Use `venue-templates` after the target venue is known. If adapters are absent, verify metadata manually against authoritative source pages and record provenance.

# Bibliography

- Create `references/references.bib` from verified metadata.
- Ensure every included corpus `bib_key` is unique.
- Preserve DOI, arXiv ID, venue, year, and publication status.
- Do not fabricate missing metadata.
- Mark manually entered CNKI or Wanfang records with their actual source.

# Citation Audit

Run:

```powershell
python ../../scripts/audit_citations.py --project <project-root> --write
```

Resolve every `FAIL`. The report is written to `audit/citations.json`.

# Venue Formatting

Check the target venue's current official template, page limit, anonymity rules, reference style, and supplementary-material rules. Do not claim compliance without inspecting the actual template or submission PDF.

After citation audit passes and formatting checks are complete, validate G7 with `--write`.

# Boundaries

- Do not add citations merely to increase reference count.
- Do not change substantive claims to make a citation fit.
- Do not treat metadata from an unopened source as verified.
- Do not package the submission at this stage.
