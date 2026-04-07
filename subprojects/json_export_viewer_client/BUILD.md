# BUILD 手順書

`json_export_viewer_client.exe` を PyInstaller で生成する手順です。

## 前提条件

- OS: Windows
- Python 3.9 以上
- `pip` が利用可能

## ビルドコマンド

```bash
pyinstaller --noconfirm --onefile --name json_export_viewer_client main.py
```

## 出力先

```text
dist\json_export_viewer_client.exe
```