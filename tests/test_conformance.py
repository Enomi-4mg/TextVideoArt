import base64
import json
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
import path_setup
from tvart.validate import validate_tva
ROOT = Path(__file__).resolve().parent.parent

class ConformanceTests(unittest.TestCase):
    def test_common_conformance(self):
        fixture = json.loads((ROOT / "tests/fixtures/conformance/cases.json").read_text())
        for case in fixture["cases"]:
            with self.subTest(case=case["id"]), TemporaryDirectory() as tmp:
                path = Path(tmp) / "case.tva"
                manifest = {**fixture["base"], **case.get("manifest", {})}
                raw = base64.b64decode(case["manifestBytes"]) if "manifestBytes" in case else case.get("rawManifest", json.dumps(manifest, ensure_ascii=True))
                with zipfile.ZipFile(path, "w") as zf:
                    zf.writestr("manifest.json", raw)
                    for i, text in enumerate(case.get("frames", ["abc\ndef\n"])):
                        zf.writestr(f"frames/{i:06d}.txt", base64.b64decode(case["frameBytes"]) if "frameBytes" in case else text)
                    for name, text in case.get("extra", []):
                        zf.writestr(name, text)
                if case.get("corruptCrc"):
                    raw = bytearray(path.read_bytes())
                    offset = raw.index(b"PK\x01\x02")
                    raw[offset + 16:offset + 20] = b"\0" * 4
                    path.write_bytes(raw)
                self.assertEqual(not validate_tva(path), case["valid"])
