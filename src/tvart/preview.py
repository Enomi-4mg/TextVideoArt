from __future__ import annotations

import sys
import time
from pathlib import Path

from .constants import DEFAULT_ASPECT_CORRECTION, DEFAULT_CHARSET, DEFAULT_FPS, DEFAULT_WIDTH
from .convert import _clear_status, _status, validate_convert_options
from .core import frame_to_text
from .play import play_tva


VIDEO_SUFFIXES = {".mp4", ".mov", ".avi", ".mkv"}


def preview_video(
    input_path: Path,
    *,
    width: int = DEFAULT_WIDTH,
    height: int | None = None,
    fps: float = DEFAULT_FPS,
    charset: str = DEFAULT_CHARSET,
    invert: bool = False,
    start: float = 0.0,
    duration: float | None = None,
    aspect_correction: float = DEFAULT_ASPECT_CORRECTION,
    loop: bool = False,
    no_clear: bool = False,
    once: bool = False,
    quiet: bool = False,
) -> int:
    if not input_path.exists():
        print(f"ERROR: input file does not exist: {input_path}")
        return 1
    if input_path.suffix.lower() not in VIDEO_SUFFIXES:
        print(f"ERROR: unsupported preview input: {input_path}")
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
        print("ERROR: opencv-python is required for video preview. Install with `pip install -e .`.")
        return 1

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        print(f"ERROR: input video cannot be opened: {input_path}")
        return 1
    _status(f"Preparing video preview: {input_path}", quiet=quiet)

    try:
        source_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        source_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        source_fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
        source_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

        if height is None:
            if source_width > 0 and source_height > 0:
                height = max(1, int(source_height / source_width * width * aspect_correction))
            else:
                height = max(1, int(width * aspect_correction))

        source_duration = source_frame_count / source_fps if source_fps > 0 and source_frame_count > 0 else None
        end_time = start + duration if duration is not None else source_duration
        delay = 1.0 / fps

        while True:
            frame_index = 0
            displayed = False
            while True:
                timestamp = start + frame_index / fps
                if end_time is not None and timestamp >= end_time:
                    break
                cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
                ok, frame = cap.read()
                if not ok:
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_AREA)
                lines = frame_to_text(resized, charset, invert)
                _clear_status(quiet=quiet)
                if not no_clear:
                    sys.stdout.write("\033[H\033[J")
                sys.stdout.write("\n".join(lines) + "\n")
                sys.stdout.flush()
                displayed = True
                if once:
                    return 0
                time.sleep(delay)
                frame_index += 1
            if not displayed:
                _clear_status(quiet=quiet)
                print("ERROR: no frames were available for preview")
                return 1
            if not loop:
                break
    except KeyboardInterrupt:
        return 0
    finally:
        cap.release()
    return 0


def preview_input(
    input_path: Path,
    *,
    width: int = DEFAULT_WIDTH,
    height: int | None = None,
    fps: float | None = None,
    charset: str = DEFAULT_CHARSET,
    invert: bool = False,
    start: float = 0.0,
    duration: float | None = None,
    aspect_correction: float = DEFAULT_ASPECT_CORRECTION,
    loop: bool = False,
    no_clear: bool = False,
    once: bool = False,
    quiet: bool = False,
) -> int:
    if input_path.suffix.lower() == ".tva":
        return play_tva(input_path, loop=loop, fps=fps, no_clear=no_clear, once=once)
    return preview_video(
        input_path,
        width=width,
        height=height,
        fps=fps if fps is not None else DEFAULT_FPS,
        charset=charset,
        invert=invert,
        start=start,
        duration=duration,
        aspect_correction=aspect_correction,
        loop=loop,
        no_clear=no_clear,
        once=once,
        quiet=quiet,
    )
