from __future__ import annotations


CHARSET_PRESETS = {
    "standard": " .:-=+*#%@",
    "simple": " .#",
    "blocks": " ░▒▓█",
    "dense": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
}


def resolve_charset(charset: str | None, preset: str | None) -> str:
    if preset is None:
        if charset is None:
            return CHARSET_PRESETS["standard"]
        return charset
    try:
        return CHARSET_PRESETS[preset]
    except KeyError as exc:
        names = ", ".join(sorted(CHARSET_PRESETS))
        raise ValueError(f"unknown charset preset: {preset}. Available presets: {names}") from exc
