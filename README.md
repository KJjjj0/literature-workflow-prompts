# AI Literature Workflow for Codex

An open-source, gate-driven literature research plugin for AI students and
researchers using Codex.

The workflow enforces nine stages from research framing through final audit. It
keeps human decisions in an append-only ledger, freezes the evidence corpus
before writing, and verifies that manuscript citations belong to that corpus.

## Install

```powershell
codex plugin marketplace add KJjjj0/literature-workflow-prompts@main
codex plugin add ai-literature-workflow@literature-workflow
```

Start a new Codex conversation after installation.

## Use

```text
$ai-literature-workflow:literature-workflow-orchestrator
```

Describe the research topic, target output, date range, source preferences, and
expected corpus size. The orchestrator performs one valid gate at a time.

See [Prompt Version 1](docs/prompt-version-1.md) for a complete starting
prompt.

## Workflow

| Gate | Outcome |
|---|---|
| G0 | Research scope frozen |
| G1 | Search protocol approved |
| G2 | Corpus frozen |
| G3 | Evidence extracted |
| G4 | Evidence quality judged |
| G5 | Synthesis approved |
| G6 | Draft ready |
| G7 | Citations verified |
| G8 | Final audit passed |

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

## Security

The bundled Python scripts run locally, use only the standard library, make no
network requests, and perform no recursive deletion. External research adapters
such as `paper-lookup` or `nature-reader` are optional and governed by their own
policies.

Read [SECURITY.md](SECURITY.md) and [PRIVACY.md](PRIVACY.md).

## Development

```powershell
python -m pip install -r requirements-dev.txt
python tools/validate_distribution.py
python -B -m unittest discover -s plugins/ai-literature-workflow/tests -v
```

The GitHub Actions workflow template is available at `ci/validate.yml` for
repositories that grant workflow write permissions.

## License

MIT. See [LICENSE](LICENSE).
