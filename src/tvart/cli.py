from __future__ import annotations

import argparse
from pathlib import Path

from .constants import (
    DEFAULT_ASPECT_CORRECTION,
    DEFAULT_CHARSET,
    DEFAULT_FPS,
    DEFAULT_WIDTH,
)
from .convert import convert_video
from .extract import extract_tva
from .info import print_info
from .pack import pack_tva
from .play import play_tva
from .validate import print_validation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tvart", description="Create and play TVA (Text Video Art) files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert = subparsers.add_parser("convert", help="convert a video file to .tva")
    convert.add_argument("input", type=Path)
    convert.add_argument("output", type=Path)
    convert.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    convert.add_argument("--height", type=int)
    convert.add_argument("--fps", type=float, default=DEFAULT_FPS)
    convert.add_argument("--charset", default=DEFAULT_CHARSET)
    convert.add_argument("--invert", action="store_true")
    convert.add_argument("--start", type=float, default=0.0)
    convert.add_argument("--duration", type=float)
    convert.add_argument("--title")
    convert.add_argument("--overwrite", action="store_true")
    convert.add_argument("--aspect-correction", type=float, default=DEFAULT_ASPECT_CORRECTION)

    play = subparsers.add_parser("play", help="play a .tva file in the terminal")
    play.add_argument("input", type=Path)
    play.add_argument("--loop", action="store_true")
    play.add_argument("--fps", type=float)
    play.add_argument("--no-clear", action="store_true")
    play.add_argument("--once", action="store_true")

    info = subparsers.add_parser("info", help="print .tva metadata")
    info.add_argument("input", type=Path)

    extract = subparsers.add_parser("extract", help="extract a .tva archive")
    extract.add_argument("input", type=Path)
    extract.add_argument("output_dir", type=Path)
    extract.add_argument("--overwrite", action="store_true")

    unpack = subparsers.add_parser("unpack", help="unpack a .tva archive into a project directory")
    unpack.add_argument("input", type=Path)
    unpack.add_argument("output_dir", type=Path)
    unpack.add_argument("--overwrite", action="store_true")

    validate = subparsers.add_parser("validate", help="validate a .tva file or extracted project directory")
    validate.add_argument("input", type=Path)

    pack = subparsers.add_parser("pack", help="pack an extracted TVA project directory")
    pack.add_argument("input_dir", type=Path)
    pack.add_argument("output", type=Path)
    pack.add_argument("--overwrite", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "convert":
        return convert_video(
            args.input,
            args.output,
            width=args.width,
            height=args.height,
            fps=args.fps,
            charset=args.charset,
            invert=args.invert,
            start=args.start,
            duration=args.duration,
            title=args.title,
            overwrite=args.overwrite,
            aspect_correction=args.aspect_correction,
        )
    if args.command == "play":
        return play_tva(args.input, loop=args.loop, fps=args.fps, no_clear=args.no_clear, once=args.once)
    if args.command == "info":
        return print_info(args.input)
    if args.command in {"extract", "unpack"}:
        return extract_tva(args.input, args.output_dir, overwrite=args.overwrite)
    if args.command == "validate":
        return print_validation(args.input)
    if args.command == "pack":
        return pack_tva(args.input_dir, args.output, overwrite=args.overwrite)

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
