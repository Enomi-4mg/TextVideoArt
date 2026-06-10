# tvart

`tvart` は、`.tva` ファイルを作成、プレビュー、確認、検証、展開、修正、pack、export、再生するためのPython CLIツールです。

`.tva` は **Text Video Art** の略で、固定サイズのUTF-8プレーンテキストフレーム列をZIPベースのコンテナとして保存します。

## できること

- 動画ファイルをモノクロのASCII/テキストアートフレームに変換できます。
- 静止画像ファイルを1フレームの `.tva` に変換できます。
- `.tva`、動画、画像をターミナルでプレビューできます。
- `.tva` ファイルをターミナルで再生できます。
- `.tva` のメタデータ、JSON、マーカーを確認できます。
- `.tva` アーカイブと展開済みプロジェクトディレクトリを検証できます。
- `.tva` アーカイブを展開またはunpackできます。
- 編集済みプロジェクトディレクトリを `.tva` にpackできます。
- `tvart fix` でフレームや未知のZIPエントリを保ったままmanifestメタデータを更新できます。
- `.tva` ファイルを単体HTMLプレイヤーへexportできます。
- 変換、プレビュー、メタデータ修正で名前付きcharset presetを使えます。
- 静的Web Playerと `TvaPlayer` APIでブラウザ再生できます。
- API demo、WebCam preview、VJ sampleなどのブラウザサンプルを試せます。

## インストール

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -e .
```

Windows PowerShell の場合:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

テスト:

```bash
python3 -m unittest discover -s tests
```

## 基本的な使い方

```bash
tvart convert input.mp4 output.tva
tvart convert input.mp4 -o output.tva
tvart convert image.png image.tva --width 100
tvart preview output.tva
tvart preview input.mp4 --width 120 --fps 12 --duration 10
tvart preview image.png --width 100
tvart play output.tva
tvart info output.tva
tvart inspect output.tva --json
tvart inspect output.tva --markers
tvart validate output.tva
tvart validate project/
tvart extract output.tva ./output
tvart unpack output.tva -o ./project
tvart pack ./project -o edited.tva
tvart fix edited.tva fixed.tva --title "New title" --tag demo
tvart export html edited.tva -o edited.html
```

## コマンド一覧

### `tvart convert input output.tva`

動画ファイルまたは静止画像ファイルを `.tva` ファイルへ変換します。出力先は `-o` / `--output` でも指定できます。

対応する動画入力: `.mp4`, `.mov`, `.avi`, `.mkv`。

対応する画像入力: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`。OpenCVで読める場合のbest-effort対応です。

画像変換では `source.type = "image"`、`fps = 1`、`duration = 1.0` の1フレーム `.tva` を作成します。

主なオプション:

- `--width`
- `--height`
- `--fps`
- `--charset`
- `--charset-preset`
- `--invert`
- `--start`
- `--duration`
- `--title`
- `--overwrite`
- `--aspect-correction`
- `--quiet`

### `tvart preview input`

`.tva`、動画、画像をターミナルでプレビューします。`.tva` 入力はターミナルプレイヤーを使い、動画と画像は一時 `.tva` を作らず直接レンダリングします。

`.tva` 再生と動画プレビューは、画面クリアが有効な場合にターミナルのalternate screenを使います。通常終了、`--once`、`Ctrl-C` のいずれでもカーソルを復元し、描画済みフレームを通常のscrollbackに残さずシェルへ戻ります。`--no-clear` は、フレームを通常のターミナル出力へ意図的に残したい場合だけ使います。

画像プレビューは1フレームだけのコマンドなので、alternate screenには入らず通常のターミナル出力へ書きます。

主なオプション:

- `--width`
- `--height`
- `--fps`
- `--charset`
- `--charset-preset`
- `--invert`
- `--start`
- `--duration`
- `--aspect-correction`
- `--loop`
- `--no-clear`
- `--once`
- `--quiet`

### その他のコマンド

- `tvart play output.tva`: `.tva` をターミナルで再生します。
- `tvart info output.tva`: 基本メタデータを表示します。
- `tvart inspect output.tva`: メタデータを確認します。`--json` と `--markers` に対応します。
- `tvart validate output.tva`: アーカイブまたは展開済みプロジェクトディレクトリを検証します。
- `tvart extract output.tva ./output`: ZIP内容を展開します。
- `tvart unpack output.tva -o ./project`: 編集用プロジェクトディレクトリへunpackします。
- `tvart pack ./project -o edited.tva`: 編集済みプロジェクトディレクトリをpackします。
- `tvart export html output.tva -o output.html`: 単体HTMLプレイヤーを書き出します。

### `tvart fix input.tva output.tva`

有効な `.tva` を読み込み、manifestメタデータを更新し、新しい `.tva` として書き出して検証します。出力先は位置引数または `-o` / `--output-file` で指定できます。

オプション:

- `--title`
- `--author`
- `--description`
- `--license`
- `--created-by`
- `--tag` 複数指定可
- `--set-charset`
- `--set-charset-preset`
- `--overwrite`

`--set-charset` はmanifestメタデータだけを変更します。フレームテキストは書き換えません。

## Charset Presets

```text
standard = " .:-=+*#%@"
simple   = " .#"
blocks   = " ░▒▓█"
dense    = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
```

詳細は `docs/charset-presets.md` を参照してください。

## Web

- 静的Web Player: `web/player/index.html`
- API demo: `web/examples/api-demo/index.html`
- WebCam preview sample: `web/examples/webcam-preview/index.html`
- VJ sample: `web/examples/vj-sample/index.html`

ブラウザ用の再生コアは `web/src/lib/player-api.js` の `TvaPlayer` として利用できます。TypeScript宣言は `web/src/lib/player-api.d.ts` にあります。

## 現在の制限

- モノクロのプレーンテキストフレームのみ対応します。
- 色レイヤーはまだ未実装です。
- 音声には未対応です。
- 字幕には未対応です。
- ブラウザサンプルは実験的な位置づけです。
- Unicodeの表示幅計算はまだ行いません。検証は文字数ベースです。

## ロードマップ

現在のロードマップは `docs/tvart-implementation-plan.md` で管理しています。

## ライセンス

ライセンス表記のプレースホルダーです。
