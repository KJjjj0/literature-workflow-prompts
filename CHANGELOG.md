# Changelog

## 0.2.1

- Make approval clicks and short positive replies sufficient human decisions.
- Make free-text rationale optional for approval decisions.
- Require rationale only for rejection, competing-option choices, or changes to
  an approved scope or claim boundary.
- Remove repeated rationale prompts from gate transitions.

## 0.2.0

- Add portable root `skills/`, `references/`, and `scripts/` source tree.
- Add standalone Codex, Claude Code, and OpenCode skill trees.
- Add native Claude Code plugin and marketplace manifests.
- Add OpenCode project configuration and global skills installation.
- Add a non-destructive cross-host synchronization and drift checker.
- Add cross-platform installers for plugin and project modes.

## 0.1.1

- Add a nine-gate literature research workflow.
- Add human decision, search, evidence, synthesis, writing, citation, and final
  audit artifacts.
- Add distribution validation and end-to-end tests.
- Reject filesystem roots and protected system directories as project roots.
- Guard generated output overwrites.
- Guard package assembly against symlink traversal.
- Add open-source security, privacy, and development documentation.
