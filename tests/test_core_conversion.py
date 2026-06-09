import contextlib
import io
import json
import sys
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from unittest.mock import patch

import path_setup  # noqa: F401
from tvart.convert import convert_video
from tvart.core import (
    TextFrameConverter,
    brightness_to_char,
    frame_to_text,
    image_to_text_frame,
)


class FakeImage:
    def __init__(self, shape: tuple[int, ...]) -> None:
        self.shape = shape


class FakeVideoCapture:
    def __init__(self, path: str) -> None:
        self.path = path
        self.frames = [FakeImage((10, 20, 3))]
        self.index = 0
        self.released = False

    def isOpened(self) -> bool:
        return True

    def get(self, prop: int) -> float:
        values = {
            1: 20,
            2: 10,
            3: 1,
            4: 1,
        }
        return values.get(prop, 0)

    def set(self, prop: int, value: float) -> None:
        return None

    def read(self) -> tuple[bool, FakeImage | None]:
        if self.index >= len(self.frames):
            return False, None
        frame = self.frames[self.index]
        self.index += 1
        return True, frame

    def release(self) -> None:
        self.released = True


class FakeLongVideoCapture(FakeVideoCapture):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.frames = [
            FakeImage((10, 20, 3)),
            FakeImage((10, 20, 3)),
        ]

    def get(self, prop: int) -> float:
        values = {
            1: 20,
            2: 10,
            3: 1,
            4: 2,
        }
        return values.get(prop, 0)


class FakeEmptyVideoCapture(FakeVideoCapture):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.frames = []


