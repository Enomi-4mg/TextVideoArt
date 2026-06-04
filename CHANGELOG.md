# Changelog

## v0.2.0 - Unreleased

- Added `tvart pack project/ output.tva` for packing extracted TVA project directories into `.tva` archives.
- Reused directory validation before packing so invalid projects are rejected before writing output.
- Added stable ZIP ordering and ignored macOS metadata files such as `.DS_Store` and `__MACOSX/`.

## v0.1.1 - 2026-06-04

- Strengthened manifest validation for numeric fields so `fps` and `duration` reject booleans.
- Made `title` and `created_by` optional manifest fields while still validating their type when present.
- Added validation errors for out-of-range frame files such as `frames/000002.txt` when `frame_count` is `2`.
- Normalized frame text by removing at most one trailing line ending.
- Added safe extraction checks that reject absolute paths and parent-directory traversal in ZIP entries.
- Updated README installation instructions to use a local `.venv`.
