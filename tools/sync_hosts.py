from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED_ITEMS = ("skills", "references", "scripts", "AGENTS.md")
HOST_ROOTS = (
    ROOT / ".codex",
    ROOT / ".claude",
    ROOT / ".opencode",
    ROOT / "plugins" / "ai-literature-workflow",
)


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def source_files(item: str) -> dict[str, Path]:
    source = ROOT / item
    if source.is_file():
        return {item: source}
    return {
        path.relative_to(ROOT).as_posix(): path
        for path in source.rglob("*")
        if path.is_file()
    }


def compare_host(host: Path) -> dict[str, list[str]]:
    missing: list[str] = []
    changed: list[str] = []
    extra: list[str] = []
    expected: set[str] = set()
    for item in SHARED_ITEMS:
        source = ROOT / item
        if not source.exists():
            missing.append(f"canonical item missing: {item}")
            continue
        for relative, source_path in source_files(item).items():
            expected.add((host.relative_to(ROOT) / relative).as_posix())
            target = host / relative
            if not target.exists():
                missing.append(relative)
            elif digest(source_path) != digest(target):
                changed.append(relative)
    if host.exists():
        for item in SHARED_ITEMS:
            target = host / item
            if target.is_file():
                candidates = [target]
            elif target.is_dir():
                candidates = [path for path in target.rglob("*") if path.is_file()]
            else:
                candidates = []
            for path in candidates:
                relative = path.relative_to(ROOT).as_posix()
                if relative not in expected:
                    extra.append(relative)
    return {
        "missing": sorted(missing),
        "changed": sorted(changed),
        "extra": sorted(extra),
    }


def sync_host(host: Path) -> tuple[int, int]:
    copied = 0
    unchanged = 0
    for item in SHARED_ITEMS:
        for relative, source_path in source_files(item).items():
            target = host / relative
            if target.exists() and digest(target) == digest(source_path):
                unchanged += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target)
            copied += 1
    return copied, unchanged


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize host-specific skill trees.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--sync", action="store_true")
    args = parser.parse_args()

    if args.sync:
        results: dict[str, dict[str, int]] = {}
        for host in HOST_ROOTS:
            copied, unchanged = sync_host(host)
            results[host.relative_to(ROOT).as_posix()] = {
                "copied": copied,
                "unchanged": unchanged,
            }
        print(json.dumps({"status": "PASS", "synced": results}, indent=2))
        return 0

    failures: dict[str, dict[str, list[str]]] = {}
    for host in HOST_ROOTS:
        differences = compare_host(host)
        if any(differences.values()):
            failures[host.relative_to(ROOT).as_posix()] = differences
    if failures:
        print(json.dumps({"status": "FAIL", "differences": failures}, indent=2))
        return 1
    print(
        json.dumps(
            {
                "status": "PASS",
                "canonical_items": list(SHARED_ITEMS),
                "host_roots": [path.relative_to(ROOT).as_posix() for path in HOST_ROOTS],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
