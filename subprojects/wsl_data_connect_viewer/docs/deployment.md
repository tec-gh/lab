# デプロイ手順

## 1. 前提

- 対象環境: Windows Subsystem for Linux
- Python: 3.12.3
- 必要に応じてインターネット接続環境またはオフライン配備資材を利用する
- 仮想環境を使用する
- `systemd` によるサービス化は行わない
- `nginx` などの外部 Web サーバは使用せず、FastAPI を直接起動して利用する
- メインアプリ本体は `project/data_connect_viewer` 配下を利用する
- WSL サブプロジェクトは `project/subprojects/wsl_data_connect_viewer` に配置する

## 2. 配備物

- アプリケーション一式
- Python パッケージの wheel 一式

## 2.1 pip 未導入時の対応

`python3.12 -m venv` が使えない場合は、先に `venv` を導入する。

Ubuntu 系 WSL の例:

```bash
sudo apt update
sudo apt install -y python3.12-venv
```

`ensurepip` が有効な環境では以下でも導入できる。

```bash
python3.12 -m ensurepip --upgrade
```

## 3. オフライン用 Python パッケージ準備

オフラインで導入する場合、インターネット接続可能な端末で以下を実施する。

```bash
python3.12 -m pip download -r requirements.txt -d wheelhouse
```

作成した `wheelhouse/` を WSL 環境へ持ち込む。

## 4. アプリ配置

以下の構成を前提とする。

```text
/mnt/d/project/
  data_connect_viewer/
  subprojects/
    wsl_data_connect_viewer/
```

設定値を変更する場合は、FastAPI 起動前に環境変数を export する。

```bash
export APP_NAME=data-connect-viewer
export APP_ENV=production
export DATABASE_URL=sqlite:///./data/app.db
export PAGE_SIZE_DEFAULT=20
export EXPORT_MAX_ROWS=10000
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=change_me
export API_KEY=
```

## 5. オフラインインストール

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --no-index --find-links=wheelhouse -r requirements.txt
```

オンラインで導入できる場合:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 6. 初期化

```bash
source .venv/bin/activate
python scripts/init_db.py
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
source .venv/bin/activate
BASE_URL=http://127.0.0.1:8000 python scripts/smoke_test.py
```

WSL では以下でも確認できる。

```bash
source .venv/bin/activate
python scripts/smoke_test.py
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
- 仮想環境有効化後に操作する
- 管理画面認証や API キーは環境変数で切り替える
