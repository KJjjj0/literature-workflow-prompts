from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from common import safe_project_root, write_csv, write_json


RAW_FIELDS = [
    "paper_id",
    "title",
    "authors",
    "year",
    "venue",
    "doi",
    "arxiv_id",
    "url",
    "abstract",
    "source",
    "retrieved_at",
    "status",
    "citation_count",
]

SCREENING_FIELDS = [
    "paper_id",
    "title",
    "decision",
    "reason",
    "screener",
    "screened_at",
]

CORPUS_FIELDS = [
    "paper_id",
    "title",
    "year",
    "venue",
    "doi",
    "arxiv_id",
    "bib_key",
    "status",
    "note_path",
]

EVIDENCE_FIELDS = [
    "paper_id",
    "bib_key",
    "problem",
    "method",
    "datasets",
    "baselines",
    "metrics",
    "main_results",
    "limitations",
    "quality",
    "claims_supported",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize a gated literature project.")
    parser.add_argument("--root", required=True, help="Research project directory.")
    parser.add_argument("--project-id", default="lit-project")
    parser.add_argument("--title", default="Untitled literature project")
    parser.add_argument(
        "--profile",
        choices=("quick", "review", "submission"),
        default="review",
    )
    return parser


def write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    args = build_parser().parse_args()
    root = safe_project_root(args.root)
    if (root / "planning" / "manifest.json").exists():
        raise SystemExit(f"Project already initialized: {root}")

    for relative in (
        "planning",
        "search",
        "corpus/notes",
        "analysis",
        "synthesis",
        "writing",
        "references",
        "audit",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)

    created_at = datetime.now(timezone.utc).isoformat()
    write_if_missing(root / "planning" / "decisions.jsonl", "")
    write_json(
        root / "planning" / "session_config.json",
        {
            "project_id": args.project_id,
            "title": args.title,
            "profile": args.profile,
            "interaction_mode": "guided",
            "default_language": "zh-CN",
        },
    )
    write_json(
        root / "planning" / "manifest.json",
        {
            "schema_version": 1,
            "project_id": args.project_id,
            "title": args.title,
            "profile": args.profile,
            "current_gate": "G0",
            "status": "research_scope_in_progress",
            "completed_gates": [],
            "allowed": {
                "search": False,
                "reading": False,
                "synthesis": False,
                "drafting": False,
                "citation_export": False,
                "final_export": False,
            },
            "blockers": ["human-approved research scope is missing"],
            "next_action": {
                "owner": "human",
                "skill": "research-scope-builder",
                "reason": "define and approve the research question and scope",
            },
            "updated_at": created_at,
        },
    )
    write_if_missing(
        root / "planning" / "question_card.md",
        f"""# Research Question Card

## Project title

{args.title}

## Research question

[TODO: State one answerable research question.]

## Why it matters

[TODO: Explain the AI research problem and expected contribution.]

## Scope

[TODO: Define task, models, data, systems, populations, or methods in scope.]

## Out of scope

[TODO: Define adjacent topics that will not be reviewed.]

## Time range

[TODO: State the publication-date range and rationale.]

## Success criteria

[TODO: Define what a sufficient evidence base and answer look like.]

## Output form

[TODO: Choose course report, thesis chapter, systematic review, proposal, or manuscript section.]
""",
    )
    write_if_missing(
        root / "search" / "search_protocol.md",
        """# Search Protocol

## Sources

[TODO: List arXiv, OpenAlex, Crossref, Semantic Scholar, OpenReview, official proceedings, or manual sources.]

## Queries

[TODO: Record exact queries and synonyms.]

## Date range

[TODO: State the date range and rationale.]

## Inclusion criteria

[TODO: Define inclusion criteria.]

## Exclusion criteria

[TODO: Define exclusion criteria.]

## Screening process

[TODO: Define title, abstract, and full-text screening.]
""",
    )
    write_if_missing(root / "analysis" / "gap_map.md", "# Research Gap Map\n\n[TODO]\n")
    write_if_missing(
        root / "synthesis" / "review_outline.md",
        "# Review Outline\n\n[TODO]\n",
    )
    write_if_missing(
        root / "writing" / "related_work.md",
        "# Related Work\n\n[TODO]\n",
    )
    write_if_missing(root / "references" / "references.bib", "")
    write_csv(root / "search" / "raw_results.csv", RAW_FIELDS, [])
    write_csv(root / "search" / "deduped.csv", RAW_FIELDS, [])
    write_csv(root / "search" / "screening.csv", SCREENING_FIELDS, [])
    write_csv(root / "corpus" / "index.csv", CORPUS_FIELDS, [])
    write_csv(root / "analysis" / "evidence_matrix.csv", EVIDENCE_FIELDS, [])
    write_if_missing(root / "search" / "queries.jsonl", "")

    print(
        json.dumps(
            {
                "status": "PASS",
                "project_root": str(root),
                "current_gate": "G0",
                "next_action": "complete planning/question_card.md and record scope_approval",
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
