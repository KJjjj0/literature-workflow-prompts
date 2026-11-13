from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

from common import is_relative_to, load_json, project_path, reject_symlink_chain, safe_project_root


PACKAGE_PATHS = (
    "planning/manifest.json",
    "planning/session_config.json",
    "planning/decisions.jsonl",
    "planning/question_card.md",
    "search/search_protocol.md",
    "search/queries.jsonl",
    "search/raw_results.csv",
    "search/deduped.csv",
    "search/screening.csv",
    "corpus/index.csv",
    "corpus/notes",
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
    "audit/completeness.json",
    "audit/final_audit.json",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package a G8-approved literature project.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    project = safe_project_root(args.project)
    manifest = load_json(project / "planning" / "manifest.json", {})
    if manifest.get("last_passed_gate") != "G8":
        raise SystemExit("Refusing package: the manifest has not passed G8.")
    for relative in ("audit/citations.json", "audit/consistency.json", "audit/final_audit.json"):
        report = load_json(project / relative, {})
        if str(report.get("status", "")).upper() != "PASS":
            raise SystemExit(f"Refusing package: audit is not PASS: {relative}")

    output = (
        Path(args.output).resolve()
        if args.output
        else project / "research-package.zip"
    )
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing package: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    packaged: list[str] = []
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in PACKAGE_PATHS:
            source = project_path(project, relative)
            if not source.exists():
                raise SystemExit(f"Missing required package artifact: {source}")
            if source.is_dir():
                for file_path in sorted(source.rglob("*")):
                    if file_path.is_file():
                        reject_symlink_chain(project, file_path)
                        archive.write(file_path, file_path.relative_to(project).as_posix())
                        packaged.append(file_path.relative_to(project).as_posix())
            else:
                reject_symlink_chain(project, source)
                archive.write(source, source.relative_to(project).as_posix())
                packaged.append(source.relative_to(project).as_posix())
    print(
        json.dumps(
            {
                "status": "PASS",
                "package": str(output),
                "files": len(packaged),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
