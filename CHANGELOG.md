# Changelog

## Unreleased - 2026-06-10

- Added `tvart fix` for safe `.tva` to `.tva` manifest metadata updates.
  - Supports positional output or `-o` / `--output-file`.
  - Supports `--title`, `--author`, `--description`, `--license`, `--created-by`, repeated `--tag`, `--set-charset`, `--set-charset-preset`, and `--overwrite`.
  - Validates input before editing and validates output after writing.
  - Preserves frame files and unknown ZIP entries.
- Expanded `tvart preview` beyond the original `.tva` playback alias.
  - Preserves `.tva` terminal playback behavior.
  - Adds direct video preview for `.mp4`, `.mov`, `.avi`, and `.mkv`.
  - Adds direct image preview for `.jpg`, `.jpeg`, `.png`, `.bmp`, and best-effort `.webp`.
  - Renders video and image previews directly without creating temporary `.tva` files.
- Added static image conversion support.
  - `tvart convert image.png output.tva` creates a single-frame `.tva`.
  - Image manifests use `source.type = "image"`, `fps = 1`, and `duration = 1.0`.
- Added named charset presets.
  - Presets: `standard`, `simple`, `blocks`, and `dense`.
  - Added `--charset-preset` for `convert` and `preview`.
  - Added `--set-charset-preset` for `fix`.
  - Documented presets in `docs/charset-presets.md`.
- Added transient CLI progress/status UX.
  - `tvart convert` and video/image preview startup can show status on stderr.
  - Added `--quiet` to suppress transient status.
  - Fixed status output so tests and terminal output do not leave noisy traces.
- Added browser renderer separation groundwork.
  - Added `web/src/lib/renderer-pre.js`.
  - Added `web/src/lib/renderer-pre.d.ts`.
  - Introduced `PreFrameRenderer` with `render(frame)` and `clear()`.
- Added experimental VJ browser sample under `web/examples/vj-sample/`.
  - Supports file picker, drag-and-drop, full-frame output, overlay controls, keyboard shortcuts, and URL parameters.
- Added docs-only research notes.
  - `docs/unicode-width.md` documents current character-count validation and future Unicode display width options.
  - `docs/color-layer-design.md` documents future sidecar color layer direction without embedding ANSI escape sequences in frame text.
- Updated `docs/tvart-implementation-plan.md` with completed v0.8.x / v0.9.0 / v0.9.1 work and the next roadmap.
- Updated `README.md` and `README_ja.md` for the current CLI, Web examples, and `python3` usage.
- Kept the Python package version at `0.7.6` pending an explicit release version decision.
- Kept TVA format version at `0.1.0`.

## v0.7.6 - 2026-06-09

- Added an experimental browser-only WebCam preview sample under `web/examples/webcam-preview/`.
- Captured webcam video with `navigator.mediaDevices.getUserMedia()` and converted live frames into grayscale text output.
- Added full-frame `<pre>` preview rendering with overlay controls for camera start/stop, width, FPS, charset, invert, and aspect correction.
- Added keyboard shortcuts for showing and hiding the overlay controls.
- Updated the Python package version to `0.7.6`.
- Kept TVA format version at `0.1.0`.

## v0.7.5 - 2026-06-09

- Realigned `docs/tvart-implementation-plan.md` with the current v0.7.4 project state.
- Documented the next roadmap sequence: v0.7.6 WebCam preview sample, v0.8.0 renderer separation, and v0.8.1 VJ sample / output mode.
- Explicitly separated experimental WebCam / VJ samples from TVA format changes.
- Moved color layer work to a later roadmap phase.
- Updated the Python package version to `0.7.5`.
- Kept TVA format version at `0.1.0`.

## v0.7.4 - 2026-06-09

- Added a browser-based API sample app under `web/examples/api-demo/`.
- Demonstrated direct use of `TvaPlayer` and `loadTvaFile`.
- Added sample UI for file loading, playback control, seeking, FPS override, loop control, manifest display, marker jumps, and player event logging.
- Organized the static Web Player app under `web/player/`.
- Updated documentation for the API demo.
- Updated the Python package version to `0.7.4`.
- Kept TVA format version at `0.1.0`.

## v0.7.3 - 2026-06-09

- Introduced a small source / converter / sink structure for the offline conversion workflow.
- Added `VideoFrameSource` for reading video frames and source metadata.
- Added `iter_text_frames()` to connect frame sources with `TextFrameConverter`.
- Added `TvaArchiveWriter` for writing TVA archives from converted text frames.
- Refactored `tvart convert` to use the new internal workflow while preserving existing CLI behavior.
- Preserved v0.7.2 manifest metadata behavior.
- Updated the Python package version to `0.7.3`.
- Kept TVA format version at `0.1.0`.

## v0.7.2 - 2026-06-09

- Enforced the TVA v0.1.0 `frame_count <= 1,000,000` limit in manifest validation.
- Updated `frame_path()` to reject frame indices outside the six-digit TVA v0.1.0 frame namespace.
- Prevented conversion from generating more than `1,000,000` frames.
- Rejected invalid file names inside the `frames/` namespace during validation.
- Added `source.type = "video"` and `source.duration` metadata to converted TVA manifests when available.
- Added `conversion` metadata to converted TVA manifests.
- Updated the Python package version to `0.7.2`.
- Kept TVA format version at `0.1.0`.

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
