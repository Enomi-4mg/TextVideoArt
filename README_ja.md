# tvart

`tvart` は、`.tva` ファイルを作成、確認、検証、展開、再生するためのPython CLIツールです。

`.tva` はファイル形式の名前です。TVAは **Text Video Art** の略で、動画を固定サイズのプレーンテキストフレーム列として保存します。内部的にはZIPベースのコンテナ形式なので、通常のZIPアーカイブとして展開することもできます。

## MVPでできること

- 動画ファイルをモノクロのASCII/テキストアートフレームに変換できます。
- `.tva` ファイルをターミナルで再生できます。
- `.tva` のメタデータを表示できます。
- `.tva` のメタデータを概要またはJSONで確認できます。
- `.tva` アーカイブと展開済みプロジェクトディレクトリを検証できます。
- `.tva` アーカイブを通常のディレクトリへ展開できます。
- `.tva` を展開、編集、検証し、再度 `.tva` にパックできます。
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
tvart validate output.tva
tvart validate project/
tvart extract output.tva ./output
tvart unpack output.tva ./project
tvart pack ./output edited.tva
```

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

### `tvart validate output.tva`

TVA v0.1.0 MVPの構造、manifest、フレーム一覧、エンコーディング、フレーム寸法を検証します。
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

## MVPの制限

- モノクロのプレーンテキストフレームのみ対応します。
- 色には未対応です。
- 音声には未対応です。
- 字幕には未対応です。
- Web再生には未対応です。
- 差分圧縮には未対応です。
- Unicodeの表示幅計算はまだ行いません。

## 今後のロードマップ

- カラーテキストフレーム
- 音声トラック
- 字幕トラック
- Web再生
- 差分圧縮
- より豊かなメタデータとプレビュー機能

## ライセンス

ライセンス表記のプレースホルダーです。
