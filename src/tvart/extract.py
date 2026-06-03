from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


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
            zf.extractall(output_dir)
    except zipfile.BadZipFile:
        print(f"ERROR: file is not a valid ZIP archive: {input_path}")
        return 1

    print(f"Extracted {input_path} to {output_dir}")
    return 0
