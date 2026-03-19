# WSL 用サブプロジェクト

このサブプロジェクトは、`project/data_connect_viewer` 配下のメイン FastAPI アプリを WSL から実行するための薄いラッパ構成です。
アプリ本体を複製せず、メインプロジェクトのコードを参照して起動します。

## 前提

- 実行環境: Windows Subsystem for Linux
- Python バージョン: 3.12.3
- 仮想環境を使用する
- `uvicorn` により直接起動する

## 起動手順

### 事前確認

`python3.12 -m venv --help` が失敗する場合は、先に `venv` を導入する。

Ubuntu 系 WSL の例:

```bash
sudo apt update
sudo apt install -y python3.12-venv
```

`pip` が無い場合は、仮想環境作成時に自動で入るケースが多いが、必要に応じて以下も実施する。

```bash
python3.12 -m ensurepip --upgrade
```

### 実行

```bash
cd /mnt/d/project/subprojects/wsl_data_connect_viewer
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/init_db.py
./scripts/start_app.sh
```

## 確認

別ターミナルで以下を実行します。

```bash
curl http://127.0.0.1:8000/health
source .venv/bin/activate
BASE_URL=http://127.0.0.1:8000 python scripts/smoke_test.py
```

詳細は [docs/deployment.md](/d:/project/subprojects/wsl_data_connect_viewer/docs/deployment.md) を参照してください。

