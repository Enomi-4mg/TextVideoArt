# Changelog

## v0.7.1 - 2026-06-09

- Added `TextFrameConverter` as a reusable settings-bearing converter for image-to-text-frame conversion.
- Updated `image_to_text_frame()` to remain as a compatibility wrapper around `TextFrameConverter`.
- Updated `tvart convert` to reuse a `TextFrameConverter` instance internally.
- Preserved existing CLI behavior and manifest semantics.
- Updated the Python package version to `0.7.1`.
- Kept TVA format version at `0.1.0`.

## v0.7.0 - 2026-06-07

- Added reusable core conversion modules under `src/tvart/core/`.
- Moved the brightness-to-character and grayscale-frame-to-text conversion path into core helpers.
- Added `image_to_text_frame()` for shared image-to-text-frame conversion.
- Updated `tvart convert` to call the new core conversion path without changing CLI arguments or manifest semantics.
- Updated the Python package version to `0.7.0`.
- Kept TVA format version at `0.1.0`.

## v0.6.2 - 2026-06-07

- Added `-o` / `--output` support to `tvart convert` while preserving positional output usage.
- Added `-o` / `--output` support to `tvart pack` while preserving positional output usage.
- Added `-o` / `--output` support to `tvart unpack` while preserving positional output directory usage.
- Added `tvart preview` as an alias for terminal playback via `tvart play` behavior.
- Kept TVA format version at `0.1.0`.

## v0.6.1 - 2026-06-04

- Updated `tvart export html` output to use the same full-frame green overlay UI as the static Web Player.
- Added `Controls` and `Manifest` overlay toggles to exported standalone HTML players.
- Updated the Python package version to `0.6.1` while keeping the TVA format version at `0.1.0`.

## v0.6.0 - 2026-06-04

- Added `TvaPlayer` in `web/src/lib/player-api.js` as an external playback control API.
- Added TypeScript declarations in `web/src/lib/player-api.d.ts`.
- Updated the Web Player UI to use the Player API instead of direct playback state management.
- Added API methods for play, pause, stop, frame/time seeking, previous/next frame, frame access, manifest access, marker access, FPS override, loop mode, and event subscriptions.
- Updated the Python package version to `0.6.0` while keeping the TVA format version at `0.1.0`.

## v0.5.0 - 2026-06-04

- Added a static Web Player at `web/index.html` for loading `.tva` files directly in the browser.
- Added browser drag-and-drop and file-picker loading for `.tva` archives.
- Added Web Player controls for play, pause, previous frame, next frame, seek, FPS override, loop, metadata display, and marker jumps.
- Split Web Player logic into parser, playback state, and app UI modules.
- Updated the Python package version to `0.5.0` while keeping the TVA format version at `0.1.0`.

## v0.4.0 - 2026-06-04

- Added `tvart export html output.tva -o output.html` for standalone HTML playback.
- Embedded manifest and plain-text frames directly into the generated HTML file.
- Added browser playback controls for play, pause, restart, seek, metadata display, and marker jumps.
- Updated the Python package version to `0.4.0` while keeping the TVA format version at `0.1.0`.

## v0.3.0 - 2026-06-04

- Added optional manifest metadata fields such as `author`, `description`, `license`, `tags`, `source`, and `conversion`.
- Added manifest `markers` validation for frame-based timeline labels.
- Added `tvart inspect output.tva --markers` for printing marker lists.
- Updated the Python package version to `0.3.0` while keeping the TVA format version at `0.1.0`.

## v0.2.0 - 2026-06-04

- Added `tvart inspect output.tva` and `tvart inspect output.tva --json`.
- Added `tvart pack project/ output.tva` for packing extracted TVA project directories into `.tva` archives.
- Added `tvart unpack output.tva project/` as a production-workflow alias for extracting editable project directories.
- Reused directory validation before packing so invalid projects are rejected before writing output.
- Added stable ZIP ordering and ignored macOS metadata files such as `.DS_Store` and `__MACOSX/`.

## v0.1.1 - 2026-06-04

- Strengthened manifest validation for numeric fields so `fps` and `duration` reject booleans.
- Made `title` and `created_by` optional manifest fields while still validating their type when present.
- Added validation errors for out-of-range frame files such as `frames/000002.txt` when `frame_count` is `2`.
- Normalized frame text by removing at most one trailing line ending.
- Added safe extraction checks that reject absolute paths and parent-directory traversal in ZIP entries.
- Updated README installation instructions to use a local `.venv`.
