from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .constants import (
    DEFAULT_ASPECT_CORRECTION,
    DEFAULT_CHARSET,
    DEFAULT_FPS,
    DEFAULT_WIDTH,
    FRAMES_PATH,
    MAX_FRAME_COUNT,
    TVA_FORMAT,
    TVA_FORMAT_NAME,
    TVA_VERSION,
)
from . import __version__
from .core import TextFrameConverter
from .sinks import TvaArchiveWriter
from .sources import VideoFrameSource, VideoSourceMetadata
from .workflow import iter_text_frames


def validate_convert_options(
    *,
    width: int,
    height: int | None,
    fps: float,
    duration: float | None,
    aspect_correction: float,
    charset: str,
) -> list[str]:
    errors: list[str] = []
    if width <= 0:
        errors.append("width must be positive")
    if height is not None and height <= 0:
        errors.append("height must be positive")
    if fps <= 0:
        errors.append("fps must be positive")
    if duration is not None and duration <= 0:
        errors.append("duration must be positive")
    if aspect_correction <= 0:
        errors.append("aspect_correction must be positive")
    if len(charset) < 2:
        errors.append("charset must contain at least 2 characters")
    if "\n" in charset or "\t" in charset:
        errors.append("charset must not contain newline or tab")
    return errors


def build_convert_manifest(
    *,
    input_path: Path,
    width: int,
    height: int,
    fps: float,
    frame_count: int,
    charset: str,
    invert: bool,
    title: str | None,
    aspect_correction: float,
    source_metadata: VideoSourceMetadata,
) -> dict:
    source = {
        "type": "video",
        "filename": source_metadata.filename,
        "width": source_metadata.width,
        "height": source_metadata.height,
        "fps": source_metadata.fps,
    }
    if source_metadata.duration is not None:
        source["duration"] = source_metadata.duration

    return {
        "format": TVA_FORMAT,
        "format_name": TVA_FORMAT_NAME,
        "version": TVA_VERSION,
        "title": title or input_path.stem,
        "created_by": "tvart",
        "width": width,
        "height": height,
        "fps": fps,
        "frame_count": frame_count,
        "duration": frame_count / fps,
        "charset": charset,
        "invert": invert,
        "encoding": "utf-8",
        "color_mode": "none",
        "frame_format": "plain_text",
        "frames_path": FRAMES_PATH,
        "source": source,
        "conversion": {
            "tool": "tvart",
            "tool_version": __version__,
            "width": width,
            "height": height,
            "fps": fps,
            "charset": charset,
            "invert": invert,
            "aspect_correction": aspect_correction,
        },
        "aspect_correction": aspect_correction,
        "created_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    }


def convert_video(
    input_path: Path,
    output_path: Path,
    *,
    width: int = DEFAULT_WIDTH,
    height: int | None = None,
    fps: float = DEFAULT_FPS,
    charset: str = DEFAULT_CHARSET,
    invert: bool = False,
    start: float = 0.0,
    duration: float | None = None,
    title: str | None = None,
    overwrite: bool = False,
    aspect_correction: float = DEFAULT_ASPECT_CORRECTION,
) -> int:
    if not input_path.exists():
        print(f"ERROR: input file does not exist: {input_path}")
        return 1
    if output_path.exists() and not overwrite:
        print(f"ERROR: output file already exists: {output_path}")
        return 1
    if start < 0:
        print("ERROR: start must be non-negative")
        return 1

    option_errors = validate_convert_options(
        width=width,
        height=height,
        fps=fps,
        duration=duration,
        aspect_correction=aspect_correction,
        charset=charset,
    )
    if option_errors:
        for error in option_errors:
            print(f"ERROR: {error}")
        return 1

    try:
        source = VideoFrameSource(input_path, fps=fps, start=start, duration=duration)
    except ImportError:
        print("ERROR: opencv-python is required for convert. Install with `pip install -e .`.")
        return 1
    except ValueError:
        print(f"ERROR: input video cannot be opened: {input_path}")
        return 1

    with source:
        converter = TextFrameConverter(
            width=width,
            height=height,
            charset=charset,
            invert=invert,
            aspect_correction=aspect_correction,
        )
        writer = TvaArchiveWriter(output_path, overwrite=overwrite)
        frame_index = 0
        frame_limit_exceeded = False

        def bounded_source() -> Iterator[Any]:
            nonlocal frame_limit_exceeded
            for frame in source:
                if frame_index >= MAX_FRAME_COUNT:
                    frame_limit_exceeded = True
                    break
                yield frame

        try:
            for lines in iter_text_frames(bounded_source(), converter):
                writer.write_frame(lines)
                frame_index += 1

            if frame_limit_exceeded:
                print("ERROR: frame_count would exceed TVA v0.1.0 limit of 1000000")
                return 1

            if frame_index == 0:
                print("ERROR: no frames were generated")
                return 1

            resolved_height = converter.height
            if resolved_height is None:
                print("ERROR: no frames were generated")
                return 1
            manifest = build_convert_manifest(
                input_path=input_path,
                width=width,
                height=resolved_height,
                fps=fps,
                frame_count=frame_index,
                charset=charset,
                invert=invert,
                title=title,
                aspect_correction=aspect_correction,
                source_metadata=source.metadata,
            )
            writer.write_manifest(manifest)
            writer.close()
        finally:
            writer.cleanup()

        print(f"Wrote {output_path} ({frame_index} frames)")
        return 0
