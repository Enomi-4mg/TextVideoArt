# tvart 実装計画

## 0. 現状

現在の `tvart` は v0.1.0 のMVP実装として、動画を `.tva` に変換し、ターミナル上で再生・情報表示・検証・展開できる状態にある。

現状の主なコマンドは以下である。

```bash
tvart convert input.mp4 output.tva
tvart play output.tva
tvart info output.tva
tvart extract output.tva ./output
tvart validate output.tva
```

現時点では、`-o` / `--output` による出力指定は未導入であり、出力先は位置引数として指定する。

```bash
# 現状
tvart convert input.mp4 output.tva

# 将来案
tvart convert input.mp4 -o output.tva
tvart convert input.mp4 --output output.tva
```

## 1. 設計方針

`tvart` は単なるPython製CLIではなく、`.tva` という Text Video Art 用コンテナ形式を扱う参照実装として育てる。

そのため、今後は以下を分離して考える。

1. `.tva` ファイル形式の仕様
2. Python CLI 実装
3. HTML export による単体共有機能
4. Web Player / Player API
5. 将来的な TypeScript ライブラリ化
6. 色レイヤーや外部ワークステーションとの連携

特に、`.tva` のフォーマットバージョンと、Pythonパッケージのバージョンは分けて扱う。

```text
TVA format version: 0.1.0
Python package version: 0.1.0, 0.1.1, 0.2.0 ...
```

ツール側の更新があっても、`.tva` 形式を不用意に破壊的変更しない。

## 2. 現状機能の整理

### 2.1 `convert`

動画素材から `.tva` を生成する。

```bash
tvart convert input.mp4 output.tva
```

実装済みオプションの例：

```text
--width
--height
--fps
--charset
--invert
--start
--duration
--title
--overwrite
--aspect-correction
```

今後は、出力指定として `-o` / `--output` を追加するか検討する。

```bash
tvart convert input.mp4 -o output.tva
```

ただし、既存の位置引数形式との互換性は維持する。

### 2.2 `play`

`.tva` をターミナル上で再生する。

```bash
tvart play output.tva
```

現状の `play` は、将来構想上の `preview` に近い役割も担っている。

実装済みオプションの例：

```text
--loop
--fps
--no-clear
--once
```

将来的には、以下のように役割を分けるか検討する。

```text
preview: 制作確認用。デバッグ寄り。
play: 鑑賞用。manifest通りに再生。
```

ただし、当面は `play` を維持し、必要になった段階で `preview` を別名または新規コマンドとして追加する。

### 2.3 `info`

`.tva` の manifest 情報を表示する。

```bash
tvart info output.tva
```

現状では、将来構想上の `inspect` に近い。

将来的には以下を検討する。

```bash
tvart inspect output.tva
tvart inspect output.tva --json
tvart inspect output.tva --markers
```

互換性のため、`info` は残しつつ `inspect` を追加する方針が望ましい。

### 2.4 `extract`

`.tva` をディレクトリに展開する。

```bash
tvart extract output.tva ./output
```

将来的には `unpack` という名称を追加する。

```bash
tvart unpack output.tva -o project/
```

`extract` は低レベルな展開、`unpack` は編集用プロジェクトとして展開、というニュアンスで整理できる。

### 2.5 `validate`

`.tva` が仕様に合っているか検証する。

```bash
tvart validate output.tva
```

現状で検証している内容：

```text
manifest.json の存在
manifest.json のUTF-8 / JSON妥当性
必須フィールドの存在
基本フィールドの型
format / format_name / version
width / height / fps / frame_count / duration の正値性
charset の妥当性
encoding == utf-8
color_mode == none
frame_format == plain_text
frames_path == frames/
必要フレームの存在
各フレームのUTF-8妥当性
各フレームの行数・桁数
```

今後の `pack`、`export html`、Web Player は正しい `.tva` を前提にするため、`validate` は最優先で強化する。

## 3. v0.1.1: 安定化パッチ

### 目的

v0.1.1 は新機能追加ではなく、後続の `pack`、`export html`、Web Player が信頼できる入力を前提にできるようにするための安定化リリースとする。

### 実装項目

#### 3.1 `fps` / `duration` の bool 拒否

Pythonでは `bool` が `int` のサブクラスであるため、`isinstance(True, (int, float))` が `True` になる。

そのため、`fps` や `duration` に `true` / `false` が入っても数値として通ってしまう可能性がある。

修正方針：

