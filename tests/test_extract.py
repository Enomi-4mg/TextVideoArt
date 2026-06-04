import contextlib
import io
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

import path_setup  # noqa: F401
from tvart.extract import extract_tva


def write_zip(path: Path, entries: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, text in entries.items():
            zf.writestr(name, text)


class ExtractTests(unittest.TestCase):
    def test_extract_rejects_parent_directory_entry(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "unsafe.tva"
            output_dir = Path(tmp) / "out"
            write_zip(input_path, {"../evil.txt": "bad"})

            with contextlib.redirect_stdout(io.StringIO()):
                result = extract_tva(input_path, output_dir)

            self.assertEqual(result, 1)
            self.assertFalse((Path(tmp) / "evil.txt").exists())

    def test_extract_rejects_absolute_entry(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "unsafe.tva"
            output_dir = Path(tmp) / "out"
            write_zip(input_path, {"/tmp/evil.txt": "bad"})

            with contextlib.redirect_stdout(io.StringIO()):
                result = extract_tva(input_path, output_dir)

            self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
