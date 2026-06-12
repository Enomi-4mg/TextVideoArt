# tvart implementation plan

Last updated: 2026-06-11

## 0. この文書の位置づけ

この文書は、`tvart` の完了済みリリース、現在の設計判断、直近ロードマップ、長期ロードマップを整理する計画書である。

正本の扱いは以下とする。

- `README.md` / `README_ja.md`: 現在の使い方、コマンド、機能説明の正本。
- `CHANGELOG.md`: リリース済み機能とバージョン履歴の正本。
- `docs/format.md`: `.tva` ファイル形式仕様の正本。
- `docs/tvart-implementation-plan.md`: 完了済み項目と未実装ロードマップの整理。
- `docs/SKILL.md`: Codex や将来の作業者向けの作業ルール。

README / CHANGELOG / docs/format.md とこの計画書が矛盾する場合は、README / CHANGELOG / docs/format.md を優先し、この計画書を更新する。

---

## 1. 現在地

現在の `tvart` は、`.tva` という Text Video Art 用コンテナ形式を扱う参照実装として進めている。v0.7.6 実装状態として、CLI、検証、pack / unpack、HTML export、Web Player、ブラウザ Player API、API demo、WebCam preview sample、Python 側の core / workflow 分離までが実装済みである。

```text
TVA format version: 0.1.0
Implemented baseline: 0.9.1
Current package release: unreleased after 0.7.6
```

重要な分離:

```text
.tva format version != tvart Python package version
```

ツール側の機能追加、内部 API 整理、Web サンプル追加があっても、`.tva` のファイル形式を変更しない限り TVA format version は不用意に上げない。

v0.8.0 から v0.9.1 までの作業は、この repository では実装済みまたは docs-only research として完了済みである。これらは `.tva` format version を変更せず、TVA format version は `0.1.0` のまま維持する。

現時点のロードマップ状態:

```text
v0.8.0  Roadmap realignment / planning update [done]
v0.8.1  Fix command MVP [done]
v0.8.2  Preview command input expansion [done]
v0.8.3  CLI progress UX [done]
v0.8.4  Image source support [done]
v0.8.5  Charset presets [done]
v0.8.6  Web renderer separation [done]
v0.8.7  VJ sample / output mode [done]
v0.9.0  Unicode display width research [done]
v0.9.1  Color layer design research [done]
v0.9.2  Test and release hygiene
v0.9.3  Pack/export workflow audit
v0.9.4  Web sample dependency hardening
v0.9.5  Public trial onboarding
v0.9.6  Output fit model / realtime display fit
v1.0.0  TVA 0.1.0 stability release

v1.1.0  Canvas renderer foundation
v1.1.1  Render frames
v1.1.2  Render video
v1.1.3  OpenCV preprocessing foundation
v1.1.4  Denoise / threshold / morphology
v1.1.5  Edge / contour modes
v1.1.6  Video temporal processing
v1.1.7  Source channel / color-derived preprocessing
v1.2.0  Frame editing utilities
```

---

## 2. 実装済みの主要機能

現時点で実装済みの主なコマンドは以下である。

```bash
tvart convert input.mp4 output.tva
tvart convert input.mp4 -o output.tva
tvart play output.tva
tvart preview output.tva
tvart info output.tva
tvart inspect output.tva --json
tvart inspect output.tva --markers
tvart validate output.tva
tvart validate project/
tvart extract output.tva ./output
tvart unpack output.tva ./project
tvart unpack output.tva -o ./project
tvart pack ./project edited.tva
tvart pack ./project -o edited.tva
tvart export html edited.tva -o edited.html
```

Web 側では以下が実装済みである。

```text
web/player/
  index.html
  app.js
  styles.css
  Static Web Player app

web/examples/api-demo/
  index.html
  app.js
  styles.css
  Browser API demo app

web/examples/webcam-preview/
  index.html
  app.js
  styles.css
  Experimental browser-side WebCam text preview sample

web/src/lib/player-api.js
  TvaPlayer playback control API

web/src/lib/player-api.d.ts
  TypeScript declarations for TvaPlayer

web/src/lib/tva.js
  Browser-side TVA ZIP loader and manifest/frame parser
```

Python 側では以下が実装済みである。

