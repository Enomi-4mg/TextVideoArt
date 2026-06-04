# tvart

`tvart` is a Python CLI tool for creating, inspecting, validating, extracting, and playing `.tva` files.

TVA means **Text Video Art**. A `.tva` file stores video as a sequence of fixed-size plain text frames. It is a ZIP-based container format, so it can also be opened or extracted as a normal ZIP archive.

## MVP features

- Convert video files to monochrome ASCII/text art frames.
- Play `.tva` files in a terminal.
- Print `.tva` metadata.
- Inspect `.tva` metadata as a summary, JSON, or marker list.
- Validate `.tva` archives and extracted project directories.
- Extract `.tva` archives to normal directories.
- Unpack, edit, validate, and pack `.tva` project directories.
- Store optional artwork metadata and frame-based timeline markers.
- Export `.tva` files to standalone HTML players.
- Load and play `.tva` files directly in the browser with the static Web Player.
- Control playback from external browser code with the `TvaPlayer` API.
- Allow unknown extra ZIP files and manifest fields for forward compatibility.

## Installation

From this repository:

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

Tests use the Python standard library:

```bash
python -m unittest discover -s tests
```

## Basic usage

```bash
tvart convert input.mp4 output.tva
tvart convert input.mp4 output.tva --width 120 --fps 12 --duration 10
tvart play output.tva
tvart info output.tva
tvart inspect output.tva --json
tvart inspect output.tva --markers
tvart validate output.tva
tvart validate project/
tvart extract output.tva ./output
tvart unpack output.tva ./project
tvart pack ./output edited.tva
tvart export html edited.tva -o edited.html
```

The static Web Player lives at `web/index.html`. Open it in a browser, then choose or drop a `.tva` file to inspect and play it.

## `.tva` file structure

```text
sample.tva
├── manifest.json
└── frames/
    ├── 000000.txt
    ├── 000001.txt
    ├── 000002.txt
    └── ...
```

Frame files are UTF-8 plain text. Each frame has exactly the same width and height in Python string characters.

## `manifest.json` example

```json
{
  "format": "TVA",
  "format_name": "Text Video Art",
  "version": "0.1.0",
  "title": "sample",
  "created_by": "tvart",
  "width": 100,
  "height": 40,
  "fps": 10,
  "frame_count": 240,
  "duration": 24.0,
  "charset": " .:-=+*#%@",
  "invert": false,
  "author": "anonymous",
  "description": "A short text video demo.",
  "license": "CC BY 4.0",
  "tags": ["ascii-art", "demo"],
  "source": {
    "type": "video",
    "filename": "input.mp4"
  },
  "conversion": {
    "width": 100,
    "fps": 10,
    "charset": " .:-=+*#%@",
    "invert": false
  },
  "markers": [
    { "frame": 0, "label": "intro" },
    { "frame": 120, "label": "main" },
    { "frame": 239, "label": "ending" }
  ],
  "encoding": "utf-8",
  "color_mode": "none",
  "frame_format": "plain_text",
  "frames_path": "frames/"
}
```

## Command reference

### `tvart convert input.mp4 output.tva`

Converts a video file into a `.tva` file.

Useful options:

- `--width 100`
- `--height 40`
- `--fps 10`
- `--charset " .:-=+*#%@"`
- `--invert`
- `--start 2.5`
- `--duration 10`
- `--title "demo"`
- `--overwrite`
- `--aspect-correction 0.5`

### `tvart play output.tva`

Plays a `.tva` file in the terminal.

Options:

- `--loop`
- `--fps 12`
- `--no-clear`
- `--once`

### `tvart info output.tva`

Prints basic metadata from `manifest.json`.

### `tvart inspect output.tva`

Inspects `.tva` metadata. By default this prints the same human-readable summary as `info`.

Options:

- `--json`
- `--markers`

### `tvart validate output.tva`

Validates the TVA v0.1.0 MVP structure, manifest, optional metadata, markers, frame list, encoding, and frame dimensions.
The input may be either a `.tva` ZIP archive or an extracted project directory.

### `tvart extract output.tva ./output`

Extracts the ZIP archive contents into a directory.

### `tvart unpack output.tva ./project`

Unpacks a `.tva` archive into an editable project directory.

Options:

- `--overwrite`

### `tvart pack ./output edited.tva`

Packs an extracted TVA project directory into a `.tva` archive.

Options:

- `--overwrite`

### `tvart export html output.tva -o output.html`

Exports a `.tva` archive to a standalone HTML player. The generated file embeds the manifest and plain-text frames, so it can be opened directly in a browser.

Options:

- `-o`, `--output`
- `--overwrite`

## Web Player

`web/index.html` is a browser app for loading `.tva` files directly. It supports file picker loading, drag-and-drop, manifest metadata, `<pre>` frame playback, previous and next frame controls, seeking, FPS override, loop playback, and marker jumps.

The Web Player keeps the frame view full-screen and uses simple black-and-white overlays for controls and manifest details. The `Controls` and `Manifest` buttons toggle those overlays.

The player uses JSZip from a CDN to read ZIP-based `.tva` archives in the browser. The generated `export html` files remain self-contained and do not use external JavaScript.

## Player API

The browser playback core is available as `TvaPlayer` in `web/src/lib/player-api.js`, with TypeScript declarations in `web/src/lib/player-api.d.ts`.

```js
import { TvaPlayer } from "./web/src/lib/player-api.js";

const player = new TvaPlayer();
player.load({ manifest, frames });
player.on("framechange", ({ index, frame }) => {
  console.log(index, frame);
});
player.play();
player.seekFrame(120);
player.pause();
```

Core methods include `play`, `pause`, `stop`, `seekFrame`, `seekTime`, `nextFrame`, `prevFrame`, `getCurrentFrame`, `getCurrentFrameIndex`, `getManifest`, `getMarkers`, `setFps`, `setLoop`, and `on`.

## MVP limitations

- Monochrome plain text frames only.
- No color.
- No audio.
- No subtitles.
- No delta compression.
- Unicode display width is not calculated; validation uses `len(line)`.

## Future roadmap

- Color text frames.
- Audio tracks.
- Subtitle tracks.
- Color layers.
- Delta compression.
- Preview tooling.

## License

License note placeholder.
# TextVideoArt
