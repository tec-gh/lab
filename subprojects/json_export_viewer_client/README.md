# JSON Export Viewer Client README

`json_export_viewer_client` は、`data_connect_viewer` が出力した JSON ファイルを読み込み、一覧表示と検索を行う Flet ベースのクライアントアプリケーションです。配布形態は `exe` を想定しています。

## 1. 配布物

基本構成:

```text
json_export_viewer_client/
  json_export_viewer_client.exe
  config.ini
  README.md
```

必要に応じて `sample_data/` を同梱できます。

## 2. 設定ファイル

`config.ini` を編集して動作を設定します。

```ini
[app]
mode = native
title = JSON Export Viewer
refresh_minutes = 5
json_folder = ./sample_data
web_port = 8550
```

設定項目:

- `mode`
  - `native`: ネイティブ GUI
  - `web`: Web GUI
- `title`
  - 画面タイトル
- `refresh_minutes`
  - JSON 再読み込み間隔(分)
- `json_folder`
  - 読み込み対象 JSON フォルダ
- `web_port`
  - `web` モード時の待受ポート

## 3. 起動方法

### 3.1 ネイティブ GUI

`config.ini` で `mode = native` を設定し、`json_export_viewer_client.exe` を起動します。

### 3.2 Web GUI

`config.ini` で `mode = web` を設定し、`json_export_viewer_client.exe` を起動します。起動後、ブラウザで以下へアクセスします。

```text
http://127.0.0.1:8550
```

ポート番号は `web_port` に従います。

重要:

- `web` モードでも `native` モードと同じく、アプリ自身が `json_folder` を読み込みます
- 読み込み元はブラウザではなく、`exe` を実行している PC 上のローカルフォルダです
- 定期再読み込み時は現在の検索条件を保持したまま更新します

## 4. 画面仕様

- 上部ヘッダー
  - タイトル
  - 監視フォルダ
  - 更新間隔
  - 最終読み込み時刻
  - 手動再読み込みボタン
- サマリーカード
  - `レコード数`
  - `検索結果`
- 表示項目設定
  - 検索欄
  - メタ情報の表示 / 非表示切り替え
- 検索結果テーブル
  - JSON の標準項目
  - 表示対象にしたメタ情報
  - `ping_test_result` / `exec_result` の色付き表示

現在の UI では詳細表示カードはありません。一覧中心で利用する構成です。

## 5. 検索機能

検索欄から以下を横断検索できます。

- `hostname`
- `ipaddress`
- `area`
- `building`
- `category`
- `model`
- `ping_test_result`
- `exec_result`
- JSON 全文
- ファイル名
- ファイルパス
- ファイル内番号
- ファイル更新日時

## 6. 表示切り替え機能

メタ情報は項目ごとに表示 / 非表示を切り替えられます。

対象項目:

- `Source File`
- `Source Path`
- `Row Index`
- `File Modified At`

切り替え結果は一覧テーブルに反映されます。

## 7. 更新仕様

- 読み込む JSON は 1 ファイル運用を想定しています
- 指定フォルダ内の `*.json` を対象に読み込みます
- `refresh_minutes` ごとに再読み込みします
- 再読み込み時は検索条件を維持したまま表示を更新します

## 8. サンプルデータ

`sample_data/records_export.json` に 50 件のサンプルデータを同梱しています。初回確認時は `json_folder = ./sample_data` のままで起動できます。

## 9. トラブルシュート

### 9.1 画面が表示されない

- `config.ini` の `mode` を確認してください
- `web` モードでは `http://127.0.0.1:<web_port>` にアクセスしてください
- `native` モードでは別ウィンドウに表示されていないか確認してください

### 9.2 データが表示されない

- `json_folder` のパスを確認してください
- `.json` ファイルが存在するか確認してください
- JSON の文法エラーがないか確認してください

### 9.3 更新されない

- `refresh_minutes` の値を確認してください
- `今すぐ再読み込み` ボタンで更新できるか確認してください

## 10. 開発者向け

Python 実行時:

```bash
python -m pip install -r requirements.txt
python main.py
```

`exe` の作成手順は [BUILD.md](/d:/project/subprojects/json_export_viewer_client/BUILD.md) を参照してください。
