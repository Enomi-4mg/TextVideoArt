from __future__ import annotations

import json
import unittest
import zipfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import path_setup  # noqa: F401
from test_manifest import valid_manifest
from tvart.fix import fix_tva
from tvart.tva import frame_path
from tvart.validate import validate_tva


def write_tva(path: Path, manifest: dict, frames: dict[int, str], extra_files: dict[str, str] | None = None) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        for index, text in frames.items():
            zf.writestr(frame_path(index), text)
        for name, text in (extra_files or {}).items():
            zf.writestr(name, text)


class FixTests(unittest.TestCase):
    def test_fix_updates_manifest_and_preserves_files(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.tva"
            output_path = Path(tmp) / "output.tva"
            write_tva(
                input_path,
                valid_manifest(),
                {0: "abc\nabc\n", 1: "abc\nabc\n"},
                {"notes/readme.txt": "keep me"},
            )

            with redirect_stdout(StringIO()):
                code = fix_tva(
                    input_path,
                    output_path,
                    title="New title",
                    author="A. User",
                    description="Updated",
                    license="MIT",
                    created_by="test",
                    tags=["demo", "fixed"],
                    charset=" .#",
                )

            self.assertEqual(code, 0)
            self.assertEqual(validate_tva(output_path), [])
            with zipfile.ZipFile(output_path, "r") as zf:
                manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
                self.assertEqual(manifest["title"], "New title")
                self.assertEqual(manifest["author"], "A. User")
                self.assertEqual(manifest["description"], "Updated")
                self.assertEqual(manifest["license"], "MIT")
                self.assertEqual(manifest["created_by"], "test")
                self.assertEqual(manifest["tags"], ["demo", "fixed"])
                self.assertEqual(manifest["charset"], " .#")
                self.assertEqual(zf.read(frame_path(0)).decode("utf-8"), "abc\nabc\n")
                self.assertEqual(zf.read("notes/readme.txt").decode("utf-8"), "keep me")

    def test_fix_rejects_invalid_input(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "bad.tva"
            output_path = Path(tmp) / "output.tva"
            manifest = valid_manifest()
            manifest["width"] = 4
            write_tva(input_path, manifest, {0: "abc\nabc\n", 1: "abc\nabc\n"})

            with redirect_stdout(StringIO()):
                code = fix_tva(input_path, output_path, title="Nope")

            self.assertEqual(code, 1)
            self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
