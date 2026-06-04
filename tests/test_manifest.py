import unittest

import path_setup  # noqa: F401
from tvart.constants import DEFAULT_CHARSET
from tvart.validate import validate_manifest


def valid_manifest() -> dict:
    return {
        "format": "TVA",
        "format_name": "Text Video Art",
        "version": "0.1.0",
        "title": "sample",
        "created_by": "tvart",
        "width": 3,
        "height": 2,
        "fps": 10,
        "frame_count": 2,
        "duration": 0.2,
        "charset": DEFAULT_CHARSET,
        "invert": False,
        "encoding": "utf-8",
        "color_mode": "none",
        "frame_format": "plain_text",
        "frames_path": "frames/",
    }


class ManifestValidationTests(unittest.TestCase):
    def test_manifest_validation_success(self) -> None:
        self.assertEqual(validate_manifest(valid_manifest()), [])

    def test_missing_required_manifest_field(self) -> None:
        manifest = valid_manifest()
        del manifest["width"]

        self.assertIn("missing manifest field: width", validate_manifest(manifest))

    def test_fps_rejects_bool(self) -> None:
        manifest = valid_manifest()
        manifest["fps"] = True

        self.assertIn("manifest field fps must be a number", validate_manifest(manifest))

    def test_duration_rejects_bool(self) -> None:
        manifest = valid_manifest()
        manifest["duration"] = False

        self.assertIn("manifest field duration must be a number", validate_manifest(manifest))

    def test_title_is_optional(self) -> None:
        manifest = valid_manifest()
        del manifest["title"]

        self.assertEqual(validate_manifest(manifest), [])

    def test_created_by_is_optional(self) -> None:
        manifest = valid_manifest()
        del manifest["created_by"]

        self.assertEqual(validate_manifest(manifest), [])


if __name__ == "__main__":
    unittest.main()