```text
fps: bool を拒否し、int または float のみ許可
duration: bool を拒否し、int または float のみ許可
```

`width`、`height`、`frame_count` などと同様に、型検証を厳密化する。

#### 3.2 `title` / `created_by` の任意化

現状では `title` と `created_by` が必須フィールドとして扱われている。

ただし、`.tva` のフォーマットとしては作品メタデータを必須にしすぎない方針とするため、`title` と `created_by` は任意フィールドに変更する。

修正方針：

```text
title が存在する場合は string であることを検証する
created_by が存在する場合は string であることを検証する
title / created_by が存在しなくても validate error にしない
convert が生成する manifest には当面 title / created_by を含めてもよい
```

#### 3.3 範囲外フレームの検出

現状では必要なフレームの存在は確認しているが、範囲外の余分なフレームを検出できていない。

例：

```text
frame_count = 2

期待されるフレーム:
frames/000000.txt
frames/000001.txt

範囲外として検出すべきフレーム:
frames/000002.txt
frames/000999.txt
```

修正方針：

```text
frames/[0-9]{6}.txt に一致するファイルを列挙する
期待範囲外の番号があれば validate error とする
それ以外の未知ZIPエントリや未知manifestフィールドは後方/前方互換のため許容する
```

#### 3.4 フレーム末尾改行の正規化

現状では `rstrip("\r\n")` により、末尾改行を複数個削除してしまう可能性がある。

望ましい挙動：

```text
末尾の LF を最大1つだけ削除する
または末尾の CRLF を最大1つだけ削除する
または末尾の CR を最大1つだけ削除する
それ以外の改行は保持する
```

修正方針：

```text
text.endswith("\r\n") なら末尾2文字だけ削除
else if text.endswith("\n") なら末尾1文字だけ削除
else if text.endswith("\r") なら末尾1文字だけ削除
それ以外はそのまま
```

#### 3.5 safe extraction path check

現状の `extract` は `zipfile.extractall()` を直接使っている。

危険なZIPエントリ例：

```text
../../evil.txt
/absolute/path/file.txt
frames/../../evil.txt
```

修正方針：

```text
extractall() の前に全エントリを検査する
展開先ディレクトリ外へ出るパスを拒否する
絶対パスを拒否する
空のパスや不正なパスを拒否する
将来の pack でも使えるよう、ZIPエントリ名の安全性チェックを共通化する
```

#### 3.6 README の `.venv` 手順化

インストール手順を `.venv` 前提に整理する。

例：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

Windows向けには以下を併記する。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

#### 3.7 CHANGELOG.md の更新

v0.1.1 の変更内容を `CHANGELOG.md` に記録する。

記載対象：

```text
validate の型検証強化
title / created_by の任意化
範囲外フレーム検出
フレーム末尾改行の正規化
safe extraction path check
README の .venv 手順化
```

#### 3.8 テスト追加

追加すべきテスト：

```text
fps に true を入れるとエラー
duration に false を入れるとエラー
title がなくてもエラーにならない
created_by がなくてもエラーにならない
範囲外の frames/000002.txt を検出
末尾改行を1つだけ正規化する
safe extract で ../ を拒否する
safe extract で絶対パスを拒否する
```

#### 3.9 git 作業

v0.1.1 の実装完了後、変更内容を git で整理する。

作業方針：

```text
作業前後で git status を確認する
必要に応じて codex/v0.1.1-stabilization ブランチを作成する
v0.1.1 の実装・テスト・ドキュメント変更をまとめて stage する
テスト成功後に v0.1.1 stabilization のコミットを作成する
未追跡または未コミットの不要ファイルがないか確認する
```

### v0.1.1 完了条件

```text
既存テストがすべて通る
上記エッジケースのテストが追加される
危険なZIPを展開しない
壊れた manifest をより確実に拒否できる
README の導入手順が .venv 前提になる
CHANGELOG.md に v0.1.1 の変更内容が記録される
git status が確認済みで、v0.1.1 の変更がコミットされている
```

## 4. v0.2.0: CLIワークフロー整備

### 目的

`.tva` を作る、展開する、編集する、検証する、再パックする、確認する、という制作ワークフローを成立させる。

目標となる流れ：

```bash
tvart convert input.mp4 output.tva
tvart extract output.tva project/
# project/ 内の manifest.json や frames/*.txt を編集
tvart validate project/
tvart pack project/ edited.tva
tvart play edited.tva
```

将来的には以下のような `-o` 形式も検討する。

