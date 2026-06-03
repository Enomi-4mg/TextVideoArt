from __future__ import annotations

import zipfile
from pathlib import Path

from .tva import read_manifest_from_zip


def print_info(path: Path) -> int:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            manifest = read_manifest_from_zip(zf)
    except FileNotFoundError:
        print(f"ERROR: file does not exist: {path}")
        return 1
    except (KeyError, zipfile.BadZipFile, UnicodeDecodeError, ValueError) as exc:
        print(f"ERROR: cannot read TVA file: {exc}")
        return 1

    print(f"Format: {manifest.get('format')} {manifest.get('version')}")
    print(f"Name: {manifest.get('format_name')}")
    print(f"Title: {manifest.get('title')}")
    print(f"Size: {manifest.get('width')} x {manifest.get('height')} chars")
    print(f"FPS: {manifest.get('fps')}")
    print(f"Frames: {manifest.get('frame_count')}")
    duration = manifest.get("duration")
    if isinstance(duration, (int, float)):
        print(f"Duration: {duration:.2f} sec")
    else:
        print(f"Duration: {duration} sec")
    print(f"Charset: {manifest.get('charset')}")
    print(f"Invert: {str(manifest.get('invert')).lower()}")
    print(f"Encoding: {manifest.get('encoding')}")
    print(f"Color mode: {manifest.get('color_mode')}")
    print(f"Frame format: {manifest.get('frame_format')}")
    return 0