```text
src/tvart/core/
  brightness_to_char
  frame_to_text
  image_to_text_frame
  TextFrameConverter

src/tvart/sources/
  VideoFrameSource
  VideoSourceMetadata

src/tvart/sinks/
  TvaArchiveWriter

src/tvart/workflow.py
  iter_text_frames
```

---

## 3. プロジェクトの層

今後は `tvart` を以下の三層に分けて扱う。

### 3.1 `.tva` format

`.tva` は保存可能で検証可能な linear text video 素材形式である。

現行の正式仕様は以下に限定する。

```text
encoding: utf-8
frame_format: plain_text
color_mode: none
TVA format version: 0.1.0
```

必須構造:

```text
sample.tva
├── manifest.json
└── frames/
    ├── 000000.txt
    ├── 000001.txt
    └── ...
```

重要な原則:

```text
frames/*.txt は plain UTF-8 text のまま維持する。
frames/*.txt に ANSI escape sequence を埋め込まない。
TVA v0.1.0 の frame namespace は frames/[0-9]{6}.txt とする。
validation が弱いまま format-level feature に進まない。
```

### 3.2 tvart core / player

`tvart core / player` は、変換・検証・再生・表示の共通部品である。

含めるもの:

```text
- CLI workflows
- manifest / archive validation
- text frame conversion
- source / converter / sink workflow
- terminal playback
- static Web Player
- browser Player API
- API sample apps
```

### 3.3 experimental live / VJ samples

experimental live / VJ samples は、将来のリアルタイム入力や VJ 出力の検証用サンプルである。最初は `.tva` format 変更ではなく、Web 上の実験的サンプルとして扱う。

含めないもの:

```text
- MIDI mapping
- OSC mapping
- WebSocket control
- audio reactivity
- effect node graph
- color layer
- .tva format changes
```

---

## 4. experimental samples の方針

WebCam preview と VJ sample は、まず実験的サンプルとして追加する。

想定配置:

```text
web/examples/webcam-preview/
  index.html
  app.js
  styles.css

web/examples/vj-sample/
  index.html
  app.js
  styles.css
```

または VJ 側は、必要になった段階で以下も検討する。

```text
web/vj/
  index.html
  app.js
  styles.css
```

制約:

```text
- WebCam preview は .tva format を変更しない。
- VJ sample は .tva format を変更しない。
- WebCam preview はまず browser-side の experimental sample として扱う。
- VJ sample はまず output mode / sample app として扱う。
- MIDI、OSC、WebSocket、audio reactivity、effect graph はまだ導入しない。
- browser-side video-to-text conversion は必要最小限の sample に限定し、format feature と混同しない。
```

---

## 5. 完了済みリリース

### v0.1.1: 安定化パッチ

完了済み。

- `fps` / `duration` の bool 拒否。
- `title` / `created_by` の任意化。
- 範囲外フレームの検出。
- フレーム末尾改行の正規化。
- unsafe ZIP path、絶対パス、親ディレクトリ traversal の拒否。
- `.venv` 前提の README 導入手順。

### v0.2.0: CLI ワークフロー整備

完了済み。

- `tvart pack project/ output.tva` の追加。
- `.tva` ZIP と展開済み project directory の両方を `validate` 対象化。
- `tvart unpack output.tva project/` の追加。
- `tvart inspect output.tva` と `--json` の追加。
- pack 前 validation、ZIP 順序安定化、`.DS_Store` / `__MACOSX/` 除外。

### v0.3.0: メタデータとマーカー

完了済み。

- `author`, `description`, `license`, `tags`, `source`, `conversion` などの任意 metadata。
- frame-based `markers`。
- metadata / markers validation。
- `tvart inspect output.tva --markers`。

### v0.4.0: HTML export

完了済み。

- `tvart export html output.tva -o output.html`。
- manifest と plain-text frames を埋め込んだ standalone HTML player。
- ブラウザ上の再生、一時停止、シーク、metadata 表示、marker jump。

### v0.5.0: Web Player

完了済み。

- 静的 Web Player。
- `.tva` ファイルの直接読み込み。
- file picker、drag-and-drop、manifest 表示、`<pre>` frame playback。
- 再生、一時停止、前後フレーム移動、seek、FPS override、loop、marker jump。
- parser、playback state、app UI の分離。

### v0.6.0: Player API

完了済み。

- `web/src/lib/player-api.js` の `TvaPlayer`。
- `web/src/lib/player-api.d.ts` の TypeScript declarations。
- play / pause / stop / seek / next / previous / frame access / manifest access / marker access / event subscription。
- Web Player の Player API 利用。

