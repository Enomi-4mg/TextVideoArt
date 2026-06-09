from __future__ import annotations

from typing import Any

from .converter import TextFrameConverter


def image_to_text_frame(
    image: Any,
    *,
    width: int,
    height: int | None,
    charset: str,
    invert: bool,
    aspect_correction: float,
) -> list[str]:
    converter = TextFrameConverter(
        width=width,
        height=height,
        charset=charset,
        invert=invert,
        aspect_correction=aspect_correction,
    )
    return converter.convert_image(image)
