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
from tvart.export import export_html
from tvart.tva import frame_path


def write_tva(path: Path, manifest: dict | None = None) -> None:
    if manifest is None:
        manifest = valid_manifest()
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr(frame_path(0), "abc\nabc\n")
        zf.writestr(frame_path(1), "def\ndef\n")


class ExportHTMLTests(unittest.TestCase):
    def test_export_html_writes_standalone_player(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "sample.tva"
            output_path = Path(tmp) / "sample.html"
            manifest = valid_manifest()
            manifest["title"] = "Sample <TVA>"
            manifest["markers"] = [{"frame": 1, "label": "Ending <tag>"}]
            write_tva(input_path, manifest)

            with contextlib.redirect_stdout(io.StringIO()):
                result = export_html(input_path, output_path)

            html = output_path.read_text(encoding="utf-8")
            self.assertEqual(result, 0)
            self.assertIn("<title>Sample &lt;TVA&gt;</title>", html)
            self.assertIn("const manifest =", html)
            self.assertIn("const frames =", html)
            self.assertIn("Ending &lt;tag&gt;", html)
            self.assertIn("abc\\nabc\\n", html)

    def test_export_html_rejects_existing_output_without_overwrite(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "sample.tva"
            output_path = Path(tmp) / "sample.html"
            write_tva(input_path)
            output_path.write_text("existing", encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                result = export_html(input_path, output_path)

            self.assertEqual(result, 1)
            self.assertEqual(output_path.read_text(encoding="utf-8"), "existing")

    def test_cli_export_html(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "sample.tva"
            output_path = Path(tmp) / "sample.html"
            write_tva(input_path)

            with contextlib.redirect_stdout(io.StringIO()):
                result = main(["export", "html", str(input_path), "-o", str(output_path)])

            self.assertEqual(result, 0)
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