### v0.6.1: export HTML UI 整合

完了済み。

- `tvart export html` の出力 UI を静的 Web Player と同じ full-frame green overlay UI に更新。
- exported standalone HTML player に `Controls` / `Manifest` overlay toggle を追加。
- TVA format version は `0.1.0` のまま維持。

### v0.6.2: CLI UX 小改善

完了済み。

- `convert` / `pack` / `unpack` に `-o` / `--output` を追加。
- 既存の位置引数形式を維持。
- `play` の別名として `preview` command を追加。
- focused CLI tests を追加。
- TVA format version は `0.1.0` のまま維持。

### v0.7.0: Core conversion module extraction

完了済み。

- `src/tvart/core/` を追加。
- `brightness_to_char()` を core helper 化。
- `frame_to_text()` を core helper 化。
- `image_to_text_frame()` を共有 image-to-text-frame helper として追加。
- `tvart convert` の出力互換、CLI 引数、manifest semantics を維持。
- TVA format version は `0.1.0` のまま維持。

### v0.7.1: Core conversion refinement

完了済み。

- `TextFrameConverter` を追加。
- `image_to_text_frame()` を `TextFrameConverter` の compatibility wrapper として維持。
- `tvart convert` が `TextFrameConverter` instance を再利用する構造へ更新。
- resolved height を manifest へ反映。
- TVA format version は `0.1.0` のまま維持。

### v0.7.2: TVA v0.1.0 validation / manifest metadata hardening

完了済み。

- `frame_count <= 1,000,000` を validation に追加。
- `frame_path()` が six-digit namespace 外の index を拒否。
- conversion が 1,000,000 frames を超えないように制限。
- `frames/` 配下の invalid file names を validation で拒否。
- converted manifest に `source.type = "video"` と `source.duration` を追加。
- converted manifest に `conversion` metadata を追加。
- TVA format version は `0.1.0` のまま維持。

### v0.7.3: Source / Converter / Sink structure

完了済み。

- `VideoFrameSource` を追加。
- `VideoSourceMetadata` を追加。
- `iter_text_frames()` を追加。
- `TvaArchiveWriter` を追加。
- `convert_video()` を `VideoFrameSource -> TextFrameConverter -> iter_text_frames -> TvaArchiveWriter` に分割。
- public CLI behavior、`convert_video()` signature、manifest semantics を維持。
- TVA format version は `0.1.0` のまま維持。

### v0.7.4: API sample web app

完了済み。

- `web/examples/api-demo/` に browser-based API sample app を追加。
- `TvaPlayer` と `loadTvaFile` の直接利用を示す。
- file loading、playback controls、seek、FPS override、loop、manifest display、marker jumps、event log を実装。
- Web Player app を `web/player/` に整理。
- TVA format version は `0.1.0` のまま維持。

### v0.7.5: Documentation / roadmap realignment

完了済み。

- `docs/tvart-implementation-plan.md` を v0.7.4 現状に合わせた。
- WebCam / VJ sample を experimental samples として明確化した。
- Color layer を v0.9.0 以降の later phase へ移した。
- 実装コードは追加していない。
- TVA format version は `0.1.0` のまま維持。

### v0.7.6: Experimental WebCam preview sample

完了済み。

- `web/examples/webcam-preview/` に browser-only の WebCam preview sample を追加。
- `navigator.mediaDevices.getUserMedia()` で WebCam stream を取得。
- hidden `<video>` と hidden `<canvas>` から frame を sample し、luma brightness を charset へ変換。
- full-frame `<pre>` に live text preview を表示。
- Start / Stop、width、FPS、charset、invert、aspect correction の overlay controls を追加。
- `H` / `Escape` keyboard shortcuts で controls overlay の表示を制御。
- `.tva` format、CLI、pack/export semantics、Python conversion workflow は変更していない。
- TVA format version は `0.1.0` のまま維持。

---

## 6. v0.8.0 から v0.9.1 の完了済み作業

### v0.8.0: Roadmap realignment / planning update

完了済み。

- Core / CLI workflow improvements を Web renderer / VJ sample より前へ整理。
- WebCam preview と VJ sample を experimental sample / output mode として扱う方針を明確化。
- Unicode display width と color layer を v0.9.x research phase として整理。
- TVA format version は `0.1.0` のまま維持。

