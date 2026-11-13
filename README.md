# AI Literature Workflow

An open-source, gate-driven literature research workflow for Codex, Claude Code,
OpenCode, and compatible Agent Skills hosts.

The workflow enforces nine stages from research framing through final audit. It
keeps human decisions in an append-only ledger, freezes the evidence corpus
before writing, and verifies that manuscript citations belong to that corpus.

## Install

### Codex

```powershell
codex plugin marketplace add KJjjj0/literature-workflow-prompts@main
codex plugin add ai-literature-workflow@literature-workflow
```

### Claude Code

```text
/plugin marketplace add KJjjj0/literature-workflow-prompts
/plugin install ai-literature-workflow@literature-workflow
```

### OpenCode

OpenCode discovers `.opencode/skills/` automatically in this repository. To
install globally:

```powershell
pwsh ./install.ps1 -Target opencode -Mode plugin
```

On macOS or Linux:

```bash
./install.sh --target opencode --mode plugin
```

### Generic Agent Skills host

Copy the root `skills/`, `references/`, `scripts/`, and `AGENTS.md` into the
project location supported by the host. The installer can do this:

```powershell
pwsh ./install.ps1 -Target generic -Mode project -ProjectDir <project>
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

OpenCode and generic Agent Skills hosts:

```text
@literature-workflow-orchestrator
```

Describe the research topic, target output, date range, source preferences, and
expected corpus size. The orchestrator performs one valid gate at a time.

An explicit `批准`, `同意`, `认可`, or `OK` reply is enough to approve a normal
gate. Free-text rationale is optional; it is requested only for rejection,
competing-option choices, or changes to an approved scope.

See [Prompt Version 1](docs/prompt-version-1.md) for a complete starting
prompt.

## Workflow

| Gate | Outcome |
|---|---|
| G0 | Research scope frozen |
| G1 | Search protocol approved |
| G2 | Corpus frozen |
| G2.5 | Corpus coverage risk screened |
| G3 | Evidence extracted |
| G4 | Evidence quality judged |
| G5 | Synthesis approved |
| G6 | Draft ready |
| G7 | Citations verified |
| G7.5 | Cross-file consistency audited |
| G7.8 | Workflow completeness audited |
| G8 | Final audit passed |

## Included Skills

- `literature-workflow-orchestrator`
- `research-scope-builder`
- `search-protocol-builder`
- `corpus-screener`
- `corpus-risk-probe`
- `paper-evidence-reader`
- `evidence-quality-judge`
- `literature-synthesizer`
- `related-work-writer`
- `citation-and-venue-auditor`
- `consistency-auditor`
- `completeness-auditor`
- `literature-final-auditor`

## Security

The bundled Python scripts run locally, use only the standard library, make no
network requests, and perform no recursive deletion. External research adapters
such as `paper-lookup` or `nature-reader` are optional and governed by their own
policies.

Read [SECURITY.md](SECURITY.md) and [PRIVACY.md](PRIVACY.md).

## Development

```powershell
python -m pip install -r requirements-dev.txt
python tools/sync_hosts.py --check
python tools/validate_distribution.py
python -B -m unittest discover -s plugins/ai-literature-workflow/tests -v
```

After changing shared skills or runtime resources:

```powershell
python tools/sync_hosts.py --sync
```

The GitHub Actions workflow template is available at `ci/validate.yml` for
repositories that grant workflow write permissions.

## Host Layout

| Host | Discovery path | Manifest |
|---|---|---|
| Codex | `.codex/skills/` | `plugins/ai-literature-workflow/.codex-plugin/plugin.json` |
| Claude Code | `.claude/skills/` | `plugins/ai-literature-workflow/.claude-plugin/plugin.json` |
| OpenCode | `.opencode/skills/` | `.opencode/opencode.json` |
| Generic Agent Skills | `skills/` | no host manifest |

All host trees are complete standalone copies. They do not use symlinks or
cross-host path dependencies.

## License

MIT. See [LICENSE](LICENSE).
