from __future__ import annotations

import json
import zipfile
from pathlib import Path

from .tva import read_manifest_from_zip


def read_manifest(path: Path) -> dict:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            return read_manifest_from_zip(zf)
    except FileNotFoundError:
        print(f"ERROR: file does not exist: {path}")
        raise
    except (KeyError, zipfile.BadZipFile, UnicodeDecodeError, ValueError) as exc:
        print(f"ERROR: cannot read TVA file: {exc}")
        raise


def print_manifest_summary(manifest: dict) -> None:
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


def print_markers(manifest: dict) -> None:
    markers = manifest.get("markers")
    if not markers:
        print("Markers: none")
        return

    print("Markers:")
    for marker in markers:
        frame = marker.get("frame")
        label = marker.get("label")
        if type(frame) is int:
            frame_text = f"{frame:06d}"
        else:
            frame_text = str(frame)
        print(f"  {frame_text} {label}")


def print_info(path: Path) -> int:
    try:
        manifest = read_manifest(path)
    except (FileNotFoundError, KeyError, zipfile.BadZipFile, UnicodeDecodeError, ValueError):
        return 1

    print_manifest_summary(manifest)
    return 0


def print_inspect(path: Path, as_json: bool = False, markers: bool = False) -> int:
    try:
        manifest = read_manifest(path)
    except (FileNotFoundError, KeyError, zipfile.BadZipFile, UnicodeDecodeError, ValueError):
        return 1

    if as_json:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    elif markers:
        print_markers(manifest)
    else:
        print_manifest_summary(manifest)
    return 0