### v0.8.1: Fix command MVP

完了済み。

- `tvart fix input.tva output.tva` を追加。
- `tvart fix input.tva -o output.tva` を追加。
- `--title`, `--author`, `--description`, `--license`, `--created-by`, `--tag`, `--set-charset`, `--overwrite` を追加。
- 入力検証、manifest metadata 更新、出力検証を行う。
- frame files と unknown ZIP entries を保持する。
- `--set-charset` は manifest metadata のみを変更し、frame text は書き換えない。

### v0.8.2: Preview command input expansion

完了済み。

- `.tva` preview behavior を維持。
- `.mp4`, `.mov`, `.avi`, `.mkv` の直接 video preview を追加。
- video preview は一時 `.tva` を作らず terminal に直接描画する。
- `.tva` playback と video preview は、画面クリアが有効な場合に alternate screen を使い、終了時に cursor と terminal state を復元して通常 scrollback を汚さない。
- `--no-clear` は、frame output を通常の terminal output に残したい場合の明示的な opt-in として扱う。
- `--width`, `--height`, `--fps`, `--charset`, `--invert`, `--start`, `--duration`, `--aspect-correction`, `--loop`, `--no-clear`, `--once` をサポート。

### v0.8.3: CLI progress UX

完了済み。

- `tvart convert` と video `tvart preview` に stderr の transient status を追加。
- `--quiet` で progress / status を抑制。
- progress 表示は frame output に残らないように同一行を消去する。
- playback / preview の frame rendering と progress/status output は混ぜない。status は stderr、frame rendering は stdout / alternate screen に限定する。
- 外部依存は追加していない。

### v0.8.4: Image source support

完了済み。

- `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp` の image input を追加。
- `tvart convert image.jpg -o image.tva` をサポート。
- `tvart preview image.jpg --width 100` をサポート。
- image conversion は `source.type = "image"` の single-frame `.tva` を作成する。
- default `fps = 1`, default `duration = 1.0`。
- TVA format version は `0.1.0` のまま維持。

### v0.8.5: Charset presets

完了済み。

- `standard`, `simple`, `blocks`, `dense` preset を追加。
- `--charset-preset` を `convert` と `preview` に追加。
- `--set-charset-preset` を `fix` に追加。
- `--charset` / `--charset-preset`、`--set-charset` / `--set-charset-preset` は mutually exclusive。
- `docs/charset-presets.md` を追加。

### v0.8.6: Web renderer separation

完了済み。

- `web/src/lib/renderer-pre.js` を追加。
- `web/src/lib/renderer-pre.d.ts` を追加。
- `PreFrameRenderer` に `render(frame)` と `clear()` を持たせた。
- `TvaPlayer` の playback state と frame rendering を分離する足場を追加。

### v0.8.7: VJ sample / output mode

完了済み。

- `web/examples/vj-sample/` を追加。
- file picker、drag-and-drop、full-frame output、overlay controls を追加。
- Space、ArrowLeft、ArrowRight、H、Escape の keyboard shortcuts を追加。
- `autoplay`, `loop`, `fps`, `fontSize`, `lineHeight`, `foreground`, `background`, `center`, `fitMode`, `scale` の URL parameters を追加。

### v0.9.0: Unicode display width research

完了済み。

- `docs/unicode-width.md` を追加。
- TVA v0.1.0 の current behavior として、width validation が character count ベースであることを明記。
- code point count、grapheme cluster、display cell width の違いを整理。
- full-width Japanese characters、combining marks、emoji、terminal / browser / font differences の課題を整理。

### v0.9.1: Color layer design research

完了済み。

- `docs/color-layer-design.md` を追加。
- `frames/*.txt` に ANSI escape sequence を埋め込まない方針を明記。
- optional sidecar layer として `colors/*.json` を検討対象にした。
- 初期案として 2D runs with `line`, `column`, `length`, `fg`, `bg` を推奨。
- hex-only color values を推奨。

---

## 7. later roadmap

### v0.9.0 or later: Color layer research / design

Color layer work は v0.7.x では扱わない。v0.9.0 以降の format-level research として再検討する。

基本方針:

