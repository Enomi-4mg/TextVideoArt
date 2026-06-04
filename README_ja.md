# tvart

`tvart` は、`.tva` ファイルを作成、確認、検証、展開、再生するためのPython CLIツールです。

`.tva` はファイル形式の名前です。TVAは **Text Video Art** の略で、動画を固定サイズのプレーンテキストフレーム列として保存します。内部的にはZIPベースのコンテナ形式なので、通常のZIPアーカイブとして展開することもできます。

## MVPでできること

- 動画ファイルをモノクロのASCII/テキストアートフレームに変換できます。
- `.tva` ファイルをターミナルで再生できます。
- `.tva` のメタデータを表示できます。
- `.tva` のメタデータを概要、JSON、マーカー一覧で確認できます。
- `.tva` アーカイブと展開済みプロジェクトディレクトリを検証できます。
- `.tva` アーカイブを通常のディレクトリへ展開できます。
- `.tva` を展開、編集、検証し、再度 `.tva` にパックできます。
- 作品メタデータとフレーム単位のタイムラインマーカーを保存できます。
- `.tva` ファイルを単体HTMLプレイヤーへ書き出せます。
- 静的Web Playerで `.tva` ファイルをブラウザから直接読み込んで再生できます。
- `TvaPlayer` APIで外部のブラウザコードから再生を制御できます。
- 将来互換性のため、ZIP内の未知の追加ファイルやmanifestの未知フィールドは許容します。

## インストール

このリポジトリからインストールします。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

Windows PowerShell の場合:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

テストはPython標準ライブラリで実行できます。

```bash
python -m unittest discover -s tests
```

## 基本的な使い方

```bash
tvart convert input.mp4 output.tva
tvart convert input.mp4 output.tva --width 120 --fps 12 --duration 10
tvart play output.tva
tvart info output.tva
tvart inspect output.tva --json
tvart inspect output.tva --markers
tvart validate output.tva
tvart validate project/
tvart extract output.tva ./output
tvart unpack output.tva ./project
tvart pack ./output edited.tva
tvart export html edited.tva -o edited.html
```

静的Web Playerは `web/index.html` にあります。ブラウザで開き、`.tva` ファイルを選択またはドラッグ&ドロップすると確認・再生できます。

## `.tva` ファイル構造

```text
sample.tva
├── manifest.json
└── frames/
    ├── 000000.txt
    ├── 000001.txt
    ├── 000002.txt
    └── ...
```

フレームファイルはUTF-8のプレーンテキストです。各フレームは同じ幅と高さを持ちます。MVPの検証では、表示幅ではなくPython文字列の `len(line)` で文字数を数えます。

## `manifest.json` の例

```json
{
  "format": "TVA",
  "format_name": "Text Video Art",
  "version": "0.1.0",
  "title": "sample",
  "created_by": "tvart",
  "width": 100,
  "height": 40,
  "fps": 10,
  "frame_count": 240,
  "duration": 24.0,
  "charset": " .:-=+*#%@",
  "invert": false,
  "author": "anonymous",
  "description": "A short text video demo.",
  "license": "CC BY 4.0",
  "tags": ["ascii-art", "demo"],
  "source": {
    "type": "video",
    "filename": "input.mp4"
  },
  "conversion": {
    "width": 100,
    "fps": 10,
    "charset": " .:-=+*#%@",
    "invert": false
  },
  "markers": [
    { "frame": 0, "label": "intro" },
    { "frame": 120, "label": "main" },
    { "frame": 239, "label": "ending" }
  ],
  "encoding": "utf-8",
  "color_mode": "none",
  "frame_format": "plain_text",
  "frames_path": "frames/"
}
```

## コマンド一覧

### `tvart convert input.mp4 output.tva`

動画ファイルを `.tva` ファイルへ変換します。

主なオプション:

- `--width 100`
- `--height 40`
- `--fps 10`
- `--charset " .:-=+*#%@"`
- `--invert`
- `--start 2.5`
- `--duration 10`
- `--title "demo"`
- `--overwrite`
- `--aspect-correction 0.5`

### `tvart play output.tva`

`.tva` ファイルをターミナルで再生します。

オプション:

- `--loop`
- `--fps 12`
- `--no-clear`
- `--once`

### `tvart info output.tva`

`manifest.json` の基本メタデータを表示します。

### `tvart inspect output.tva`

`.tva` のメタデータを確認します。標準では `info` と同じ人間向けの概要を表示します。

オプション:

- `--json`
- `--markers`

### `tvart validate output.tva`

TVA v0.1.0 MVPの構造、manifest、任意メタデータ、マーカー、フレーム一覧、エンコーディング、フレーム寸法を検証します。
入力には `.tva` ZIPアーカイブまたは展開済みプロジェクトディレクトリを指定できます。

### `tvart extract output.tva ./output`

ZIPアーカイブの内容をディレクトリへ展開します。

### `tvart unpack output.tva ./project`

`.tva` アーカイブを編集用プロジェクトディレクトリへ展開します。

オプション:

- `--overwrite`

### `tvart pack ./output edited.tva`

展開済みTVAプロジェクトディレクトリを `.tva` アーカイブへパックします。

オプション:

- `--overwrite`

### `tvart export html output.tva -o output.html`

`.tva` アーカイブを単体HTMLプレイヤーへ書き出します。生成されたHTMLにはmanifestとプレーンテキストフレームが埋め込まれるため、ブラウザで直接開けます。

オプション:

- `-o`, `--output`
- `--overwrite`

## Web Player

`web/index.html` は `.tva` ファイルをブラウザで直接読み込むためのWebアプリです。ファイル選択、ドラッグ&ドロップ、manifestメタデータ表示、`<pre>` によるフレーム再生、前後フレーム移動、シーク、FPS変更、ループ再生、マーカージャンプに対応します。

ブラウザ上でZIPベースの `.tva` アーカイブを読むため、Web PlayerはCDN上のJSZipを使用します。一方、`export html` で生成するHTMLは引き続き外部JavaScriptなしの単体ファイルです。

## Player API

ブラウザ用の再生コアは `web/src/lib/player-api.js` の `TvaPlayer` として利用できます。TypeScript宣言は `web/src/lib/player-api.d.ts` にあります。

```js
import { TvaPlayer } from "./web/src/lib/player-api.js";

const player = new TvaPlayer();
player.load({ manifest, frames });
player.on("framechange", ({ index, frame }) => {
  console.log(index, frame);
});
player.play();
player.seekFrame(120);
player.pause();
```

主なメソッドは `play`, `pause`, `stop`, `seekFrame`, `seekTime`, `nextFrame`, `prevFrame`, `getCurrentFrame`, `getCurrentFrameIndex`, `getManifest`, `getMarkers`, `setFps`, `setLoop`, `on` です。

## MVPの制限

- モノクロのプレーンテキストフレームのみ対応します。
- 色には未対応です。
- 音声には未対応です。
- 字幕には未対応です。
- 差分圧縮には未対応です。
- Unicodeの表示幅計算はまだ行いません。

## 今後のロードマップ

- カラーテキストフレーム
- 音声トラック
- 字幕トラック
- 色レイヤー
- 差分圧縮
- プレビュー機能

## ライセンス

ライセンス表記のプレースホルダーです。
