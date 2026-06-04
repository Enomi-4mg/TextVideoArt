from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from .tva import unsafe_zip_member_reason


def validate_zip_members_for_extract(zf: zipfile.ZipFile) -> list[str]:
    errors: list[str] = []
    for name in zf.namelist():
        reason = unsafe_zip_member_reason(name)
        if reason is not None:
            errors.append(reason)
    return errors


def extract_tva(input_path: Path, output_dir: Path, overwrite: bool = False) -> int:
    if not input_path.exists():
        print(f"ERROR: input file does not exist: {input_path}")
        return 1
    if output_dir.exists() and any(output_dir.iterdir()) and not overwrite:
        print(f"ERROR: output directory already exists and is not empty: {output_dir}")
        return 1
    if output_dir.exists() and overwrite:
        shutil.rmtree(output_dir)

    try:
        with zipfile.ZipFile(input_path, "r") as zf:
            errors = validate_zip_members_for_extract(zf)
            if errors:
                print("ERROR: unsafe ZIP entry.")
                print()
                for error in errors:
                    print(f"- {error}")
                return 1
            zf.extractall(output_dir)
    except zipfile.BadZipFile:
        print(f"ERROR: file is not a valid ZIP archive: {input_path}")
        return 1

    print(f"Extracted {input_path} to {output_dir}")
    return 0
