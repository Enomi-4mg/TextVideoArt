import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import path_setup  # noqa: F401
from tvart.core import brightness_to_char, frame_to_text, image_to_text_frame


class FakeImage:
    def __init__(self, shape: tuple[int, ...]) -> None:
        self.shape = shape


class CoreConversionTests(unittest.TestCase):
    def test_brightness_to_char_maps_range(self) -> None:
        self.assertEqual(brightness_to_char(0, "abc"), "a")
        self.assertEqual(brightness_to_char(127, "abc"), "a")
        self.assertEqual(brightness_to_char(128, "abc"), "b")
        self.assertEqual(brightness_to_char(255, "abc"), "c")

    def test_brightness_to_char_invert_reverses_mapping(self) -> None:
        self.assertEqual(brightness_to_char(0, "abc", invert=True), "c")
        self.assertEqual(brightness_to_char(255, "abc", invert=True), "a")

    def test_frame_to_text_converts_grayscale_rows(self) -> None:
        gray_frame = [
            [0, 128, 255],
            [255, 0, 128],
        ]

        self.assertEqual(frame_to_text(gray_frame, "abc", False), ["abc", "cab"])

    def test_image_to_text_frame_uses_patched_cv2(self) -> None:
        calls: dict[str, object] = {}

        def cvt_color(image: object, code: int) -> list[list[int]]:
            calls["cvtColor"] = (image, code)
            return [[0, 255], [128, 0]]

        def resize(gray: object, size: tuple[int, int], interpolation: int) -> list[list[int]]:
            calls["resize"] = (gray, size, interpolation)
            return [[0, 255]]

        fake_cv2 = SimpleNamespace(
            COLOR_BGR2GRAY=7,
            INTER_AREA=3,
            cvtColor=cvt_color,
            resize=resize,
        )

        with patch.dict(sys.modules, {"cv2": fake_cv2}):
            result = image_to_text_frame(
                FakeImage((10, 20, 3)),
                width=2,
                height=1,
                charset="ab",
                invert=False,
                aspect_correction=0.5,
            )

        self.assertEqual(result, ["ab"])
        self.assertEqual(calls["resize"], ([[0, 255], [128, 0]], (2, 1), 3))

    def test_image_to_text_frame_derives_height_when_missing(self) -> None:
        calls: dict[str, object] = {}

        def resize(gray: object, size: tuple[int, int], interpolation: int) -> list[list[int]]:
            calls["size"] = size
            return [[0], [255], [128]]

        fake_cv2 = SimpleNamespace(
            COLOR_BGR2GRAY=7,
            INTER_AREA=3,
            cvtColor=lambda image, code: [[0]],
            resize=resize,
        )

        with patch.dict(sys.modules, {"cv2": fake_cv2}):
            result = image_to_text_frame(
                FakeImage((40, 20, 3)),
                width=4,
                height=None,
                charset="ab",
                invert=False,
                aspect_correction=0.5,
            )

        self.assertEqual(calls["size"], (4, 4))
        self.assertEqual(result, ["a", "b", "a"])


if __name__ == "__main__":
    unittest.main()
