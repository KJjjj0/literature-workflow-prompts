from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import (
    file_has_content,
    has_human_decision,
    load_decisions,
    load_json,
    read_csv,
    safe_project_root,
    write_json,
)


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
GATE_DEFINITIONS = load_json(PLUGIN_ROOT / "references" / "gates.json")
GATE_ORDER: list[str] = GATE_DEFINITIONS["order"]
GATES: dict[str, dict[str, Any]] = GATE_DEFINITIONS["gates"]

ALLOWED_BY_GATE = {
    "G0": {
        "search": False,
        "reading": False,
        "synthesis": False,
        "drafting": False,
        "citation_export": False,
        "final_export": False,
    },
    "G1": {
        "search": True,
        "reading": False,
        "synthesis": False,
        "drafting": False,
        "citation_export": False,
        "final_export": False,
    },
    "G2": {
        "search": True,
        "reading": True,
        "synthesis": False,
        "drafting": False,
        "citation_export": False,
        "final_export": False,
    },
    "G3": {
        "search": True,
        "reading": True,
        "synthesis": False,
        "drafting": False,
        "citation_export": False,
        "final_export": False,
    },
    "G4": {
        "search": True,
        "reading": True,
        "synthesis": True,
        "drafting": False,
        "citation_export": False,
        "final_export": False,
    },
    "G5": {
        "search": True,
        "reading": True,
        "synthesis": True,
        "drafting": True,
        "citation_export": False,
        "final_export": False,
    },
    "G6": {
        "search": True,
        "reading": True,
        "synthesis": True,
        "drafting": True,
        "citation_export": True,
        "final_export": False,
    },
    "G7": {
        "search": True,
        "reading": True,
        "synthesis": True,
        "drafting": True,
        "citation_export": True,
        "final_export": False,
    },
    "G8": {
        "search": True,
        "reading": True,
        "synthesis": True,
        "drafting": True,
        "citation_export": True,
        "final_export": True,
    },
}

