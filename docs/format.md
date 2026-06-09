# TVA Format Specification

## Status

This document describes TVA format version `0.1.0` as implemented by the current `tvart` reference tools.

The `tvart` Python package version and the TVA format version are independent. The current planning/package release is `0.7.5`, while the TVA format version remains `0.1.0`.

Tool updates do not necessarily change the format version. The format version should change only when file format semantics change, such as required fields, frame layout, path rules, or the meaning of existing fields.

This is a current specification for TVA `0.1.0`, not the complete future `1.0` specification.

## Overview

`.tva` is a ZIP-based container format for storing video as a sequence of fixed-size UTF-8 plain text frames.

TVA `0.1.0` formally supports only:

```text
color_mode: none
frame_format: plain_text
encoding: utf-8
```

Color, audio, subtitles, and delta compression are not part of the formal TVA `0.1.0` specification.

## Container

A `.tva` file is a ZIP-based archive.

The archive must contain:

```text
manifest.json
frames/000000.txt
frames/000001.txt
...
```

Paths inside the ZIP archive are POSIX-style relative paths. Backslashes (`\`) must not be used. Unsafe paths must always be rejected.

## Required Layout

A valid TVA `0.1.0` archive has this required layout:

```text
sample.tva
├── manifest.json
└── frames/
    ├── 000000.txt
    ├── 000001.txt
    ├── 000002.txt
    └── ...
```

The `manifest.json` entry describes the archive and frame sequence. The `frames/` namespace contains one plain text file per frame.

## Manifest

`manifest.json` is a UTF-8 encoded JSON object. It contains required format fields, required playback and frame fields, and optional metadata fields.

### Required Fields

A TVA `0.1.0` manifest must include these fields:

```json
{
  "format": "TVA",
  "format_name": "Text Video Art",
  "version": "0.1.0",
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

Required field meanings and types:

| Field | Type | Meaning |
| --- | --- | --- |
| `format` | string | Must be `"TVA"`. |
| `format_name` | string | Must be `"Text Video Art"`. |
| `version` | string | TVA format version. Currently must be `"0.1.0"`. |
| `width` | integer | Positive frame width, measured in string characters per line. |
| `height` | integer | Positive frame height, measured in lines. |
| `fps` | number | Positive playback frame rate. Boolean values must be rejected. |
| `frame_count` | integer | Positive number of frames. Must be no more than `1,000,000`. |
| `duration` | number | Positive duration in seconds. Boolean values must be rejected. |
| `charset` | string | Character ramp used during conversion. Must contain at least 2 characters. Newline and tab are not allowed. |
| `invert` | boolean | Whether the character ramp was inverted during conversion. |
| `encoding` | string | Must be `"utf-8"`. |
| `color_mode` | string | Currently must be `"none"`. |
| `frame_format` | string | Currently must be `"plain_text"`. |
| `frames_path` | string | Currently must be `"frames/"`. |

### Optional Fields

TVA `0.1.0` defines these optional manifest fields:

| Field | Type |
| --- | --- |
| `title` | string |
| `created_by` | string |
| `author` | string |
| `description` | string |
| `license` | string |
| `created_at` | string |
| `tags` | array of non-empty strings |
| `source` | object |
| `conversion` | object |
| `markers` | array |

Optional fields must have the expected type when present.

### Source Metadata

`source` is an optional object inside `manifest.json`. It must not be physically split into a separate `source.json` file for TVA `0.1.0`.

Recommended example:

```json
{
  "source": {
    "type": "video",
    "filename": "input.mp4",
    "width": 1920,
    "height": 1080,
    "fps": 29.97,
    "duration": 12.3
  }
}
```

`source.type` should be `"video"` for video inputs. Future versions may extend this to image sequences, text sources, or other source types.

### Conversion Metadata

`conversion` is an optional object inside `manifest.json`. It must not be physically split into a separate `conversion.json` file for TVA `0.1.0`.

Recommended example:

```json
{
  "conversion": {
    "tool": "tvart",
    "tool_version": "0.7.5",
    "width": 100,
    "height": 40,
    "fps": 10,
    "charset": " .:-=+*#%@",
    "invert": false,
    "aspect_correction": 0.5
  }
}
```

### Markers

`markers` is an optional array of frame-based timeline markers. TVA `0.1.0` formally specifies frame-based markers only. Time-based markers are not part of this version.

Example:

```json
{
  "markers": [
    { "frame": 0, "label": "intro" },
    { "frame": 120, "label": "main" },
    { "frame": 239, "label": "ending" }
  ]
}
```

Marker validation rules:

- `markers` must be an array.
- Each marker must be an object.
- `frame` must be an integer.
- `frame` must satisfy `0 <= frame < frame_count`.
- `label` must be a non-empty string.
- Additional marker fields, such as `id`, may be allowed for forward compatibility.

### Unknown Manifest Fields

Unknown manifest fields are allowed for forward compatibility. Readers may ignore unknown fields.

Unknown fields must not change the semantics of required TVA `0.1.0` fields. Data that is specific to a vendor or tool should use clearly named manifest fields or files under `extensions/`.

## Frames

Frames are UTF-8 plain text files stored under `frames/`. Each frame represents one fixed-size text image.

### Frame File Names

TVA `0.1.0` uses fixed six-digit zero-padded decimal frame names:

```text
frames/000000.txt
frames/000001.txt
...
frames/999999.txt
```

Valid frame paths are `frames/000000.txt` through `frames/999999.txt`.

Future versions may introduce a `frame_digits` field if more than `1,000,000` frames are needed.

### Frame Count Limit

TVA `0.1.0` defines `frame_count <= 1,000,000`.

This limit keeps `frame_count` consistent with fixed six-digit frame file names.

### Encoding

`manifest.json` is UTF-8 JSON. Frame files are UTF-8 plain text.

The `encoding` manifest field formally supports only `"utf-8"` in TVA `0.1.0`.

### Dimensions

Each frame must contain:

```text
height lines
width characters per line
```

Validation counts string characters, not terminal display cells. Unicode display width is not calculated in TVA `0.1.0`. Full-width characters, combining characters, and emoji are not fully specified in TVA `0.1.0`.

### Line Ending Normalization

During validation, one final line ending may be ignored. The recognized final line endings are:

```text
LF
CRLF
CR
```

Additional trailing blank lines are actual frame content. Readers should not strip all trailing line endings.

## Reserved Top-Level Paths

TVA `0.1.0` reserves these top-level paths:

| Path | Status | Meaning |
| --- | --- | --- |
| `metadata/` | reserved | Future external metadata files. |
| `colors/` | reserved | Future color layers. |
| `subtitles/` | reserved | Future subtitles or captions. |
| `thumbnails/` | reserved | Future poster or preview images. |
| `assets/` | reserved | Future related assets. |
| `extensions/` | reserved | Vendor-specific or tool-specific extension data. |

TVA `0.1.0` readers formally read only `manifest.json` and `frames/`.

## Unknown Files

Unknown top-level files and directories are allowed by default for forward compatibility. Reserved directories may be ignored by TVA `0.1.0` readers. Vendor-specific or tool-specific data should be placed under `extensions/`.

Files with invalid names under `frames/` are not ordinary unknown files. They are structural errors because they occupy the frame namespace.

Examples of invalid `frames/` names:

```text
frames/1000000.txt
frames/foo.txt
frames/000001.json
frames/000001.txt.bak
frames/subdir/000001.txt
```

## Unsafe Paths

Unsafe paths must always be rejected.

Unsafe paths include:

- Empty paths.
- Absolute paths.
- Paths containing `..`.
- Paths containing `.`.
- Paths containing empty path segments.
- Windows drive prefixes, such as `C:`.
- Paths containing backslashes.

Examples:

```text
../evil.txt
/absolute/path.txt
C:/evil.txt
frames/../../evil.txt
frames\000000.txt
```

## Validation Rules

A TVA `0.1.0` validator must enforce these rules:

- `manifest.json` must exist.
- `manifest.json` must be valid UTF-8 JSON.
- Required fields must exist.
- Required fields must have valid types.
- `fps` and `duration` must reject booleans.
- `width`, `height`, and `frame_count` must be positive integers.
- `fps` and `duration` must be positive numbers.
- `frame_count` must be no more than `1,000,000`.
- `encoding` must be `"utf-8"`.
- `color_mode` must be `"none"`.
- `frame_format` must be `"plain_text"`.
- `frames_path` must be `"frames/"`.
- All required frame files must exist.
- Out-of-range frame files must be rejected.
- Invalid names inside `frames/` must be rejected.
- Each frame must be valid UTF-8.
- Each frame must have exactly `height` lines.
- Each line must have exactly `width` characters.
- Optional metadata fields must have valid types when present.
- Markers must refer to existing frame indices.

Current reference implementation notes:

- `validate_manifest` enforces `frame_count <= 1,000,000`.
- `frame_path` rejects indices greater than `999999`.
- `convert` stops before generating more than `1,000,000` frames.
- `validate` rejects invalid file names under `frames/`.
- `convert` includes `source.type = "video"`.
- `convert` includes `source.duration` when source duration is available.
- `convert` includes `conversion` metadata, including `tool`, `tool_version`, `width`, `height`, `fps`, `charset`, `invert`, and `aspect_correction`.

## Versioning Policy

The TVA format version is independent from the `tvart` package version.

Tool releases may add CLI features, Web Player features, export features, or documentation without changing the format version.

The format version should change when required fields, frame layout, path rules, or semantic meaning of existing fields change.

Adding optional metadata fields does not necessarily require a format version bump.

Adding fully specified color layers, subtitle tracks, audio references, or alternate frame formats may require a future format version such as `0.2.0`.

## Reserved Future Extensions

The following are reserved future extension areas. They are not part of the formal TVA `0.1.0` specification:

- Color layers.
- Subtitle tracks.
- Audio references.
- Thumbnail images.
- Delta compression.
- Alternate frame formats.
- Streaming-friendly layout.
- `frame_digits` for more than `1,000,000` frames.
- Workstation/project formats.
