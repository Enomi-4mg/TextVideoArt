import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WebPlayerTests(unittest.TestCase):
    def test_web_player_files_exist(self) -> None:
        self.assertTrue((ROOT / "web" / "player" / "index.html").exists())
        self.assertTrue((ROOT / "web" / "player" / "app.js").exists())
        self.assertTrue((ROOT / "web" / "player" / "styles.css").exists())
        self.assertTrue((ROOT / "web" / "src" / "lib" / "tva.js").exists())
        self.assertTrue((ROOT / "web" / "src" / "lib" / "player-api.js").exists())
        self.assertTrue((ROOT / "web" / "src" / "lib" / "player-api.d.ts").exists())
        self.assertTrue((ROOT / "web" / "src" / "lib" / "player-state.js").exists())

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
        self.assertIn('id="camera-video"', html)
        self.assertIn('id="sample-canvas"', html)
        self.assertIn('id="controls-overlay"', html)
        self.assertIn('id="controls-toggle"', html)
        self.assertNotIn('id="width-input"', html)

    def test_tva_parser_uses_zip_library_and_validates_plain_text_tva(self) -> None:
        parser = (ROOT / "web" / "src" / "lib" / "tva.js").read_text(encoding="utf-8")

        self.assertIn("jszip@3.10.1", parser)
        self.assertIn("export async function loadTvaFile", parser)
        self.assertIn("color_mode", parser)
        self.assertIn("plain_text", parser)
        self.assertIn("framePath(index)", parser)

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
        self.assertIn(".workspace.is-hidden", css)

    def test_web_player_css_keeps_original_color_design(self) -> None:
        css = (ROOT / "web" / "player" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("--paper: #000000", css)
        self.assertIn("--ink: #00ff66", css)
        self.assertIn("--accent: #00ff66", css)
        self.assertIn("Helvetica Neue", css)
        self.assertIn("box-shadow: 8px 8px 0 var(--ink)", css)
        self.assertIn("position: fixed", css)
        self.assertIn("border-radius: 0", css)
        self.assertNotIn("--panel", css)
        self.assertNotIn("#e5392d", css)
        self.assertNotIn("#0039a6", css)
        self.assertNotIn("#ffcc00", css)
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

        self.assertIn("navigator.mediaDevices.getUserMedia", demo)
        self.assertIn('event.key === "h"', demo)
        self.assertIn('event.key === "H"', demo)
        self.assertIn('event.key === "Escape"', demo)
        self.assertIn("fitFrameSize", demo)
        self.assertIn("availablePreviewSize", demo)
        self.assertIn("measureCharacterCell", demo)
        self.assertIn("brightnessToChar", demo)
        self.assertIn("0.299 * r + 0.587 * g + 0.114 * b", demo)
        self.assertIn("context.getImageData", demo)
        self.assertIn("stream.getTracks()", demo)
        self.assertNotIn("widthInput", demo)


if __name__ == "__main__":
    unittest.main()