```bash
tvart unpack output.tva -o project/
tvart pack project/ -o edited.tva
```

### 実装項目

#### 4.1 `pack`

展開済みディレクトリから `.tva` を生成する。

```bash
tvart pack project/ output.tva
```

将来互換の候補：

```bash
tvart pack project/ -o output.tva
```

挙動：

```text
project/manifest.json を読む
project/frames/ を読む
validate を実行する
問題がなければZIPとして .tva を生成する
```

基本方針：

```text
pack 前 validate はデフォルトで有効
--no-validate は将来的に追加してもよいが非推奨
既存 output.tva がある場合は --overwrite がない限り拒否
ZIP内のファイル順序を安定化する
__MACOSX/ や .DS_Store などのOS由来ファイルはZIPに含めない
```

実装状況:

```text
tvart pack project/ output.tva を追加
pack 前 validate を常に実行する
既存出力は --overwrite がない限り拒否する
ZIP内は manifest.json を先頭にし、それ以外を名前順で格納する
__MACOSX/ や .DS_Store を除外する
```

#### 4.2 `validate` のディレクトリ対応

現状の `validate` は `.tva` ファイル中心だが、v0.2.0では展開済みディレクトリも検証対象にする。

```bash
tvart validate output.tva
tvart validate project/
```

`.tva` とディレクトリの両方で同じ検証ロジックを使えるようにする。

実装状況:

```text
validate_tva() が .tva ZIP と展開済みディレクトリを自動判別する
manifest / frame の検証ロジックを validate_tva_contents() に共通化する
ディレクトリ入力でも必要フレーム、範囲外フレーム、寸法を検証する
```

#### 4.3 `unpack` の追加検討

既存の `extract` は残しつつ、将来の制作ワークフロー向けに `unpack` を追加する。

```bash
tvart unpack output.tva -o project/
```

当面は `extract` の別名として実装してもよい。

```text
extract: 既存互換用
unpack: 今後のドキュメントで推奨する名称
```

実装状況:

```text
tvart unpack output.tva project/ を追加
内部では extract_tva() を再利用する
safe extraction path check と --overwrite の挙動は extract と同じ
```

#### 4.4 `info` から `inspect` への拡張

現状の `info` は維持する。

追加候補：

```bash
tvart inspect output.tva
tvart inspect output.tva --json
tvart inspect output.tva --frames
tvart inspect output.tva --markers
```

v0.2.0では `inspect` を `info` の別名として追加し、`--json` も実装する。

実装状況:

```text
tvart inspect output.tva を追加
通常出力は info と同じ human-readable summary
tvart inspect output.tva --json で manifest を整形JSONとして出力する
```

#### 4.5 `play` / `preview` の整理

現状の `play` は維持する。

`preview` は将来的に追加する候補とする。

```text
play: 既存の再生コマンド
preview: 制作確認用の別名または拡張コマンド
```

v0.2.0では必須ではない。

### v0.2.0 完了条件

```text
project/ から .tva を再生成できる
.tva → project/ → .tva の往復が成立する
validate が .tva と project/ の両方に対応する
pack がOS由来ファイルを .tva に含めない
inspect --json で manifest をJSONとして出力できる
既存コマンドとの互換性を壊さない
```

## 5. v0.3.0: メタデータとマーカー

### 目的

`.tva` を単なるフレーム列ではなく、作品として管理・共有しやすくする。

### 5.1 メタデータ拡張

追加候補：

```json
{
  "title": "Sample Text Video",
  "author": "anonymous",
  "description": "A short text video demo.",
  "created_at": "2026-06-04T00:00:00Z",
  "license": "CC BY 4.0",
  "tags": ["ascii-art", "demo"],
  "source": {
    "type": "video",
    "filename": "input.mp4"
  }
}
```

必須にしすぎない。

必須フィールド：

```text
format
format_name
version
width
height
fps
frame_count
duration
charset
encoding
color_mode
frame_format
frames_path
```

任意フィールド：

```text
title
created_by
author
description
license
tags
created_at
source
conversion
```

`conversion` には変換時のパラメータを残す。

```json
{
  "conversion": {
    "width": 120,
    "fps": 12,
    "charset": " .:-=+*#%@",
    "invert": false,
    "aspect_correction": 0.5
  }
}
```

### 5.2 マーカー

マーカーは、タイムライン上の目印として扱う。

インタラクションそのものは `.tva` に含めない。

例：

```json
{
  "markers": [
    { "frame": 0, "label": "intro" },
    { "frame": 120, "label": "main" },
    { "frame": 240, "label": "ending" }
  ]
}
```

