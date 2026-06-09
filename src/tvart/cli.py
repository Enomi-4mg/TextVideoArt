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
from .export import export_html
from .extract import extract_tva
from .fix import fix_tva
from .info import print_info, print_inspect
from .pack import pack_tva
from .play import play_tva
from .preview import preview_input
from .validate import print_validation


def resolve_output_path(
    parser: argparse.ArgumentParser,
    positional: Path | None,
    option: Path | None,
    command_name: str,
) -> Path:
    if positional is None and option is None:
        parser.error(f"{command_name} requires an output path via positional argument or -o/--output")
    if positional is not None and option is not None:
        parser.error(f"{command_name} output path must be provided either positionally or via -o/--output, not both")
    return positional if positional is not None else option


def add_playback_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("input", type=Path)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--fps", type=float)
    parser.add_argument("--no-clear", action="store_true")
    parser.add_argument("--once", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tvart", description="Create and play TVA (Text Video Art) files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert = subparsers.add_parser("convert", help="convert a video file to .tva")
    convert.add_argument("input", type=Path)
    convert.add_argument("output", nargs="?", type=Path)
    convert.add_argument("-o", "--output", dest="output_option", type=Path)
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
    convert.set_defaults(_parser=convert)

    play = subparsers.add_parser("play", help="play a .tva file in the terminal")
    add_playback_arguments(play)

    preview = subparsers.add_parser("preview", help="preview a .tva file in the terminal")
    add_playback_arguments(preview)

    preview = subparsers.add_parser("preview", help="preview a .tva or video file in the terminal")
    preview.add_argument("input", type=Path)
    preview.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    preview.add_argument("--height", type=int)
    preview.add_argument("--fps", type=float)
    preview.add_argument("--charset", default=DEFAULT_CHARSET)
    preview.add_argument("--invert", action="store_true")
    preview.add_argument("--start", type=float, default=0.0)
    preview.add_argument("--duration", type=float)
    preview.add_argument("--aspect-correction", type=float, default=DEFAULT_ASPECT_CORRECTION)
    preview.add_argument("--loop", action="store_true")
    preview.add_argument("--no-clear", action="store_true")
    preview.add_argument("--once", action="store_true")

    info = subparsers.add_parser("info", help="print .tva metadata")
    info.add_argument("input", type=Path)

    inspect = subparsers.add_parser("inspect", help="inspect .tva metadata")
    inspect.add_argument("input", type=Path)
    inspect.add_argument("--json", action="store_true")
    inspect.add_argument("--markers", action="store_true")

    extract = subparsers.add_parser("extract", help="extract a .tva archive")
    extract.add_argument("input", type=Path)
    extract.add_argument("output_dir", type=Path)
    extract.add_argument("--overwrite", action="store_true")

    unpack = subparsers.add_parser("unpack", help="unpack a .tva archive into a project directory")
    unpack.add_argument("input", type=Path)
    unpack.add_argument("output_dir", nargs="?", type=Path)
    unpack.add_argument("-o", "--output", dest="output_option", type=Path)
    unpack.add_argument("--overwrite", action="store_true")
    unpack.set_defaults(_parser=unpack)

    validate = subparsers.add_parser("validate", help="validate a .tva file or extracted project directory")
    validate.add_argument("input", type=Path)

    pack = subparsers.add_parser("pack", help="pack an extracted TVA project directory")
    pack.add_argument("input_dir", type=Path)
    pack.add_argument("output", nargs="?", type=Path)
    pack.add_argument("-o", "--output", dest="output_option", type=Path)
    pack.add_argument("--overwrite", action="store_true")
    pack.set_defaults(_parser=pack)

    export = subparsers.add_parser("export", help="export a .tva file")
    export_subparsers = export.add_subparsers(dest="export_format", required=True)
    export_html_parser = export_subparsers.add_parser("html", help="export a standalone HTML player")
    export_html_parser.add_argument("input", type=Path)
    export_html_parser.add_argument("-o", "--output", required=True, type=Path)
    export_html_parser.add_argument("--overwrite", action="store_true")

    fix = subparsers.add_parser("fix", help="update .tva manifest metadata")
    fix.add_argument("input", type=Path)
    fix.add_argument("output", type=Path, nargs="?")
    fix.add_argument("-o", "--output-file", type=Path)
    fix.add_argument("--title")
    fix.add_argument("--author")
    fix.add_argument("--description")
    fix.add_argument("--license")
    fix.add_argument("--created-by")
    fix.add_argument("--tag", action="append", dest="tags")
    fix.add_argument("--set-charset", dest="charset")
    fix.add_argument("--overwrite", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "convert":
        output = resolve_output_path(args._parser, args.output, args.output_option, "convert")
        return convert_video(
            args.input,
            output,
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
    if args.command in {"play", "preview"}:
        return play_tva(args.input, loop=args.loop, fps=args.fps, no_clear=args.no_clear, once=args.once)
    if args.command == "preview":
        return preview_input(
            args.input,
            width=args.width,
            height=args.height,
            fps=args.fps,
            charset=args.charset,
            invert=args.invert,
            start=args.start,
            duration=args.duration,
            aspect_correction=args.aspect_correction,
            loop=args.loop,
            no_clear=args.no_clear,
            once=args.once,
        )
    if args.command == "info":
        return print_info(args.input)
    if args.command == "inspect":
        return print_inspect(args.input, as_json=args.json, markers=args.markers)
    if args.command in {"extract", "unpack"}:
        output_dir = args.output_dir
        if args.command == "unpack":
            output_dir = resolve_output_path(args._parser, args.output_dir, args.output_option, "unpack")
        return extract_tva(args.input, output_dir, overwrite=args.overwrite)
    if args.command == "validate":
        return print_validation(args.input)
    if args.command == "pack":
        output = resolve_output_path(args._parser, args.output, args.output_option, "pack")
        return pack_tva(args.input_dir, output, overwrite=args.overwrite)
    if args.command == "export" and args.export_format == "html":
        return export_html(args.input, args.output, overwrite=args.overwrite)
    if args.command == "fix":
        output = args.output_file or args.output
        if output is None:
            parser.error("fix requires an output path, either positional or with -o/--output-file")
        if args.output_file is not None and args.output is not None:
            parser.error("fix output must be provided either positionally or with -o/--output-file, not both")
        return fix_tva(
            args.input,
            output,
            title=args.title,
            author=args.author,
            description=args.description,
            license=args.license,
            created_by=args.created_by,
            tags=args.tags,
            charset=args.charset,
            overwrite=args.overwrite,
        )

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