```text
- frames/*.txt は純粋な UTF-8 plain text のまま維持する。
- ANSI escape sequence を frame 本文へ埋め込まない。
- 色を入れる場合は colors/*.json などの別レイヤーとして検討する。
- 色非対応環境では frames/*.txt だけで再生できる。
- validation を十分に固めてから format-level feature として扱う。
```

検討例:

```text
project/
  manifest.json
  frames/
    000000.txt
    000001.txt
  colors/
    000000.json
    000001.json
```

### v1.0.0: Format stability milestone

v1.0.0 では、`.tva` の長期互換性を意識した安定版仕様を定義する。

候補:

- manifest required fields の確定。
- optional metadata の整理。
- reserved directories の整理。
- path validation の確定。
- frame naming / frame_count limit の確定。
- color layer を v1.0 に入れるか v1.x へ送るかの判断。

### v1.x: tvart-live / workstation / external timeline

`.tva` 本体では扱わない複合編集やライブ状態を、別レイヤーで扱う。

候補構成:

```text
.tvart-project/
  project.json
  assets/
    visual.tva
    audio.mp3
  timeline.json
```

ワークステーション側の責務:

- 音声。
- タイムライン。
- 複数 `.tva` の配置。
- Web 上での編集。
- 書き出し設定。
- scene / deck / layer。
- external controller mapping。

---

## 8. 当面やらないこと

以下は現時点では `.tva` 本体へ入れない。

```text
- WebCam / screen capture source を .tva format feature として扱うこと
- MIDI mapping
- OSC mapping
- WebSocket control
- audio reactivity
- effect node graph
- .tva 内への音声ファイル同梱
- .tva 内へのインタラクション仕様
- 分岐シナリオ
- クリックイベント
- ゲーム的状態管理
- npm publish
- Rust / Go など他言語 CLI
- mp4 / gif export
- native output / Spout / Syphon / NDI の直接実装
```

ただし、将来的に Player API、Web workstation、外部プロジェクト形式、tvart-live で扱う候補として残す。

---

## 9. 最重要原則

```text
validate が弱いまま pack / export / Web Player / future display features / format-level features に進まない。
```

壊れた `.tva` を確実に拒否できるようにし、その上で制作、共有、再生、外部連携機能を拡張する。

---

## 10. 次の計画

### v0.9.2: Test and release hygiene

目的:

```text
新しく追加された CLI と Web sample を検証しやすくし、release しやすい状態に整える。
```

範囲:

- CLI parser tests を追加または改善する。
- charset preset mutual exclusion の tests を追加する。
- image / video preview routing の tests を追加する。
- valid `.tva` archive 用の fixture helper を整理する。
- 意図的に stdout / stderr output を出す tests を整理する。
- package version を `0.9.x` に進めるか unreleased 扱いにするか決める。
- 完了済み unreleased work の changelog entries を追加または準備する。

範囲外:

- `.tva` format fields の追加。
- release publishing automation。
- GitHub Actions 追加。ただし、明示的に依頼された場合は別途検討する。

### v0.9.3: Pack / export workflow audit

目的:

```text
README に記載された pack / export workflow と実際の CLI surface を監査する。
```

範囲:

- README / README_ja / CHANGELOG / docs/format.md の一貫性を監査する。
- pack / unpack / export / inspect / fix / preview の command reference を再点検する。
- pack / export が今後の機能でなく既存機能であることを明確化する。
- `.tva` format version は、具体的な format change が承認されるまで `0.1.0` のまま維持する。

範囲外:

- color export implementation。
- HTML renderer の大きな設計変更。
- 新しい media dependency の追加。

### v0.9.4: Web sample dependency hardening

目的:

```text
browser examples を runtime CDN 依存なしでも扱いやすくする。
```

範囲:

- browser examples の runtime CDN dependency を削減するか文書化する。
- `web/examples/vj-sample/` と、JSZip などを CDN から読む他の examples を重点的に確認する。
- browser examples を local static server で動かすための短い README を追加する。
- VJ sample の keyboard shortcuts と URL parameters を確認し、文書化する。
- `PreFrameRenderer` は小さく独立した部品として維持する。

範囲外:

- framework adoption。
- build system migration。
- canvas renderer。
- color renderer。

### v0.9.5: Public trial onboarding

目的:

```text
v1.0.0 stability release の前に、他の人が tvart を試せる repository 状態へ整える。
```

前提:

- GitHub repository は public になる想定で準備する。
- README.md と README_ja.md の両方を維持する。
- 大きな sample files は repository に直接 commit せず、GitHub Releases への添付を優先する。

