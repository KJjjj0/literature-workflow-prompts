from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from common import (
    dedupe_key,
    load_json,
    normalize_arxiv,
    normalize_doi,
    project_path,
    read_csv,
    safe_project_root,
    write_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit frozen literature corpus coverage.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    project = safe_project_root(args.project)
    manifest = load_json(project / "planning" / "manifest.json", {})
    profile = str(manifest.get("profile", "review"))
    _, raw_rows = read_csv(project_path(project, "search/raw_results.csv"))
    _, screening_rows = read_csv(project_path(project, "search/screening.csv"))
    _, corpus_rows = read_csv(project_path(project, "corpus/index.csv"))

    corpus_ids = {row.get("paper_id", "").strip() for row in corpus_rows if row.get("paper_id")}
    raw_by_id = {row.get("paper_id", "").strip(): row for row in raw_rows}
    sources: set[str] = set()
    venues: set[str] = set()
    years: list[int] = []
    identifier_count = 0
    status_counts: Counter[str] = Counter()
    for paper_id in corpus_ids:
        row = raw_by_id.get(paper_id, {})
        for source in row.get("source", "").split(";"):
            if source.strip():
                sources.add(source.strip())
        if row.get("venue"):
            venues.add(row["venue"].strip())
        try:
            years.append(int(row.get("year", "")))
        except (TypeError, ValueError):
            pass
        if normalize_doi(row.get("doi")) or normalize_arxiv(row.get("arxiv_id")):
            identifier_count += 1
        status_counts[row.get("status", "unknown") or "unknown"] += 1

    screening_decisions = Counter(
        row.get("decision", "").strip().lower() for row in screening_rows
    )
    raw_keys = [dedupe_key(row) for row in raw_rows]
    duplicate_count = len(raw_keys) - len(set(raw_keys))
    included_count = len(corpus_ids)
    identifier_ratio = identifier_count / included_count if included_count else 0.0
    current_year = datetime.now(timezone.utc).year
    recent_count = sum(1 for year in years if year >= current_year - 4)
    year_span = (max(years) - min(years) + 1) if years else 0

    thresholds = {
        "quick": {"included": 3, "sources": 1, "year_span": 2, "identifiers": 0.4},
        "review": {"included": 8, "sources": 2, "year_span": 3, "identifiers": 0.5},
        "submission": {"included": 15, "sources": 3, "year_span": 5, "identifiers": 0.7},
    }
    required = thresholds.get(profile, thresholds["review"])
    warnings: list[str] = []
    blockers: list[str] = []
    if included_count == 0:
        blockers.append("frozen corpus is empty")
    if included_count < required["included"]:
        warnings.append(f"included corpus is below the {profile} target: {included_count} < {required['included']}")
    if len(sources) < required["sources"]:
        warnings.append(f"source diversity is low: {len(sources)} < {required['sources']}")
    if year_span < required["year_span"]:
        warnings.append(f"publication-year span is narrow: {year_span} < {required['year_span']}")
    if identifier_ratio < required["identifiers"]:
        warnings.append(
            f"DOI/arXiv coverage is low: {identifier_ratio:.0%} < {required['identifiers']:.0%}"
        )
    if screening_decisions.get("maybe", 0):
        warnings.append(f"unresolved maybe screening decisions: {screening_decisions['maybe']}")
    if not any(status == "peer-reviewed" for status in status_counts):
        warnings.append("no peer-reviewed record is present in the frozen corpus")
    for corpus_id in corpus_ids:
        row = raw_by_id.get(corpus_id)
        if not row:
            warnings.append(f"included paper missing from raw search results: {corpus_id}")
        elif not re.match(r"^(19|20)\d{2}$", row.get("year", "").strip()):
            warnings.append(f"missing or invalid publication year: {corpus_id}")

    status = "FAIL" if blockers else ("CONDITIONAL" if warnings else "PASS")
    report = {
        "status": status,
        "profile": profile,
        "counts": {
            "raw": len(raw_rows),
            "included": included_count,
            "duplicates_removed": duplicate_count,
            "recent_five_years": recent_count,
        },
        "coverage": {
            "sources": sorted(sources),
            "source_count": len(sources),
            "venues": sorted(venues),
            "venue_count": len(venues),
            "year_min": min(years) if years else None,
            "year_max": max(years) if years else None,
            "year_span": year_span,
            "identifier_count": identifier_count,
            "identifier_ratio": round(identifier_ratio, 4),
            "status_counts": dict(status_counts),
            "screening_counts": dict(screening_decisions),
        },
        "thresholds": required,
        "warnings": warnings,
        "blockers": blockers,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    if args.write:
        write_json(project_path(project, "analysis/corpus_risk_report.json"), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
