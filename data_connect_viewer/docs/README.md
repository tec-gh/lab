# Data Connect Viewer README

## 1. このアプリでできること

このアプリは、外部システムから `POST` された JSON データを受信して SQLite に保存し、ブラウザで一覧表示・詳細表示・CSV 出力・JSON 出力を行う FastAPI アプリケーションです。

主な機能:

- JSON データ受信 API
- 同一 `hostname` 受信時の既存レコード更新
- 保存済みデータの一覧表示
- 詳細画面での JSON 確認
- CSV / JSON ダウンロード
- 項目マッピング設定画面
- SFTP への定期 JSON 転送

## 2. 動作環境

- OS: RHEL 7.9
- Python: 3.9.10
- 仮想環境: 使用しない
- Web サーバ: FastAPI + Uvicorn を直接起動

必要な Python パッケージ:

- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `jinja2`
- `python-multipart`
- `paramiko`

依存定義は [requirements.txt](/d:/project/data_connect_viewer/requirements.txt) を参照してください。

## 3. フォルダ構成

```text
data_connect_viewer/
  app/                 アプリ本体
  docs/                設計書・導入手順
  scripts/             初期化・起動確認用スクリプト
  data/                SQLite DB 保存先
  requirements.txt     Python 依存パッケージ
```

## 4. 導入方法

### 4.1 オンライン導入

```bash
cd /opt/data-connect-viewer
python3.9 -m pip install -r requirements.txt
```

### 4.2 オフライン導入

インターネット接続可能な端末で wheel を取得する。

```bash
python3.9 -m pip download -r requirements.txt -d wheelhouse
```

取得した `wheelhouse/` をサーバへ持ち込み、以下を実行する。

```bash
cd /opt/data-connect-viewer
python3.9 -m pip install --no-index --find-links=wheelhouse -r requirements.txt
```

## 5. 初回セットアップ

### 5.1 配置

アプリ一式を任意ディレクトリへ配置します。例:

```bash
mkdir -p /opt/data-connect-viewer
cd /opt/data-connect-viewer
```

### 5.2 環境変数設定

必要に応じて起動前に環境変数を設定します。

```bash
export APP_NAME=data-connect-viewer
export APP_ENV=production
export DATABASE_URL=sqlite:////opt/data-connect-viewer/data/app.db
export PAGE_SIZE_DEFAULT=20
export EXPORT_MAX_ROWS=10000
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=change_me
export API_KEY=
export SFTP_HOST=
export SFTP_USERNAME=
export SFTP_PASSWORD=
export SFTP_FREQUENCY_MINUTES=60
```

通常は未設定でも起動できます。未設定時はアプリ内のデフォルト値を使用します。

## 6. DB 初期化

初回起動前に DB を初期化します。

```bash
python3.9 scripts/init_db.py
```

この処理で以下が実行されます。

- SQLite DB ファイルの作成
- テーブル作成
- 初期マッピング定義の投入

## 7. 起動方法

### 7.1 起動

```bash
./scripts/start_app.sh
```

または直接起動:

```bash
python3.9 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 7.2 停止

起動中のターミナルで `Ctrl + C` を押します。

## 8. 動作確認

### 8.1 ヘルスチェック

```bash
curl http://127.0.0.1:8000/health
```

正常時:

```json
{"status":"ok"}
```

### 8.2 画面確認

ブラウザで以下へアクセスします。

```text
http://127.0.0.1:8000/records
```

一覧画面には自動更新トグルがあります。

- `自動更新`: 30 秒ごとに一覧を自動再読み込み
- `更新停止中`: 自動再読み込みを停止

ボタンは1つで、クリックするたびに表示が切り替わります。

### 8.3 スモークテスト

```bash
BASE_URL=http://127.0.0.1:8000 python3.9 scripts/smoke_test.py
```

## 9. データ登録方法

サンプル:

```bash
curl -H "Content-Type: application/json" \
  -d '{"hostname":"sv-01","ipaddress":"192.168.0.10","area":"tokyo","building":"dc-a","category":"server","model":"test","ping_test_result":"success","exec_result":"ok"}' \
  http://127.0.0.1:8000/api/v1/records
```

補足:

- 新しい `hostname` の場合は新規登録されます
- 既に同じ `hostname` が DB に存在する場合は、新規作成ではなく既存レコードを更新します
- 更新時のレスポンスは `200`、メッセージは `updated` です

API キーを使う場合:

```bash
curl -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"hostname":"sv-01","ipaddress":"192.168.0.10"}' \
  http://127.0.0.1:8000/api/v1/records
```

## 10. よく使うURL

| URL | 用途 |
| --- | --- |
| `/health` | ヘルスチェック |
| `/records` | 一覧画面 |
| `/records/{id}` | 詳細画面 |
| `/settings/mappings` | 項目マッピング設定画面 |
| `/api/v1/records` | データ登録 API |
| `/api/v1/records/export.csv` | CSV ダウンロード |
| `/api/v1/records/export.json` | JSON ダウンロード |

## 11. SFTP 定期転送設定

管理画面 `/settings/mappings` から以下を設定できます。

- SFTP接続先IPアドレス
- ユーザ名
- パスワード
- 転送頻度(分)

転送される JSON は、画面の JSON 出力ボタンでダウンロードできるものと同一形式です。
転送先ファイル名は `records_export.json` 固定です。

## 12. トラブルシュート

### 11.1 `No module named ...`

依存パッケージが不足しています。

```bash
python3.9 -m pip install -r requirements.txt
```

`No module named 'paramiko'` の場合も同様に依存パッケージを再導入してください。

### 11.2 `Connection refused`

アプリが起動していません。先に `./scripts/start_app.sh` を実行してください。

### 11.3 DB を作り直したい

`data/app.db` を削除し、再度初期化します。

```bash
rm -f data/app.db
python3.9 scripts/init_db.py
```

## 13. 関連資料

- 詳細な導入手順: [docs/deployment.md](/d:/project/data_connect_viewer/docs/deployment.md)
- 設計書: [docs/design.md](/d:/project/data_connect_viewer/docs/design.md)
