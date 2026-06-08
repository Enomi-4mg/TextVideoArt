from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any

from .core import TextFrameConverter


def iter_text_frames(source: Iterable[Any], converter: TextFrameConverter) -> Iterator[list[str]]:
    for frame in source:
        yield converter.convert_image(frame)
