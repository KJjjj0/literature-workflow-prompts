from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "ai-literature-workflow"
EXPECTED_SKILLS = {
    "literature-workflow-orchestrator",
    "research-scope-builder",
    "corpus-screener",
    "paper-evidence-reader",
    "evidence-quality-judge",
    "literature-synthesizer",
    "related-work-writer",
    "citation-and-venue-auditor",
    "literature-final-auditor",
}
ANTHROPIC_AUTH_MARKER = "ANTHROPIC_" + "AUTH_TOKEN"
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(ANTHROPIC_AUTH_MARKER),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
)
PERSONAL_PATH_PATTERNS = (
    re.compile("C:" + r"\\Users\\[^\\\s]+", re.IGNORECASE),
    re.compile(r"/Users/[^/\s]+"),
    re.compile("E:" + r"\\配置", re.IGNORECASE),
    re.compile("306" + "13"),
)
DANGEROUS_COMMAND_PATTERNS = (
    re.compile(r"Remove-Item\s+-Recurse", re.IGNORECASE),
    re.compile(r"rm\s+-rf", re.IGNORECASE),
    re.compile(r"del\s+/s", re.IGNORECASE),
    re.compile(r"rd\s+/s", re.IGNORECASE),
)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"missing YAML frontmatter: {path}")
    try:
        _, frontmatter, _ = text.split("---", 2)
    except ValueError:
        fail(f"unclosed YAML frontmatter: {path}")
    data = yaml.safe_load(frontmatter)
    if not isinstance(data, dict):
        fail(f"frontmatter is not a mapping: {path}")
    return data


def main() -> int:
    portable_manifest = json.loads((PLUGIN / "plugin.json").read_text(encoding="utf-8"))
    codex_manifest = json.loads(
        (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    marketplace = json.loads(
        (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8")
    )
    if portable_manifest.get("name") != "ai-literature-workflow":
        fail("portable plugin name mismatch")
    if codex_manifest.get("name") != "ai-literature-workflow":
        fail("Codex plugin name mismatch")
    if codex_manifest.get("skills") != "./skills/":
        fail("Codex manifest must declare ./skills/")
    if marketplace.get("name") != "literature-workflow":
        fail("marketplace name mismatch")
    entries = marketplace.get("plugins", [])
    if len(entries) != 1 or entries[0].get("name") != "ai-literature-workflow":
        fail("marketplace must expose exactly ai-literature-workflow")

    skill_dirs = sorted(path.name for path in (PLUGIN / "skills").iterdir() if path.is_dir())
    if set(skill_dirs) != EXPECTED_SKILLS:
        fail(f"unexpected skill directories: {sorted(set(skill_dirs) ^ EXPECTED_SKILLS)}")
    names: set[str] = set()
    for skill_dir in sorted((PLUGIN / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        manifest_path = skill_dir / "SKILL.md"
        if not manifest_path.is_file():
            fail(f"missing SKILL.md: {skill_dir}")
        data = parse_frontmatter(manifest_path)
        if data.get("name") != skill_dir.name:
            fail(f"skill name/folder mismatch: {skill_dir}")
        if not str(data.get("description", "")).strip():
            fail(f"missing skill description: {skill_dir}")
        names.add(skill_dir.name)
        text = manifest_path.read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if link.startswith(("http://", "https://", "#")):
                continue
            target = (skill_dir / link).resolve()
            if not target.exists():
                fail(f"broken skill link in {skill_dir.name}: {link}")

    text_files = [
        path
        for path in PLUGIN.rglob("*")
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".py", ".txt", ".yml", ".yaml"}
    ]
    for path in text_files:
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                fail(f"possible secret pattern in {path.relative_to(ROOT)}")
        for pattern in PERSONAL_PATH_PATTERNS:
            if pattern.search(text):
                fail(f"personal/local path in {path.relative_to(ROOT)}")
        for pattern in DANGEROUS_COMMAND_PATTERNS:
            if pattern.search(text):
                fail(f"dangerous command pattern in {path.relative_to(ROOT)}")
        if path.is_symlink():
            fail(f"symlink found in distribution: {path.relative_to(ROOT)}")

    for script in (PLUGIN / "scripts").glob("*.py"):
        ast.parse(script.read_text(encoding="utf-8"), filename=str(script))

    print(
        json.dumps(
            {
                "status": "PASS",
                "plugin": portable_manifest["name"],
                "version": portable_manifest["version"],
                "skills": len(names),
                "text_files_scanned": len(text_files),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
