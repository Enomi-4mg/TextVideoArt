from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import path_setup  # noqa: F401
from tvart.preview import preview_input


class ProgressTests(unittest.TestCase):
    def test_quiet_option_reaches_video_preview(self) -> None:
        with patch("tvart.preview.preview_video", return_value=0) as preview_video:
            code = preview_input(Path("clip.mp4"), quiet=True)

        self.assertEqual(code, 0)
        self.assertTrue(preview_video.call_args.kwargs["quiet"])


if __name__ == "__main__":
    unittest.main()
