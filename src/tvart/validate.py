from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any, Callable

from .constants import (
    FRAMES_PATH,
    MANIFEST_NAME,
    MAX_FRAME_COUNT,
    TVA_FORMAT,
    TVA_FORMAT_NAME,
    TVA_VERSION,
)
from .tva import frame_path, normalize_frame_text


FRAME_NAME_RE = re.compile(r"^frames/([0-9]{6})\.txt$")


REQUIRED_FIELDS = {
    "format": str,
    "format_name": str,
    "version": str,
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

OPTIONAL_FIELDS = {
    "title": str,
    "created_by": str,
    "author": str,
    "description": str,
    "license": str,
    "created_at": str,
    "tags": list,
    "source": dict,
    "conversion": dict,
    "markers": list,
}

ReadText = Callable[[str], str]


def field_type_error(field: str, expected_type: type) -> str:
    type_name = {
        str: "string",
        list: "array",
        dict: "object",
    }[expected_type]
    article = "an" if type_name[0] in "ao" else "a"
    return f"manifest field {field} must be {article} {type_name}"


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
        elif field in {"fps", "duration"}:
            if type(manifest[field]) not in {int, float}:
                errors.append(f"manifest field {field} must be a number")
        elif not isinstance(manifest[field], expected_type):
            type_name = "number" if expected_type == (int, float) else "string"
            errors.append(f"manifest field {field} must be a {type_name}")

    for field, expected_type in OPTIONAL_FIELDS.items():
        if field in manifest and not isinstance(manifest[field], expected_type):
            errors.append(field_type_error(field, expected_type))

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
    if manifest["frame_count"] > MAX_FRAME_COUNT:
        errors.append("frame_count must be no more than 1000000")
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
    errors.extend(validate_optional_metadata(manifest))

    return errors


def validate_optional_metadata(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if "tags" in manifest:
        for index, tag in enumerate(manifest["tags"]):
            if not isinstance(tag, str) or tag == "":
                errors.append(f"manifest field tags[{index}] must be a non-empty string")

    if "markers" in manifest:
        frame_count = manifest["frame_count"]
        for index, marker in enumerate(manifest["markers"]):
            if not isinstance(marker, dict):
                errors.append(f"manifest field markers[{index}] must be an object")
                continue
            label = marker.get("label")
            if not isinstance(label, str) or label == "":
                errors.append(f"manifest field markers[{index}].label must be a non-empty string")
            frame = marker.get("frame")
            if type(frame) is not int:
                errors.append(f"manifest field markers[{index}].frame must be an integer")
            elif frame < 0 or frame >= frame_count:
                errors.append(f"manifest field markers[{index}].frame must be between 0 and {frame_count - 1}")

    return errors


def validate_tva_contents(names: set[str], read_text: ReadText) -> list[str]:
    errors: list[str] = []
    if MANIFEST_NAME not in names:
        return ["manifest.json is missing"]
    try:
        manifest = json.loads(read_text(MANIFEST_NAME))
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

    for name in sorted(names):
        if name.startswith(FRAMES_PATH) and name != FRAMES_PATH and not FRAME_NAME_RE.match(name):
            errors.append(f"invalid frame file name: {name}")

    for name in sorted(names):
        match = FRAME_NAME_RE.match(name)
        if match and int(match.group(1)) >= frame_count:
            errors.append(f"out-of-range frame: {name}")

    for index in range(frame_count):
        name = frame_path(index)
        if name not in names:
            errors.append(f"missing frame: {name}")
            continue
        try:
            text = read_text(name)
        except UnicodeDecodeError:
            errors.append(f"{name} is not valid UTF-8")
            continue
        lines = normalize_frame_text(text)
        if len(lines) != height:
            errors.append(f"{name} has {len(lines)} lines, expected {height}.")
            continue
        for line_number, line in enumerate(lines, start=1):
            if len(line) != width:
                errors.append(f"{name} line {line_number} has {len(line)} characters, expected {width}.")

    return errors


def validate_tva_file(path: Path) -> list[str]:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            names = set(zf.namelist())

            def read_text(name: str) -> str:
                return zf.read(name).decode("utf-8")

            return validate_tva_contents(names, read_text)
    except zipfile.BadZipFile:
        return ["file is not a valid ZIP archive"]


def validate_tva_directory(path: Path) -> list[str]:
    names = {item.relative_to(path).as_posix() for item in path.rglob("*") if item.is_file()}

    def read_text(name: str) -> str:
        return (path / name).read_text(encoding="utf-8")

    return validate_tva_contents(names, read_text)


def validate_tva(path: Path) -> list[str]:
    if not path.exists():
        return [f"file does not exist: {path}"]
    if path.is_dir():
        return validate_tva_directory(path)
    return validate_tva_file(path)


def print_validation(path: Path) -> int:
    errors = validate_tva(path)
    if not errors:
        target = "directory" if path.is_dir() else "file"
        print(f"OK: {path} is a valid TVA {TVA_VERSION} {target}.")
        return 0
    print("ERROR: invalid TVA file.")
    print()
    for error in errors:
        print(f"- {error}")
    return 1
