# JSON Export Viewer Client

`json_export_viewer_client` は、メインアプリ `data_connect_viewer` が出力した JSON を読み込み、一覧表示する Flet クライアントです。

## 概要

- ネイティブ GUI モードと Web GUI モードに対応します。
- 起動設定は `config.ini` で行います。
- 読込対象はメインアプリの JSON 出力形式です。

## 設定ファイル

```ini
[app]
mode = native
title = JSON Export Viewer
refresh_minutes = 5
json_folder = ./sample_data
web_port = 8550
```

- `mode`: `native` または `web`
- `refresh_minutes`: JSON 再読込間隔(分)
- `json_folder`: JSON 読込先フォルダ
- `web_port`: Web GUI モードのポート

## 起動方法

- ネイティブ GUI で使う場合は `mode = native` とします。
- Web GUI で使う場合は `mode = web` とし、`http://127.0.0.1:8550` へアクセスします。

## サンプルデータ

- `sample_data/records_export.json` を同梱しています。
- `json_folder = ./sample_data` ですぐ動作確認できます。