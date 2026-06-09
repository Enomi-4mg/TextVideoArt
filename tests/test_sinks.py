import json
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

import path_setup  # noqa: F401
from test_manifest import valid_manifest
from tvart.sinks import TvaArchiveWriter


class TvaArchiveWriterTests(unittest.TestCase):
    def test_writes_tva_archive(self) -> None:
        with TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "output.tva"
            manifest = valid_manifest()
            manifest["frame_count"] = 2

            writer = TvaArchiveWriter(output_path)
            writer.write_frame(["abc", "abc"])
            writer.write_frame(["def", "def"])
            writer.write_manifest(manifest)
            writer.close()

            with zipfile.ZipFile(output_path) as zf:
                self.assertEqual(zf.namelist(), ["manifest.json", "frames/000000.txt", "frames/000001.txt"])
                self.assertEqual(json.loads(zf.read("manifest.json").decode("utf-8"))["format"], "TVA")
                self.assertEqual(zf.read("frames/000000.txt").decode("utf-8"), "abc\nabc\n")
                self.assertEqual(zf.read("frames/000001.txt").decode("utf-8"), "def\ndef\n")

    def test_rejects_existing_output_without_overwrite(self) -> None:
        with TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "output.tva"
            output_path.write_bytes(b"exists")

            with self.assertRaises(FileExistsError):
                TvaArchiveWriter(output_path)


if __name__ == "__main__":
    unittest.main()
