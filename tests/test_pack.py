import contextlib
import io
import json
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

import path_setup  # noqa: F401
from test_manifest import valid_manifest
from tvart.pack import pack_tva
from tvart.tva import frame_path
from tvart.validate import validate_tva


def write_project(path: Path, frames: dict[int, str]) -> None:
    (path / "frames").mkdir(parents=True)
    (path / "manifest.json").write_text(json.dumps(valid_manifest()), encoding="utf-8")
    for index, text in frames.items():
        (path / frame_path(index)).write_text(text, encoding="utf-8")


class PackTests(unittest.TestCase):
    def test_pack_valid_project(self) -> None:
        with TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "project"
            output_path = Path(tmp) / "packed.tva"
            write_project(input_dir, {0: "abc\nabc\n", 1: "abc\nabc\n"})

            with contextlib.redirect_stdout(io.StringIO()):
                result = pack_tva(input_dir, output_path)

            self.assertEqual(result, 0)
            self.assertEqual(validate_tva(output_path), [])

    def test_pack_rejects_invalid_project(self) -> None:
        with TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "project"
            output_path = Path(tmp) / "packed.tva"
            write_project(input_dir, {0: "abc\nabc\n"})

            with contextlib.redirect_stdout(io.StringIO()):
                result = pack_tva(input_dir, output_path)

            self.assertEqual(result, 1)
            self.assertFalse(output_path.exists())

    def test_pack_rejects_existing_output_without_overwrite(self) -> None:
        with TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "project"
            output_path = Path(tmp) / "packed.tva"
            write_project(input_dir, {0: "abc\nabc\n", 1: "abc\nabc\n"})
            output_path.write_text("existing", encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                result = pack_tva(input_dir, output_path)

            self.assertEqual(result, 1)
            self.assertEqual(output_path.read_text(encoding="utf-8"), "existing")

    def test_pack_overwrites_existing_output(self) -> None:
        with TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "project"
            output_path = Path(tmp) / "packed.tva"
            write_project(input_dir, {0: "abc\nabc\n", 1: "abc\nabc\n"})
            output_path.write_text("existing", encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                result = pack_tva(input_dir, output_path, overwrite=True)

            self.assertEqual(result, 0)
            self.assertEqual(validate_tva(output_path), [])

    def test_pack_uses_stable_zip_order_and_ignores_os_files(self) -> None:
        with TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "project"
            output_path = Path(tmp) / "packed.tva"
            write_project(input_dir, {1: "abc\nabc\n", 0: "abc\nabc\n"})
            (input_dir / ".DS_Store").write_text("ignored", encoding="utf-8")
            (input_dir / "__MACOSX").mkdir()
            (input_dir / "__MACOSX" / "junk").write_text("ignored", encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                result = pack_tva(input_dir, output_path)

            self.assertEqual(result, 0)
            with zipfile.ZipFile(output_path, "r") as zf:
                self.assertEqual(zf.namelist(), ["manifest.json", "frames/000000.txt", "frames/000001.txt"])


if __name__ == "__main__":
    unittest.main()
