# Data Connect Viewer README

## 概要

`data_connect_viewer` は、HTTP POST で受信した JSON を SQLite に保存し、ブラウザ上で一覧表示し、CSV / JSON 出力や SFTP 転送を行える FastAPI アプリケーションです。

現在の実装はテンプレート駆動です。テンプレート JSON により、次の内容を定義できます。

- テンプレート名
- 受信 API 名
- 一意キー項目
- 項目一覧
- 各項目の表示名
- 各項目の JSON パス
- 表示可否 / 検索可否 / 出力可否
- 更新方式 `overwrite` / `skip`
- 外部 API 実行設定

画面上ではテンプレートをドロップダウンで切り替えられ、レコード受信 API は `POST /api/v1/records/{template_name}` で利用します。

## 動作環境

- OS: RHEL 7.9
- Python: 3.9.10
- Web 実行環境: FastAPI + Uvicorn
- データベース: SQLite
- UI: Jinja2 テンプレート + ローカル Bootstrap 資材

依存パッケージは [requirements.txt](/d:/project/data_connect_viewer/requirements.txt) を参照してください。

## フォルダ構成

```text
data_connect_viewer/
  app/                 アプリケーション本体
  docs/                ドキュメント
  scripts/             補助スクリプト
  data/                SQLite DB 出力先
  requirements.txt     Python 依存関係
```

## 導入方法

### オンライン導入

```bash
cd /opt/data-connect-viewer
python3.9 -m pip install -r requirements.txt
```

### オフライン導入

インターネット接続可能な端末で wheel を取得します。

```bash
python3.9 -m pip download -r requirements.txt -d wheelhouse
```

取得した `wheelhouse/` を対象サーバへ持ち込み、次のように導入します。

```bash
cd /opt/data-connect-viewer
python3.9 -m pip install --no-index --find-links=wheelhouse -r requirements.txt
```

## 初期セットアップ

```bash
mkdir -p /opt/data-connect-viewer
cd /opt/data-connect-viewer
python3.9 scripts/init_db.py
```

必要に応じて環境変数を指定してください。

```bash
export APP_NAME=data-connect-viewer
export DATABASE_URL=sqlite:////opt/data-connect-viewer/data/app.db
export PAGE_SIZE_DEFAULT=20
export EXPORT_MAX_ROWS=10000
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=change_me
export API_KEY=changeme
export SFTP_HOST=
export SFTP_USERNAME=
export SFTP_PASSWORD=
export SFTP_FREQUENCY_MINUTES=60
export SFTP_REMOTE_PATH=records_export.json
```

## 起動方法

```bash
./scripts/start_app.sh
```

または直接起動します。

```bash
python3.9 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 主な URL

- `/health`: ヘルスチェック
- `/records`: レコード一覧画面
- `/records/{id}?template_name=<name>`: レコード詳細画面
- `/settings/mappings`: テンプレート / SFTP 設定画面
- `/api/v1/templates`: テンプレート一覧 API
- `/api/v1/templates/upload`: テンプレートアップロード API
- `/api/v1/records/{template_name}`: レコード受信 API
- `/api/v1/records/export.csv?template_name=<name>`: CSV 出力
- `/api/v1/records/export.json?template_name=<name>`: JSON 出力

## テンプレート JSON 例

```json
{
  "template_name": "servers",
  "api_name": "servers-api",
  "unique_key_field": "hostname",
  "external_api": {
    "enabled": true,
    "url": "http://127.0.0.1:9000/notify",
    "headers": {
      "X-System": "viewer"
    },
    "body": {
      "hostname": "{{hostname}}",
      "payload": "{{payload_json}}"
    }
  },
  "fields": [
    {
      "field_key": "hostname",
      "display_name": "ホスト名",
      "json_path": "hostname",
      "is_visible": true,
      "is_searchable": true,
      "is_exportable": true,
      "update_mode": "skip",
      "sort_order": 1
    },
    {
      "field_key": "exec_result",
      "display_name": "実行結果",
      "json_path": "exec_result",
      "is_visible": true,
      "is_searchable": true,
      "is_exportable": true,
      "update_mode": "overwrite",
      "sort_order": 2
    }
  ]
}
```

## レコード受信仕様

`POST /api/v1/records/{template_name}` で JSON を受信した際の動作は次のとおりです。

- `template_name` でテンプレートを解決し、互換のため必要なら `api_name` でも解決する
- テンプレート定義に従って値を抽出する
- 一意キー項目の値で既存レコードを検索する
- 既存レコードが無い場合は新規作成する
- 既存レコードがある場合は、受信 JSON に含まれていた項目だけを更新候補にする
- `update_mode = skip` の項目は既存値があれば保持する
- `update_mode = overwrite` の項目は常に上書きする

## 手動外部 API 実行

テンプレートで `external_api.enabled = true` かつ URL が設定されている場合、一覧画面に `Run` ボタンが表示されます。

- 行単位で外部 API を手動実行できる
- リクエストヘッダ / ボディはテンプレート定義から設定する
- `{{hostname}}` や `{{payload_json}}` などのプレースホルダを利用できる
- 実行結果、応答内容、最終実行日時はレコードごとに保存される

## JSON 出力形式

JSON 出力はテンプレート情報を含むラップ形式です。

```json
{
  "template_name": "servers",
  "api_name": "servers-api",
  "unique_key_field": "hostname",
  "fields": [...],
  "records": [...]
}
```

Flet クライアントサブプロジェクトはこの形式をそのまま読み込みます。

## 補足

- SFTP 転送はテンプレートごとに JSON を出力して送信します。
- テンプレートが 1 件のみで、転送先パスが `.json` で終わる場合はそのパスをそのまま使います。
- テンプレートが複数ある場合はテンプレートごとにファイル名を自動生成します。

## 関連資料

- 詳細導入手順: [deployment.md](/d:/project/data_connect_viewer/docs/deployment.md)
- 設計書: [design.md](/d:/project/data_connect_viewer/docs/design.md)
