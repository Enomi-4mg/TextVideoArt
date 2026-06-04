import contextlib
import io
import json
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

import path_setup  # noqa: F401
from test_manifest import valid_manifest
from tvart.cli import main
from tvart.tva import frame_path


def write_tva(path: Path, entries: dict[str, str] | None = None) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if entries is None:
            zf.writestr("manifest.json", json.dumps(valid_manifest()))
            zf.writestr(frame_path(0), "abc\nabc\n")
            zf.writestr(frame_path(1), "abc\nabc\n")
        else:
            for name, text in entries.items():
                zf.writestr(name, text)


class CLITests(unittest.TestCase):
    def test_inspect_prints_metadata(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "sample.tva"
            write_tva(input_path)
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                result = main(["inspect", str(input_path)])

            self.assertEqual(result, 0)
            self.assertIn("Format: TVA 0.1.0", stdout.getvalue())

    def test_inspect_prints_manifest_json(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "sample.tva"
            write_tva(input_path)
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                result = main(["inspect", str(input_path), "--json"])

            self.assertEqual(result, 0)
            self.assertEqual(json.loads(stdout.getvalue())["format"], "TVA")

    def test_unpack_extracts_archive(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "sample.tva"
            output_dir = Path(tmp) / "project"
            write_tva(input_path)

            with contextlib.redirect_stdout(io.StringIO()):
                result = main(["unpack", str(input_path), str(output_dir)])

            self.assertEqual(result, 0)
            self.assertTrue((output_dir / "manifest.json").exists())
            self.assertTrue((output_dir / frame_path(0)).exists())

    def test_unpack_rejects_unsafe_archive(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "unsafe.tva"
            output_dir = Path(tmp) / "project"
            write_tva(input_path, {"../evil.txt": "bad"})

            with contextlib.redirect_stdout(io.StringIO()):
                result = main(["unpack", str(input_path), str(output_dir)])

            self.assertEqual(result, 1)
            self.assertFalse((Path(tmp) / "evil.txt").exists())


if __name__ == "__main__":
    unittest.main()
