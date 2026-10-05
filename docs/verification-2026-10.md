# Initial-publication verification — 2026-10-06 (JST)

Claude planned the work and reviewed the complete diff. Codex implemented it and addressed the review. Estimated effort is 15–20 person-days with shared conversion/layout/rendering counted once; this is a planning estimate, not measured elapsed labor. Stage estimates are in tvart-implementation-plan.md.

## Actual verification

- `.venv/bin/python -m unittest discover -s tests`: 109 tests passed, including actual FFmpeg/ffprobe media generation (no skips in this environment).
- `node --test tests/web/*.test.mjs`: 59 tests passed. Shared valid/invalid archive fixtures, existing landing demo, CRC corruption, Unicode code points, layout/viewport density, conversion, recipes and MIME selection.
- `PYTHONPATH=src .venv/bin/python -m tvart.cli render mp4 web/samples/landing-demo.tva -o /tmp/text-video-art-smoke-20261006.mp4 --size 320x180`: succeeded.
- `ffprobe -v error -count_frames -show_entries stream=codec_name,width,height,nb_read_frames,r_frame_rate,duration -of json /tmp/text-video-art-smoke-20261006.mp4`: H.264, 320×180, 6 fps, 18 frames, 3 seconds, matching the source.
- `python3 -m http.server 8765 --bind 127.0.0.1`: local server worked in the parent environment. In-app browser displayed the procedural sample, Edge preset and generated recipe URL.
- Chrome saved PNG, TXT and recipe JSON. Inspected actual files in Downloads: PNG 1080×1080 with nonconstant pixels; TXT 38 rows × 100 characters; recipe format tvart-recipe/version 1/Clean, with no source filename/path/material.
- `git diff --check`: passed.

## Remaining platform acceptance

Browser video input/recording and real camera, Safari/iPhone, OBS remain unverified. The browser extension file chooser needed file URL access; the Mac was locked when attempting native selection. No permission settings were changed. Module MIME tests do not prove browser encoding success. Player/WebCam integration has code and layout tests; actual stage resizing and camera hardware should be checked before declaring universal support.

Manual checks: serve the repository, open web/playground/, choose a photo/video, save PNG/TXT, record up to five seconds in each aspect, inspect the actual container/duration, reload recipe JSON and a shared URL, then test camera start/stop/hidden-tab cleanup. In web/player, check Text Contain and Canvas Contain/Native/Cover on portrait and landscape stages at DPR 1/2. Test standalone HTML in OBS using docs/obs-web-guide.md.

## Decisions and review fixes

TVA 0.1.0 and package 0.7.6 remain unchanged. Mathematical JSON integers including 1.0 are accepted in both runtimes. UTF-8 is strict, dimensions count code points, line endings are LF/CRLF/CR, and reader limits are separate from format requirements. ZIP paths, duplicates, effective names and streamed CRC are checked. Directory symlinks are rejected; ordinary file symlinks remain usable.

Player Canvas uses actual stage dimensions and device pixel density, observes resize and preserves existing Text Contain links. Canvas options use font size/family and foreground/background; PRE-specific scale, line height and glow remain in Text mode. Clean uses fixed light contrast; Edge uses Sobel magnitude; Terminal uses a short green ramp. Recipe version 1 pins these semantics and excludes material/paths. The procedural sample is project-authored under MIT.

Motion Cards use actual recorder MIME for extension/label, no audio and at most five seconds, with PNG fallback. Short video preview resumes after recording. Local renderer uses existing OpenCV for ASCII and ░▒▓█; other Unicode receives an explicit error. FFmpeg uses argument arrays, libx264, even dimensions and temporary PNG cleanup. Existing HTML controls provide Play/loop; automatic playback/hide-controls exporter flags were not added.

## Collaboration recovery

The initial ai-pair plan succeeded. PATH Codex CLI 0.139.0 rejected the configured model before implementation. Retried the saved plan with the app-bundled 0.160.0 CLI using the same default model/account, without changing global configuration. That implementation subprocess had HTTP/CLI restrictions; the parent subsequently executed the tests/media/browser checks above. Claude reviewed the diff and identified the stage-sizing defect and stale documentation; these were repaired before commit. Local collaboration logs are in .git/ai-pair/20261006-020805-073659/ and are not published.

Full-width persistence, per-cell color, audio, full editing, cloud galleries and Stable temporal processing remain future work. No dependencies were added.

References consulted: [W3C recording API](https://www.w3.org/TR/mediastream-recording/), [FFmpeg formats](https://ffmpeg.org/ffmpeg-formats.html), [OBS Browser Source](https://obsproject.com/kb/browser-source).
