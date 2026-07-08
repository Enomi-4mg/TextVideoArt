import unittest
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WebPlayerTests(unittest.TestCase):
    def test_web_player_files_exist(self) -> None:
        self.assertTrue((ROOT / "web" / "player" / "index.html").exists())
        self.assertTrue((ROOT / "web" / "player" / "app.js").exists())
        self.assertTrue((ROOT / "web" / "player" / "styles.css").exists())
        self.assertTrue((ROOT / "web" / "src" / "lib" / "tva.js").exists())
        self.assertTrue((ROOT / "web" / "src" / "lib" / "charsets.js").exists())
        self.assertTrue((ROOT / "web" / "src" / "lib" / "player-api.js").exists())
        self.assertTrue((ROOT / "web" / "src" / "lib" / "player-api.d.ts").exists())
        self.assertTrue((ROOT / "web" / "src" / "lib" / "player-state.js").exists())
        self.assertTrue((ROOT / "web" / "vendor" / "jszip.esm.js").exists())
        self.assertTrue((ROOT / "web" / "index.js").exists())
        self.assertTrue((ROOT / "web" / "samples" / "landing-demo.tva").exists())

    def test_removed_browser_samples_do_not_exist(self) -> None:
        self.assertFalse((ROOT / "web" / "examples" / "api-demo").exists())
        self.assertFalse((ROOT / "web" / "examples" / "vj-sample").exists())

    def test_webcam_preview_files_exist(self) -> None:
        self.assertTrue((ROOT / "web" / "examples" / "webcam-preview" / "index.html").exists())
        self.assertTrue((ROOT / "web" / "examples" / "webcam-preview" / "app.js").exists())
        self.assertTrue((ROOT / "web" / "examples" / "webcam-preview" / "styles.css").exists())

    def test_web_player_index_loads_integrated_tabs(self) -> None:
        html = (ROOT / "web" / "player" / "index.html").read_text(encoding="utf-8")

        self.assertIn('type="module"', html)
        self.assertIn("./app.js", html)
        self.assertIn("./styles.css", html)
        self.assertIn('id="drop-zone"', html)
        self.assertIn('id="file-input"', html)
        for tab_name in ("Player", "Debug", "VJ"):
            self.assertIn(tab_name, html)
        for element_id in (
            "panel-player",
            "panel-debug",
            "panel-vj",
            "event-log",
            "debug-state",
            "manifest-json",
            "markers-json",
            "vj-font-size",
            "vj-line-height",
            "vj-theme",
            "vj-foreground",
            "vj-background",
            "vj-scale",
            "vj-fit-mode",
            "vj-hide-ui",
        ):
            self.assertIn(f'id="{element_id}"', html)

    def test_webcam_preview_loads_module_and_expected_elements(self) -> None:
        html = (ROOT / "web" / "examples" / "webcam-preview" / "index.html").read_text(encoding="utf-8")

        self.assertIn('type="module"', html)
        self.assertIn("./app.js", html)
        self.assertIn("./styles.css", html)
        self.assertIn('id="frame-output"', html)
        self.assertIn('id="frame-canvas"', html)
        self.assertIn('id="preview-stage"', html)
        self.assertIn('id="camera-video"', html)
        self.assertIn('id="sample-canvas"', html)
        self.assertIn('id="controls-overlay"', html)
        self.assertIn('id="controls-toggle"', html)
        self.assertIn('id="resolution-input"', html)
        self.assertIn('min="1"', html)
        self.assertIn('max="64"', html)
        self.assertIn('step="1"', html)
        self.assertIn('value="24"', html)
        self.assertIn('id="aspect-input"', html)
        self.assertIn('value="1"', html)
        self.assertIn("Resolution", html)
        self.assertIn("<select id=\"charset-input\">", html)
        for preset_name in ("standard", "simple", "blocks", "dense"):
            self.assertIn(f'value="{preset_name}"', html)
        self.assertNotIn('id="width-input"', html)
        self.assertNotIn("Experimental browser-side text preview.", html)

    def test_tva_parser_uses_zip_library_and_validates_plain_text_tva(self) -> None:
        parser = (ROOT / "web" / "src" / "lib" / "tva.js").read_text(encoding="utf-8")

        self.assertIn("../../vendor/jszip.esm.js", parser)
        self.assertIn("export async function loadTvaArchive", parser)
        self.assertIn("export async function loadTvaFile", parser)
        self.assertIn("export async function loadTvaUrl", parser)
        self.assertIn("color_mode", parser)
        self.assertIn("plain_text", parser)
        self.assertIn("framePath(index)", parser)

    def test_landing_page_loads_sample_demo(self) -> None:
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "web" / "index.js").read_text(encoding="utf-8")

        self.assertIn('<meta property="og:title" content="TEXT VIDEO ART">', html)
        self.assertIn('id="landing-demo"', html)
        self.assertIn("./index.js", html)
        self.assertIn("./samples/landing-demo.tva", app)
        self.assertIn("loadTvaUrl", app)
        self.assertIn("prefers-reduced-motion: reduce", app)
        self.assertIn("new TvaPlayer({ loop: true })", app)

    def test_landing_demo_tva_is_valid_plain_text_archive(self) -> None:
        sample = ROOT / "web" / "samples" / "landing-demo.tva"

        with zipfile.ZipFile(sample) as zf:
            manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
            self.assertEqual(manifest["format"], "TVA")
            self.assertEqual(manifest["format_name"], "Text Video Art")
            self.assertEqual(manifest["color_mode"], "none")
            self.assertEqual(manifest["frame_format"], "plain_text")
            for index in range(manifest["frame_count"]):
                frame_name = f"frames/{index:06d}.txt"
                self.assertIn(frame_name, zf.namelist())
                frame = zf.read(frame_name).decode("utf-8")
                self.assertEqual(len(frame.splitlines()), manifest["height"])

    def test_integrated_player_uses_player_api_and_loader(self) -> None:
        app = (ROOT / "web" / "player" / "app.js").read_text(encoding="utf-8")

        self.assertIn("TvaPlayer", app)
        self.assertIn("PreFrameRenderer", app)
        self.assertIn('../src/lib/player-api.js', app)
        self.assertIn('../src/lib/tva.js', app)
        self.assertIn('../src/lib/renderer-pre.js', app)
        self.assertIn("const player = new TvaPlayer();", app)
        self.assertIn("await loadTvaFile(file)", app)
        self.assertIn("player.load(tva)", app)
        self.assertIn("dragover", app)
        self.assertIn("drop", app)
        self.assertIn("setActiveTab", app)
        self.assertIn("mode\") === \"vj\"", app)

    def test_integrated_player_exposes_api_debug_controls(self) -> None:
        app = (ROOT / "web" / "player" / "app.js").read_text(encoding="utf-8")

        for call in (
            "player.play()",
            "player.pause()",
            "player.stop()",
            "player.prevFrame()",
            "player.nextFrame()",
            "player.seekFrame",
            "player.seekTime",
            "player.setFps",
            "player.setLoop",
            "player.getCurrentFrameIndex()",
            "player.getFrameCount()",
            "player.getFps()",
            "player.getManifest()",
            "player.getMarkers()",
            "player.isPlaying()",
        ):
            self.assertIn(call, app)
        for event_name in ("load", "framechange", "play", "pause", "stop", "ended", "fpschange", "loopchange"):
            self.assertIn(event_name, app)
        self.assertIn("logEvent", app)

    def test_integrated_player_supports_vj_capture_controls(self) -> None:
        app = (ROOT / "web" / "player" / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "web" / "player" / "styles.css").read_text(encoding="utf-8")

        for name in (
            "fontSize",
            "lineHeight",
            "foreground",
            "background",
            "scale",
            "fitMode",
            "theme",
            "autoplay",
            "loop",
        ):
            self.assertIn(name, app)
        self.assertIn('event.key === " "', app)
        self.assertIn('event.key === "ArrowLeft"', app)
        self.assertIn('event.key === "ArrowRight"', app)
        self.assertIn('event.key === "h"', app)
        self.assertIn('event.key === "H"', app)
        self.assertIn('event.key === "Escape"', app)
        self.assertIn("--vj-font-size", css)
        self.assertIn("--vj-foreground", css)
        self.assertIn("--vj-glow", css)
        self.assertIn("dataset.theme", app)
        self.assertIn('value="crt-green"', (ROOT / "web" / "player" / "index.html").read_text(encoding="utf-8"))
        self.assertIn(".workspace.is-hidden", css)

    def test_web_player_css_supports_vj_theme_presets(self) -> None:
        css = (ROOT / "web" / "player" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("--paper: #000000", css)
        self.assertIn("--ink: #00ff66", css)
        self.assertIn("--accent: #00ff66", css)
        self.assertIn('--vj-glow: transparent', css)
        self.assertIn('.stage[data-theme="crt-green"]::before', css)
        self.assertIn('.stage[data-theme="amber"]::before', css)
        self.assertIn("text-shadow: 0 0 8px var(--vj-glow)", css)
        self.assertIn("Helvetica Neue", css)
        self.assertIn("box-shadow: 8px 8px 0 var(--ink)", css)
        self.assertIn("position: fixed", css)
        self.assertIn("border-radius: 0", css)
        self.assertNotIn("--panel", css)
        self.assertNotIn("border-radius: 6px", css)

    def test_public_links_do_not_reference_removed_samples(self) -> None:
        files = [
            ROOT / "README.md",
            ROOT / "README_ja.md",
            ROOT / "web" / "index.html",
            ROOT / "web" / "examples" / "README.md",
        ]
        for path in files:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("web/examples/api-demo", text)
            self.assertNotIn("web/examples/vj-sample", text)
            self.assertNotIn("./examples/api-demo/", text)
            self.assertNotIn("./examples/vj-sample/", text)

    def test_player_api_exposes_external_control_surface(self) -> None:
        api = (ROOT / "web" / "src" / "lib" / "player-api.js").read_text(encoding="utf-8")

        self.assertIn("export class TvaPlayer", api)
        self.assertIn("play()", api)
        self.assertIn("pause()", api)
        self.assertIn("stop()", api)
        self.assertIn("seekFrame(index)", api)
        self.assertIn("seekTime(time)", api)
        self.assertIn("nextFrame()", api)
        self.assertIn("prevFrame()", api)
        self.assertIn("requestAnimationFrame", api)
        self.assertIn("tick(timestamp)", api)
        self.assertNotIn("setInterval", api)
        self.assertIn("getCurrentFrame()", api)
        self.assertIn("getCurrentFrameIndex()", api)
        self.assertIn("getManifest()", api)
        self.assertIn("getMarkers()", api)
        self.assertIn("on(type, handler)", api)

    def test_player_api_has_typescript_declarations(self) -> None:
        declarations = (ROOT / "web" / "src" / "lib" / "player-api.d.ts").read_text(encoding="utf-8")

        self.assertIn("export type TvaManifest", declarations)
        self.assertIn("export type TvaPlayerEventMap", declarations)
        self.assertIn("export class TvaPlayer", declarations)
        self.assertIn("seekFrame(index: number): void", declarations)
        self.assertIn("on<K extends keyof TvaPlayerEventMap>", declarations)

    def test_webcam_preview_uses_camera_overlay_shortcuts_and_conversion(self) -> None:
        demo = (ROOT / "web" / "examples" / "webcam-preview" / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "web" / "examples" / "webcam-preview" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("navigator.mediaDevices.getUserMedia", demo)
        self.assertIn('event.key === "h"', demo)
        self.assertIn('event.key === "H"', demo)
        self.assertIn('event.key === "Escape"', demo)
        self.assertIn("readResolution", demo)
        self.assertIn("resolutionToFrameSize", demo)
        self.assertIn("availablePreviewSize", demo)
        self.assertIn("cameraDisplaySize", demo)
        self.assertIn("video.videoWidth", demo)
        self.assertIn("video.videoHeight", demo)
        self.assertIn("previewCanvasSize(columns, rows)", demo)
        self.assertIn("const scale = Math.min(\n    available.width / nativeSize.width,\n    available.height / nativeSize.height,\n  );", demo)
        self.assertIn("available.width / nativeSize.width", demo)
        self.assertIn("available.height / nativeSize.height", demo)
        self.assertIn("resizeOutputCanvas", demo)
        self.assertIn("drawTextFrame", demo)
        self.assertIn("frameCanvas", demo)
        self.assertIn('../../src/lib/charsets.js', demo)
        self.assertIn("CHARSET_PRESETS", demo)
        self.assertIn("resolutionInput", demo)
        self.assertIn("brightnessToChar", demo)
        self.assertIn("0.299 * r + 0.587 * g + 0.114 * b", demo)
        self.assertIn("context.getImageData", demo)
        self.assertIn("stream.getTracks()", demo)
        self.assertNotIn("widthInput", demo)
        self.assertNotIn("fontSizeInput", demo)
        self.assertNotIn("applyFontSize", demo)
        self.assertIn(".preview-stage", css)
        self.assertIn("grid-column: 2", css)
        self.assertIn(".preview-surface.controls-hidden", css)
        self.assertIn(".preview-surface.controls-hidden .preview-stage", css)
        self.assertIn("place-items: center", css)
        self.assertIn("minmax(220px, 280px)", css)
        self.assertIn(".frame-canvas", css)
        self.assertIn("width: 100%", css)
        self.assertIn("height: 100%", css)
        self.assertIn(".controls-overlay", css)
        self.assertIn("grid-column: 1", css)


if __name__ == "__main__":
    unittest.main()
