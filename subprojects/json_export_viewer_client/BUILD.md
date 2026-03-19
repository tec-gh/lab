# BUILD 手順

この文書は、`json_export_viewer_client` を `PyInstaller` で `exe` 化するための手順です。

## 1. 前提

- OS: Windows
- Python 3.9 以上
- `pip` が利用可能
- ビルド対象フォルダ: `json_export_viewer_client`

## 2. 依存導入

```bash
cd D:\project\subprojects\json_export_viewer_client
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

## 3. ビルド実行

```bash
pyinstaller --noconfirm --onefile --name json_export_viewer_client main.py
```

## 4. 生成物

ビルド後、以下に `exe` が出力されます。

```text
dist\json_export_viewer_client.exe
```

配布時は以下の構成にしてください。

```text
json_export_viewer_client/
  json_export_viewer_client.exe
  config.ini
  README.md
```

必要であれば `sample_data/` も同梱できます。

## 5. 配布時の注意

- `config.ini` は `exe` と同じフォルダに配置してください
- `json_folder` は配布先PCで存在するパスに変更してください
- `web` モードでも `exe` 実行PC上のローカルフォルダを読み込みます
- セキュリティソフトの設定によっては、初回起動時に許可確認が出ることがあります

## 6. 更新時の再ビルド

ソース修正後は、再度以下を実行してください。

```bash
pyinstaller --noconfirm --onefile --name json_export_viewer_client main.py
```

## 7. 補足

必要に応じてアイコンや追加データを含める場合は、`PyInstaller` の `--icon`、`--add-data` オプションを使用してください。
