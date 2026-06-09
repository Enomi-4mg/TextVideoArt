from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


@dataclass(frozen=True)
class VideoSourceMetadata:
    filename: str
    width: int
    height: int
    fps: float
    frame_count: int
    duration: float | None


class VideoFrameSource:
    def __init__(
        self,
        input_path: Path,
        *,
        fps: float,
        start: float = 0.0,
        duration: float | None = None,
    ) -> None:
        if not input_path.exists():
            raise FileNotFoundError(f"input file does not exist: {input_path}")

        try:
            import cv2
        except ImportError as exc:
            raise ImportError(
                "opencv-python is required for convert. Install with `pip install -e .`."
            ) from exc

        self.input_path = input_path
        self.fps = fps
        self.start = start
        self.duration = duration
        self._cv2 = cv2
        self._cap = cv2.VideoCapture(str(input_path))
        if not self._cap.isOpened():
            raise ValueError(f"input video cannot be opened: {input_path}")

        source_width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        source_height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        source_fps = float(self._cap.get(cv2.CAP_PROP_FPS) or 0)
        source_frame_count = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        source_duration = (
            source_frame_count / source_fps
            if source_fps > 0 and source_frame_count > 0
            else None
        )
        self.metadata = VideoSourceMetadata(
            filename=input_path.name,
            width=source_width,
            height=source_height,
            fps=source_fps,
            frame_count=source_frame_count,
            duration=source_duration,
        )

    def __iter__(self) -> Iterator[Any]:
        frame_index = 0
        end_time = self.start + self.duration if self.duration is not None else self.metadata.duration

        while True:
            timestamp = self.start + frame_index / self.fps
            if end_time is not None and timestamp >= end_time:
                break
            self._cap.set(self._cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
            ok, frame = self._cap.read()
            if not ok:
                break
            yield frame
            frame_index += 1

    def close(self) -> None:
        self._cap.release()

    def __enter__(self) -> "VideoFrameSource":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()
