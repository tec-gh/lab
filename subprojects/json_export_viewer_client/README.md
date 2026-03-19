# JSON Export Viewer Client README

このクライアントは、`data_connect_viewer` が出力した JSON ファイルを読み込み、見やすく表示する Flet ベースの閲覧アプリケーションです。
配布形態は `exe` を想定しています。

## 1. 配布物

配布時は、少なくとも以下の構成にします。

```text
json_export_viewer_client/
  json_export_viewer_client.exe
  config.ini
  README.md
```

必要に応じて、サンプルデータ確認用に `sample_data/` を同梱しても構いません。

## 2. 導入手順

### 2.1 フォルダ配置

配布された ZIP などを任意のフォルダへ展開します。

例:

```text
C:\Apps\json_export_viewer_client\
```

### 2.2 設定ファイル編集

同梱されている `config.ini` をテキストエディタで開き、必要な値を設定します。

```ini
[app]
mode = native
title = JSON Export Viewer
refresh_minutes = 5
json_folder = C:/export_json
web_port = 8550
```

設定項目:

- `mode`
  - `native`: ネイティブ GUI で表示
  - `web`: Web GUI で表示
- `title`
  - 画面タイトル
- `refresh_minutes`
  - JSON フォルダを再読み込みする間隔(分)
- `json_folder`
  - 読み込み対象の JSON ファイル配置先フォルダ
- `web_port`
  - `web` モード時の待受ポート

## 3. 起動方法

### 3.1 ネイティブ GUI モード

`config.ini` の `mode = native` を設定した状態で、以下を実行します。

```text
json_export_viewer_client.exe をダブルクリック
```

アプリ自身が `json_folder` を監視し、定期的に JSON を再読み込みして画面を更新します。

### 3.2 Web GUI モード

`config.ini` の `mode = web` を設定した状態で、以下を実行します。

```text
json_export_viewer_client.exe をダブルクリック
```

起動後、ブラウザで以下へアクセスします。

```text
http://127.0.0.1:8550
```

ポート番号は `config.ini` の `web_port` に従います。

重要:

- `web` モードでも、`native` モードと同じくクライアントアプリ自身が `json_folder` を読み込みます
- 読み込み元はブラウザ側ではなく、`exe` を実行しているPC上の指定フォルダです
- JSON 再読み込み時は Web 画面側の表示も更新されます

## 4. 画面仕様

- 上部に設定内容、監視フォルダ、更新間隔、最終読み込み時刻を表示
- JSON ファイル数、レコード数、最新ファイル名を表示
- 中央にレコード一覧テーブルを表示
- 下部に選択レコードの整形 JSON を表示
- 手動再読み込みボタンで即時更新可能

## 5. 更新仕様

- 指定フォルダ内の `*.json` を定期的に読み込みます
- 設定した間隔ごとに再読み込みを行います
- 再読み込み時に画面表示を更新します
- JSON が複数ある場合は、フォルダ内の全 JSON を読み込み対象にします
- `web` モード、`native` モードともに同一の読み込み方式です

## 6. 取り込み対象 JSON

以下を想定しています。

- `data_connect_viewer` の JSON 出力機能で生成した JSON
- 配列形式、または単一オブジェクト形式の JSON

## 7. トラブルシュート

### 7.1 画面が表示されない

- `config.ini` の `mode` が正しいか確認してください
- `web` モードでは、ブラウザで `http://127.0.0.1:<web_port>` にアクセスしてください
- `native` モードでは、アプリ画面が別ウィンドウで開いているか確認してください

### 7.2 データが表示されない

- `json_folder` のパスが正しいか確認してください
- 対象フォルダに `.json` ファイルがあるか確認してください
- JSON の文法が正しいか確認してください
- `web` モードでも読み込み元はローカルPC上の `json_folder` です

### 7.3 更新されない

- `refresh_minutes` の値を確認してください
- 手動再読み込みボタンで更新できるか確認してください

## 8. 開発者向け補足

Python 実行で動かす場合は以下です。

```bash
python -m pip install -r requirements.txt
python main.py
```

`exe` の build 方法は [BUILD.md](BUILD.md) を参照してください。
