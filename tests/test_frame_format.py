import unittest

import path_setup  # noqa: F401
from tvart.tva import frame_path


class FrameFormatTests(unittest.TestCase):
    def test_frame_path_generation(self) -> None:
        self.assertEqual(frame_path(0), "frames/000000.txt")
        self.assertEqual(frame_path(1), "frames/000001.txt")
        self.assertEqual(frame_path(239), "frames/000239.txt")


if __name__ == "__main__":
    unittest.main()
