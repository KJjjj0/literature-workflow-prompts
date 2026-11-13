from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "ai-literature-workflow"
MARKETPLACE_NAME = "literature-workflow"


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def tree_files(path: Path) -> dict[str, str]:
    return {
        item.relative_to(path).as_posix(): digest(item)
        for item in path.rglob("*")
        if item.is_file()
    }


def equal(source: Path, destination: Path) -> bool:
    if source.is_file():
        return destination.is_file() and digest(source) == digest(destination)
    return destination.is_dir() and tree_files(source) == tree_files(destination)


def backup_path(destination: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return destination.with_name(f"{destination.name}.backup-{stamp}")


def copy_item(source: Path, destination: Path, *, force: bool, dry_run: bool) -> str:
    if destination.exists() and equal(source, destination):
        return f"unchanged: {destination}"
    if destination.exists() and not force:
        raise RuntimeError(
            f"destination exists and differs: {destination}; rerun with --force"
        )
    if dry_run:
        return f"would copy: {source} -> {destination}"
    if destination.exists():
        backup = backup_path(destination)
        destination.rename(backup)
        print(f"backup: {destination} -> {backup}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)
    return f"copied: {source} -> {destination}"


def printable(command: list[str]) -> str:
    return " ".join(json.dumps(part) if " " in part else part for part in command)


def resolve_command(command: list[str]) -> list[str]:
    executable = shutil.which(command[0])
    if executable:
        return [executable, *command[1:]]
    if os.name == "nt":
        appdata = Path(os.environ.get("APPDATA", ""))
        for suffix in (".cmd", ".exe"):
            candidate = appdata / "npm" / f"{command[0]}{suffix}"
            if candidate.is_file():
                return [str(candidate), *command[1:]]
        script = appdata / "npm" / f"{command[0]}.ps1"
        pwsh = shutil.which("pwsh")
        if script.is_file() and pwsh:
            return [pwsh, "-NoProfile", "-File", str(script), *command[1:]]
    return command


def run(command: list[str], dry_run: bool, optional: bool = False) -> bool:
    resolved = resolve_command(command)
    print(f"+ {printable(resolved)}")
    if dry_run:
        return True
    try:
        result = subprocess.run(resolved, check=False)
    except FileNotFoundError:
        if optional:
            print(f"warning: command not found: {command[0]}")
            return False
        raise
    return result.returncode == 0


def install_codex_plugin(dry_run: bool) -> None:
    run(["codex", "plugin", "marketplace", "add", str(ROOT)], dry_run)
    run(
        ["codex", "plugin", "add", f"{PLUGIN_NAME}@{MARKETPLACE_NAME}"],
        dry_run,
    )


def install_claude_plugin(dry_run: bool, scope: str) -> None:
    run(
        ["claude", "plugin", "marketplace", "add", str(ROOT), "--scope", scope],
        dry_run,
    )
    run(
        [
            "claude",
            "plugin",
            "install",
            f"{PLUGIN_NAME}@{MARKETPLACE_NAME}",
            "--scope",
            scope,
        ],
        dry_run,
    )


def install_opencode_global(
    *, force: bool, dry_run: bool
) -> None:
    destination = Path.home() / ".config" / "opencode"
    print("Installing OpenCode skills globally")
    for skill in (ROOT / "skills").iterdir():
        if not skill.is_dir():
            continue
        print(
            copy_item(
                skill,
                destination / "skills" / skill.name,
                force=force,
                dry_run=dry_run,
            )
        )
    for item in ("references", "scripts"):
        print(
            copy_item(
                ROOT / item,
                destination / item,
                force=force,
                dry_run=dry_run,
            )
        )


def install_project(target: str, project_dir: Path, *, force: bool, dry_run: bool) -> None:
    if not project_dir.is_dir():
        raise RuntimeError(f"project directory does not exist: {project_dir}")
    print(f"Installing project files for {target} into {project_dir}")
    if target == "codex":
        mappings = {
            ROOT / ".codex": project_dir / ".codex",
            ROOT / "AGENTS.md": project_dir / "AGENTS.md",
        }
    elif target == "claude":
        mappings = {
            ROOT / ".claude": project_dir / ".claude",
            ROOT / "CLAUDE.md": project_dir / "CLAUDE.md",
            ROOT / "AGENTS.md": project_dir / "AGENTS.md",
        }
    elif target == "opencode":
        mappings = {
            ROOT / ".opencode": project_dir / ".opencode",
            ROOT / "AGENTS.md": project_dir / "AGENTS.md",
        }
    elif target == "generic":
        mappings = {
            ROOT / "skills": project_dir / "skills",
            ROOT / "references": project_dir / "references",
            ROOT / "scripts": project_dir / "scripts",
            ROOT / "AGENTS.md": project_dir / "AGENTS.md",
        }
    else:
        raise RuntimeError(f"unsupported target: {target}")
    for source, destination in mappings.items():
        print(copy_item(source, destination, force=force, dry_run=dry_run))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install AI Literature Workflow for agent hosts.")
    parser.add_argument(
        "--target",
        choices=("all", "codex", "claude", "opencode", "generic"),
        default="all",
    )
    parser.add_argument("--mode", choices=("plugin", "project"), default="plugin")
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--scope", choices=("user", "project", "local"), default="user")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    targets = (
        ["codex", "claude", "opencode"]
        if args.target == "all"
        else [args.target]
    )
    if args.mode == "plugin":
        if "generic" in targets:
            raise SystemExit("generic target supports project mode only")
        for target in targets:
            if target == "codex":
                install_codex_plugin(args.dry_run)
            elif target == "claude":
                install_claude_plugin(args.dry_run, args.scope)
            elif target == "opencode":
                install_opencode_global(force=args.force, dry_run=args.dry_run)
    else:
        project_dir = Path(args.project_dir).expanduser().resolve()
        for target in targets:
            install_project(
                target,
                project_dir,
                force=args.force,
                dry_run=args.dry_run,
            )
    print("Installation complete" if not args.dry_run else "Dry run complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
