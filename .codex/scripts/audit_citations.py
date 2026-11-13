from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import (
    load_json,
    normalize_arxiv,
    normalize_doi,
    project_path,
    read_csv,
    safe_project_root,
    write_json,
)


BIB_ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)")
BRACKET_CITATION_RE = re.compile(r"\[([^\]]*@[^\]]+)\]")
LATEX_CITATION_RE = re.compile(r"\\cite[a-zA-Z]*\s*\{([^}]+)\}")
KEY_RE = re.compile(r"@([A-Za-z0-9_.:-]+)")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
ARXIV_RE = re.compile(r"^\d{4}\.\d{4,5}$|^[a-z.-]+/\d{7}$", re.IGNORECASE)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit manuscript citations against the corpus.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--draft", default="writing/related_work.md")
    parser.add_argument("--write", action="store_true")
    return parser


def extract_citation_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for match in BRACKET_CITATION_RE.finditer(text):
        keys.update(KEY_RE.findall(match.group(1)))
    for match in LATEX_CITATION_RE.finditer(text):
        keys.update(part.strip() for part in match.group(1).split(",") if part.strip())
    return keys


def main() -> int:
    args = build_parser().parse_args()
    project = safe_project_root(args.project)
    draft_path = project_path(project, args.draft)
    bib_path = project_path(project, "references/references.bib")
    errors: list[str] = []
    warnings: list[str] = []

    if not draft_path.exists():
        raise SystemExit(f"Missing draft: {draft_path}")
    if not bib_path.exists():
        raise SystemExit(f"Missing bibliography: {bib_path}")

    draft_text = draft_path.read_text(encoding="utf-8")
    bib_text = bib_path.read_text(encoding="utf-8")
    cited_keys = extract_citation_keys(draft_text)
    bib_keys = set(BIB_ENTRY_RE.findall(bib_text))
    _, corpus_rows = read_csv(project_path(project, "corpus/index.csv"))
    corpus_by_bib = {
        row.get("bib_key", "").strip(): row
        for row in corpus_rows
        if row.get("bib_key", "").strip()
    }

    missing_from_bib = sorted(cited_keys - bib_keys)
    if missing_from_bib:
        errors.append("citations missing from references.bib: " + ", ".join(missing_from_bib))
    missing_from_corpus = sorted(cited_keys - set(corpus_by_bib))
    if missing_from_corpus:
        errors.append("citations missing from frozen corpus: " + ", ".join(missing_from_corpus))
    if not cited_keys:
        errors.append("draft contains no recognized citation keys")

    for row in corpus_rows:
        doi = normalize_doi(row.get("doi"))
        arxiv_id = normalize_arxiv(row.get("arxiv_id"))
        if doi and not DOI_RE.match(doi):
            errors.append(f"invalid DOI in corpus for {row.get('paper_id')}: {doi}")
        if arxiv_id and not ARXIV_RE.match(arxiv_id):
            errors.append(f"invalid arXiv ID in corpus for {row.get('paper_id')}: {arxiv_id}")
        if row.get("bib_key") and row.get("bib_key") not in bib_keys:
            warnings.append(f"corpus bibliography key not present in BibTeX: {row.get('bib_key')}")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "draft": str(draft_path),
        "bibliography": str(bib_path),
        "cited_keys": sorted(cited_keys),
        "bibliography_keys": sorted(bib_keys),
        "errors": errors,
        "warnings": warnings,
    }
    if args.write:
        write_json(project_path(project, "audit/citations.json"), report)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