範囲:

- quickstart documentation を改善する。
- command cheatsheet を追加または整理する。
- known limitations を明確にする。
- `web/index.html` を GitHub Pages / local static server の入口として追加する。
- Pages 入口から以下へ到達できるようにする。
  - Web Player
  - API demo
  - WebCam preview sample
  - VJ sample
- examples README を追加または整理し、起動方法、制限、CDN dependency、sample asset policy を明記する。
- lightweight sample assets を追加または計画する。
  - `examples/source/`
  - `examples/tva/`
  - `examples/exported/`
- `.gitignore` がすべての `.tva` を除外している場合、tracked sample `.tva` を実際に追加する時だけ `!examples/**/*.tva` のような限定例外を追加する。
- GitHub issue templates を追加する。
  - bug report
  - feature request
  - conversion result feedback
- GitHub Discussions の用途を有効化または文書化する。
  - announcements
  - questions
  - ideas
  - show and tell
- `v0.9.x-preview` または `v1.0.0-rc.1` のような pre-release flow を準備する。

範囲外:

- PyPI publishing。
- large video sample の直接 commit。
- npm publishing。
- 新しい `.tva` format feature。

### v0.9.6: Output fit model / realtime display fit

目的:

```text
common output fit model を定義し、browser VJ sample に最小適用して realtime / VJ usability を改善する。
```

方針:

- renderer / output concern として扱い、`.tva` archive structure は変更しない。
- まず existing browser VJ sample へ URL parameters として適用する。

最小 fit model:

```text
targetWidth
targetHeight
fitMode
alignX
alignY
foreground
background
```

初期 `fitMode` values:

```text
native
contain
cover
stretch
```

optional / future `fitMode` values:

```text
width
height
scroll
```

初期 alignment values:

```text
alignX: left | center | right
alignY: top | center | bottom
```

URL parameter direction:

```text
?targetWidth=1920&targetHeight=1080&fitMode=cover&alignX=center&alignY=center&foreground=%23ffffff&background=%23000000
```

TouchDesigner integration path:

```text
tvart VJ sample / Web renderer
→ Browser window or OBS Browser Source
→ Window Capture / Spout / Syphon / NDI via existing tools
→ TouchDesigner TOP workflow
```

Existing VJ software integration path:

```text
tvart VJ sample / Web renderer
→ OBS / Browser capture / NDI / Spout / Syphon through existing tools
→ Resolume / VDMX / other VJ software
```

Later VJ media path:

```text
tvart render frames/video
→ import as media asset
```

Blender integration path:

```text
future tvart render frames/video
→ Blender Video Sequencer / Image Texture / Plane
```

範囲外:

- v1.0.0 前の Canvas renderer。
- v1.0.0 前の render frames。
- v1.0.0 前の render video。
- direct Spout / Syphon / NDI implementation。
- realtime Blender Text Object integration。
- `.tva` format change。

### v1.0.0: TVA 0.1.0 stability release

目的:

```text
current TVA 0.1.0 toolchain と documentation を public use 向けに安定化する。
```

範囲:

- README / README_ja の最終確認。
- CLI help と documentation が実装に一致していることを確認する。
- examples が usable であることを確認する。
- GitHub Pages onboarding path が機能することを確認する。
- tracked sample `.tva` files を追加した場合は valid であることを確認する。
- package metadata と release notes を確認する。
- TVA format version は `0.1.0` のまま維持する。

範囲外:

- OpenCV preprocessing。
- Canvas renderer。
- render frames / video。
- color layer implementation。
- Unicode display width behavior changes。
- TVA format version bump。

### v1.1.0: Canvas renderer foundation

目的:

```text
future export, VJ, TouchDesigner, Blender workflows のために fixed-pixel render surface を導入する。
```

範囲:

- canvas-based renderer concept を追加する。
- `<pre>` renderer は引き続き利用可能にする。
- fit / layout logic は可能な範囲で共有する。
- image / video export の土台を準備する。

範囲外:

- direct NDI / Spout / Syphon。
- 別途承認されていない color layer renderer。

### v1.1.1: Render frames

目的:

```text
`.tva` playback frames を image sequence assets として export する。
```

範囲:

- `.tva` から PNG sequence を出力する。
- width / height / fit options を提供する。
- foreground / background options を提供する。
- transparent background を検討する。

