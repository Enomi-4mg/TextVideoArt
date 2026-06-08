from __future__ import annotations

from typing import Any

from .charset import brightness_to_char


def frame_to_text(gray_frame: Any, charset: str, invert: bool) -> list[str]:
    rows: list[str] = []
    for row in gray_frame:
        rows.append("".join(brightness_to_char(int(value), charset, invert) for value in row))
    return rows
