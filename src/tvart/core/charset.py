from __future__ import annotations


def brightness_to_char(value: int, charset: str, invert: bool = False) -> str:
    index = int(value / 255 * (len(charset) - 1))
    if invert:
        index = (len(charset) - 1) - index
    return charset[index]
