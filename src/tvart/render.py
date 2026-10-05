"""Local monochrome rendering. OpenCV ASCII/block glyphs; no new dependency."""
from __future__ import annotations
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from .tva import frame_path, normalize_frame_text
from .validate import validate_tva


def compute_layout(columns, rows, width, height, fit="contain", cell_aspect=0.5, cell_height=16):
    if columns < 1 or rows < 1 or width < 1 or height < 1 or fit not in {"native", "contain", "cover"}:
        raise ValueError("invalid layout")
    native_width, native_height = columns * cell_height * cell_aspect, rows * cell_height
    scale = 1 if fit == "native" else (max if fit == "cover" else min)(width / native_width, height / native_height)
    return ((width - native_width * scale) / 2, (height - native_height * scale) / 2,
            cell_height * cell_aspect * scale, cell_height * scale)


def color(value):
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError("colors must be #rrggbb")
    return tuple(int(value[i:i+2], 16) for i in (5, 3, 1))


def render_frame(lines, size=(1280, 720), fit="contain", fg="#ffffff", bg="#050505"):
    import cv2
    import numpy as np
    width, height = size
    if any(ord(c) > 126 and c not in "░▒▓█" for line in lines for c in line):
        raise ValueError("local renderer supports ASCII and ░▒▓█ only; use browser PNG for other Unicode")
    image = np.empty((height, width, 3), dtype=np.uint8)
    foreground, background = color(fg), color(bg)
    image[:] = background
    x0, y0, cw, ch = compute_layout(len(lines[0]), len(lines), width, height, fit)
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            left, top = round(x0 + x*cw), round(y0 + y*ch)
            right, bottom = round(x0 + (x+1)*cw), round(y0 + (y+1)*ch)
            if char in "░▒▓█":
                alpha = ("░▒▓█".index(char) + 1) / 4
                shade = tuple(round(b + alpha*(f-b)) for f, b in zip(foreground, background))
                cv2.rectangle(image, (left, top), (right-1, bottom-1), shade, -1)
            elif char != " ":
                scale = min(ch / 24, cw / 20)
                (tw, th), baseline = cv2.getTextSize(char, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)
                cv2.putText(image, char, (round(left+(cw-tw)/2), round(top+(ch+th)/2)),
                            cv2.FONT_HERSHEY_SIMPLEX, scale, foreground, 1, cv2.LINE_AA)
    return image


def write_png_sequence(input_path, directory, *, size=(1280,720), fit="contain", fg="#ffffff", bg="#050505"):
    import cv2
    errors = validate_tva(input_path)
    if errors:
        raise ValueError("\n".join(errors))
    if input_path.is_dir():
        manifest = json.loads((input_path / "manifest.json").read_text(encoding="utf-8"))
        read = lambda name: (input_path/name).read_text(encoding="utf-8")
        archive = None
    else:
        archive = zipfile.ZipFile(input_path)
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        read = lambda name: archive.read(name).decode("utf-8")
    try:
        directory.mkdir(parents=True, exist_ok=False)
        for i in range(int(manifest["frame_count"])):
            image = render_frame(normalize_frame_text(read(frame_path(i))), size, fit, fg, bg)
            if not cv2.imwrite(str(directory / f"{i:06d}.png"), image):
                raise ValueError("PNG write failed")
        return manifest
    finally:
        if archive:
            archive.close()


def ffmpeg_arguments(ffmpeg, directory, output, fps, overwrite=False):
    return [str(ffmpeg), "-hide_banner", "-loglevel", "error", "-y" if overwrite else "-n",
            "-framerate", str(fps), "-start_number", "0", "-i", str(directory / "%06d.png"),
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)]


def render_tva(input_path: Path, output: Path, *, format="png", size="1280x720", fit="contain",
               fg="#ffffff", bg="#050505", ffmpeg="ffmpeg", overwrite=False) -> int:
    try:
        match = re.fullmatch(r"([0-9]+)x([0-9]+)", size)
        if not match:
            raise ValueError("size must be WIDTHxHEIGHT")
        dimensions = tuple(int(n) for n in match.groups())
        if min(dimensions) < 2 or max(dimensions) > 4096:
            raise ValueError("size must be between 2 and 4096 pixels")
        color(fg); color(bg)
        if output.exists() and (format == "png" or not overwrite):
            raise ValueError("output already exists; PNG requires a new directory")
        if format == "png":
            write_png_sequence(input_path, output, size=dimensions, fit=fit, fg=fg, bg=bg)
        else:
            if output.suffix.lower() != ".mp4":
                raise ValueError("MP4 output requires .mp4 extension")
            executable = shutil.which(str(ffmpeg))
            if not executable:
                raise ValueError("FFmpeg is unavailable; install FFmpeg with libx264")
            encoders = subprocess.run([executable, "-hide_banner", "-encoders"], capture_output=True, text=True, check=True)
            if "libx264" not in encoders.stdout:
                raise ValueError("FFmpeg has no libx264 encoder")
            dimensions = tuple(n + n % 2 for n in dimensions)
            with tempfile.TemporaryDirectory(prefix="tvart-render-") as tmp:
                frames = Path(tmp) / "frames"
                manifest = write_png_sequence(input_path, frames, size=dimensions, fit=fit, fg=fg, bg=bg)
                subprocess.run(ffmpeg_arguments(executable, frames, output, manifest["fps"], overwrite), check=True)
            if not output.is_file() or output.stat().st_size == 0:
                raise ValueError("FFmpeg produced no output")
        print(f"Saved {output}")
        return 0
    except (ValueError, OSError, ImportError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}")
        return 1
