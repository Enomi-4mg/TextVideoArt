from __future__ import annotations

import contextlib
import io
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from unittest.mock import patch

import path_setup  # noqa: F401
from tvart.play import leave_playback_screen
from tvart.preview import VIDEO_SUFFIXES, preview_input, preview_video


class FakePreviewCapture:
    def __init__(self, path: str) -> None:
        self.path = path

    def isOpened(self) -> bool:
        return True

    def get(self, prop: int) -> float:
        return {1: 2, 2: 2, 3: 1, 4: 1}.get(prop, 0)

    def set(self, prop: int, value: float) -> None:
        return None

    def read(self) -> tuple[bool, list[list[int]]]:
        return True, [[0, 255], [255, 0]]

    def release(self) -> None:
        return None


class PreviewTests(unittest.TestCase):
    def test_video_suffixes_include_planned_formats(self) -> None:
        self.assertEqual(VIDEO_SUFFIXES, {".mp4", ".mov", ".avi", ".mkv"})

    def test_preview_tva_delegates_to_player(self) -> None:
        with patch("tvart.preview.play_tva", return_value=0) as play:
            code = preview_input(Path("sample.tva"), loop=True, fps=12, no_clear=True, once=True)

        self.assertEqual(code, 0)
        play.assert_called_once_with(Path("sample.tva"), loop=True, fps=12, no_clear=True, once=True)

    def test_video_preview_leaves_playback_screen_when_once_returns(self) -> None:
        fake_cv2 = SimpleNamespace(
            CAP_PROP_FRAME_WIDTH=1,
            CAP_PROP_FRAME_HEIGHT=2,
            CAP_PROP_FPS=3,
            CAP_PROP_FRAME_COUNT=4,
            CAP_PROP_POS_MSEC=5,
            COLOR_BGR2GRAY=6,
            INTER_AREA=7,
            VideoCapture=FakePreviewCapture,
            cvtColor=lambda frame, mode: frame,
            resize=lambda frame, size, interpolation: [[0, 255]],
        )
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.mp4"
            input_path.write_bytes(b"fake")
            with (
                patch.dict(sys.modules, {"cv2": fake_cv2}),
                patch("tvart.preview.enter_playback_screen", return_value=True) as enter,
                patch("tvart.preview.leave_playback_screen") as leave,
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                code = preview_video(input_path, width=2, fps=1, once=True)

        self.assertEqual(code, 0)
        enter.assert_called_once()
        leave.assert_called_once()

    def test_leave_playback_screen_clears_before_restoring_terminal(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            leave_playback_screen()

        self.assertEqual(stdout.getvalue(), "\033[H\033[J\033[?25h\033[?1049l")


if __name__ == "__main__":
    unittest.main()
