from __future__ import annotations

import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from .constants import (
    DEFAULT_ASPECT_CORRECTION,
    DEFAULT_CHARSET,
    DEFAULT_FPS,
    DEFAULT_WIDTH,
    FRAMES_PATH,
    MANIFEST_NAME,
    MAX_FRAME_COUNT,
    TVA_FORMAT,
    TVA_FORMAT_NAME,
    TVA_VERSION,
)
from . import __version__
from .core import TextFrameConverter
from .tva import frame_path, write_frame, write_manifest


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
        import cv2
    except ImportError:
        print("ERROR: opencv-python is required for convert. Install with `pip install -e .`.")
        return 1

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        print(f"ERROR: input video cannot be opened: {input_path}")
        return 1

    source_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    source_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    source_fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
    source_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

    source_duration = source_frame_count / source_fps if source_fps > 0 and source_frame_count > 0 else None
    end_time = start + duration if duration is not None else source_duration
    converter = TextFrameConverter(
        width=width,
        height=height,
        charset=charset,
        invert=invert,
        aspect_correction=aspect_correction,
    )

    temp_dir = Path(tempfile.mkdtemp(prefix="tvart-"))
    try:
        frames_dir = temp_dir / FRAMES_PATH
        frames_dir.mkdir(parents=True, exist_ok=True)

        frame_index = 0
        while True:
            timestamp = start + frame_index / fps
            if end_time is not None and timestamp >= end_time:
                break
            if frame_index >= MAX_FRAME_COUNT:
                print("ERROR: frame_count would exceed TVA v0.1.0 limit of 1000000")
                return 1
            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
            ok, frame = cap.read()
            if not ok:
                break
            lines = converter.convert_image(frame)
            write_frame(temp_dir / frame_path(frame_index), lines)
            frame_index += 1

        if frame_index == 0:
            print("ERROR: no frames were generated")
            return 1

        actual_duration = frame_index / fps
        height = converter.height
        source = {
            "type": "video",
            "filename": input_path.name,
            "width": source_width,
            "height": source_height,
            "fps": source_fps,
        }
        if source_duration is not None:
            source["duration"] = source_duration

        manifest = {
            "format": TVA_FORMAT,
            "format_name": TVA_FORMAT_NAME,
            "version": TVA_VERSION,
            "title": title or input_path.stem,
            "created_by": "tvart",
            "width": width,
            "height": height,
            "fps": fps,
            "frame_count": frame_index,
            "duration": actual_duration,
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
        write_manifest(temp_dir / MANIFEST_NAME, manifest)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(temp_dir / MANIFEST_NAME, MANIFEST_NAME)
            for index in range(frame_index):
                name = frame_path(index)
                zf.write(temp_dir / name, name)

        print(f"Wrote {output_path} ({frame_index} frames)")
        return 0
    finally:
        cap.release()
        shutil.rmtree(temp_dir, ignore_errors=True)
