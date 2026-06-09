from __future__ import annotations

from typing import Any

from .text_frame import frame_to_text


class TextFrameConverter:
    width: int
    height: int | None
    charset: str
    invert: bool
    aspect_correction: float

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

    def convert_image(self, image: Any) -> list[str]:
        try:
            import cv2
        except ImportError as exc:
            raise ImportError(
                "OpenCV is required for image-to-text conversion. Install opencv-python."
            ) from exc

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height = self._resolve_height(image)
        resized = cv2.resize(gray, (self.width, height), interpolation=cv2.INTER_AREA)
        return frame_to_text(resized, self.charset, self.invert)

    def _resolve_height(self, image: Any) -> int:
        if self.height is not None:
            return self.height

        source_height, source_width = _image_dimensions(image)
        if source_width > 0 and source_height > 0:
            self.height = max(
                1,
                int(source_height / source_width * self.width * self.aspect_correction),
            )
        else:
            self.height = max(1, int(self.width * self.aspect_correction))
        return self.height


def _image_dimensions(image: Any) -> tuple[int, int]:
    shape = getattr(image, "shape", None)
    if shape is None or len(shape) < 2:
        return 0, 0
    return int(shape[0] or 0), int(shape[1] or 0)
