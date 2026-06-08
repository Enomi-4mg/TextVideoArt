import unittest

import path_setup  # noqa: F401
from tvart.workflow import iter_text_frames


class FakeConverter:
    def __init__(self) -> None:
        self.frames: list[object] = []

    def convert_image(self, frame: object) -> list[str]:
        self.frames.append(frame)
        return [f"text-{frame}"]


class WorkflowTests(unittest.TestCase):
    def test_iter_text_frames_converts_source_frames(self) -> None:
        converter = FakeConverter()

        result = list(iter_text_frames(["a", "b"], converter))

        self.assertEqual(result, [["text-a"], ["text-b"]])
        self.assertEqual(converter.frames, ["a", "b"])


if __name__ == "__main__":
    unittest.main()
