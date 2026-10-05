# tvart

## Initial-publication implementation (Unreleased)

Open [Playground](web/playground/) from the Web entry. No install or build is required on a static host. A project-authored procedural sample (MIT) appears immediately. Choose a photo, video or camera; apply Clean, Edge or Terminal; save TXT/PNG or a Motion Card up to five seconds in 1:1, 9:16 or 16:9. Recording checks browser support and uses the actual MP4/WebM container; unsupported recording falls back to PNG. Camera requires HTTPS or localhost.

Save/import a version-1 recipe JSON or share a recipe URL. Settings links contain no material, filename or path: recipients supply their own material. Artwork is saved separately as TXT, PNG or video.

Python/Web validation now shares conformance fixtures, strict UTF-8, code-point dimensions, finite numbers, namespace checks and bounded reading. TVA remains 0.1.0; package remains 0.7.6. Canvas native/contain/cover rendering is shared with Player and WebCam.

Local media path: `tvart render png input.tva -o frames` or `tvart render mp4 input.tva -o output.mp4` (FFmpeg/libx264 required). Local glyph support is ASCII plus ░▒▓█. See [Web/OBS examples](docs/obs-web-guide.md).

Status: Python and Web suites passed; local H.264 MP4 generation and Chrome PNG/TXT/recipe JSON downloads verified. Sample/Edge display and settings links were exercised in the browser. Browser recording, camera hardware, Safari/iPhone and OBS remain unverified. See [verification record](docs/verification-2026-10.md) and [current plan](docs/tvart-implementation-plan.md). Full-width persistence, per-cell color, audio, full editing and cloud galleries are deferred.


`tvart` is a Python CLI tool for creating, previewing, inspecting, validating,
extracting, fixing, packing, exporting, and playing `.tva` files.

TVA means **Text Video Art**. A `.tva` file stores video as fixed-size UTF-8
plain text frames inside a ZIP-based container.

## Features

- Convert video files to monochrome ASCII/text art frames.
- Convert static image files to single-frame `.tva` files.
- Preview `.tva`, video, and image inputs in a terminal.
- Play `.tva` files in a terminal.
- Print and inspect `.tva` metadata, JSON, and markers.
- Validate `.tva` archives and extracted project directories.
- Extract or unpack `.tva` archives to directories.
- Pack edited project directories back into `.tva` archives.
- Update manifest metadata with `tvart fix` while preserving frames and unknown ZIP entries.
- Export `.tva` files to standalone HTML players.
- Use named charset presets for conversion, preview, and metadata fixes.
- Load, debug, and capture `.tva` files in the browser with the unified Web Player and `TvaPlayer` API.
- Try browser tools, including WebCam preview and Web Player Debug / VJ tabs.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -e .
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

Run tests:

```bash
python3 -m unittest discover -s tests
```

## Basic Usage

```bash
tvart convert input.mp4 output.tva
tvart convert input.mp4 -o output.tva
tvart convert image.png image.tva --width 100
tvart preview output.tva
tvart preview input.mp4 --width 120 --fps 12 --duration 10
tvart preview image.png --width 100
tvart play output.tva
tvart info output.tva
tvart inspect output.tva --json
tvart inspect output.tva --markers
tvart validate output.tva
tvart validate project/
tvart extract output.tva ./output
tvart unpack output.tva -o ./project
tvart pack ./project -o edited.tva
tvart fix edited.tva fixed.tva --title "New title" --tag demo
tvart export html edited.tva -o edited.html
```

## Command Reference

### `tvart convert input output.tva`

Converts a video or static image file into a `.tva` file. Output can also be
passed with `-o` / `--output`.

Supported video inputs: `.mp4`, `.mov`, `.avi`, `.mkv`.

Supported image inputs: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp` best-effort
through OpenCV.

Image conversion creates one frame with `source.type = "image"`, `fps = 1`,
and `duration = 1.0`.

Useful options:

- `--width`
- `--height`
- `--fps`
- `--charset`
- `--charset-preset`
- `--invert`
- `--start`
- `--duration`
- `--title`
- `--overwrite`
- `--aspect-correction`
- `--quiet`

### `tvart preview input`

Previews a `.tva`, video, or image input in the terminal. `.tva` inputs use the
terminal player; video and image inputs render directly without creating a
temporary `.tva` file.

`.tva` playback and video preview use the terminal alternate screen when
clearing is enabled. On normal exit, `--once`, or `Ctrl-C`, tvart restores the
cursor and returns to the shell without leaving rendered frames in the scrollback.
Use `--no-clear` only when you intentionally want frames written into the normal
terminal output.

Image preview is a single-frame command, so it writes to the normal terminal
output instead of entering the alternate screen.

Useful options:

- `--width`
- `--height`
- `--fps`
- `--charset`
- `--charset-preset`
- `--invert`
- `--start`
- `--duration`
- `--aspect-correction`
- `--loop`
- `--no-clear`
- `--once`
- `--quiet`

### Other Commands

- `tvart play output.tva`: play a `.tva` file in the terminal.
- `tvart info output.tva`: print basic metadata.
- `tvart inspect output.tva`: inspect metadata, with `--json` and `--markers`.
- `tvart validate output.tva`: validate an archive or extracted project directory.
- `tvart extract output.tva ./output`: extract ZIP contents.
- `tvart unpack output.tva -o ./project`: unpack an archive into an editable project directory.
- `tvart pack ./project -o edited.tva`: pack an edited project directory.
- `tvart export html output.tva -o output.html`: export a standalone HTML player.

### `tvart fix input.tva output.tva`

Reads a valid `.tva`, updates manifest metadata, writes a new `.tva`, and
validates the output. Output can be passed positionally or with
`-o` / `--output-file`.

Options:

- `--title`
- `--author`
- `--description`
- `--license`
- `--created-by`
- `--tag` multiple allowed
- `--set-charset`
- `--set-charset-preset`
- `--overwrite`

`--set-charset` changes manifest metadata only. It does not rewrite frame text.

## Charset Presets

```text
standard = " .:-=+*#%@"
simple   = " .#"
blocks   = " ░▒▓█"
dense    = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
```

See `docs/charset-presets.md` for details.

## Web

- GitHub Pages entry point: `web/index.html`
- Unified Web Player: `web/player/index.html`
  - Debug tab: `web/player/index.html?tab=debug`
  - VJ tab: `web/player/index.html?tab=vj`
- WebCam preview sample: `web/examples/webcam-preview/index.html`

The browser playback core is available as `TvaPlayer` in
`web/src/lib/player-api.js`, with TypeScript declarations in
`web/src/lib/player-api.d.ts`.

Serve the repository with a local static server to try the browser tools:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/web/`. Browser TVA archive loading uses the
vendored JSZip module in `web/vendor/`, so the Player and landing demo do not
need a CDN at runtime. See `web/examples/README.md` for the browser sample notes
and sample asset policy.

GitHub Discussions, when enabled for the public repository, are intended for
announcements, questions, ideas, and show-and-tell posts.

## Current Limitations

- Monochrome plain text frames only.
- No color layer implementation yet.
- No audio.
- No subtitles.
- Browser examples are experimental.
- Unicode display width is not calculated; validation uses character count.

## Roadmap

The active roadmap is tracked in `docs/tvart-implementation-plan.md`.

## License

MIT. See `LICENSE`.
