# tvart work skill

## Purpose

This document captures project-specific work rules for Codex and future contributors working on `tvart`.

Use this document for implementation hygiene and decision making. Use `README.md`, `README_ja.md`, and `CHANGELOG.md` as the source of truth for current behavior and released history.

## Source of truth

- Treat `README.md` and `README_ja.md` as the source of truth for current usage, commands, and feature descriptions.
- Treat `CHANGELOG.md` as the source of truth for released versions and completed features.
- Treat `docs/tvart-implementation-plan.md` as roadmap and planning context, not as the final authority when it conflicts with README or CHANGELOG.
- When a completed feature still appears as an unfinished task in the plan, update the plan instead of re-implementing the feature.

## Versioning rules

- Keep TVA format version and Python package version separate.
- Do not change the TVA format version just because the Python package changes.
- Preserve compatibility with existing TVA format `0.1.0` files unless a future plan explicitly introduces a format migration.
- Document package-version changes in `CHANGELOG.md`.

## Format principles

- Keep `.tva` focused on linear text video.
- Keep `frames/*.txt` as plain UTF-8 text.
- Do not embed ANSI escape sequences into frame text for color.
- Prefer optional sidecar layers, such as future `colors/*.json`, for features that should degrade gracefully.
- Do not add audio, branching, click events, or game state directly into `.tva` without a separate design pass.

## Validation principle

Do not build pack, export, Web Player, or future display features on weak validation.

Before adding a feature that consumes `.tva` content, make sure validation covers the new manifest fields, file layout, encoding expectations, dimensions, and compatibility behavior.

## File operation policy

- Keep edits scoped to the requested files and the files required by the change.
- Do not edit `README.md`, `README_ja.md`, or `CHANGELOG.md` unless the requested task includes documentation or release-history updates.
- Do not edit implementation code when the request is only to update planning documents.
- Do not delete, move, or rewrite untracked files unless the user explicitly asks.
- Preserve user changes in the working tree; do not revert unrelated edits.

## Git policy

- Check `git status --short` before and after meaningful work.
- Do not create branches, stage files, commit, push, or open pull requests unless the user explicitly asks.
- Do not run destructive Git commands such as `git reset --hard` or `git checkout --` for cleanup.
- Mention remaining untracked files in the final report when relevant.

## Testing policy

- For documentation-only changes, tests are optional but useful as a sanity check.
- For behavior changes, add focused tests near the affected subsystem.
- Prefer `python3 -m unittest discover -s tests` for the full current test suite in this repository.
- If `python` is unavailable, use `python3`.

## Roadmap hygiene

- Keep completed work and future work separated.
- Move released items into a completed-release section instead of leaving them as active TODOs.
- Keep future roadmap sections decision-oriented and concise.
- Keep "not now" items as future candidates when they may belong in Player API, Web workstation, or external project formats later.