EVIDENCE_FIELDS = {
    "paper_id",
    "title",
    "year",
    "venue",
    "status",
    "problem",
    "method",
    "datasets",
    "baselines",
    "metrics",
    "main_results",
    "limitations",
    "claims_supported",
    "quality",
    "provenance",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a literature workflow gate.")
    parser.add_argument("--project", required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--gate", choices=GATE_ORDER)
    group.add_argument("--next", action="store_true")
    parser.add_argument("--write", action="store_true")
    return parser


def require_text(path: Path, headings: tuple[str, ...] = ()) -> list[str]:
    if not file_has_content(path):
        return [f"missing or unresolved content: {path}"]
    text = path.read_text(encoding="utf-8")
    return [f"missing heading {heading}: {path}" for heading in headings if heading not in text]


def require_decision(project: Path, decision_type: str | None) -> list[str]:
    if not decision_type:
        return []
    decisions = load_decisions(project / "planning" / "decisions.jsonl")
    if not has_human_decision(decisions, decision_type):
        return [f"missing human decision: {decision_type}"]
    return []


def require_csv_fields(
    path: Path,
    required: set[str],
    minimum_rows: int = 0,
) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [f"missing CSV: {path}"], []
    fields, rows = read_csv(path)
    errors = [
        f"missing CSV field {field}: {path}"
        for field in required
        if field not in fields
    ]
    if len(rows) < minimum_rows:
        errors.append(f"expected at least {minimum_rows} row(s): {path}")
    return errors, rows


def validate_g0(project: Path) -> list[str]:
    errors = require_text(
        project / "planning" / "question_card.md",
        (
            "## Research question",
            "## Scope",
            "## Success criteria",
            "## Output form",
        ),
    )
    errors += require_decision(project, "scope_approval")
    return errors


def validate_g1(project: Path) -> list[str]:
    errors = require_text(
        project / "search" / "search_protocol.md",
        (
            "## Sources",
            "## Queries",
            "## Date range",
            "## Inclusion criteria",
            "## Exclusion criteria",
        ),
    )
    errors += require_decision(project, "search_protocol_approval")
    return errors


def validate_g2(project: Path) -> list[str]:
    errors: list[str] = []
    raw_errors, raw_rows = require_csv_fields(
        project / "search" / "raw_results.csv",
        {"paper_id", "title", "source", "retrieved_at"},
        minimum_rows=1,
    )
    screening_errors, screening_rows = require_csv_fields(
        project / "search" / "screening.csv",
        {"paper_id", "decision", "reason"},
        minimum_rows=1,
    )
    corpus_errors, corpus_rows = require_csv_fields(
        project / "corpus" / "index.csv",
        {"paper_id", "title", "bib_key", "status"},
        minimum_rows=1,
    )
    errors += raw_errors + screening_errors + corpus_errors
    if raw_rows and len(screening_rows) == 0:
        errors.append("screening.csv must contain screening decisions")
    corpus_ids = {row.get("paper_id", "").strip() for row in corpus_rows}
    if "" in corpus_ids:
        errors.append("every corpus row requires paper_id")
    screened_ids = {row.get("paper_id", "").strip() for row in screening_rows}
    missing = sorted(corpus_ids - screened_ids)
    if missing:
        errors.append("included corpus papers lack screening decisions: " + ", ".join(missing))
    errors += require_decision(project, "corpus_freeze")
    return errors


def validate_g3(project: Path) -> list[str]:
    corpus_errors, corpus_rows = require_csv_fields(
        project / "corpus" / "index.csv",
        {"paper_id", "title", "bib_key", "status"},
        minimum_rows=1,
    )
    matrix_errors, matrix_rows = require_csv_fields(
        project / "analysis" / "evidence_matrix.csv",
        {"paper_id", "bib_key", "method", "main_results", "quality"},
        minimum_rows=1,
    )
    errors = corpus_errors + matrix_errors
    matrix_ids = {row.get("paper_id", "").strip() for row in matrix_rows}
    for row in corpus_rows:
        paper_id = row.get("paper_id", "").strip()
        note_path = project / "corpus" / "notes" / f"{paper_id}.json"
        if not note_path.exists():
            errors.append(f"missing evidence card: {note_path}")
            continue
        try:
            card = load_json(note_path, {})
        except json.JSONDecodeError as exc:
            errors.append(f"invalid evidence card JSON {note_path}: {exc}")
            continue
        missing = sorted(EVIDENCE_FIELDS - set(card))
        if missing:
            errors.append(f"evidence card {paper_id} missing fields: {', '.join(missing)}")
        if card.get("paper_id") != paper_id:
            errors.append(f"evidence card ID mismatch: {paper_id}")
        if paper_id not in matrix_ids:
            errors.append(f"paper missing from evidence matrix: {paper_id}")
    return errors


def validate_g4(project: Path) -> list[str]:
    path = project / "analysis" / "quality_report.json"
    if not path.exists():
        return [f"missing quality report: {path}"]
    try:
        report = load_json(path, {})
    except json.JSONDecodeError as exc:
        return [f"invalid quality report JSON: {exc}"]
    errors: list[str] = []
    if str(report.get("status", "")).upper() != "PASS":
        errors.append("quality report status must be PASS")
    papers = report.get("papers", {})
    if not isinstance(papers, dict) or not papers:
        errors.append("quality report requires a non-empty papers object")
    _, corpus_rows = read_csv(project / "corpus" / "index.csv")
    for row in corpus_rows:
        paper_id = row.get("paper_id", "").strip()
        assessment = papers.get(paper_id) if isinstance(papers, dict) else None
        if not isinstance(assessment, dict):
            errors.append(f"quality report missing paper: {paper_id}")
            continue
        if assessment.get("quality") not in {"high", "medium", "low"}:
            errors.append(f"quality report unassessed paper: {paper_id}")
    errors += require_decision(project, "quality_scope_approval")
    return errors


def validate_g5(project: Path) -> list[str]:
    errors = require_text(project / "analysis" / "gap_map.md", ("##",))
    errors += require_text(project / "synthesis" / "review_outline.md", ("##",))
    errors += require_decision(project, "synthesis_approval")
    return errors


def validate_g6(project: Path) -> list[str]:
    draft = project / "writing" / "related_work.md"
    errors = require_text(draft, ("#",))
    if not errors and not re.search(r"\[@[A-Za-z0-9_.:-]+", draft.read_text(encoding="utf-8")):
        errors.append("draft requires at least one Pandoc citation such as [@bib_key]")
    return errors


def validate_g7(project: Path) -> list[str]:
    bib = project / "references" / "references.bib"
    audit = project / "audit" / "citations.json"
    errors: list[str] = []
    if not bib.exists() or not re.search(r"@\w+\s*\{\s*[^,\s]+", bib.read_text(encoding="utf-8")):
        errors.append("references.bib requires at least one BibTeX entry")
    if not audit.exists():
        errors.append(f"missing citation audit: {audit}")
    else:
        try:
            report = load_json(audit, {})
        except json.JSONDecodeError as exc:
            errors.append(f"invalid citation audit JSON: {exc}")
        else:
            if str(report.get("status", "")).upper() != "PASS":
                errors.append("citation audit status must be PASS")
    return errors


def validate_g8(project: Path) -> list[str]:
    errors: list[str] = []
    for relative in ("audit/consistency.json", "audit/final_audit.json"):
        path = project / relative
        if not path.exists():
            errors.append(f"missing audit: {path}")
            continue
        try:
            report = load_json(path, {})
        except json.JSONDecodeError as exc:
            errors.append(f"invalid audit JSON {path}: {exc}")
            continue
        if str(report.get("status", "")).upper() != "PASS":
            errors.append(f"audit status must be PASS: {path}")
    errors += require_decision(project, "submission_approval")
    return errors


VALIDATORS = {
    "G0": validate_g0,
    "G1": validate_g1,
    "G2": validate_g2,
    "G3": validate_g3,
    "G4": validate_g4,
    "G5": validate_g5,
    "G6": validate_g6,
    "G7": validate_g7,
    "G8": validate_g8,
}


def evaluate_through(project: Path, target: str) -> tuple[list[str], str | None]:
    completed: list[str] = []
    for gate_id in GATE_ORDER:
        errors = VALIDATORS[gate_id](project)
        if errors:
            return errors, gate_id
        completed.append(gate_id)
        if gate_id == target:
            return [], gate_id
    return [], target


def update_manifest(project: Path, passed_gate: str) -> None:
    path = project / "planning" / "manifest.json"
    manifest = load_json(path, {})
    completed = GATE_ORDER[: GATE_ORDER.index(passed_gate) + 1]
    next_index = GATE_ORDER.index(passed_gate) + 1
    next_gate = GATE_ORDER[next_index] if next_index < len(GATE_ORDER) else "DONE"
    next_skill = GATES[passed_gate].get("next_skill")
    manifest.update(
        {
            "current_gate": next_gate,
            "last_passed_gate": passed_gate,
            "status": (
                "workflow_complete"
                if next_gate == "DONE"
                else f"awaiting_{GATES[next_gate]['name'].casefold()}"
            ),
            "completed_gates": completed,
            "allowed": ALLOWED_BY_GATE[passed_gate],
            "blockers": [] if next_gate == "DONE" else [f"next gate: {next_gate}"],
            "next_action": {
                "owner": "workflow",
                "skill": next_skill,
                "reason": (
                    "workflow complete"
                    if not next_skill
                    else f"advance {next_gate} with {next_skill}"
                ),
            },
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    write_json(path, manifest)


def main() -> int:
    args = build_parser().parse_args()
    project = safe_project_root(args.project)
    manifest_path = project / "planning" / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Missing project manifest: {manifest_path}")

    if args.next or not args.gate:
        target = "G8"
    else:
        target = args.gate

    errors, failed_gate = evaluate_through(project, target)
    result: dict[str, Any] = {
        "status": "FAIL" if errors else "PASS",
        "target_gate": target,
        "failed_gate": failed_gate if errors else None,
        "errors": errors,
    }
    if not errors:
        result["next_action"] = GATES[target].get("next_skill")
        if args.write:
            update_manifest(project, target)
            result["manifest_updated"] = True
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
