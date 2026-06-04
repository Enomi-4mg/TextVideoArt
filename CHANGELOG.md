# Changelog

## v0.1.1 - 2026-06-04

- Strengthened manifest validation for numeric fields so `fps` and `duration` reject booleans.
- Made `title` and `created_by` optional manifest fields while still validating their type when present.
- Added validation errors for out-of-range frame files such as `frames/000002.txt` when `frame_count` is `2`.
- Normalized frame text by removing at most one trailing line ending.
- Added safe extraction checks that reject absolute paths and parent-directory traversal in ZIP entries.
- Updated README installation instructions to use a local `.venv`.