class FakeConverter:
    instances: list["FakeConverter"] = []

    def __init__(
        self,
        *,
        width: int,
        height: int | None,
        charset: str,
        invert: bool = False,
        aspect_correction: float = 0.5,
    ) -> None:
        self.width = width
        self.height = height
        self.charset = charset
        self.invert = invert
        self.aspect_correction = aspect_correction
        self.images: list[object] = []
        FakeConverter.instances.append(self)

    def convert_image(self, image: object) -> list[str]:
        self.images.append(image)
        if self.height is None:
            self.height = 4
        return ["ab"]


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

    def test_text_frame_converter_converts_fake_image(self) -> None:
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
            converter = TextFrameConverter(
                width=2,
                height=1,
                charset="ab",
                invert=False,
                aspect_correction=0.5,
            )
            result = converter.convert_image(FakeImage((10, 20, 3)))

        self.assertEqual(result, ["ab"])
        self.assertEqual(calls["resize"], ([[0, 255], [128, 0]], (2, 1), 3))

    def test_text_frame_converter_respects_invert(self) -> None:
        fake_cv2 = SimpleNamespace(
            COLOR_BGR2GRAY=7,
            INTER_AREA=3,
            cvtColor=lambda image, code: [[0, 255]],
            resize=lambda gray, size, interpolation: [[0, 255]],
        )

        with patch.dict(sys.modules, {"cv2": fake_cv2}):
            converter = TextFrameConverter(
                width=2,
                height=1,
                charset="ab",
                invert=True,
                aspect_correction=0.5,
            )
            result = converter.convert_image(FakeImage((10, 20, 3)))

        self.assertEqual(result, ["ba"])

    def test_text_frame_converter_respects_explicit_height(self) -> None:
        calls: dict[str, object] = {}

        def resize(gray: object, size: tuple[int, int], interpolation: int) -> list[list[int]]:
            calls["size"] = size
            return [[0], [255]]

        fake_cv2 = SimpleNamespace(
            COLOR_BGR2GRAY=7,
            INTER_AREA=3,
            cvtColor=lambda image, code: [[0]],
            resize=resize,
        )

        with patch.dict(sys.modules, {"cv2": fake_cv2}):
            converter = TextFrameConverter(
                width=3,
                height=2,
                charset="ab",
                invert=False,
                aspect_correction=0.5,
            )
            converter.convert_image(FakeImage((100, 10, 3)))

        self.assertEqual(converter.height, 2)
        self.assertEqual(calls["size"], (3, 2))

    def test_text_frame_converter_derives_and_stores_height(self) -> None:
        sizes: list[tuple[int, int]] = []

        def resize(gray: object, size: tuple[int, int], interpolation: int) -> list[list[int]]:
            sizes.append(size)
            return [[0], [255], [128]]

        fake_cv2 = SimpleNamespace(
            COLOR_BGR2GRAY=7,
            INTER_AREA=3,
            cvtColor=lambda image, code: [[0]],
            resize=resize,
        )

        with patch.dict(sys.modules, {"cv2": fake_cv2}):
            converter = TextFrameConverter(
                width=4,
                height=None,
                charset="ab",
                invert=False,
                aspect_correction=0.5,
            )
            result = converter.convert_image(FakeImage((40, 20, 3)))
            converter.convert_image(FakeImage((100, 10, 3)))

        self.assertEqual(converter.height, 4)
        self.assertEqual(sizes, [(4, 4), (4, 4)])
        self.assertEqual(result, ["a", "b", "a"])

    def test_image_to_text_frame_still_works(self) -> None:
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

    def test_convert_video_reuses_converter_and_writes_manifest_height(self) -> None:
        FakeConverter.instances = []
        fake_cv2 = SimpleNamespace(
            CAP_PROP_FRAME_WIDTH=1,
            CAP_PROP_FRAME_HEIGHT=2,
            CAP_PROP_FPS=3,
            CAP_PROP_FRAME_COUNT=4,
            CAP_PROP_POS_MSEC=5,
            VideoCapture=FakeVideoCapture,
        )

        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.mp4"
            output_path = Path(tmp) / "output.tva"
            input_path.write_bytes(b"fake")

            with (
                patch.dict(sys.modules, {"cv2": fake_cv2}),
                patch("tvart.convert.TextFrameConverter", FakeConverter),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                result = convert_video(input_path, output_path, width=2, fps=1)

            with zipfile.ZipFile(output_path) as zf:
                manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
                frame_text = zf.read("frames/000000.txt").decode("utf-8")

        self.assertEqual(result, 0)
        self.assertEqual(len(FakeConverter.instances), 1)
        self.assertEqual(len(FakeConverter.instances[0].images), 1)
        self.assertEqual(manifest["height"], 4)
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["source"]["type"], "video")
        self.assertEqual(manifest["source"]["duration"], 1.0)
        self.assertEqual(
            manifest["conversion"],
            {
                "tool": "tvart",
                "tool_version": "0.7.6",
                "width": 2,
                "height": 4,
                "fps": 1,
                "charset": " .:-=+*#%@",
                "invert": False,
                "aspect_correction": 0.5,
            },
        )
        self.assertEqual(frame_text, "ab\n")

    def test_convert_video_rejects_more_than_max_frame_count(self) -> None:
        FakeConverter.instances = []
        fake_cv2 = SimpleNamespace(
            CAP_PROP_FRAME_WIDTH=1,
            CAP_PROP_FRAME_HEIGHT=2,
            CAP_PROP_FPS=3,
            CAP_PROP_FRAME_COUNT=4,
            CAP_PROP_POS_MSEC=5,
            VideoCapture=FakeLongVideoCapture,
        )

        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.mp4"
            output_path = Path(tmp) / "output.tva"
            input_path.write_bytes(b"fake")
            stdout = io.StringIO()

            with (
                patch.dict(sys.modules, {"cv2": fake_cv2}),
                patch("tvart.convert.TextFrameConverter", FakeConverter),
                patch("tvart.convert.MAX_FRAME_COUNT", 1),
                contextlib.redirect_stdout(stdout),
            ):
                result = convert_video(input_path, output_path, width=2, fps=1)

        self.assertEqual(result, 1)
        self.assertFalse(output_path.exists())
        self.assertIn("ERROR: frame_count would exceed TVA v0.1.0 limit of 1000000", stdout.getvalue())
        self.assertEqual(len(FakeConverter.instances), 1)
        self.assertEqual(len(FakeConverter.instances[0].images), 1)

    def test_convert_video_returns_error_when_no_frames_generated(self) -> None:
        FakeConverter.instances = []
        fake_cv2 = SimpleNamespace(
            CAP_PROP_FRAME_WIDTH=1,
            CAP_PROP_FRAME_HEIGHT=2,
            CAP_PROP_FPS=3,
            CAP_PROP_FRAME_COUNT=4,
            CAP_PROP_POS_MSEC=5,
            VideoCapture=FakeEmptyVideoCapture,
        )

        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.mp4"
            output_path = Path(tmp) / "output.tva"
            input_path.write_bytes(b"fake")
            stdout = io.StringIO()

            with (
                patch.dict(sys.modules, {"cv2": fake_cv2}),
                patch("tvart.convert.TextFrameConverter", FakeConverter),
                contextlib.redirect_stdout(stdout),
            ):
                result = convert_video(input_path, output_path, width=2, fps=1)

        self.assertEqual(result, 1)
        self.assertFalse(output_path.exists())
        self.assertIn("ERROR: no frames were generated", stdout.getvalue())

    def test_convert_video_rejects_existing_output_without_overwrite(self) -> None:
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.mp4"
            output_path = Path(tmp) / "output.tva"
            input_path.write_bytes(b"fake")
            output_path.write_bytes(b"exists")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                result = convert_video(input_path, output_path)

        self.assertEqual(result, 1)
        self.assertIn(f"ERROR: output file already exists: {output_path}", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
