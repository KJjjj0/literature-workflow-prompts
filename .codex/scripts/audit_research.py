from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from common import (
    has_human_decision,
    load_decisions,
    load_json,
    project_path,
    read_csv,
    safe_project_root,
    text_has_placeholder,
    write_json,
)


BIB_ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic literature research audits.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--layer", required=True, choices=("consistency", "completeness", "final"))
    parser.add_argument("--write", action="store_true")
    return parser


def consistency_audit(project: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    _, corpus_rows = read_csv(project_path(project, "corpus/index.csv"))
    _, matrix_rows = read_csv(project_path(project, "analysis/evidence_matrix.csv"))
    corpus_ids = {row.get("paper_id", "").strip() for row in corpus_rows if row.get("paper_id")}
    matrix_ids = {row.get("paper_id", "").strip() for row in matrix_rows if row.get("paper_id")}
    if corpus_ids - matrix_ids:
        errors.append("papers missing from evidence matrix: " + ", ".join(sorted(corpus_ids - matrix_ids)))
    if matrix_ids - corpus_ids:
        errors.append("evidence matrix contains non-corpus papers: " + ", ".join(sorted(matrix_ids - corpus_ids)))
    for paper_id in sorted(corpus_ids):
        note_path = project_path(project, f"corpus/notes/{paper_id}.json")
        if not note_path.is_file():
            errors.append(f"missing evidence card: {paper_id}")
            continue
        card = load_json(note_path, {})
        if card.get("paper_id") != paper_id:
            errors.append(f"evidence-card ID mismatch: {paper_id}")
    bib_path = project_path(project, "references/references.bib")
    bib_keys = set(BIB_ENTRY_RE.findall(bib_path.read_text(encoding="utf-8")))
    corpus_keys = {row.get("bib_key", "").strip() for row in corpus_rows if row.get("bib_key")}
    if corpus_ids and not bib_keys:
        errors.append("bibliography is empty")
    if corpus_keys - bib_keys:
        warnings.append("corpus bibliography keys missing from BibTeX: " + ", ".join(sorted(corpus_keys - bib_keys)))
    citation_report = load_json(project_path(project, "audit/citations.json"), {})
    if str(citation_report.get("status", "")).upper() != "PASS":
        errors.append("citation audit has not passed")
    return {
        "status": "FAIL" if errors else "PASS",
        "layer": "consistency",
        "errors": errors,
        "warnings": warnings,
        "corpus_count": len(corpus_ids),
        "matrix_count": len(matrix_ids),
        "bibliography_keys": len(bib_keys),
    }


def completeness_audit(project: Path) -> dict[str, Any]:
    required = (
        "planning/manifest.json",
        "planning/decisions.jsonl",
        "planning/question_card.md",
        "search/search_protocol.md",
        "search/raw_results.csv",
        "search/screening.csv",
        "corpus/index.csv",
        "analysis/corpus_risk_report.json",
        "analysis/evidence_matrix.csv",
        "analysis/claim_evidence_map.csv",
        "analysis/quality_report.json",
        "analysis/gap_map.md",
        "synthesis/review_outline.md",
        "writing/related_work.md",
        "references/references.bib",
        "audit/citations.json",
        "audit/consistency.json",
    )
    missing = [relative for relative in required if not project_path(project, relative).exists()]
    placeholders: list[str] = []
    for relative in required:
        path = project_path(project, relative)
        if path.is_file() and path.suffix.lower() in {".md", ".json"}:
            if text_has_placeholder(path.read_text(encoding="utf-8")):
                placeholders.append(relative)
    _, corpus_rows = read_csv(project_path(project, "corpus/index.csv"))
    _, matrix_rows = read_csv(project_path(project, "analysis/evidence_matrix.csv"))
    _, claim_rows = read_csv(project_path(project, "analysis/claim_evidence_map.csv"))
    corpus_ids = {row.get("paper_id", "").strip() for row in corpus_rows if row.get("paper_id")}
    matrix_ids = {row.get("paper_id", "").strip() for row in matrix_rows if row.get("paper_id")}
    claim_ids = {
        row.get("paper_id", "").strip()
        for row in claim_rows
        if row.get("paper_id", "").strip()
    }
    errors = [f"missing required artifact: {relative}" for relative in missing]
    errors += [f"unresolved placeholder: {relative}" for relative in placeholders]
    if corpus_ids - matrix_ids:
        errors.append("evidence matrix is incomplete")
    if corpus_ids - claim_ids:
        errors.append("claim-evidence map is incomplete")
    return {
        "status": "FAIL" if errors else "PASS",
        "layer": "completeness",
        "errors": errors,
        "warnings": [],
        "required_count": len(required),
        "included_count": len(corpus_ids),
    }


def final_audit(project: Path) -> dict[str, Any]:
    errors: list[str] = []
    for relative in ("audit/citations.json", "audit/consistency.json", "audit/completeness.json"):
        report = load_json(project_path(project, relative), {})
        if str(report.get("status", "")).upper() != "PASS":
            errors.append(f"upstream audit must pass: {relative}")
    draft = project_path(project, "writing/related_work.md").read_text(encoding="utf-8")
    if text_has_placeholder(draft):
        errors.append("draft contains unresolved placeholders")
    decisions = load_decisions(project_path(project, "planning/decisions.jsonl"))
    if not has_human_decision(decisions, "submission_approval"):
        errors.append("missing human submission approval")
    return {
        "status": "FAIL" if errors else "PASS",
        "layer": "final",
        "errors": errors,
        "warnings": [],
    }


def main() -> int:
    args = build_parser().parse_args()
    project = safe_project_root(args.project)
    report = {
        "consistency": consistency_audit,
        "completeness": completeness_audit,
        "final": final_audit,
    }[args.layer](project)
    if args.write:
        output_name = "final_audit.json" if args.layer == "final" else f"{args.layer}.json"
        write_json(project_path(project, f"audit/{output_name}"), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
