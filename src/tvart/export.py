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
        f'<button class="marker" type="button" data-frame="{marker.get("frame")}">{escape(marker.get("label"))}</button>'
        for marker in markers
        if type(marker.get("frame")) is int and isinstance(marker.get("label"), str)
    )
    marker_section = (
        f"""
      <section class="panel">
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
    :root {{
      color-scheme: dark;
      --bg: #111318;
      --panel: #1b1f27;
      --text: #f2f0e8;
      --muted: #aab0ba;
      --accent: #6ee7b7;
      --line: #343a46;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      min-height: 100vh;
      display: grid;
      grid-template-columns: minmax(0, 1fr) 320px;
    }}
    .stage {{
      min-width: 0;
      display: grid;
      grid-template-rows: minmax(0, 1fr) auto;
      border-right: 1px solid var(--line);
    }}
    pre {{
      margin: 0;
      padding: 24px;
      overflow: auto;
      white-space: pre;
      color: var(--text);
      font: 14px/1.08 ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
    }}
    .controls {{
      display: grid;
      grid-template-columns: auto auto minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 14px;
      border-top: 1px solid var(--line);
      background: #171a21;
    }}
    button {{
      height: 34px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      color: var(--text);
      cursor: pointer;
    }}
    button:hover {{ border-color: var(--accent); }}
    input[type="range"] {{ width: 100%; }}
    .counter {{ color: var(--muted); font-variant-numeric: tabular-nums; }}
    aside {{
      padding: 18px;
      overflow: auto;
    }}
    h1 {{
      margin: 0 0 14px;
      font-size: 20px;
      line-height: 1.2;
    }}
    h2 {{
      margin: 0 0 10px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .panel {{
      padding: 14px 0;
      border-top: 1px solid var(--line);
    }}
    dl {{
      margin: 0;
      display: grid;
      grid-template-columns: 110px minmax(0, 1fr);
      gap: 8px 12px;
      font-size: 14px;
    }}
    dt {{ color: var(--muted); }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    .markers {{
      display: grid;
      gap: 8px;
    }}
    .marker {{
      width: 100%;
      text-align: left;
      padding: 0 10px;
    }}
    @media (max-width: 760px) {{
      main {{ grid-template-columns: 1fr; }}
      .stage {{ border-right: 0; }}
      aside {{ border-top: 1px solid var(--line); }}
      pre {{ padding: 14px; font-size: 11px; }}
      .controls {{ grid-template-columns: auto auto minmax(0, 1fr); }}
      .counter {{ grid-column: 1 / -1; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="stage">
      <pre id="frame" aria-live="off"></pre>
      <div class="controls">
        <button id="play" type="button">Play</button>
        <button id="restart" type="button">Restart</button>
        <input id="seek" type="range" min="0" max="0" value="0">
        <span id="counter" class="counter">0 / 0</span>
      </div>
    </section>
    <aside>
      <h1>{escaped_title}</h1>
      <section class="panel">
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

    const frameEl = document.getElementById("frame");
    const playEl = document.getElementById("play");
    const restartEl = document.getElementById("restart");
    const seekEl = document.getElementById("seek");
    const counterEl = document.getElementById("counter");
    const metadataEl = document.getElementById("metadata");

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
          stop();
          return;
        }}
        renderFrame(currentFrame + 1);
      }}, 1000 / Number(manifest.fps || 10));
    }}

    playEl.addEventListener("click", () => playing ? stop() : play());
    restartEl.addEventListener("click", () => {{
      stop();
      renderFrame(0);
    }});
    seekEl.addEventListener("input", () => renderFrame(Number(seekEl.value)));
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
