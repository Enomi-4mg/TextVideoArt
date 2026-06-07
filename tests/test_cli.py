import contextlib
import io
import json
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

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
    def assert_parser_error(self, argv: list[str], expected: str) -> None:
        stderr = io.StringIO()

        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
            main(argv)

        self.assertEqual(raised.exception.code, 2)
        self.assertIn(expected, stderr.getvalue())

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

    def test_inspect_prints_markers(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "sample.tva"
            manifest = valid_manifest()
            manifest["markers"] = [
                {"frame": 0, "label": "intro"},
                {"frame": 1, "label": "ending"},
            ]
            write_tva(
                input_path,
                {
                    "manifest.json": json.dumps(manifest),
                    frame_path(0): "abc\nabc\n",
                    frame_path(1): "abc\nabc\n",
                },
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                result = main(["inspect", str(input_path), "--markers"])

            self.assertEqual(result, 0)
            self.assertIn("Markers:", stdout.getvalue())
            self.assertIn("  000000 intro", stdout.getvalue())
            self.assertIn("  000001 ending", stdout.getvalue())

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

    def test_unpack_validate_pack_validate_roundtrip(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "sample.tva"
            project_dir = Path(tmp) / "project"
            output_path = Path(tmp) / "roundtrip.tva"
            write_tva(input_path)

            with contextlib.redirect_stdout(io.StringIO()):
                unpack_result = main(["unpack", str(input_path), str(project_dir)])
                validate_project_result = main(["validate", str(project_dir)])
                pack_result = main(["pack", str(project_dir), str(output_path)])
                validate_output_result = main(["validate", str(output_path)])

            self.assertEqual(unpack_result, 0)
            self.assertEqual(validate_project_result, 0)
            self.assertEqual(pack_result, 0)
            self.assertEqual(validate_output_result, 0)
            self.assertTrue(output_path.exists())

    def test_convert_accepts_output_option(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.mp4"
            output_path = Path(tmp) / "output.tva"

            for flag in ("-o", "--output"):
                with self.subTest(flag=flag), patch("tvart.cli.convert_video", return_value=0) as convert_video:
                    result = main(["convert", str(input_path), flag, str(output_path)])

                self.assertEqual(result, 0)
                self.assertEqual(convert_video.call_args.args[:2], (input_path, output_path))

    def test_convert_rejects_missing_output(self) -> None:
        self.assert_parser_error(
            ["convert", "input.mp4"],
            "convert requires an output path via positional argument or -o/--output",
        )

    def test_convert_rejects_positional_and_output_option(self) -> None:
        self.assert_parser_error(
            ["convert", "input.mp4", "positional.tva", "--output", "option.tva"],
            "convert output path must be provided either positionally or via -o/--output, not both",
        )

    def test_pack_accepts_output_option(self) -> None:
        with TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "project"
            output_path = Path(tmp) / "edited.tva"

            for flag in ("-o", "--output"):
                with self.subTest(flag=flag), patch("tvart.cli.pack_tva", return_value=0) as pack_tva:
                    result = main(["pack", str(input_dir), flag, str(output_path)])

                self.assertEqual(result, 0)
                self.assertEqual(pack_tva.call_args.args[:2], (input_dir, output_path))

    def test_pack_rejects_missing_output(self) -> None:
        self.assert_parser_error(
            ["pack", "project"],
            "pack requires an output path via positional argument or -o/--output",
        )

    def test_pack_rejects_positional_and_output_option(self) -> None:
        self.assert_parser_error(
            ["pack", "project", "positional.tva", "--output", "option.tva"],
            "pack output path must be provided either positionally or via -o/--output, not both",
        )

    def test_unpack_accepts_output_option(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "sample.tva"
            output_dir = Path(tmp) / "project"

            for flag in ("-o", "--output"):
                with self.subTest(flag=flag), patch("tvart.cli.extract_tva", return_value=0) as extract_tva:
                    result = main(["unpack", str(input_path), flag, str(output_dir)])

                self.assertEqual(result, 0)
                self.assertEqual(extract_tva.call_args.args[:2], (input_path, output_dir))

    def test_unpack_rejects_missing_output(self) -> None:
        self.assert_parser_error(
            ["unpack", "output.tva"],
            "unpack requires an output path via positional argument or -o/--output",
        )

    def test_unpack_rejects_positional_and_output_option(self) -> None:
        self.assert_parser_error(
            ["unpack", "output.tva", "positional", "--output", "option"],
            "unpack output path must be provided either positionally or via -o/--output, not both",
        )

    def test_preview_plays_valid_archive_once(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "sample.tva"
            write_tva(input_path)
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                result = main(["preview", str(input_path), "--once"])

            self.assertEqual(result, 0)
            self.assertIn("abc", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