または time 指定も許容するか検討する。

```json
{
  "markers": [
    { "time": 0.0, "label": "intro" },
    { "time": 10.5, "label": "main" }
  ]
}
```

初期案では、検証しやすい `frame` 指定を推奨する。

検証項目：

```text
markers は配列である
label は空でない文字列である
frame は 0 <= frame < frame_count の整数である
id を導入する場合は重複しない
```

### 5.3 `inspect` での表示

```bash
tvart inspect output.tva --markers
```

表示例：

```text
Markers:
  000000 intro
  000120 main
  000240 ending
```

### v0.3.0 完了条件

```text
manifest に任意メタデータを持てる
markers を manifest に持てる
validate が metadata / markers を検証できる
info または inspect で metadata / markers を表示できる
既存の v0.1.0 .tva と互換性を保つ
```

## 6. v0.4.0: HTML export

### 目的

`.tva` を知らない人にも作品として共有できるようにする。

`.tva` を単体HTMLに変換し、ブラウザだけで再生できるようにする。

```bash
tvart export html output.tva -o output.html
```

### 実装方針

初期HTML export は、単体HTMLを出力する。

```text
外部サーバー不要
外部JS不要
ブラウザで開くだけで再生可能
frames をHTML内に埋め込む
manifest もHTML内に埋め込む
```

### 最小UI

```text
再生 / 一時停止
先頭へ戻る
シークバー
現在フレーム / 総フレーム数表示
fps表示
タイトル表示
メタデータ表示
マーカー一覧
```

### 仕様

```text
plain_text のみ正式対応
color_mode == none のみ正式対応
frame_format == plain_text のみ正式対応
```

色レイヤーや音声はこの段階では扱わない。

### v0.4.0 完了条件

```text
.tva から単体HTMLを生成できる
生成HTMLをブラウザで開くと再生できる
メタデータを表示できる
マーカーにジャンプできる
既存の plain_text .tva を扱える
```

## 7. v0.5.0: Web Player

### 目的

ブラウザ上で `.tva` を直接読み込み、再生できるWebアプリ型プレイヤーを作る。

将来的なJSライブラリ化に備え、UI部分とコアロジックを分離して実装する。

### 最小機能

```text
.tva ファイル読み込み
ドラッグ&ドロップ
manifest 表示
<pre> によるフレーム表示
再生 / 一時停止
前後フレーム移動
シークバー
fps変更
ループ
マーカー表示
マーカークリックでジャンプ
メタデータ表示
```

### 内部構成案

```text
web/src/lib/
  tva parser
  manifest validator
  frame loader
  player state
  timing controller

web/src/app/
  file input
  playback UI
  controls
  metadata panel
  marker list
```

### v0.5.0 完了条件

```text
ブラウザで .tva を直接読み込める
plain_text の .tva を再生できる
metadata / markers を表示できる
player core と UI が分離されている
将来のライブラリ化に耐える構成になっている
```

## 8. v0.6.0: Player API / TypeScript core

### 目的

`.tva` にインタラクション仕様そのものは入れず、外部アプリがプレイヤーを操作できるAPIを提供する。

`.tva` は linear text video として保つ。

外部アプリや展示用アプリ、授業用アプリ、Webワークステーションが API 経由で自由に操作できるようにする。

### API候補

```ts
player.play();
player.pause();
player.stop();
player.seekFrame(120);
player.seekTime(10.0);
player.nextFrame();
player.prevFrame();
player.getCurrentFrame();
player.getCurrentFrameIndex();
player.getManifest();
player.getMarkers();
player.on("framechange", callback);
player.on("ended", callback);
```

### 方針

```text
.tva に分岐やクリックイベントは持たせない
プレイヤー側APIで外部から操作できるようにする
マーカーはジャンプ先や構造情報として利用する
```

### v0.6.0 完了条件

```text
TypeScript core が .tva を読み込める
Player API で再生制御できる
Web Player がそのAPIを使って動作する
外部アプリから利用できる最小APIが定義されている
```

## 9. v0.7.0: 色レイヤー

### 目的

プレーンテキスト互換を維持しながら、色付きText Video Artを扱えるようにする。

色はフレーム本文にANSI escape sequenceとして埋め込まず、別レイヤーとして持つ方針とする。

### 方針

```text
frames/*.txt は純粋なテキストのまま維持する
colors/*.json に色情報を持たせる
色非対応環境では frames/*.txt だけで再生できる
色対応環境では frames + colors を重ねて表示する
```

