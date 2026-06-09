from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import path_setup  # noqa: F401
from tvart.preview import VIDEO_SUFFIXES, preview_input


class PreviewTests(unittest.TestCase):
    def test_video_suffixes_include_planned_formats(self) -> None:
        self.assertEqual(VIDEO_SUFFIXES, {".mp4", ".mov", ".avi", ".mkv"})

    def test_preview_tva_delegates_to_player(self) -> None:
        with patch("tvart.preview.play_tva", return_value=0) as play:
            code = preview_input(Path("sample.tva"), loop=True, fps=12, no_clear=True, once=True)

        self.assertEqual(code, 0)
        play.assert_called_once_with(Path("sample.tva"), loop=True, fps=12, no_clear=True, once=True)


if __name__ == "__main__":
    unittest.main()
