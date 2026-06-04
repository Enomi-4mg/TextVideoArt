import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WebPlayerTests(unittest.TestCase):
    def test_web_player_files_exist(self) -> None:
        self.assertTrue((ROOT / "web" / "index.html").exists())
        self.assertTrue((ROOT / "web" / "src" / "lib" / "tva.js").exists())
        self.assertTrue((ROOT / "web" / "src" / "lib" / "player-api.js").exists())
        self.assertTrue((ROOT / "web" / "src" / "lib" / "player-api.d.ts").exists())
        self.assertTrue((ROOT / "web" / "src" / "lib" / "player-state.js").exists())
        self.assertTrue((ROOT / "web" / "src" / "app" / "app.js").exists())
        self.assertTrue((ROOT / "web" / "src" / "app" / "styles.css").exists())

    def test_web_player_index_loads_app_module(self) -> None:
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn('type="module"', html)
        self.assertIn("./src/app/app.js", html)
        self.assertIn('id="drop-zone"', html)
        self.assertIn('id="file-input"', html)
        self.assertIn('id="controls-toggle"', html)
        self.assertIn('id="manifest-toggle"', html)
        self.assertIn('id="controls-overlay"', html)
        self.assertIn('id="manifest-overlay"', html)

    def test_tva_parser_uses_zip_library_and_validates_plain_text_tva(self) -> None:
        parser = (ROOT / "web" / "src" / "lib" / "tva.js").read_text(encoding="utf-8")

        self.assertIn("jszip@3.10.1", parser)
        self.assertIn("export async function loadTvaFile", parser)
        self.assertIn("color_mode", parser)
        self.assertIn("plain_text", parser)
        self.assertIn("framePath(index)", parser)

    def test_app_supports_expected_player_controls(self) -> None:
        app = (ROOT / "web" / "src" / "app" / "app.js").read_text(encoding="utf-8")

        self.assertIn("TvaPlayer", app)
        self.assertIn("dragover", app)
        self.assertIn("drop", app)
        self.assertIn("playButton", app)
        self.assertIn("prevButton", app)
        self.assertIn("nextButton", app)
        self.assertIn("fpsInput", app)
        self.assertIn("loopInput", app)
        self.assertIn("renderMarkers", app)
        self.assertIn("toggleOverlay", app)
        self.assertIn("controlsOverlay", app)
        self.assertIn("manifestOverlay", app)

    def test_web_player_css_uses_green_overlay_ui(self) -> None:
        css = (ROOT / "web" / "src" / "app" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("background: #000", css)
        self.assertIn("color: #fff", css)
        self.assertIn("#00ff66", css)
        self.assertIn("position: fixed", css)
        self.assertIn(".overlay.is-hidden", css)
        self.assertNotIn("--accent", css)
        self.assertNotIn("border-radius: 6px", css)

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


if __name__ == "__main__":
    unittest.main()