構成例：

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

色レイヤー例：

```json
{
  "runs": [
    { "start": 0, "length": 10, "fg": "#ffffff", "bg": "#000000" },
    { "start": 10, "length": 5, "fg": "#ff0000" }
  ]
}
```

検討事項：

```text
start / length は1次元の文字インデックスでよいか
line / column / length 形式にするか
fg / bg の両方を持つか
透明・未指定をどう扱うか
HTML export と Web Player で同じ表示結果を目指すか
```

初期実装では、色レイヤーは後方互換な任意機能として扱う。

```json
{
  "color_mode": "layer",
  "color_path": "colors/",
  "color_format": "runs_json"
}
```

### v0.7.0 完了条件

```text
色なし .tva との互換性を保つ
色レイヤー付き .tva を validate できる
Web Player または HTML export のどちらかで色表示できる
frames/*.txt はANSIを含まない純粋テキストとして維持する
```

## 10. v0.8.0以降: ワークステーション / 外部連携

### 目的

音声や複合編集を `.tva` 本体に直接持たせるのではなく、別のワークステーションやプロジェクト形式で扱う。

`.tva` の責務：

```text
テキスト映像本体
```

ワークステーション側の責務：

```text
音声
タイムライン
複数 .tva の配置
Web上での編集
書き出し設定
```

将来構成案：

```text
.tvart-project/
  project.json
  assets/
    visual.tva
    audio.mp3
  timeline.json
```

ただし、これはかなり後の段階でよい。

## 11. 推奨ロードマップ

```text
v0.1.1
  安定化パッチ
  validate強化
  title / created_by 任意化
  safe extract
  README更新
  CHANGELOG更新
  エッジケーステスト追加

v0.2.0
  CLIワークフロー整備
  pack追加
  validate directory対応
  unpack追加検討
  inspect --json追加

v0.3.0
  metadata拡張
  markers追加
  inspect/info表示強化

v0.4.0
  export html
  単体HTML共有
  metadata / markers表示

v0.5.0
  Web Player
  .tva直接読み込み
  metadata / markers対応

v0.6.0
  Player API
  TypeScript core
  外部アプリからの操作性向上

v0.7.0
  color layer
  色付き表示
  plain_text互換維持

v0.8.0以降
  workstation / project形式
  音声・タイムライン・複合作品管理
```

## 12. 直近でCodexに依頼する単位

### 第1段階: v0.1.1 安定化

```text
validate_manifest で fps / duration の bool を拒否する
validate_manifest で title / created_by を任意フィールドにする
validate_tva で範囲外フレームを検出する
normalize_frame_text を末尾改行1つだけ除去する実装に変更する
extract_tva に safe extraction path check を追加する
README の install 手順を .venv 前提に更新する
CHANGELOG.md に v0.1.1 の変更内容を記録する
上記の focused tests を追加する
```

### 第2段階: v0.2.0 pack / directory validate

```text
展開済み project directory を validate できるようにする
project directory から .tva を生成する pack コマンドを追加する
pack 前に validate を実行する
pack 時に __MACOSX/ や .DS_Store などのOS由来ファイルを除外する
extract の別名として unpack を追加するか検討する
info の別名として inspect を追加し、inspect --json を実装する
```

### 第3段階: v0.3.0 metadata / markers

```text
manifest の任意メタデータ仕様を追加する
markers 仕様を追加する
validate で metadata / markers を検証する
info / inspect で metadata / markers を表示する
```

### 第4段階: v0.4.0 export html

```text
.tva から単体HTMLを生成する export html コマンドを追加する
plain_text frame をHTML内に埋め込む
再生/一時停止/シーク/マーカージャンプを実装する
metadata を表示する
```

## 13. 現時点で入れないもの

以下は当面入れない。

```text
.tva 内への音声ファイル同梱
.tva 内へのインタラクション仕様
分岐シナリオ
クリックイベント
ゲーム的状態管理
npm publish
Rust / Go など他言語CLI
mp4 / gif export
```

ただし、将来的に外部Webワークステーションや Player API から利用できるよう、内部設計は拡張可能にしておく。

## 14. 最重要原則

```text
validate が弱いまま pack / export / Web Player に進まない。
```

まず壊れた `.tva` を確実に拒否できるようにし、その上で制作・共有・再生機能を拡張する。

`.tva` は、まず linear text video のための軽量で堅牢なコンテナ形式として安定させる。
