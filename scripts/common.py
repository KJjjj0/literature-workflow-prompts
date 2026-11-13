from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Iterable


PLACEHOLDER_PATTERNS = (
    "[TODO:",
    "TODO:",
    "TBD",
    "PLACEHOLDER",
    "[FILL",
    "<fill",
)


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def protected_roots() -> list[Path]:
    roots = [Path("/"), Path("/etc"), Path("/usr"), Path("/var")]
    if os.name == "nt":
        for variable in ("SystemRoot", "ProgramFiles", "ProgramFiles(x86)", "ProgramData"):
            value = os.environ.get(variable)
            if value:
                roots.append(Path(value))
    return roots


def safe_project_root(path: str | Path) -> Path:
    root = Path(path).expanduser().resolve()
    if root == Path(root.anchor):
        raise ValueError(f"Refusing filesystem root as project directory: {root}")
    for protected in protected_roots():
        protected = protected.resolve()
        if root == protected or is_relative_to(root, protected):
            raise ValueError(f"Refusing protected directory as project root: {root}")
    return root


def project_path(project: Path, value: str | Path) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = project / candidate
    resolved = candidate.resolve()
    if not is_relative_to(resolved, project):
        raise ValueError(f"Path escapes project root: {value}")
    return resolved


def reject_symlink_chain(project: Path, path: Path) -> None:
    current = project
    for part in path.relative_to(project).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Refusing symlink in project artifact path: {current}")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    return fields, rows


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def normalize_text(value: Any) -> str:
    text = str(value or "").casefold()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_doi(value: Any) -> str:
    text = str(value or "").strip().casefold()
    text = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", text)
    text = re.sub(r"^doi:\s*", "", text)
    return text.strip()


def normalize_arxiv(value: Any) -> str:
    text = str(value or "").strip().casefold()
    text = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "", text)
    text = re.sub(r"^arxiv:\s*", "", text)
    text = re.sub(r"\.pdf$", "", text)
    text = re.sub(r"v\d+$", "", text)
    return text.strip()


def text_has_placeholder(text: str) -> bool:
    upper = text.upper()
    return any(pattern.upper() in upper for pattern in PLACEHOLDER_PATTERNS)


def file_has_content(path: Path, minimum_chars: int = 20) -> bool:
    if not path.exists() or not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return len(text.strip()) >= minimum_chars and not text_has_placeholder(text)


def load_decisions(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid decision JSON at line {number}: {exc}") from exc
        if isinstance(record, dict):
            records.append(record)
    return records


def has_human_decision(decisions: list[dict[str, Any]], decision_type: str) -> bool:
    for record in decisions:
        if (
            record.get("decision_type") == decision_type
            and record.get("status") == "DECIDED"
            and str(record.get("decided_by", "")).casefold() == "human"
            and str(record.get("rationale", "")).strip()
            and not text_has_placeholder(str(record.get("rationale", "")))
        ):
            return True
    return False


def stable_paper_id(row: dict[str, Any]) -> str:
    doi = normalize_doi(row.get("doi"))
    arxiv_id = normalize_arxiv(row.get("arxiv_id"))
    if doi:
        return "doi_" + re.sub(r"[^a-z0-9]+", "_", doi).strip("_")
    if arxiv_id:
        return "arxiv_" + re.sub(r"[^a-z0-9]+", "_", arxiv_id).strip("_")
    title = normalize_text(row.get("title"))
    year = str(row.get("year", "")).strip()
    digest = hashlib.sha256(f"{title}|{year}".encode("utf-8")).hexdigest()[:12]
    return f"title_{digest}"


def dedupe_key(row: dict[str, Any]) -> str:
    doi = normalize_doi(row.get("doi"))
    if doi:
        return f"doi:{doi}"
    arxiv_id = normalize_arxiv(row.get("arxiv_id"))
    if arxiv_id:
        return f"arxiv:{arxiv_id}"
    return f"title:{normalize_text(row.get('title'))}|{str(row.get('year', '')).strip()}"
