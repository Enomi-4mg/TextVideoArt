from __future__ import annotations


def brightness_to_char(value: int, charset: str, invert: bool = False) -> str:
    """Map one grayscale brightness value to a character from a concrete ramp."""
    index = int(value / 255 * (len(charset) - 1))
    if invert:
        index = (len(charset) - 1) - index
    return charset[index]
