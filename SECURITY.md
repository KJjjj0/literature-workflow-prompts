# Security Policy

## Supported Versions

Security fixes are provided for the latest published `0.1.x` release.

## Reporting

Use a private GitHub security advisory when available. Do not publish secrets,
private manuscripts, or sensitive research data in an issue.

## Security Model

- Bundled scripts use the Python standard library only.
- Bundled scripts make no network requests.
- Bundled scripts perform no recursive deletion.
- Existing generated files are not overwritten unless explicitly allowed.
- Filesystem roots and protected system directories are rejected as project roots.
- Distribution packaging rejects symlink traversal.
- The session-start hook prints a fixed reminder and executes nothing else.
- The cross-platform installer supports `--dry-run` and backs up conflicting
  files before replacement when `--force` is explicitly supplied.
- Native Codex and Claude installation invokes the already-installed host CLI;
  OpenCode and generic installation only copies local skill trees.
- Optional research adapters are not bundled and may have separate network and
  privacy behavior.

See `plugins/ai-literature-workflow/SECURITY.md` for the detailed threat model.
