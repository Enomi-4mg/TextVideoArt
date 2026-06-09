from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

from .constants import MANIFEST_NAME
from .tva import read_manifest_from_zip
from .validate import validate_tva


def validate_fix_options(*, charset: str | None) -> list[str]:
    errors: list[str] = []
    if charset is not None:
        if len(charset) < 2:
            errors.append("charset must contain at least 2 characters")
        if "\n" in charset or "\t" in charset:
            errors.append("charset must not contain newline or tab")
    return errors


def _copy_zip_with_manifest(input_path: Path, output_path: Path, manifest: dict[str, Any]) -> None:
    with zipfile.ZipFile(input_path, "r") as source:
        entries = [(info, source.read(info.filename)) for info in source.infolist() if info.filename != MANIFEST_NAME]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as target:
        target.writestr(
            MANIFEST_NAME,
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        )
        for info, data in entries:
            target.writestr(info, data)


def fix_tva(
    input_path: Path,
    output_path: Path,
    *,
    title: str | None = None,
    author: str | None = None,
    description: str | None = None,
    license: str | None = None,
    created_by: str | None = None,
    tags: list[str] | None = None,
    charset: str | None = None,
    overwrite: bool = False,
) -> int:
    if not input_path.exists():
        print(f"ERROR: input file does not exist: {input_path}")
        return 1
    if output_path.exists() and not overwrite:
        print(f"ERROR: output file already exists: {output_path}")
        return 1

    option_errors = validate_fix_options(charset=charset)
    if option_errors:
        for error in option_errors:
            print(f"ERROR: {error}")
        return 1

    input_errors = validate_tva(input_path)
    if input_errors:
        print("ERROR: input TVA file is invalid.")
        print()
        for error in input_errors:
            print(f"- {error}")
        return 1

    try:
        with zipfile.ZipFile(input_path, "r") as zf:
            manifest = read_manifest_from_zip(zf)
    except (KeyError, zipfile.BadZipFile, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read input TVA file: {exc}")
        return 1

    if title is not None:
        manifest["title"] = title
    if author is not None:
        manifest["author"] = author
    if description is not None:
        manifest["description"] = description
    if license is not None:
        manifest["license"] = license
    if created_by is not None:
        manifest["created_by"] = created_by
    if tags:
        manifest["tags"] = tags
    if charset is not None:
        manifest["charset"] = charset

    try:
        _copy_zip_with_manifest(input_path, output_path, manifest)
    except OSError as exc:
        print(f"ERROR: cannot write output TVA file: {exc}")
        return 1

    output_errors = validate_tva(output_path)
    if output_errors:
        print("ERROR: output TVA file is invalid.")
        print()
        for error in output_errors:
            print(f"- {error}")
        return 1

    print(f"Wrote {output_path}")
    return 0
