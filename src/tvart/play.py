from __future__ import annotations

import sys
import time
import zipfile
from pathlib import Path

from .tva import frame_path, read_manifest_from_zip


def enter_playback_screen() -> bool:
    if not sys.stdout.isatty():
        return False
    sys.stdout.write("\033[?1049h\033[?25l\033[H\033[J")
    sys.stdout.flush()
    return True


def leave_playback_screen() -> None:
    sys.stdout.write("\033[?25h\033[?1049l")
    sys.stdout.flush()


def play_tva(
    path: Path,
    *,
    loop: bool = False,
    fps: float | None = None,
    no_clear: bool = False,
    once: bool = False,
) -> int:
    playback_screen = False
    try:
        with zipfile.ZipFile(path, "r") as zf:
            manifest = read_manifest_from_zip(zf)
            playback_fps = fps if fps is not None else float(manifest["fps"])
            if playback_fps <= 0:
                print("ERROR: fps must be positive")
                return 1
            frame_count = int(manifest["frame_count"])
            frame_names = [frame_path(index) for index in range(frame_count)]
            delay = 1.0 / playback_fps
            if not no_clear:
                playback_screen = enter_playback_screen()

            while True:
                for name in frame_names:
                    frame = zf.read(name).decode("utf-8")
                    if playback_screen:
                        sys.stdout.write("\033[H\033[J")
                    sys.stdout.write(frame)
                    if not frame.endswith("\n"):
                        sys.stdout.write("\n")
                    sys.stdout.flush()
                    if once:
                        return 0
                    time.sleep(delay)
                if not loop:
                    break
    except KeyboardInterrupt:
        return 0
    except FileNotFoundError:
        print(f"ERROR: file does not exist: {path}")
        return 1
    except (KeyError, zipfile.BadZipFile, UnicodeDecodeError, ValueError) as exc:
        print(f"ERROR: cannot play TVA file: {exc}")
        return 1
    finally:
        if playback_screen:
            leave_playback_screen()
    return 0
