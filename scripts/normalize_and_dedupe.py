from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import (
    dedupe_key,
    normalize_arxiv,
    normalize_doi,
    read_csv,
    stable_paper_id,
    write_csv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize and deduplicate paper search results.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing output file.",
    )
    return parser


def merge_rows(existing: dict[str, str], candidate: dict[str, str]) -> dict[str, str]:
    merged = dict(existing)
    for key, value in candidate.items():
        if value and not merged.get(key):
            merged[key] = value
    sources = sorted(
        {
            part.strip()
            for value in (existing.get("source", ""), candidate.get("source", ""))
            for part in value.split(";")
            if part.strip()
        }
    )
    merged["source"] = ";".join(sources)
    if len(candidate.get("abstract", "")) > len(existing.get("abstract", "")):
        merged["abstract"] = candidate["abstract"]
    return merged


def main() -> int:
    args = build_parser().parse_args()
    input_path = Path(args.input).resolve()
    output_path = (
        Path(args.output).resolve()
        if args.output
        else input_path.with_name("deduped.csv")
    )
    if output_path.exists() and not args.overwrite:
        raise SystemExit(f"Refusing to overwrite existing output: {output_path}")
    fields, rows = read_csv(input_path)
    for field in ("paper_id", "title", "doi", "arxiv_id", "source"):
        if field not in fields:
            fields.append(field)
    if "dedupe_key" not in fields:
        fields.append("dedupe_key")

    merged: dict[str, dict[str, str]] = {}
    duplicate_count = 0
    for row in rows:
        row = {key: str(value or "").strip() for key, value in row.items()}
        row["doi"] = normalize_doi(row.get("doi"))
        row["arxiv_id"] = normalize_arxiv(row.get("arxiv_id"))
        key = dedupe_key(row)
        row["dedupe_key"] = key
        row["paper_id"] = row.get("paper_id") or stable_paper_id(row)
        if key in merged:
            duplicate_count += 1
            merged[key] = merge_rows(merged[key], row)
        else:
            merged[key] = row

    write_csv(output_path, fields, merged.values())
    print(
        json.dumps(
            {
                "status": "PASS",
                "input_rows": len(rows),
                "output_rows": len(merged),
                "duplicates_removed": duplicate_count,
                "output": str(output_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
