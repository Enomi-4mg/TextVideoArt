from __future__ import annotations

import zipfile
from pathlib import Path

from .constants import MANIFEST_NAME
from .tva import unsafe_zip_member_reason
from .validate import validate_tva


IGNORED_NAMES = {".DS_Store"}
IGNORED_PREFIXES = ("__MACOSX/",)


def should_pack_file(name: str) -> bool:
    if name in IGNORED_NAMES:
        return False
    if any(part in IGNORED_NAMES for part in name.split("/")):
        return False
    if name.startswith(IGNORED_PREFIXES):
        return False
    return True


def iter_pack_files(input_dir: Path) -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for path in input_dir.rglob("*"):
        if not path.is_file():
            continue
        name = path.relative_to(input_dir).as_posix()
        if not should_pack_file(name):
            continue
        reason = unsafe_zip_member_reason(name)
        if reason is not None:
            raise ValueError(reason)
        files.append((name, path))
    return sorted(files, key=lambda item: (item[0] != MANIFEST_NAME, item[0]))


def pack_tva(input_dir: Path, output_path: Path, overwrite: bool = False) -> int:
    if not input_dir.exists():
        print(f"ERROR: input directory does not exist: {input_dir}")
        return 1
    if not input_dir.is_dir():
        print(f"ERROR: input path is not a directory: {input_dir}")
        return 1
    if output_path.exists() and not overwrite:
        print(f"ERROR: output file already exists: {output_path}")
        return 1

    errors = validate_tva(input_dir)
    if errors:
        print("ERROR: invalid TVA project directory.")
        print()
        for error in errors:
            print(f"- {error}")
        return 1

    try:
        files = iter_pack_files(input_dir)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, path in files:
            zf.write(path, arcname=name)

    print(f"Packed {input_dir} to {output_path}")
    return 0
