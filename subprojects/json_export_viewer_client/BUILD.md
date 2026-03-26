# BUILD 手順

この文書は `json_export_viewer_client` を `PyInstaller` で `exe` 化する手順です。

## 1. 前提

- OS: Windows
- Python 3.9 以上
- `pip` が利用可能
- ビルド対象: `d:\project\subprojects\json_export_viewer_client`

## 2. 依存導入

```bash
cd D:\project\subprojects\json_export_viewer_client
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

## 3. ビルド

```bash
pyinstaller --noconfirm --onefile --name json_export_viewer_client main.py
```

## 4. 生成物

ビルド後、以下が生成されます。

```text
dist\json_export_viewer_client.exe
```

必要に応じて、配布用フォルダを以下のようにまとめてください。

```text
json_export_viewer_client/
  json_export_viewer_client.exe
  config.ini
  README.md
  sample_data/
```

## 5. 配布時の注意

- `config.ini` は `exe` と同じフォルダに配置してください
- `json_folder` は配布先 PC に存在するパスへ変更してください
- `web` モードでもローカル PC 上の `json_folder` を読み込みます
- 現在の UI は一覧中心で、詳細カードはありません
- サンプル確認用に `sample_data/records_export.json` を同梱できます

## 6. 再ビルド

ソース更新後は再度以下を実行します。

```bash
pyinstaller --noconfirm --onefile --name json_export_viewer_client main.py
```

## 7. 補足

必要に応じて以下を追加できます。

- `--icon` によるアイコン埋め込み
- `--add-data` による追加ファイル同梱
- `spec` ファイルを用いた詳細制御