注記:

- video export より先に実装する。

### v1.1.2: Render video

目的:

```text
VJ software、Blender、sharing 用に `.tva` playback を video export する。
```

範囲:

- `.tva` から mp4 を出力する。
- ffmpeg dependency は許容する。
- fps / width / height / fit options を提供する。
- 必要に応じて MOV / WebM など alpha-capable formats を後で検討する。

### v1.1.3: OpenCV preprocessing foundation

目的:

```text
text-frame conversion 前の visual conversion quality を改善する。
```

初期 CLI strategy:

```text
Start with individual options plus a few presets.
Add filter-chain syntax later.
```

初期 options:

```text
--interpolation area|nearest|linear|cubic|lanczos
--contrast-stretch
--gamma FLOAT
--brightness INT
--contrast FLOAT
--image-preset clean|high-contrast|binary|edge
```

初期 processing order:

```text
1. channel / grayscale
2. denoise
3. contrast / gamma
4. threshold / edge
5. resize / interpolation
6. text conversion
```

metadata 記録方針:

```json
{
  "conversion": {
    "preprocessing": {
      "preset": "clean",
      "interpolation": "area",
      "contrast_stretch": true,
      "gamma": 1.2
    }
  }
}
```

注記:

- arbitrary user-defined filter ordering はまだ実装しない。
- preprocessing metadata は required TVA format field にしない。
- formal TVA format specification を変更するより、`docs/preprocessing.md` の design note 追加を検討する。

### v1.1.4: Denoise / threshold / morphology

目的:

- black background 上の小さな white speckles を減らす。
- `simple` charset と安定した binary conversion を組み合わせやすくする。
- noisy camera / video source conversion を改善する。

範囲:

```text
--denoise none|median|gaussian|bilateral
--denoise-ksize 3
--threshold 128
--threshold-otsu
--morph-open 1
--morph-close 1
--remove-speckles 3
```

### v1.1.5: Edge / contour modes

目的:

- line-art / edge-based ASCII conversion modes を追加する。
- quality cleanup だけではなく、visual expression modes として扱う。

範囲:

```text
--mode normal|edge|binary|contour
--edge canny|sobel|laplacian|scharr
--canny-threshold1 50
--canny-threshold2 150
--contour-min-area 20
```

### v1.1.6: Video temporal processing

範囲:

```text
--temporal-smooth FLOAT
--contrast-scope frame|rolling|global
--frame-diff
--background-subtract
```

実装方針:

- simple に始める。
- 初期実装では per-frame processing を許容する。
- rolling / global behavior は後で追加する。global contrast は video pre-scan が必要になる可能性がある。

### v1.1.7: Source channel / color-derived preprocessing

目的:

- `.tva` は当面 monochrome のまま維持する。
- input color information を text intensity の決定に使う。
- color layers を TVA に追加せず、VJ / chroma-key-like source workflows を支援する。

範囲:

```text
--channel gray|red|green|blue|hue|saturation|value
--chroma-key green
--hue-range START:END
```

### v1.2.0: Frame editing utilities

目的:

```text
metadata-only の `fix` と混同しない形で、既存 TVA text frames を編集する utilities を追加する。
```

範囲:

```text
tvart edit-frame input.tva -o output.tva --frame 120 --replace frame.txt
tvart edit-frame input.tva -o output.tva --frame 120 --from-image still.png
```

possible later features:

- frame range export / import。
- batch frame replacement。
- preprocessing pipeline を使った image-to-frame replacement。

重要な区別:

- `fix` は metadata-oriented のまま維持する。
- `edit-frame` は frame-content editing として扱う。

### preserve principles

- 明示的な format migration が承認されるまで、TVA format version は `0.1.0` のまま維持する。
- `frames/*.txt` は plain UTF-8 text のまま維持する。
- ANSI escape sequences を frame text に埋め込まない。
- color はこの update の対象ではなく、future sidecar layer として扱う。
- OpenCV preprocessing は conversion-time behavior として扱い、required TVA format feature にしない。
- fit model は renderer / output behavior として扱い、TVA archive structure にしない。
- completed work と future roadmap を明確に分ける。
- README / CHANGELOG / docs/format.md とこの planning document が矛盾する場合は、source-of-truth documents を優先し、この planning document を更新するか優先関係を明記する。
