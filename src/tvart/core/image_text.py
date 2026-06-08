from __future__ import annotations

from typing import Any

from .text_frame import frame_to_text


def image_to_text_frame(
    image: Any,
    *,
    width: int,
    height: int | None,
    charset: str,
    invert: bool,
    aspect_correction: float,
) -> list[str]:
    try:
        import cv2
    except ImportError as exc:
        raise ImportError(
            "OpenCV is required for image-to-text conversion. Install opencv-python."
        ) from exc

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if height is None:
        source_height, source_width = _image_dimensions(image)
        if source_width > 0 and source_height > 0:
            height = max(1, int(source_height / source_width * width * aspect_correction))
        else:
            height = max(1, int(width * aspect_correction))

    resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_AREA)
    return frame_to_text(resized, charset, invert)


def _image_dimensions(image: Any) -> tuple[int, int]:
    shape = getattr(image, "shape", None)
    if shape is None or len(shape) < 2:
        return 0, 0
    return int(shape[0] or 0), int(shape[1] or 0)
