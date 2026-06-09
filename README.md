# tvart

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
- Load and play `.tva` files in the browser with the static Web Player and `TvaPlayer` API.
- Try browser examples, including API demo, WebCam preview, and VJ sample.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
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
python -m unittest discover -s tests
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

- Static Web Player: `web/player/index.html`
- API demo: `web/examples/api-demo/index.html`
- WebCam preview sample: `web/examples/webcam-preview/index.html`
- VJ sample: `web/examples/vj-sample/index.html`

The browser playback core is available as `TvaPlayer` in
`web/src/lib/player-api.js`, with TypeScript declarations in
`web/src/lib/player-api.d.ts`.

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

License note placeholder.
