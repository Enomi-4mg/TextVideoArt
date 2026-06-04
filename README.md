# tvart

`tvart` is a Python CLI tool for creating, inspecting, validating, extracting, and playing `.tva` files.

TVA means **Text Video Art**. A `.tva` file stores video as a sequence of fixed-size plain text frames. It is a ZIP-based container format, so it can also be opened or extracted as a normal ZIP archive.

## MVP features

- Convert video files to monochrome ASCII/text art frames.
- Play `.tva` files in a terminal.
- Print `.tva` metadata.
- Validate the TVA v0.1.0 MVP format.
- Extract `.tva` archives to normal directories.
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
tvart validate output.tva
tvart extract output.tva ./output
```

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

### `tvart validate output.tva`

Validates the TVA v0.1.0 MVP structure, manifest, frame list, encoding, and frame dimensions.

### `tvart extract output.tva ./output`

Extracts the ZIP archive contents into a directory.

## MVP limitations

- Monochrome plain text frames only.
- No color.
- No audio.
- No subtitles.
- No Web playback.
- No delta compression.
- Unicode display width is not calculated; validation uses `len(line)`.

## Future roadmap

- Color text frames.
- Audio tracks.
- Subtitle tracks.
- Web playback.
- Delta compression.
- Richer metadata and preview tooling.

## License

License note placeholder.
# TextVideoArt
