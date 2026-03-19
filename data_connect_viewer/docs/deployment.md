# デプロイ手順

## 1. 前提

- 対象OS: RHEL 7.9
- Python: 3.9.10
- インターネット非接続環境で動作させる
- 仮想環境は使用しない
- `systemd` によるサービス化は行わない
- `nginx` などの外部 Web サーバは使用せず、FastAPI を直接起動して利用する
- 配備対象は本リポジトリ一式と Python パッケージ一式

## 2. 配備物

- アプリケーション一式
- Python パッケージの wheel 一式

## 3. オフライン用 Python パッケージ準備

インターネット接続可能な端末で以下を実施する。

```bash
python3.9 -m pip download -r requirements.txt -d wheelhouse
```

作成した `wheelhouse/` をアプリと一緒に RHEL サーバへ持ち込む。

## 4. アプリ配置

```bash
mkdir -p /opt/data-connect-viewer
cd /opt/data-connect-viewer
```

アプリ一式を配置する。

設定値を変更する場合は、FastAPI 起動前に環境変数を export する。

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

## 5. オフラインインストール

```bash
python3.9 -m pip install --no-index --find-links=wheelhouse -r requirements.txt
```

## 6. 初期化

```bash
python3.9 scripts/init_db.py
```

## 7. 起動確認

```bash
./scripts/start_app.sh
```

別ターミナルで以下を確認する。

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/records
```

## 8. スモークテスト

```bash
BASE_URL=http://127.0.0.1:8000 python3.9 scripts/smoke_test.py
```

API キーを利用する場合:

```bash
curl -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"hostname":"sv-01","ipaddress":"192.168.0.10"}' \
  http://127.0.0.1/api/v1/records
```

## 9. 運用メモ

- 本アプリは `uvicorn` により直接起動する
- 常駐化しない前提のため、必要時に手動起動・手動停止する
- 管理画面認証や API キーは環境変数で切り替える
