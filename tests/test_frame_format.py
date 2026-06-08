import unittest

import path_setup  # noqa: F401
from tvart.tva import frame_path, normalize_frame_text


class FrameFormatTests(unittest.TestCase):
    def test_frame_path_generation(self) -> None:
        self.assertEqual(frame_path(0), "frames/000000.txt")
        self.assertEqual(frame_path(1), "frames/000001.txt")
        self.assertEqual(frame_path(239), "frames/000239.txt")
        self.assertEqual(frame_path(999999), "frames/999999.txt")

    def test_frame_path_rejects_negative_index(self) -> None:
        with self.assertRaises(ValueError):
            frame_path(-1)

    def test_frame_path_rejects_index_outside_six_digit_namespace(self) -> None:
        with self.assertRaises(ValueError):
            frame_path(1000000)

    def test_normalize_frame_text_removes_only_one_trailing_lf(self) -> None:
        self.assertEqual(normalize_frame_text("abc\n\n"), ["abc", ""])

    def test_normalize_frame_text_removes_only_one_trailing_crlf(self) -> None:
        self.assertEqual(normalize_frame_text("abc\r\n\r\n"), ["abc", ""])

    def test_normalize_frame_text_removes_only_one_trailing_cr(self) -> None:
        self.assertEqual(normalize_frame_text("abc\r\r"), ["abc", ""])


if __name__ == "__main__":
    unittest.main()
