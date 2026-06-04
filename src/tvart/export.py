from __future__ import annotations

import json
import zipfile
from html import escape
from pathlib import Path

from .tva import frame_path, read_manifest_from_zip
from .validate import validate_tva


def script_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def build_html(manifest: dict, frames: list[str]) -> str:
    title = manifest.get("title") or "TVA Player"
    escaped_title = escape(str(title))
    manifest_json = script_json(manifest)
    frames_json = script_json(frames)
    markers = manifest.get("markers") or []
    marker_buttons = "\n".join(
        f'<button class="marker-button" type="button" data-frame="{marker.get("frame")}">{marker.get("frame"):06d} {escape(marker.get("label"))}</button>'
        for marker in markers
        if type(marker.get("frame")) is int and isinstance(marker.get("label"), str)
    )
    marker_section = (
        f"""
      <section class="details">
        <h2>Markers</h2>
        <div class="markers">
          {marker_buttons}
        </div>
      </section>"""
        if marker_buttons
        else ""
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
  <style>
    * {{ box-sizing: border-box; }}
    html,
    body {{
      margin: 0;
      min-height: 100%;
      background: #000;
      color: #fff;
      font-family: system-ui, sans-serif;
    }}
    button,
    input {{
      font: inherit;
    }}
    button,
    input[type="number"] {{
      border: 1px solid #00ff66;
      border-radius: 0;
      background: #000;
      color: #00ff66;
    }}
    button {{
      min-height: 32px;
      padding: 4px 10px;
      cursor: pointer;
    }}
    .app-shell,
    .stage {{
      min-height: 100vh;
    }}
    .stage {{
      position: relative;
      overflow: hidden;
    }}
    .frame-output {{
      width: 100vw;
      height: 100vh;
      margin: 0;
      padding: 16px;
      overflow: auto;
      white-space: pre;
      color: #fff;
      background: #000;
      font: 14px/1.1 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }}
    .overlay-actions {{
      position: fixed;
      top: 8px;
      right: 8px;
      z-index: 3;
      display: flex;
      gap: 8px;
    }}
    .overlay {{
      position: fixed;
      z-index: 2;
      border: 1px solid #00ff66;
      background: #000;
      color: #00ff66;
    }}
    .overlay.is-hidden {{
      display: none;
    }}
    .controls-overlay {{
      left: 8px;
      right: 8px;
      bottom: 8px;
      display: grid;
      grid-template-columns: auto auto auto minmax(120px, 1fr) auto auto auto;
      gap: 8px;
      align-items: center;
      padding: 8px;
    }}
    .manifest-overlay {{
      top: 48px;
      right: 8px;
      width: min(360px, calc(100vw - 16px));
      max-height: calc(100vh - 112px);
      overflow: auto;
    }}
    input[type="range"] {{
      width: 100%;
      min-width: 0;
    }}
    .counter {{
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}
    .numeric-control,
    .toggle-control {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }}
    .numeric-control input {{
      width: 64px;
      min-height: 32px;
      padding: 0 6px;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 14px;
      line-height: 1.2;
    }}
    h2 {{
      margin: 0 0 10px;
      font-size: 14px;
      line-height: 1.2;
    }}
    .details {{
      padding: 12px;
      border-bottom: 1px solid #00ff66;
    }}
    .details:last-child {{
      border-bottom: 0;
    }}
    dl {{
      margin: 0;
      display: grid;
      grid-template-columns: 88px minmax(0, 1fr);
      gap: 6px 10px;
      font-size: 13px;
    }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    .markers {{
      display: grid;
      gap: 6px;
    }}
    .marker-button {{
      width: 100%;
      text-align: left;
    }}
    @media (max-width: 760px) {{
      .frame-output {{ font-size: 11px; }}
      .controls-overlay {{
        grid-template-columns: auto auto auto;
        max-height: 45vh;
        overflow: auto;
      }}
      input[type="range"],
      .counter {{
        grid-column: 1 / -1;
      }}
      .numeric-control,
      .toggle-control {{
        grid-column: 1 / -1;
      }}
    }}
  </style>
</head>
<body>
  <main class="app-shell">
    <section class="stage">
      <pre id="frame" class="frame-output" aria-live="off"></pre>
      <div class="overlay-actions">
        <button id="controls-toggle" type="button" aria-expanded="true" aria-controls="controls-overlay">Controls</button>
        <button id="manifest-toggle" type="button" aria-expanded="false" aria-controls="manifest-overlay">Manifest</button>
      </div>
      <section class="overlay controls-overlay" id="controls-overlay">
        <button id="prev" type="button">Prev</button>
        <button id="play" type="button">Play</button>
        <button id="next" type="button">Next</button>
        <input id="seek" type="range" min="0" max="0" value="0">
        <span id="counter" class="counter">0 / 0</span>
        <label class="numeric-control">
          FPS
          <input id="fps" type="number" min="1" step="1" value="{manifest.get("fps", 10)}">
        </label>
        <label class="toggle-control">
          <input id="loop" type="checkbox">
          Loop
        </label>
      </section>
    </section>
    <aside class="overlay manifest-overlay is-hidden" id="manifest-overlay">
      <section class="details">
      <h1>{escaped_title}</h1>
        <h2>Metadata</h2>
        <dl id="metadata"></dl>
      </section>{marker_section}
    </aside>
  </main>
  <script>
    const manifest = {manifest_json};
    const frames = {frames_json};
    let currentFrame = 0;
    let playing = false;
    let timerId = null;
    let playbackFps = Number(manifest.fps || 10);
    let loop = false;

    const frameEl = document.getElementById("frame");
    const playEl = document.getElementById("play");
    const prevEl = document.getElementById("prev");
    const nextEl = document.getElementById("next");
    const seekEl = document.getElementById("seek");
    const counterEl = document.getElementById("counter");
    const fpsEl = document.getElementById("fps");
    const loopEl = document.getElementById("loop");
    const metadataEl = document.getElementById("metadata");
    const controlsToggle = document.getElementById("controls-toggle");
    const manifestToggle = document.getElementById("manifest-toggle");
    const controlsOverlay = document.getElementById("controls-overlay");
    const manifestOverlay = document.getElementById("manifest-overlay");

    seekEl.max = Math.max(0, frames.length - 1);

    function renderMetadata() {{
      const rows = [
        ["Format", `${{manifest.format}} ${{manifest.version}}`],
        ["Size", `${{manifest.width}} x ${{manifest.height}} chars`],
        ["FPS", manifest.fps],
        ["Frames", manifest.frame_count],
        ["Duration", `${{Number(manifest.duration).toFixed(2)}} sec`],
        ["Author", manifest.author],
        ["License", manifest.license]
      ].filter((row) => row[1] !== undefined && row[1] !== null && row[1] !== "");
      metadataEl.innerHTML = rows
        .map(([name, value]) => `<dt>${{escapeHtml(name)}}</dt><dd>${{escapeHtml(String(value))}}</dd>`)
        .join("");
    }}

    function escapeHtml(value) {{
      return value
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }}

    function renderFrame(index) {{
      currentFrame = Math.max(0, Math.min(frames.length - 1, index));
      frameEl.textContent = frames[currentFrame] || "";
      seekEl.value = String(currentFrame);
      counterEl.textContent = `${{currentFrame + 1}} / ${{frames.length}}`;
    }}

    function setOverlayVisible(toggle, overlay, visible) {{
      overlay.classList.toggle("is-hidden", !visible);
      toggle.setAttribute("aria-expanded", String(visible));
    }}

    function toggleOverlay(toggle, overlay) {{
      setOverlayVisible(toggle, overlay, overlay.classList.contains("is-hidden"));
    }}

    function stop() {{
      playing = false;
      playEl.textContent = "Play";
      if (timerId !== null) {{
        clearInterval(timerId);
        timerId = null;
      }}
    }}

    function play() {{
      playing = true;
      playEl.textContent = "Pause";
      timerId = setInterval(() => {{
        if (currentFrame >= frames.length - 1) {{
          if (loop) {{
            renderFrame(0);
          }} else {{
            stop();
          }}
          return;
        }}
        renderFrame(currentFrame + 1);
      }}, 1000 / playbackFps);
    }}

    playEl.addEventListener("click", () => playing ? stop() : play());
    controlsToggle.addEventListener("click", () => toggleOverlay(controlsToggle, controlsOverlay));
    manifestToggle.addEventListener("click", () => toggleOverlay(manifestToggle, manifestOverlay));
    prevEl.addEventListener("click", () => renderFrame(currentFrame - 1));
    nextEl.addEventListener("click", () => renderFrame(currentFrame + 1));
    seekEl.addEventListener("input", () => renderFrame(Number(seekEl.value)));
    fpsEl.addEventListener("change", () => {{
      const nextFps = Number(fpsEl.value);
      if (!Number.isFinite(nextFps) || nextFps <= 0) return;
      const wasPlaying = playing;
      stop();
      playbackFps = nextFps;
      if (wasPlaying) play();
    }});
    loopEl.addEventListener("change", () => {{
      loop = loopEl.checked;
    }});
    document.querySelectorAll(".marker").forEach((button) => {{
      button.addEventListener("click", () => {{
        stop();
        renderFrame(Number(button.dataset.frame));
      }});
    }});

    renderMetadata();
    renderFrame(0);
  </script>
</body>
</html>
"""


def read_tva_for_export(input_path: Path) -> tuple[dict, list[str]]:
    with zipfile.ZipFile(input_path, "r") as zf:
        manifest = read_manifest_from_zip(zf)
        frames = [zf.read(frame_path(index)).decode("utf-8") for index in range(manifest["frame_count"])]
    return manifest, frames


def export_html(input_path: Path, output_path: Path, overwrite: bool = False) -> int:
    if output_path.exists() and not overwrite:
        print(f"ERROR: output file already exists: {output_path}")
        return 1

    errors = validate_tva(input_path)
    if errors:
        print("ERROR: invalid TVA file.")
        print()
        for error in errors:
            print(f"- {error}")
        return 1

    try:
        manifest, frames = read_tva_for_export(input_path)
    except (KeyError, zipfile.BadZipFile, UnicodeDecodeError, ValueError) as exc:
        print(f"ERROR: cannot read TVA file: {exc}")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(manifest, frames), encoding="utf-8", newline="\n")
    print(f"Wrote {output_path}")
    return 0
