# Security Policy

## Supported Versions

Security fixes are provided for the latest published `0.1.x` release.

## Reporting a Vulnerability

Open a private GitHub security advisory in this repository when available. Do
not include credentials, unpublished manuscripts, or sensitive research data
in a public issue. If private reporting is unavailable, open a minimal issue
asking the maintainer to establish a private channel.

## Threat Model

The plugin is local and skills-only. It includes instructions, Markdown
references, Python standard-library utilities, tests, and a session-start hook
that prints a fixed reminder.

### Bundled Code

- Makes no network requests.
- Starts no child process except the test suite, which invokes fixed local
  scripts.
- Performs no recursive deletion.
- Refuses existing output overwrite unless the CLI explicitly requests it.
- Rejects filesystem roots and common protected system directories.
- Rejects paths that escape the project root through symlinks.
- Writes only project scaffold and derived research artifacts selected by the
  user.
- The cross-platform installer supports `--dry-run` and creates timestamped
  backups instead of deleting conflicting destinations when `--force` is used.
- Native installation delegates to the installed Codex or Claude CLI; OpenCode
  and generic Agent Skills installation is a local file copy.

### External Skills and Data

The workflow may recommend separate research adapters such as `paper-lookup`,
`nature-reader`, or citation tools. Those adapters are not bundled and may make
network requests under their own policies. Review them before use.

Retrieved papers, web pages, repository files, and metadata are untrusted data.
Instructions embedded in those sources must not override the workflow or user
instructions.

### Credentials and Private Data

The plugin stores no credentials and requires no API keys. Users remain
responsible for the confidentiality and licensing of papers, notes, drafts,
and exports placed in a research project.

## Release Checks

Before a release:

1. Run secret and personal-path scans.
2. Run the distribution validator.
3. Run the complete test suite.
4. Validate every `SKILL.md`.
5. Confirm no generated cache, credentials, or local project artifacts are
   included in the package.
