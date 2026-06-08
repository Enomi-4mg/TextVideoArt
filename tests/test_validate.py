import json
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

import path_setup  # noqa: F401
from test_manifest import valid_manifest
from tvart.tva import frame_path
from tvart.validate import validate_tva


def write_tva(path: Path, manifest: dict, frames: dict[int, str]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        for index, text in frames.items():
            zf.writestr(frame_path(index), text)


def write_tva_directory(path: Path, manifest: dict, frames: dict[int, str]) -> None:
    frames_dir = path / "frames"
    frames_dir.mkdir(parents=True)
    (path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    for index, text in frames.items():
        (path / frame_path(index)).write_text(text, encoding="utf-8")


def add_zip_entries(path: Path, entries: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "a", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, text in entries.items():
            zf.writestr(name, text)


class TVAValidationTests(unittest.TestCase):
    def test_invalid_frame_dimensions(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad-dimensions.tva"
            manifest = valid_manifest()
            write_tva(path, manifest, {0: "abc\nde\n", 1: "abc\nabc\n"})

            errors = validate_tva(path)

            self.assertIn("frames/000000.txt line 2 has 2 characters, expected 3.", errors)

    def test_missing_frame_file(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing-frame.tva"
            manifest = valid_manifest()
            write_tva(path, manifest, {0: "abc\nabc\n"})

            errors = validate_tva(path)

            self.assertIn("missing frame: frames/000001.txt", errors)

    def test_out_of_range_frame_file(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "extra-frame.tva"
            manifest = valid_manifest()
            write_tva(path, manifest, {0: "abc\nabc\n", 1: "abc\nabc\n", 2: "abc\nabc\n"})

            errors = validate_tva(path)

            self.assertIn("out-of-range frame: frames/000002.txt", errors)

    def test_zip_rejects_invalid_names_under_frames_namespace(self) -> None:
        invalid_names = [
            "frames/foo.txt",
            "frames/000001.json",
            "frames/1000000.txt",
            "frames/000001.txt.bak",
            "frames/subdir/000001.txt",
        ]

        for invalid_name in invalid_names:
            with self.subTest(invalid_name=invalid_name), TemporaryDirectory() as tmp:
                path = Path(tmp) / "invalid-frame-name.tva"
                manifest = valid_manifest()
                write_tva(path, manifest, {0: "abc\nabc\n", 1: "abc\nabc\n"})
                add_zip_entries(path, {invalid_name: "abc\nabc\n"})

                errors = validate_tva(path)

                self.assertIn(f"invalid frame file name: {invalid_name}", errors)

    def test_zip_still_reports_valid_looking_frame_beyond_frame_count_as_out_of_range(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "extra-frame.tva"
            manifest = valid_manifest()
            write_tva(path, manifest, {0: "abc\nabc\n", 1: "abc\nabc\n"})
            add_zip_entries(path, {"frames/000002.txt": "abc\nabc\n"})

            errors = validate_tva(path)

            self.assertIn("out-of-range frame: frames/000002.txt", errors)
            self.assertNotIn("invalid frame file name: frames/000002.txt", errors)

    def test_valid_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "project"
            manifest = valid_manifest()
            write_tva_directory(path, manifest, {0: "abc\nabc\n", 1: "abc\nabc\n"})

            errors = validate_tva(path)

            self.assertEqual(errors, [])

    def test_directory_missing_frame_file(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "project"
            manifest = valid_manifest()
            write_tva_directory(path, manifest, {0: "abc\nabc\n"})

            errors = validate_tva(path)

            self.assertIn("missing frame: frames/000001.txt", errors)

    def test_directory_out_of_range_frame_file(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "project"
            manifest = valid_manifest()
            write_tva_directory(path, manifest, {0: "abc\nabc\n", 1: "abc\nabc\n", 2: "abc\nabc\n"})

            errors = validate_tva(path)

            self.assertIn("out-of-range frame: frames/000002.txt", errors)

    def test_directory_rejects_invalid_names_under_frames_namespace(self) -> None:
        invalid_names = [
            "frames/foo.txt",
            "frames/000001.json",
            "frames/1000000.txt",
            "frames/000001.txt.bak",
            "frames/subdir/000001.txt",
        ]

        for invalid_name in invalid_names:
            with self.subTest(invalid_name=invalid_name), TemporaryDirectory() as tmp:
                path = Path(tmp) / "project"
                manifest = valid_manifest()
                write_tva_directory(path, manifest, {0: "abc\nabc\n", 1: "abc\nabc\n"})
                invalid_path = path / invalid_name
                invalid_path.parent.mkdir(parents=True, exist_ok=True)
                invalid_path.write_text("abc\nabc\n", encoding="utf-8")

                errors = validate_tva(path)

                self.assertIn(f"invalid frame file name: {invalid_name}", errors)


if __name__ == "__main__":
    unittest.main()
