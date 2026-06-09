from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable

from ..constants import FRAMES_PATH, MANIFEST_NAME, MAX_FRAME_COUNT
from ..tva import Manifest, frame_path, write_frame, write_manifest


class TvaArchiveWriter:
    def __init__(self, output_path: Path, *, overwrite: bool = False) -> None:
        if output_path.exists() and not overwrite:
            raise FileExistsError(f"output file already exists: {output_path}")
        self.output_path = output_path
        self.temp_dir = Path(tempfile.mkdtemp(prefix="tvart-"))
        self.frames_dir = self.temp_dir / FRAMES_PATH
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.frame_count = 0
        self._manifest_written = False
        self._closed = False

    def write_frame(self, lines: list[str]) -> None:
        if self.frame_count >= MAX_FRAME_COUNT:
            raise ValueError("frame_count would exceed TVA v0.1.0 limit of 1000000")
        write_frame(self.temp_dir / frame_path(self.frame_count), lines)
        self.frame_count += 1

    def write_manifest(self, manifest: Manifest) -> None:
        write_manifest(self.temp_dir / MANIFEST_NAME, manifest)
        self._manifest_written = True

    def write(self, manifest: Manifest, frames: Iterable[list[str]]) -> None:
        for lines in frames:
            self.write_frame(lines)
        self.write_manifest(manifest)
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        if not self._manifest_written:
            raise RuntimeError("manifest must be written before closing TVA archive")

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(self.output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(self.temp_dir / MANIFEST_NAME, MANIFEST_NAME)
            for index in range(self.frame_count):
                name = frame_path(index)
                zf.write(self.temp_dir / name, name)
        self._closed = True
        self.cleanup()

    def cleanup(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def __enter__(self) -> "TvaArchiveWriter":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if not self._closed:
            self.cleanup()
