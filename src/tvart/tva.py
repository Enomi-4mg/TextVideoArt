from __future__ import annotations

import json
import zipfile
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

from .constants import FRAMES_PATH, MANIFEST_NAME


Manifest = dict[str, Any]


def frame_path(index: int) -> str:
    if index < 0:
        raise ValueError("frame index must be non-negative")
    return f"{FRAMES_PATH}{index:06d}.txt"


def normalize_frame_text(text: str) -> list[str]:
    if text.endswith("\r\n"):
        text = text[:-2]
    elif text.endswith("\n") or text.endswith("\r"):
        text = text[:-1]
    lines = text.splitlines()
    if text.endswith(("\n", "\r")):
        lines.append("")
    return lines


def unsafe_zip_member_reason(name: str) -> str | None:
    if not name:
        return "ZIP entry path is empty"
    if "\\" in name:
        return f"ZIP entry path contains a backslash: {name}"
    if len(name) >= 2 and name[1] == ":":
        return f"ZIP entry path contains a drive prefix: {name}"
    path = PurePosixPath(name)
    if path.is_absolute():
        return f"ZIP entry path is absolute: {name}"
    if str(path) in {"", "."}:
        return f"ZIP entry path is invalid: {name}"
    if any(part in {"", ".", ".."} for part in path.parts):
        return f"ZIP entry path escapes the output directory: {name}"
    return None


def read_manifest_from_zip(zf: zipfile.ZipFile) -> Manifest:
    try:
        raw = zf.read(MANIFEST_NAME)
    except KeyError as exc:
        raise KeyError("manifest.json is missing") from exc
    return json.loads(raw.decode("utf-8"))


def write_manifest(path: Path, manifest: Manifest) -> None:
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_frame(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def open_tva(path: Path) -> zipfile.ZipFile:
    return zipfile.ZipFile(path, "r")
