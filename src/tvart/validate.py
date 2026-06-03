from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

from .constants import (
    MANIFEST_NAME,
    TVA_FORMAT,
    TVA_FORMAT_NAME,
    TVA_VERSION,
)
from .tva import frame_path, normalize_frame_text


REQUIRED_FIELDS = {
    "format": str,
    "format_name": str,
    "version": str,
    "title": str,
    "created_by": str,
    "width": int,
    "height": int,
    "fps": (int, float),
    "frame_count": int,
    "duration": (int, float),
    "charset": str,
    "invert": bool,
    "encoding": str,
    "color_mode": str,
    "frame_format": str,
    "frames_path": str,
}


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in manifest:
            errors.append(f"missing manifest field: {field}")
            continue
        if field == "invert":
            if type(manifest[field]) is not bool:
                errors.append("manifest field invert must be boolean")
        elif field in {"width", "height", "frame_count"}:
            if type(manifest[field]) is not int:
                errors.append(f"manifest field {field} must be an integer")
        elif not isinstance(manifest[field], expected_type):
            type_name = "number" if expected_type == (int, float) else "string"
            errors.append(f"manifest field {field} must be a {type_name}")

    if errors:
        return errors

    if manifest["format"] != TVA_FORMAT:
        errors.append('format must be "TVA"')
    if manifest["format_name"] != TVA_FORMAT_NAME:
        errors.append('format_name must be "Text Video Art"')
    if manifest["version"] != TVA_VERSION:
        errors.append('version must be "0.1.0"')
    if manifest["width"] <= 0:
        errors.append("width must be positive")
    if manifest["height"] <= 0:
        errors.append("height must be positive")
    if manifest["fps"] <= 0:
        errors.append("fps must be positive")
    if manifest["frame_count"] <= 0:
        errors.append("frame_count must be positive")
    if manifest["duration"] <= 0:
        errors.append("duration must be positive")
    if len(manifest["charset"]) < 2:
        errors.append("charset must contain at least 2 characters")
    if "\n" in manifest["charset"] or "\t" in manifest["charset"]:
        errors.append("charset must not contain newline or tab")
    if manifest["encoding"] != "utf-8":
        errors.append('encoding must be "utf-8"')
    if manifest["color_mode"] != "none":
        errors.append('color_mode must be "none"')
    if manifest["frame_format"] != "plain_text":
        errors.append('frame_format must be "plain_text"')
    if manifest["frames_path"] != "frames/":
        errors.append('frames_path must be "frames/"')

    return errors


def validate_tva(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"file does not exist: {path}"]

    try:
        with zipfile.ZipFile(path, "r") as zf:
            names = set(zf.namelist())
            if MANIFEST_NAME not in names:
                return ["manifest.json is missing"]
            try:
                manifest = json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))
            except UnicodeDecodeError:
                return ["manifest.json is not valid UTF-8"]
            except json.JSONDecodeError as exc:
                return [f"manifest.json is not valid JSON: {exc}"]

            errors.extend(validate_manifest(manifest))
            if errors:
                return errors

            width = manifest["width"]
            height = manifest["height"]
            frame_count = manifest["frame_count"]

            for index in range(frame_count):
                name = frame_path(index)
                if name not in names:
                    errors.append(f"missing frame: {name}")
                    continue
                try:
                    text = zf.read(name).decode("utf-8")
                except UnicodeDecodeError:
                    errors.append(f"{name} is not valid UTF-8")
                    continue
                lines = normalize_frame_text(text)
                if len(lines) != height:
                    errors.append(f"{name} has {len(lines)} lines, expected {height}.")
                    continue
                for line_number, line in enumerate(lines, start=1):
                    if len(line) != width:
                        errors.append(
                            f"{name} line {line_number} has {len(line)} characters, expected {width}."
                        )
    except zipfile.BadZipFile:
        return ["file is not a valid ZIP archive"]

    return errors


def print_validation(path: Path) -> int:
    errors = validate_tva(path)
    if not errors:
        print(f"OK: {path} is a valid TVA {TVA_VERSION} file.")
        return 0
    print("ERROR: invalid TVA file.")
    print()
    for error in errors:
        print(f"- {error}")
    return 1
