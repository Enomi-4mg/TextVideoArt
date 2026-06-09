from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import path_setup  # noqa: F401
from tvart.convert import IMAGE_SUFFIXES, convert_input
from tvart.preview import preview_input


class ImageSupportTests(unittest.TestCase):
    def test_image_suffixes_include_planned_formats(self) -> None:
        self.assertEqual(IMAGE_SUFFIXES, {".jpg", ".jpeg", ".png", ".bmp", ".webp"})

    def test_convert_input_routes_images_to_image_converter(self) -> None:
        with patch("tvart.convert.convert_image", return_value=0) as convert_image:
            code = convert_input(Path("still.png"), Path("still.tva"))

        self.assertEqual(code, 0)
        convert_image.assert_called_once()

    def test_preview_input_routes_images_to_image_preview(self) -> None:
        with patch("tvart.preview.preview_image", return_value=0) as preview_image:
            code = preview_input(Path("still.jpg"))

        self.assertEqual(code, 0)
        preview_image.assert_called_once()


if __name__ == "__main__":
    unittest.main()
