import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

import path_setup  # noqa: F401
from tvart.sources import VideoFrameSource


class FakeVideoCapture:
    instances: list["FakeVideoCapture"] = []

    def __init__(self, path: str) -> None:
        self.path = path
        self.frames = ["frame-0", "frame-1", "frame-2"]
        self.index = 0
        self.timestamps: list[float] = []
        self.released = False
        FakeVideoCapture.instances.append(self)

    def isOpened(self) -> bool:
        return True

    def get(self, prop: int) -> float:
        values = {
            1: 640,
            2: 480,
            3: 30,
            4: 90,
        }
        return values.get(prop, 0)

    def set(self, prop: int, value: float) -> None:
        self.timestamps.append(value)

    def read(self) -> tuple[bool, str | None]:
        if self.index >= len(self.frames):
            return False, None
        frame = self.frames[self.index]
        self.index += 1
        return True, frame

    def release(self) -> None:
        self.released = True


class ClosedVideoCapture(FakeVideoCapture):
    def isOpened(self) -> bool:
        return False


def fake_cv2(capture: type[FakeVideoCapture] = FakeVideoCapture) -> SimpleNamespace:
    return SimpleNamespace(
        CAP_PROP_FRAME_WIDTH=1,
        CAP_PROP_FRAME_HEIGHT=2,
        CAP_PROP_FPS=3,
        CAP_PROP_FRAME_COUNT=4,
        CAP_PROP_POS_MSEC=5,
        VideoCapture=capture,
    )


class VideoFrameSourceTests(unittest.TestCase):
    def test_reads_metadata_and_frames(self) -> None:
        FakeVideoCapture.instances = []

        with TemporaryDirectory() as tmp, patch.dict(sys.modules, {"cv2": fake_cv2()}):
            input_path = Path(tmp) / "input.mp4"
            input_path.write_bytes(b"fake")

            with VideoFrameSource(input_path, fps=2, start=1.0, duration=1.0) as source:
                metadata = source.metadata
                frames = list(source)

        self.assertEqual(metadata.filename, "input.mp4")
        self.assertEqual(metadata.width, 640)
        self.assertEqual(metadata.height, 480)
        self.assertEqual(metadata.fps, 30)
        self.assertEqual(metadata.frame_count, 90)
        self.assertEqual(metadata.duration, 3.0)
        self.assertEqual(frames, ["frame-0", "frame-1"])
        self.assertEqual(FakeVideoCapture.instances[0].timestamps, [1000.0, 1500.0])
        self.assertTrue(FakeVideoCapture.instances[0].released)

    def test_rejects_unopenable_video(self) -> None:
        with TemporaryDirectory() as tmp, patch.dict(sys.modules, {"cv2": fake_cv2(ClosedVideoCapture)}):
            input_path = Path(tmp) / "input.mp4"
            input_path.write_bytes(b"fake")

            with self.assertRaises(ValueError):
                VideoFrameSource(input_path, fps=1)


if __name__ == "__main__":
    unittest.main()
