# AI Literature Workflow

A skills-only literature research plugin for Codex, Claude Code, OpenCode, and
compatible Agent Skills hosts.

The workflow enforces nine gates from question framing to final audit. It keeps
human decisions separate from AI-generated analysis and blocks manuscript
writing until the evidence corpus is frozen and judged.

## Gates

1. `G0`: research scope frozen.
2. `G1`: search protocol approved.
3. `G2`: corpus frozen.
4. `G3`: evidence extracted.
5. `G4`: evidence quality and claim scope judged.
6. `G5`: synthesis and research gaps approved.
7. `G6`: draft ready.
8. `G7`: citations and venue formatting verified.
9. `G8`: final audit passed.

## Included Skills

- `literature-workflow-orchestrator`
- `research-scope-builder`
- `corpus-screener`
- `paper-evidence-reader`
- `evidence-quality-judge`
- `literature-synthesizer`
- `related-work-writer`
- `citation-and-venue-auditor`
- `literature-final-auditor`

## Install

Codex:

```powershell
codex plugin marketplace add KJjjj0/literature-workflow-prompts@main
codex plugin add ai-literature-workflow@literature-workflow
```

Claude Code:

```text
/plugin marketplace add KJjjj0/literature-workflow-prompts
/plugin install ai-literature-workflow@literature-workflow
```

OpenCode:

```powershell
pwsh ./install.ps1 -Target opencode -Mode plugin
```

## Use

Codex:

```text
$ai-literature-workflow:literature-workflow-orchestrator
```

Claude Code:

```text
/ai-literature-workflow:literature-workflow-orchestrator
```

OpenCode:

```text
@literature-workflow-orchestrator
```

Then describe the research topic, target output, date range, source preferences,
and expected corpus size. The orchestrator will identify and execute only the
next valid gate.

See [Prompt Version 1](docs/prompt-version-1.md) for complete prompts.

## Dependencies

The bundled Python tools use only the standard library. Research adapters such
as `paper-lookup`, `nature-reader`, `scientific-critical-thinking`,
`scientific-writing`, `citation-management`, and `venue-templates` are optional.
The workflow does not bundle or silently install them.

## Security

- Bundled scripts make no network requests.
- Bundled scripts perform no recursive deletion.
- Output generation refuses overwrites unless explicitly allowed.
- Project roots cannot be filesystem roots or protected system directories.
- Packaging refuses project paths that escape through symlinks.
- Retrieved papers and web content are treated as untrusted data.

Read [SECURITY.md](SECURITY.md) and [PRIVACY.md](PRIVACY.md) before use.

## Development

```powershell
python -m pip install -r requirements-dev.txt
python tools/validate_distribution.py
python -B -m unittest discover -s tests -v
```

## License

MIT. See [LICENSE](LICENSE).
